"""
Modern z/OS FTP Client with Python 3.10+ features.
"""

import ftplib
import io
import re
import sys
import threading
import concurrent.futures
from collections import deque
from pathlib import Path
from typing import List, Optional, Tuple

from .models import ConnectionConfig, Dataset, Job, PDSMember
from .exceptions import (
    ZosFtpError, ZosConnectionError, AuthenticationError,
    JobNotFoundError, DatasetNotFoundError, JesInterfaceLevelError,
    InvalidJobNameError, TransferError
)


def extract_return_code(output_lines: List[str]) -> Optional[str]:
    """Extract return code from job output.
    
    Parses job output to find the completion code (RC) or ABEND code.
    
    Args:
        output_lines: List of job output lines
        
    Returns:
        Return code string (e.g., "0000", "0004", "ABEND S0C4") or None if not found
    """
    # Pattern 1: $HASP395 jobname ENDED - RC=nnnn
    hasp_pattern = re.compile(r'\$HASP395\s+\S+\s+ENDED\s+-\s+RC=(\d+)', re.IGNORECASE)
    
    # Pattern 2: ENDED.*RC=nnnn (alternative JES format)
    alt_pattern = re.compile(r'ENDED.*RC=(\d+)', re.IGNORECASE)
    
    # Pattern 3: ABEND codes (e.g., ABEND S0C4, ABEND U0001)
    abend_pattern = re.compile(r'ABEND\s+([SU]\d{3,4})', re.IGNORECASE)
    
    # Pattern 4: JCL ERROR or JCL ABEND
    jcl_error_pattern = re.compile(r'JCL\s+(ERROR|ABEND)', re.IGNORECASE)
    
    # Pattern 5: IEF142I step STEP WAS EXECUTED - COND CODE nnnn
    cond_code_pattern = re.compile(r'IEF142I.*COND CODE\s+(\d+)', re.IGNORECASE)
    
    for line in output_lines:
        # Check for HASP395 message (most reliable)
        match = hasp_pattern.search(line)
        if match:
            return match.group(1).zfill(4)  # Pad to 4 digits
        
        # Check for ABEND
        match = abend_pattern.search(line)
        if match:
            return f"ABEND {match.group(1).upper()}"
        
        # Check for JCL ERROR
        match = jcl_error_pattern.search(line)
        if match:
            return f"JCL {match.group(1).upper()}"
    
    # Second pass: look for alternative patterns
    for line in output_lines:
        # Check alternative RC format
        match = alt_pattern.search(line)
        if match:
            return match.group(1).zfill(4)
        
        # Check condition code
        match = cond_code_pattern.search(line)
        if match:
            return match.group(1).zfill(4)
    
    return None


def extract_jobname_from_jcl(jcl: str) -> Optional[str]:
    """Extract jobname from JCL.
    
    Parses the first line of JCL to extract the jobname.
    JCL format: //JOBNAME JOB ...
    
    Args:
        jcl: JCL content as string
        
    Returns:
        Jobname (up to 8 characters) or None if not found
    """
    lines = jcl.strip().split('\n')
    if not lines:
        return None
    
    first_line = lines[0].strip()
    
    # JCL job card pattern: //JOBNAME JOB
    # Jobname can be 1-8 characters, alphanumeric plus national characters (@, #, $)
    match = re.match(r'^//([A-Z0-9@#$]{1,8})\s+JOB\s', first_line, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    return None


class ZosFtpClient:
    """Modern z/OS FTP client with type hints and structured returns."""
    
    def __init__(self, config: ConnectionConfig):
        """Initialize the FTP client.
        
        Args:
            config: Connection configuration
        """
        self.config = config
        self._ftp: Optional[ftplib.FTP] = None
        self._jes_level: Optional[int] = None
        self._connected = False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def connect(self) -> None:
        """Establish FTP connection to mainframe."""
        try:
            self._ftp = ftplib.FTP()
            
            # Note: We use custom debug logging instead of ftplib's set_debuglevel
            # because set_debuglevel can cause blocking issues with stdout
            if self.config.debug:
                print(f"[DEBUG] FTP debug mode enabled", file=sys.stderr)
            
            self._ftp.connect(self.config.host, self.config.port, timeout=self.config.timeout)
            if self.config.debug:
                print(f"[DEBUG] Connected to {self.config.host}:{self.config.port}", file=sys.stderr)
            
            self._ftp.login(self.config.user, self.config.password)
            if self.config.debug:
                print(f"[DEBUG] Logged in as {self.config.user}", file=sys.stderr)
            
            # Verify it's a z/OS system
            syst = self._ftp.sendcmd('SYST')
            if self.config.debug:
                print(f"[DEBUG] SYST response: {syst}", file=sys.stderr)
            if 'z/OS' not in syst:
                raise ZosConnectionError(f"Not a z/OS system: {syst}")
            
            # Set default encoding if configured (persists across all operations)
            # NOTE: SBDATACONN requires ICONV translation tables to be installed on z/OS
            # If not available, FTP will use default 7-bit ASCII to EBCDIC 1047 translation
            if self.config.default_encoding:
                encoding = self.config.default_encoding
                # Remove parentheses if present - z/OS FTP expects format without parens
                if encoding.startswith('(') and encoding.endswith(')'):
                    encoding = encoding[1:-1]
                try:
                    if self.config.debug:
                        print(f"[DEBUG] Sending SITE sbdataconn={encoding}", file=sys.stderr)
                    response = self._ftp.sendcmd(f'SITE sbdataconn={encoding}')
                    if self.config.debug:
                        print(f"[DEBUG] SBDATACONN response: {response}", file=sys.stderr)
                except Exception as e:
                    if self.config.debug:
                        print(f"[DEBUG] SBDATACONN failed: {e}, using default translation", file=sys.stderr)
            
            # Set default line ending if configured
            if self.config.default_line_ending:
                if self.config.debug:
                    print(f"[DEBUG] Sending SITE SBSENDEOL={self.config.default_line_ending.upper()}", file=sys.stderr)
                response = self._ftp.sendcmd(f'SITE SBSENDEOL={self.config.default_line_ending.upper()}')
                if self.config.debug:
                    print(f"[DEBUG] SBSENDEOL response: {response}", file=sys.stderr)
            
            # Detect JES interface level
            self._detect_jes_level()
            self._connected = True
            
        except ftplib.error_perm as e:
            raise AuthenticationError(f"Login failed: {str(e)}")
        except Exception as e:
            raise ZosConnectionError(f"Connection failed: {str(e)}")
    
    def disconnect(self) -> None:
        """Close FTP connection."""
        if self._ftp:
            try:
                self._ftp.quit()
            except Exception:
                pass
            finally:
                self._ftp = None
                self._connected = False
    
    def _detect_jes_level(self) -> None:
        """Detect JESINTERFACELEVEL from server."""
        try:
            stat = self._ftp.sendcmd('STAT')
            match = re.search(r'JESINTERFACELEVEL.*?(\d)', stat)
            if match:
                self._jes_level = int(match.group(1))
            else:
                self._jes_level = 1  # Default to 1
        except Exception:
            self._jes_level = 1
    
    @property
    def jes_interface_level(self) -> int:
        """Get JES interface level."""
        return self._jes_level or 1
    
    def _ensure_connected(self) -> None:
        """Ensure FTP connection is active."""
        if not self._connected or not self._ftp:
            raise ZosConnectionError("Not connected. Call connect() first.")
    
    def _sanitize_dataset_name(self, name: str) -> str:
        """Sanitize MVS dataset name."""
        if name:
            return "'" + name.strip().replace("'", "").replace('"', '') + "'"
        return name
    
    def _validate_jobname_for_jes1(self, jobname: str) -> None:
        """Validate jobname for JESINTERFACELEVEL=1.
        
        Args:
            jobname: Job name to validate
            
        Raises:
            InvalidJobNameError: If jobname doesn't match required pattern
        """
        if self.jes_interface_level == 1:
            userid = self.config.user
            # Jobname must be userid + exactly one character
            if not (jobname.startswith(userid) and len(jobname) == len(userid) + 1):
                raise InvalidJobNameError(jobname, userid)
    
    # ========== Dataset Operations ==========
    
    def list_datasets(self, pattern: str) -> List[Dataset]:
        """List datasets matching pattern.
        
        Args:
            pattern: Dataset name pattern (e.g., 'USER.*')
            
        Returns:
            List of Dataset objects
        """
        self._ensure_connected()
        
        datasets = []
        pattern = self._sanitize_dataset_name(pattern)
        
        if self.config.debug:
            print(f"[DEBUG] Listing datasets matching pattern: {pattern}", file=sys.stderr)
        
        # Switch to SEQ mode
        response = self._ftp.sendcmd('SITE FILETYPE=SEQ')
        if self.config.debug:
            print(f"[DEBUG] SITE FILETYPE=SEQ response: {response}", file=sys.stderr)
        
        response = self._ftp.cwd("''")
        if self.config.debug:
            print(f"[DEBUG] CWD '' response: {response}", file=sys.stderr)
        
        def parse_line(line: str):
            """Parse catalog listing line."""
            if 'DSNAME' in line.upper():
                return  # Skip header
            
            # Parse fixed-width format
            ds = Dataset(
                name=line[56:].replace("'", "").strip(),
                volume=line[0:6].strip() or None,
                unit=line[7:14].strip() or None,
                referred=line[14:24].strip() or None,
                ext=line[24:27].strip() or None,
                used=line[27:32].strip() or None,
                recfm=line[34:39].strip() or None,
                lrecl=line[39:44].strip() or None,
                blksz=line[45:50].strip() or None,
                dsorg=line[51:55].strip() or None
            )
            if ds.name:
                datasets.append(ds)
        
        try:
            self._ftp.dir(pattern, parse_line)
            if self.config.debug:
                print(f"[DEBUG] Found {len(datasets)} datasets", file=sys.stderr)
        except ftplib.error_perm as e:
            if '550 No data sets found' in str(e):
                if self.config.debug:
                    print(f"[DEBUG] No datasets found matching {pattern}", file=sys.stderr)
                return []
            raise DatasetNotFoundError(str(e))
        
        return datasets

    
    def download_dataset(self, name: str, target: Path, binary: bool = False,
                        line_ending: Optional[str] = None,
                        preserve_trailing_spaces: Optional[bool] = None) -> Path:
        """Download a dataset.
        
        Args:
            name: Dataset name
            target: Target file path
            binary: Download in binary mode
            line_ending: Line ending format ('CRLF', 'LF', 'CR', 'NONE'). Uses default_line_ending if not specified.
            preserve_trailing_spaces: Preserve trailing blanks. Uses config default if not specified.
            
        Returns:
            Path to downloaded file
        """
        self._ensure_connected()
        
        name = self._sanitize_dataset_name(name)
        
        if self.config.debug:
            mode = "binary" if binary else "text"
            print(f"[DEBUG] Downloading dataset {name} in {mode} mode to {target}", file=sys.stderr)
        
        response = self._ftp.sendcmd('SITE FILETYPE=SEQ')
        if self.config.debug:
            print(f"[DEBUG] SITE FILETYPE=SEQ response: {response}", file=sys.stderr)
        
        # Override line ending if specified (encoding is set at connection time)
        if not binary and line_ending:
            response = self._ftp.sendcmd(f'SITE SBSENDEOL={line_ending.upper()}')
            if self.config.debug:
                print(f"[DEBUG] SITE SBSENDEOL={line_ending.upper()} response: {response}", file=sys.stderr)
        
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Helper functions to avoid lambda closure issues
        def write_line_with_spaces(f, line_end):
            def writer(line):
                f.write(line + line_end)
            return writer
        
        def write_line_stripped(f, line_end):
            def writer(line):
                f.write(line.rstrip() + line_end)
            return writer
        
        try:
            if binary:
                response = self._ftp.sendcmd('SITE RDW')
                if self.config.debug:
                    print(f"[DEBUG] SITE RDW response: {response}", file=sys.stderr)
                with open(target, 'wb') as f:
                    self._ftp.retrbinary(f'RETR {name}', f.write)
            else:
                # Text mode download
                actual_line_ending = line_ending or self.config.default_line_ending
                actual_preserve_spaces = preserve_trailing_spaces if preserve_trailing_spaces is not None else self.config.preserve_trailing_spaces
                
                # Determine line ending to add (retrlines strips CRLF, we add back what we want)
                line_ending_map = {'CRLF': '\r\n', 'LF': '\n', 'CR': '\r', 'NONE': ''}
                actual_line_ending_str = line_ending_map.get(actual_line_ending, '\n') if actual_line_ending else '\n'
                
                # Use retrlines for text mode
                # Note: retrlines strips CRLF, so we add back the desired line ending
                with open(target, 'w') as f:
                    if actual_preserve_spaces:
                        self._ftp.retrlines(f'RETR {name}', write_line_with_spaces(f, actual_line_ending_str))
                    else:
                        self._ftp.retrlines(f'RETR {name}', write_line_stripped(f, actual_line_ending_str))
            
            if self.config.debug:
                size = target.stat().st_size
                print(f"[DEBUG] Download complete: {size} bytes written to {target}", file=sys.stderr)
        except ftplib.error_perm as e:
            if self.config.debug:
                print(f"[DEBUG] Download failed: {e}", file=sys.stderr)
            raise DatasetNotFoundError(f"Cannot download {name}: {str(e)}")
        except Exception as e:
            if self.config.debug:
                print(f"[DEBUG] Download failed: {e}", file=sys.stderr)
            raise TransferError(f"Download failed: {str(e)}")
        
        return target
    
    def upload_dataset(self, source: Path, name: str, binary: bool = False, 
                      site_params: str = '') -> None:
        """Upload a dataset.
        
        Args:
            source: Source file path
            name: Target dataset name
            binary: Upload in binary mode
            site_params: Additional SITE parameters (e.g., 'lrecl=80 blk=3200 recfm=FB cyl pri=1 sec=5')
        """
        self._ensure_connected()
        
        source = Path(source)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        name = self._sanitize_dataset_name(name)
        self._ftp.sendcmd('SITE FILETYPE=SEQ')
        
        if site_params:
            self._ftp.sendcmd(f'SITE {site_params}')
        
        try:
            with open(source, 'rb') as f:
                if binary:
                    self._ftp.storbinary(f'STOR {name}', f)
                else:
                    self._ftp.storlines(f'STOR {name}', f)
        except Exception as e:
            raise TransferError(f"Upload failed: {str(e)}")

    
    def download_pds_members(self, pds: str, members: List[str], 
                            target_dir: Path, binary: bool = False,
                            extension: str = '',
                            line_ending: Optional[str] = None,
                            preserve_trailing_spaces: Optional[bool] = None) -> Tuple[List[Path], List[str]]:
        """Download members from a PDS.
        
        Args:
            pds: PDS name
            members: List of member names (or ['*'] for all)
            target_dir: Target directory
            binary: Download in binary mode
            extension: File extension to add (e.g., '.jcl', '.cbl', '.txt')
            line_ending: Line ending format ('CRLF', 'LF', 'CR', 'NONE'). Uses default_line_ending if not specified.
            preserve_trailing_spaces: Preserve trailing blanks. Uses config default if not specified.
            
        Returns:
            Tuple of (downloaded_paths, failed_members) where:
                - downloaded_paths: List of successfully downloaded file paths
                - failed_members: List of error messages for failed downloads
        """
        self._ensure_connected()
        
        pds = self._sanitize_dataset_name(pds)
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        mode = "binary" if binary else "text"
        if self.config.debug:
            print(f"[DEBUG] Downloading PDS members from {pds} in {mode} mode", file=sys.stderr)
        
        response = self._ftp.sendcmd('SITE FILETYPE=SEQ')
        if self.config.debug:
            print(f"[DEBUG] SITE FILETYPE=SEQ response: {response}", file=sys.stderr)
        
        # Override line ending if specified (encoding is set at connection time)
        if not binary and line_ending:
            response = self._ftp.sendcmd(f'SITE SBSENDEOL={line_ending.upper()}')
            if self.config.debug:
                print(f"[DEBUG] SITE SBSENDEOL={line_ending.upper()} response: {response}", file=sys.stderr)
        
        # CWD into PDS (sanitize_dataset_name already adds quotes)
        try:
            response = self._ftp.cwd(pds)
            if self.config.debug:
                print(f"[DEBUG] CWD {pds} response: {response}", file=sys.stderr)
            if 'partitioned data set' not in response.lower():
                raise DatasetNotFoundError(f"{pds} is not a partitioned dataset")
        except Exception as e:
            if self.config.debug:
                print(f"[DEBUG] Cannot access PDS: {e}", file=sys.stderr)
            raise DatasetNotFoundError(f"Cannot access PDS {pds}: {str(e)}")
        
        # Get member list if needed
        if not members or members == ['*']:
            members = self._ftp.nlst()
            if self.config.debug:
                print(f"[DEBUG] Retrieved {len(members)} members from PDS", file=sys.stderr)
        elif isinstance(members, str):
            # Single member as string
            members = [members]
        
        # Determine line ending to add (retrlines strips CRLF, we add back what we want)
        actual_line_ending = line_ending or self.config.default_line_ending
        actual_preserve_spaces = preserve_trailing_spaces if preserve_trailing_spaces is not None else self.config.preserve_trailing_spaces
        line_ending_map = {'CRLF': '\r\n', 'LF': '\n', 'CR': '\r', 'NONE': ''}
        actual_line_ending_str = line_ending_map.get(actual_line_ending, '\n') if not binary and actual_line_ending else '\n'
        
        # Helper functions to avoid lambda closure issues
        def write_line_with_spaces(f, line_end):
            def writer(line):
                f.write(line + line_end)
            return writer
        
        def write_line_stripped(f, line_end):
            def writer(line):
                f.write(line.rstrip() + line_end)
            return writer
        
        downloaded = []
        failed = []
        for member in members:
            # Add extension if provided
            filename = f"{member}{extension}" if extension else member
            target = target_dir / filename
            
            if self.config.debug:
                print(f"[DEBUG] Downloading member: {member}", file=sys.stderr)
            
            # Use simple RETR member (we're already in the PDS via CWD)
            try:
                if binary:
                    with open(target, 'wb') as f:
                        self._ftp.retrbinary(f'RETR {member}', f.write)
                else:
                    # Text mode - use retrlines for EBCDIC-to-ASCII conversion
                    # Note: retrlines strips CRLF, so we add back the desired line ending
                    with open(target, 'w') as f:
                        if actual_preserve_spaces:
                            self._ftp.retrlines(f'RETR {member}', write_line_with_spaces(f, actual_line_ending_str))
                        else:
                            self._ftp.retrlines(f'RETR {member}', write_line_stripped(f, actual_line_ending_str))
                downloaded.append(target)
                if self.config.debug:
                    size = target.stat().st_size
                    print(f"[DEBUG] Downloaded {member}: {size} bytes", file=sys.stderr)
            except Exception as e:
                # Log error but continue with other members
                error_msg = f"{member}: {str(e)}"
                print(f"Error downloading {error_msg}", file=sys.stderr)
                if self.config.debug:
                    print(f"[DEBUG] Failed to download {member}: {e}", file=sys.stderr)
                failed.append(error_msg)
        
        if self.config.debug:
            print(f"[DEBUG] PDS download complete: {len(downloaded)} succeeded, {len(failed)} failed", file=sys.stderr)
        
        # Return both successful and failed downloads
        return downloaded, failed
    
    # ========== Job Operations ==========
    
    def submit_job(self, jcl: str, jobname: str = '') -> Job:
        """Submit a JCL job.
        
        Args:
            jcl: JCL content
            jobname: Deprecated - jobname is extracted from JCL automatically
            
        Returns:
            Job object with job ID
            
        Raises:
            ZosFtpError: If JCL is invalid or jobname cannot be extracted
            InvalidJobNameError: If jobname doesn't match JESINTERFACELEVEL=1 requirements
        """
        self._ensure_connected()
        
        # Extract jobname from JCL
        extracted_jobname = extract_jobname_from_jcl(jcl)
        if not extracted_jobname:
            raise ZosFtpError("Cannot extract jobname from JCL. First line must be: //JOBNAME JOB ...")
        
        # Validate jobname for JESINTERFACELEVEL=1
        self._validate_jobname_for_jes1(extracted_jobname)
        
        if self.config.debug:
            jcl_lines = jcl.count('\n') + 1
            print(f"[DEBUG] Submitting job {extracted_jobname} ({jcl_lines} lines of JCL)", file=sys.stderr)
        
        # Switch to JES mode
        response = self._ftp.sendcmd('SITE FILETYPE=JES')
        if self.config.debug:
            print(f"[DEBUG] SITE FILETYPE=JES response: {response}", file=sys.stderr)
        
        # Submit job - create a file-like object from JCL
        import io
        jcl_file = io.BytesIO(jcl.encode())
        response = self._ftp.storlines('STOR INTRDR', jcl_file)
        
        if self.config.debug:
            print(f"[DEBUG] STOR INTRDR response: {response}", file=sys.stderr)
        
        # Extract job ID from response
        match = re.search(r'(JOB\d{5})', response)
        if not match:
            raise ZosFtpError(f"Could not extract job ID from response: {response}")
        
        jobid = match.group(1)
        
        if self.config.debug:
            print(f"[DEBUG] Job submitted successfully: {jobid}", file=sys.stderr)
        
        # Get job info
        try:
            return self.get_job_info(jobid)
        except Exception:
            # Return minimal info if we can't get details
            return Job(
                jobid=jobid,
                jobname=extracted_jobname,
                status="SUBMITTED"
            )
    
    def list_jobs(self, jobmask: str = '', owner: str = '', 
                  status: str = 'ALL') -> List[Job]:
        """List jobs from JES spool.
        
        Args:
            jobmask: Job name pattern (supports wildcards: * and ?)
            owner: Job owner (defaults to current user)
            status: Job status filter - 'ALL' (default), 'OUTPUT', 'ACTIVE', 'INPUT'
            
        Returns:
            List of Job objects
            
        Note:
            With JESINTERFACELEVEL=1, server-side filtering may not work.
            Client-side filtering is applied to jobmask parameter.
        """
        self._ensure_connected()
        
        if self.config.debug:
            print(f"[DEBUG] Listing jobs: jobmask={jobmask or 'none'}, owner={owner or 'current'}, status={status}", file=sys.stderr)
        
        # Switch to JES mode
        response = self._ftp.sendcmd('SITE FILETYPE=JES')
        if self.config.debug:
            print(f"[DEBUG] SITE FILETYPE=JES response: {response}", file=sys.stderr)
        
        # Try to set server-side filters (may not work with JESINTERFACELEVEL=1)
        if jobmask:
            try:
                response = self._ftp.sendcmd(f'SITE JESJOBNAME={jobmask}')
                if self.config.debug:
                    print(f"[DEBUG] SITE JESJOBNAME={jobmask} response: {response}", file=sys.stderr)
            except Exception as e:
                if self.config.debug:
                    print(f"[DEBUG] SITE JESJOBNAME failed: {e}", file=sys.stderr)
        
        if owner:
            try:
                response = self._ftp.sendcmd(f'SITE JESOWNER={owner}')
                if self.config.debug:
                    print(f"[DEBUG] SITE JESOWNER={owner} response: {response}", file=sys.stderr)
            except Exception as e:
                if self.config.debug:
                    print(f"[DEBUG] SITE JESOWNER failed: {e}", file=sys.stderr)
        
        if status and status.upper() in ('ALL', 'INPUT', 'OUTPUT', 'ACTIVE'):
            try:
                response = self._ftp.sendcmd(f'SITE JESSTATUS={status.upper()}')
                if self.config.debug:
                    print(f"[DEBUG] SITE JESSTATUS={status.upper()} response: {response}", file=sys.stderr)
            except Exception as e:
                if self.config.debug:
                    print(f"[DEBUG] SITE JESSTATUS failed: {e}", file=sys.stderr)
        
        # Get job list
        job_lines = []
        try:
            self._ftp.retrlines('LIST', job_lines.append)
        except ftplib.error_perm as e:
            if 'No jobs found' in str(e):
                return []
            raise
        
        # Parse jobs
        jobs = []
        for line in job_lines:
            if line and not line.startswith('JOBNAME'):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        spool_count = int(parts[3])
                    except (ValueError, IndexError):
                        spool_count = 0
                    
                    job = Job(
                        jobname=parts[0],
                        jobid=parts[1],
                        status=parts[2],
                        spool_files=spool_count
                    )
                    jobs.append(job)
        
        # Apply client-side filtering if server-side didn't work
        if jobmask:
            import fnmatch
            original_count = len(jobs)
            jobs = [job for job in jobs if fnmatch.fnmatch(job.jobname, jobmask)]
            if self.config.debug:
                print(f"[DEBUG] Client-side filtering: {original_count} -> {len(jobs)} jobs", file=sys.stderr)
        
        if self.config.debug:
            print(f"[DEBUG] Found {len(jobs)} jobs", file=sys.stderr)
        
        return jobs
    
    def get_job_info(self, jobid: str) -> Job:
        """Get detailed job information.
        
        Args:
            jobid: Job ID
            
        Returns:
            Job object with details
        """
        self._ensure_connected()
        
        if self.config.debug:
            print(f"[DEBUG] Getting job info for: {jobid}", file=sys.stderr)
        
        # Switch to JES mode
        response = self._ftp.sendcmd('SITE FILETYPE=JES')
        if self.config.debug:
            print(f"[DEBUG] SITE FILETYPE=JES response: {response}", file=sys.stderr)
        
        # Get job info
        job_lines = []
        try:
            self._ftp.retrlines(f'LIST {jobid}', job_lines.append)
        except ftplib.error_perm as e:
            raise JobNotFoundError(f"Job {jobid} not found: {str(e)}")
        
        # Parse job info
        for line in job_lines:
            if line and not line.startswith('JOBNAME') and jobid in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        spool_count = int(parts[3])
                    except (ValueError, IndexError):
                        spool_count = 0
                    
                    return Job(
                        jobname=parts[0],
                        jobid=parts[1],
                        status=parts[2],
                        spool_files=spool_count
                    )
        
        raise JobNotFoundError(f"Job {jobid} not found in output")
    
    def download_job_spool(self, jobid: str, target: Path) -> Tuple[Path, Optional[str]]:
        """Download job spool output with clear separators and extract return code.
        
        Args:
            jobid: Job ID
            target: Target file path
            
        Returns:
            Tuple of (Path to downloaded file, Return code or None)
        """
        self._ensure_connected()
        
        if self.config.debug:
            print(f"[DEBUG] Downloading spool for job: {jobid}", file=sys.stderr)
        
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Switch to JES mode
        response = self._ftp.sendcmd('SITE FILETYPE=JES')
        if self.config.debug:
            print(f"[DEBUG] SITE FILETYPE=JES response: {response}", file=sys.stderr)
        
        # Open file for streaming write
        spool_count = 0
        return_code_lines: deque = deque(maxlen=100)  # O(1) buffer for return code extraction
        
        with open(target, 'w') as f:
            # Helper function to write line and optionally buffer for RC extraction
            def write_line(line):
                f.write(line + '\n')
                return_code_lines.append(line)
            
            # Write header
            write_line("=" * 80)
            write_line(f"JOB SPOOL OUTPUT FOR: {jobid}")
            write_line("=" * 80)
            write_line("")
            
            try:
                # Try direct retrieval (gets all spool files)
                def process_line(line):
                    nonlocal spool_count
                    if "!! END OF JES SPOOL FILE !!" in line:
                        spool_count += 1
                        write_line("")
                        write_line("=" * 80)
                        write_line(f"END OF SPOOL FILE #{spool_count}")
                        write_line("=" * 80)
                        write_line("")
                    else:
                        write_line(line)
                
                if self.config.debug:
                    print(f"[DEBUG] Attempting RETR {jobid}", file=sys.stderr)
                self._ftp.retrlines(f'RETR {jobid}', process_line)
                if self.config.debug:
                    print(f"[DEBUG] Retrieved {spool_count} spool files", file=sys.stderr)
                
            except ftplib.error_perm as e:
                if self.config.debug:
                    print(f"[DEBUG] RETR {jobid} failed: {e}, trying {jobid}.x", file=sys.stderr)
                # Try with .x suffix
                try:
                    def process_line_x(line):
                        nonlocal spool_count
                        if "!! END OF JES SPOOL FILE !!" in line:
                            spool_count += 1
                            write_line("")
                            write_line("=" * 80)
                            write_line(f"END OF SPOOL FILE #{spool_count}")
                            write_line("=" * 80)
                            write_line("")
                        else:
                            write_line(line)
                    
                    self._ftp.retrlines(f'RETR {jobid}.x', process_line_x)
                    if self.config.debug:
                        print(f"[DEBUG] Retrieved {spool_count} spool files using .x suffix", file=sys.stderr)
                    
                except ftplib.error_perm as e2:
                    if self.config.debug:
                        print(f"[DEBUG] RETR {jobid}.x failed: {e2}, trying individual files", file=sys.stderr)
                    # Try individual spool files
                    for i in range(1, 20):
                        try:
                            spool_count += 1
                            write_line("=" * 80)
                            write_line(f"SPOOL FILE #{spool_count} (ID: {i})")
                            write_line("=" * 80)
                            
                            self._ftp.retrlines(f'RETR {jobid}.{i}', write_line)
                            
                            write_line("")
                            write_line("=" * 80)
                            write_line(f"END OF SPOOL FILE #{spool_count}")
                            write_line("=" * 80)
                            write_line("")
                        except Exception:
                            spool_count -= 1  # Decrement if this spool file doesn't exist
                            break
                    if self.config.debug:
                        print(f"[DEBUG] Retrieved {spool_count} individual spool files", file=sys.stderr)
            
            # Write footer
            if spool_count > 0:
                write_line("")
                write_line("=" * 80)
                write_line(f"TOTAL SPOOL FILES: {spool_count}")
                write_line("=" * 80)
        
        if spool_count == 0:
            if self.config.debug:
                print(f"[DEBUG] No spool output found for {jobid}", file=sys.stderr)
            raise JobNotFoundError(
                f"No spool output for job {jobid}. "
                f"Job may be purged or inaccessible with JESINTERFACELEVEL={self.jes_interface_level}"
            )
        
        # Extract return code from buffered lines
        return_code = extract_return_code(return_code_lines)
        
        if self.config.debug:
            size = target.stat().st_size
            print(f"[DEBUG] Spool download complete: {size} bytes, return_code={return_code or 'not found'}", file=sys.stderr)
        
        return target, return_code
    
    def delete_job(self, jobid: str) -> bool:
        """Delete a job from JES spool.
        
        Args:
            jobid: Job ID
            
        Returns:
            True if successful
        """
        self._ensure_connected()
        
        # Switch to JES mode
        self._ftp.sendcmd('SITE FILETYPE=JES')
        
        try:
            self._ftp.sendcmd(f'DELE {jobid}')
            return True
        except ftplib.error_perm:
            return False
    
    # ========== Utility Methods ==========
    
    def test_connection(self) -> bool:
        """Test if connection is working.
        
        Returns:
            True if connected and working
        """
        try:
            self._ensure_connected()
            self._ftp.sendcmd('NOOP')
            return True
        except Exception:
            return False
    
    def get_connection_info(self) -> dict:
        """Get current connection information.
        
        Returns:
            Dictionary with connection details
        """
        return {
            "host": self.config.host,
            "port": self.config.port,
            "user": self.config.user,
            "connected": self._connected,
            "jes_interface_level": self.jes_interface_level,
            "timeout": self.config.timeout,
            "download_path": self.config.download_path,
            "default_encoding": self.config.default_encoding or "none",
            "default_line_ending": self.config.default_line_ending or "none",
            "preserve_trailing_spaces": self.config.preserve_trailing_spaces
        }

    
    def get_dataset_text(self, name: str) -> str:
        """Get dataset content as text string.
        
        Args:
            name: Dataset name
            
        Returns:
            Dataset content as string
        """
        self._ensure_connected()
        
        name = self._sanitize_dataset_name(name)
        self._ftp.sendcmd('SITE FILETYPE=SEQ')
        
        lines = []
        try:
            self._ftp.retrlines(f'RETR {name}', lines.append)
        except ftplib.error_perm as e:
            raise DatasetNotFoundError(f"Cannot retrieve {name}: {str(e)}")
        
        return '\n'.join(lines)
    
    def get_dataset_binary(self, name: str) -> bytes:
        """Get dataset content as bytes.
        
        Args:
            name: Dataset name
            
        Returns:
            Dataset content as bytes
        """
        self._ensure_connected()
        
        name = self._sanitize_dataset_name(name)
        self._ftp.sendcmd('SITE FILETYPE=SEQ')
        self._ftp.sendcmd('SITE RDW')
        
        data = bytearray()
        try:
            self._ftp.retrbinary(f'RETR {name}', data.extend)
        except ftplib.error_perm as e:
            raise DatasetNotFoundError(f"Cannot retrieve {name}: {str(e)}")
        
        return bytes(data)
    
    def get_pds_directory(self, pds: str, with_attrs: bool = False) -> dict:
        """Get PDS directory listing.
        
        Args:
            pds: PDS name
            with_attrs: Include member attributes
            
        Returns:
            Dictionary of member names to attributes (or None if with_attrs=False)
        """
        self._ensure_connected()
        
        pds = self._sanitize_dataset_name(pds)
        self._ftp.sendcmd('SITE FILETYPE=SEQ')
        
        # Check if PDS
        response = self._ftp.cwd(pds)
        if 'partitioned data set' not in response:
            raise DatasetNotFoundError(f"{pds} is not a partitioned dataset")
        
        directory = {}
        
        if with_attrs:
            # Parse detailed directory listing
            def parse_line(line: str):
                if 'NAME' in line.upper():
                    return  # Skip header
                member = line[0:8].strip()
                if member:
                    # Parse attributes based on format
                    directory[member] = {
                        'size': line[44:49].strip() if len(line) > 49 else None,
                        'created': line[16:26].strip() if len(line) > 26 else None,
                        'changed': line[27:37].strip() if len(line) > 37 else None,
                    }
            
            try:
                self._ftp.dir(parse_line)
            except ftplib.error_perm as e:
                if "550 No members found" in str(e):
                    return {}
                raise
        else:
            # Simple member list
            try:
                members = self._ftp.nlst()
                directory = {m: None for m in members}
            except ftplib.error_perm as e:
                if "550 No members found" in str(e):
                    return {}
                raise
        
        return directory
    
    def submit_and_wait_job(self, jcl: str, jobname: str = '', 
                           timeout: Optional[float] = None,
                           purge: bool = False) -> Tuple[Job, str]:
        """Submit a job and wait for completion, returning output with return code.
        
        Args:
            jcl: JCL content
            jobname: Job name (must follow JESINTERFACELEVEL=1 rules)
            timeout: Wait timeout in seconds (None = use connection timeout)
            purge: Delete job after retrieving output
            
        Returns:
            Tuple of (Job object with return_code, output string)
            
        Note:
            This method uploads JCL to a temporary dataset, submits it,
            and waits for completion. Your session will be suspended
            during job execution.
        """
        self._ensure_connected()
        
        if jobname:
            self._validate_jobname_for_jes1(jobname)
        else:
            jobname = self.config.user
        
        # Create temporary dataset name
        temp_dataset = f"'{self.config.user}.FTPTEMP0.CNTL'"
        
        # Upload JCL to temporary dataset
        self._ftp.sendcmd('SITE FILETYPE=SEQ')
        self._ftp.sendcmd('SITE lrecl=80 blk=3200 cyl pri=1 sec=5')
        
        import io
        jcl_file = io.BytesIO(jcl.encode())
        self._ftp.storlines(f'STOR {temp_dataset}', jcl_file)
        
        # Switch to JES mode and submit
        self._ftp.sendcmd('SITE FILETYPE=JES NOJESGETBYDSN')
        
        if self.jes_interface_level == 1:
            if not jobname.startswith(self.config.user):
                raise InvalidJobNameError(jobname, self.config.user)
        
        self._ftp.sendcmd(f'SITE JESJOBNAME={jobname}*')
        
        # Retrieve (this waits for job completion)
        output_lines = []
        self._ftp.retrlines(f'RETR {temp_dataset}', output_lines.append)
        
        output = '\n'.join(output_lines)
        
        # Extract return code from output
        return_code = extract_return_code(output_lines)
        
        # Extract job ID from output
        match = re.search(r'(JOB\d{5})', output)
        if match:
            jobid = match.group(1)
            try:
                job = self.get_job_info(jobid)
                job.return_code = return_code  # Add extracted return code
                
                if purge:
                    self.delete_job(jobid)
                    job.status += ' (purged)'
                
                return job, output
            except Exception:
                # Return minimal job info if we can't get details
                return Job(
                    jobid=jobid,
                    jobname=jobname,
                    status="COMPLETED",
                    return_code=return_code
                ), output
        
        raise ZosFtpError("Could not extract job ID from output")

    
    def download_pds_members_parallel(self, pds: str, members: List[str],
                                     target_dir: Path, binary: bool = False,
                                     max_workers: int = 4, extension: str = '',
                                     line_ending: Optional[str] = None,
                                     preserve_trailing_spaces: Optional[bool] = None) -> Tuple[List[Path], List[str]]:
        """Download PDS members in parallel using multiple FTP connections.
        
        Args:
            pds: PDS name
            members: List of member names (or ['*'] for all)
            target_dir: Target directory
            binary: Download in binary mode
            max_workers: Number of parallel FTP connections (1-16)
            extension: File extension to add (e.g., '.jcl', '.cbl', '.txt')
            line_ending: Line ending format ('CRLF', 'LF', 'CR', 'NONE'). Uses default_line_ending if not specified.
            preserve_trailing_spaces: Preserve trailing blanks. Uses config default if not specified.
            
        Returns:
            Tuple of (downloaded_paths, failed_members) where:
                - downloaded_paths: List of successfully downloaded file paths
                - failed_members: List of error messages for failed downloads
            
        Note:
            This is significantly faster than sequential downloads for large PDSs.
            Each worker creates its own FTP connection with encoding set at connection time.
        """
        self._ensure_connected()
        
        pds = self._sanitize_dataset_name(pds)
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Get member list if needed
        if members == ['*'] or not members:
            members = list(self.get_pds_directory(pds, with_attrs=False).keys())
        
        if not members:
            return [], []  # Fixed: return proper tuple type
        
        # Limit workers
        max_workers = min(max(1, max_workers), 16)
        
        mode = "binary" if binary else "text"
        if self.config.debug:
            print(f"[DEBUG] Parallel download: {len(members)} members from {pds} using {max_workers} workers in {mode} mode", file=sys.stderr)
        
        # Determine actual line ending and preserve spaces
        actual_line_ending = line_ending or self.config.default_line_ending
        actual_preserve_spaces = preserve_trailing_spaces if preserve_trailing_spaces is not None else self.config.preserve_trailing_spaces
        
        # Helper functions to avoid lambda closure issues
        def write_line_with_spaces(f, line_end):
            def writer(line):
                f.write(line + line_end)
            return writer
        
        def write_line_stripped(f, line_end):
            def writer(line):
                f.write(line.rstrip() + line_end)
            return writer
        
        downloaded = []
        failed = []
        lock = threading.Lock()
        
        def download_member(member: str) -> Optional[Path]:
            """Download a single member using a new FTP connection."""
            worker_ftp = None
            try:
                # Create new FTP connection for this thread
                worker_ftp = ftplib.FTP()
                worker_ftp.connect(self.config.host, self.config.port, 
                                  timeout=self.config.timeout)
                worker_ftp.login(self.config.user, self.config.password)
                
                # Set encoding at connection time (like main connection)
                if self.config.default_encoding:
                    encoding = self.config.default_encoding
                    # Remove parentheses if present - z/OS FTP expects format without parens
                    if encoding.startswith('(') and encoding.endswith(')'):
                        encoding = encoding[1:-1]
                    try:
                        worker_ftp.sendcmd(f'SITE sbdataconn={encoding}')
                    except Exception:
                        pass  # Ignore SBDATACONN errors, use default translation
                
                # Set default line ending at connection time
                if self.config.default_line_ending:
                    worker_ftp.sendcmd(f'SITE SBSENDEOL={self.config.default_line_ending.upper()}')
                
                worker_ftp.sendcmd('SITE FILETYPE=SEQ')
                
                # Override line ending if specified for this download
                if not binary and line_ending:
                    worker_ftp.sendcmd(f'SITE SBSENDEOL={line_ending.upper()}')
                
                # CWD into PDS
                worker_ftp.cwd(pds)
                
                # Determine line ending to add (retrlines strips CRLF, we add back what we want)
                line_ending_map = {'CRLF': '\r\n', 'LF': '\n', 'CR': '\r', 'NONE': ''}
                actual_line_ending_str = line_ending_map.get(actual_line_ending, '\n') if not binary and actual_line_ending else '\n'
                
                # Add extension if provided
                filename = f"{member}{extension}" if extension else member
                target = target_dir / filename
                
                # Use simple RETR member (we're already in the PDS via CWD)
                if binary:
                    with open(target, 'wb') as f:
                        worker_ftp.retrbinary(f'RETR {member}', f.write)
                else:
                    # Use retrlines for text mode
                    with open(target, 'w') as f:
                        if actual_preserve_spaces:
                            worker_ftp.retrlines(f'RETR {member}', write_line_with_spaces(f, actual_line_ending_str))
                        else:
                            worker_ftp.retrlines(f'RETR {member}', write_line_stripped(f, actual_line_ending_str))
                
                with lock:
                    downloaded.append(target)
                
                return target
                
            except Exception as e:
                with lock:
                    failed.append((member, str(e)))
                return None
            finally:
                # Ensure FTP connection is always closed
                if worker_ftp:
                    try:
                        worker_ftp.quit()
                    except Exception:
                        pass
        
        # Download in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(download_member, member) for member in members]
            concurrent.futures.wait(futures)
        
        if self.config.debug:
            print(f"[DEBUG] Parallel download complete: {len(downloaded)} succeeded, {len(failed)} failed", file=sys.stderr)
        
        if failed and not downloaded:
            # All downloads failed
            raise TransferError(
                f"Failed to download any members. First error: {failed[0][1]}"
            )
        
        return downloaded, [f"{m}: {e}" for m, e in failed]

