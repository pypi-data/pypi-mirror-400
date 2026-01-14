"""
Modern MCP server using ZosFtpClient.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

try:
    from .zos_ftp import ZosFtpClient
    from .models import ConnectionConfig
    from .exceptions import (
        ZosFtpError, ZosConnectionError, AuthenticationError,
        JobNotFoundError, DatasetNotFoundError
    )
except ImportError:
    # Fallback for direct execution
    from zos_ftp_mcp.zos_ftp import ZosFtpClient
    from zos_ftp_mcp.models import ConnectionConfig
    from zos_ftp_mcp.exceptions import (
        ZosFtpError, ZosConnectionError, AuthenticationError,
        JobNotFoundError, DatasetNotFoundError
    )

# Create the MCP server
mcp = FastMCP("MainframeZOS")


def _get_connection_config() -> ConnectionConfig:
    """Get connection configuration from environment variables."""
    # Parse preserve_trailing_spaces as boolean
    preserve_trailing_spaces_str = os.environ.get('ZFTP_PRESERVE_TRAILING_SPACES', 'false').lower()
    preserve_trailing_spaces = preserve_trailing_spaces_str in ('true', '1', 'yes')
    
    # Parse debug as boolean
    debug_str = os.environ.get('ZFTP_DEBUG', 'false').lower()
    debug = debug_str in ('true', '1', 'yes')
    
    # Parse allow_write as boolean
    allow_write_str = os.environ.get('ZFTP_ALLOW_WRITE', 'false').lower()
    allow_write = allow_write_str in ('true', '1', 'yes')
    
    return ConnectionConfig(
        host=os.environ.get('ZFTP_HOST', ''),
        port=int(os.environ.get('ZFTP_PORT', '21')),
        user=os.environ.get('ZFTP_USER', ''),
        password=os.environ.get('ZFTP_PASSWORD', ''),
        timeout=float(os.environ.get('ZFTP_TIMEOUT', '600.0')),
        download_path=os.environ.get('ZFTP_DOWNLOAD_PATH', '/tmp/mainframe-downloads'),
        default_encoding=os.environ.get('ZFTP_DEFAULT_ENCODING') or None,
        default_line_ending=os.environ.get('ZFTP_DEFAULT_LINE_ENDING') or None,
        preserve_trailing_spaces=preserve_trailing_spaces,
        debug=debug,
        allow_write=allow_write
    )


def _validate_config(config: ConnectionConfig) -> Optional[str]:
    """Validate connection configuration.
    
    Returns:
        Error message if validation fails, None if valid
    """
    if not config.host:
        return "Host is required. Set ZFTP_HOST environment variable."
    if not config.user:
        return "Username is required. Set ZFTP_USER environment variable."
    if not config.password:
        return "Password is required. Set ZFTP_PASSWORD environment variable."
    
    # Validate port range
    if config.port < 1 or config.port > 65535:
        return f"Invalid port {config.port}. Port must be between 1 and 65535."
    
    # Validate timeout
    if config.timeout <= 0:
        return f"Invalid timeout {config.timeout}. Timeout must be greater than 0."
    
    # Check if download path exists, create if possible
    import os
    from pathlib import Path
    try:
        download_path = Path(config.download_path)
        if not download_path.exists():
            download_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return f"Cannot create download path '{config.download_path}': {str(e)}. Check ZFTP_DOWNLOAD_PATH."
    
    return None


# ========== Dataset Operations ==========

@mcp.tool(description="List datasets from mainframe catalog matching a pattern with pagination support")
def list_catalog(pattern: str = 'SYS1.*', limit: Optional[int] = None, offset: int = 0) -> dict:
    """Lists datasets from mainframe catalog matching the specified pattern.
    
    Args:
        pattern: Dataset name pattern with wildcards (default: 'SYS1.*')
                 Use * to match any characters at any position
                 Examples: 'USER.*', 'SYS1.PROC*', '*.CNTL'
        limit: Maximum number of datasets to return (default: None = all)
        offset: Number of datasets to skip (default: 0)
    
    Returns:
        Dictionary with:
            - success: True if operation succeeded
            - datasets: List of dataset objects with attributes:
                - Dsname, Volume, Unit, Referred, Ext, Used, Recfm, Lrecl, BlkSz, Dsorg
            - count: Number of datasets returned
            - total: Total number of datasets matching pattern
            - offset: Current offset
            - has_more: True if more datasets available
    
    Examples:
        list_catalog('USER.TEST.*')              # All datasets under USER.TEST
        list_catalog('USER.*', limit=50)         # First 50 datasets
        list_catalog('USER.*', limit=50, offset=50)  # Next 50 datasets
    """
    config = _get_connection_config()
    error = _validate_config(config)
    if error:
        return {"success": False, "error": error}
    
    try:
        with ZosFtpClient(config) as client:
            datasets = client.list_datasets(pattern)
            
            # Convert Dataset objects to dicts
            all_results = []
            for ds in datasets:
                ds_dict = {
                    "Dsname": ds.name,
                    "Volume": ds.volume,
                    "Unit": ds.unit,
                    "Referred": ds.referred,
                    "Ext": ds.ext,
                    "Used": ds.used,
                    "Recfm": ds.recfm,
                    "Lrecl": ds.lrecl,
                    "BlkSz": ds.blksz,
                    "Dsorg": ds.dsorg
                }
                all_results.append(ds_dict)
            
            total = len(all_results)
            
            # Apply pagination
            if limit is not None:
                result = all_results[offset:offset + limit]
                has_more = (offset + limit) < total
            else:
                result = all_results[offset:]
                has_more = False
            
            return {
                "success": True,
                "datasets": result,
                "count": len(result),
                "total": total,
                "offset": offset,
                "has_more": has_more
            }
            
    except DatasetNotFoundError as e:
        return {"success": True, "datasets": [], "count": 0, "total": 0, "offset": offset, "has_more": False}
    except Exception as e:
        if config.debug:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


@mcp.tool(description="Download a dataset from mainframe in binary format")
def download_binary(source_dataset: str, target_file: Optional[str] = None) -> dict:
    """Downloads a dataset from the mainframe in binary format.
    
    Args:
        source_dataset: Source dataset name (e.g., 'USER.LOAD.LIB')
        target_file: Optional target file path (defaults to download_path/dataset.dat)
    
    Returns:
        Dictionary with success status, source, target path, and port used
    
    Examples:
        download_binary('USER.LOAD.MODULE')
        download_binary('SYS1.LINKLIB', '/tmp/linklib.dat')
    
    Note:
        Binary mode preserves exact byte content, suitable for load modules,
        object code, and other non-text datasets.
    """
    config = _get_connection_config()
    error = _validate_config(config)
    if error:
        return {"success": False, "error": error}
    
    # Determine target file path
    if not target_file:
        target_file = os.path.join(config.download_path, f"{source_dataset}.dat")
    elif os.path.isdir(target_file):
        target_file = os.path.join(target_file, f"{source_dataset}.dat")
    
    try:
        with ZosFtpClient(config) as client:
            target_path = client.download_dataset(source_dataset, Path(target_file), binary=True)
            
            return {
                "success": True,
                "source": source_dataset,
                "target": str(target_path),
                "port_used": config.port
            }
    except Exception as e:
        if config.debug:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


@mcp.tool(description="Download a dataset from mainframe in text format")
def download_text(source_dataset: str, target_file: Optional[str] = None,
                 line_ending: Optional[str] = None,
                 preserve_trailing_spaces: Optional[bool] = None) -> dict:
    """Downloads a dataset from the mainframe in text format.
    
    Args:
        source_dataset: Source dataset name (e.g., 'USER.JCL.CNTL')
        target_file: Optional target file path (defaults to download_path/dataset.txt)
        line_ending: Line ending format ('CRLF', 'LF', 'CR', 'NONE')
        preserve_trailing_spaces: Preserve trailing blanks (True/False)
    
    Returns:
        Dictionary with success status, encoding info, and line ending used
    
    Examples:
        download_text('USER.JCL.CNTL')
        download_text('USER.COBOL.SOURCE', line_ending='CRLF')
        download_text('USER.DATA.TEXT', preserve_trailing_spaces=True)
        
    Note:
        Encoding is set at connection time via ZFTP_DEFAULT_ENCODING environment variable.
        Text mode performs EBCDIC to ASCII conversion automatically.
    """
    config = _get_connection_config()
    error = _validate_config(config)
    if error:
        return {"success": False, "error": error}
    
    # Determine target file path
    if not target_file:
        target_file = os.path.join(config.download_path, f"{source_dataset}.txt")
    elif os.path.isdir(target_file):
        target_file = os.path.join(target_file, f"{source_dataset}.txt")
    
    try:
        with ZosFtpClient(config) as client:
            target_path = client.download_dataset(source_dataset, Path(target_file), 
                                                 binary=False,
                                                 line_ending=line_ending,
                                                 preserve_trailing_spaces=preserve_trailing_spaces)
            
            return {
                "success": True,
                "source": source_dataset,
                "target": str(target_path),
                "port_used": config.port,
                "encoding_configured": config.default_encoding or "default FTP translation",
                "line_ending_used": line_ending or config.default_line_ending or "LF",
                "trailing_spaces_preserved": preserve_trailing_spaces if preserve_trailing_spaces is not None else config.preserve_trailing_spaces
            }
    except Exception as e:
        if config.debug:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


@mcp.tool(description="Download members from a partitioned dataset (PDS)")
def download_pds_members(dataset: str, target_dir: Optional[str] = None,
                        members: str = '*', retr_mode: str = 'ascii',
                        ftp_threads: int = 1,
                        extension: str = '',
                        line_ending: Optional[str] = None,
                        preserve_trailing_spaces: Optional[bool] = None) -> dict:
    """Downloads members from a partitioned dataset (PDS) to a local directory.
    
    Args:
        dataset: PDS name
        target_dir: Target directory (defaults to download_path)
        members: Member names ('*' for all, or comma-separated list)
        retr_mode: 'binary' or 'ascii'
        ftp_threads: Number of parallel threads (1=sequential, 2-16=parallel)
        extension: File extension to add (e.g., '.jcl', '.cbl', '.txt')
        line_ending: Line ending format for text mode ('CRLF', 'LF', 'CR', 'NONE')
        preserve_trailing_spaces: Preserve trailing blanks (True/False)
        
    Note:
        Encoding is set at connection time via ZFTP_DEFAULT_ENCODING environment variable.
    """
    config = _get_connection_config()
    error = _validate_config(config)
    if error:
        return {"success": False, "error": error}
    
    if retr_mode not in ['binary', 'ascii']:
        return {"success": False, "error": "Invalid retr_mode. Must be 'binary' or 'ascii'."}
    
    target_dir = target_dir or config.download_path
    
    try:
        with ZosFtpClient(config) as client:
            # Get member list
            if members == '*':
                member_list = ['*']
            else:
                member_list = [m.strip() for m in members.split(',')]
            
            # Use parallel download if ftp_threads > 1
            if ftp_threads > 1:
                downloaded, failed = client.download_pds_members_parallel(
                    dataset, member_list, Path(target_dir),
                    binary=(retr_mode == 'binary'),
                    max_workers=ftp_threads,
                    extension=extension,
                    line_ending=line_ending,
                    preserve_trailing_spaces=preserve_trailing_spaces
                )
            else:
                downloaded, failed = client.download_pds_members(
                    dataset, member_list, Path(target_dir),
                    binary=(retr_mode == 'binary'),
                    extension=extension,
                    line_ending=line_ending,
                    preserve_trailing_spaces=preserve_trailing_spaces
                )
            
            result = {
                "success": len(failed) == 0,
                "source": dataset,
                "target_dir": target_dir,
                "total_members": len(downloaded),
                "downloaded_members": [p.name for p in downloaded],
                "retr_mode": retr_mode,
                "extension_used": extension if extension else "none",
                "encoding_configured": config.default_encoding or "default FTP translation",
                "line_ending_used": line_ending or config.default_line_ending or "LF",
                "trailing_spaces_preserved": preserve_trailing_spaces if preserve_trailing_spaces is not None else config.preserve_trailing_spaces
            }
            
            if failed:
                result["failed_members"] = failed
                result["warning"] = f"{len(failed)} member(s) failed to download"
            
            return result
    except Exception as e:
        if config.debug:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


# ========== Upload Operations (conditional on ZFTP_ALLOW_WRITE) ==========

# Register upload tool only if write operations are enabled
if os.environ.get('ZFTP_ALLOW_WRITE', 'false').lower() in ('true', '1', 'yes'):
    @mcp.tool(description="Upload a local file to a mainframe dataset")
    def upload_dataset(source_file: str, target_dataset: str, binary: bool = False,
                       lrecl: Optional[int] = None, blksize: Optional[int] = None,
                       recfm: Optional[str] = None, space: Optional[str] = None) -> dict:
        """Uploads a local file to a mainframe dataset or PDS member.
        
        Args:
            source_file: Local file path to upload
            target_dataset: Target dataset name or PDS member (e.g., 'USER.TEST.DATA' or 'USER.JCL.LIB(MEMBER1)')
            binary: Upload in binary mode (default: False for text mode)
            lrecl: Logical record length (e.g., 80 for JCL/source code)
            blksize: Block size (e.g., 3200, 27920)
            recfm: Record format (e.g., 'FB' for fixed block, 'VB' for variable block)
            space: Space allocation (e.g., 'cyl pri=1 sec=5' or 'trk pri=10 sec=5')
            
        Returns:
            Success status and details
            
        Note:
            For sequential datasets: target_dataset='USER.DATA.SEQ'
            For PDS members: target_dataset='USER.JCL.LIB(MEMBER1)'
            
            If dataset doesn't exist, it will be created with specified attributes.
            Common settings for text files: lrecl=80, blksize=3200, recfm='FB'
        """
        config = _get_connection_config()
        error = _validate_config(config)
        if error:
            return {"success": False, "error": error}
        
        # Check if source file exists
        if not os.path.exists(source_file):
            return {"success": False, "error": f"Source file not found: {source_file}"}
        
        try:
            with ZosFtpClient(config) as client:
                # Build SITE parameters if provided
                site_params = []
                if lrecl:
                    site_params.append(f"lrecl={lrecl}")
                if blksize:
                    site_params.append(f"blk={blksize}")
                if recfm:
                    site_params.append(f"recfm={recfm}")
                if space:
                    site_params.append(space)
                
                site_params_str = ' '.join(site_params) if site_params else ''
                
                client.upload_dataset(Path(source_file), target_dataset, binary, site_params_str)
                
                file_size = os.path.getsize(source_file)
                
                return {
                    "success": True,
                    "source": source_file,
                    "target": target_dataset,
                    "mode": "binary" if binary else "text",
                    "file_size": file_size,
                    "site_params": site_params_str if site_params_str else "none"
                }
        except Exception as e:
            if config.debug:
                import traceback
                import sys
                traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}


# ========== Job Operations ==========

# Submit job tool - only available when write operations are enabled
if os.environ.get('ZFTP_ALLOW_WRITE', 'false').lower() in ('true', '1', 'yes'):
    @mcp.tool(description="Submit a JCL job to the mainframe")
    def submit_job(jcl: str, is_file: bool = False) -> dict:
        """Submits a JCL job to the mainframe and returns the job ID.
        
        Args:
            jcl: Either JCL content as string OR path to a file containing JCL
            is_file: If True, treat 'jcl' parameter as a file path and read the file.
                     If False (default), treat 'jcl' as JCL content directly.
        
        Returns:
            Dictionary with job ID, jobname (extracted from JCL), status, and spool file count
        
        Examples:
            # Submit JCL content directly
            submit_job("//MYJOB JOB\\n//STEP1 EXEC PGM=IEFBR14\\n//")
            
            # Submit JCL from file
            submit_job("/path/to/job.jcl", is_file=True)
        
        IMPORTANT - JESINTERFACELEVEL=1 Limitation:
            If your mainframe uses JESINTERFACELEVEL=1, the jobname in your JCL
            (first line //JOBNAME) must be your userid plus exactly one character.
            For example, if userid is 'ARUNKSE', jobname must be 'ARUNKSEJ' or similar.
            
            The jobname is automatically extracted from the JCL and validated.
            Invalid jobnames will be rejected before submission.
        """
        config = _get_connection_config()
        error = _validate_config(config)
        if error:
            return {"success": False, "error": error}
        
        # Read from file if is_file is True
        jcl_content = jcl
        if is_file:
            if not os.path.isfile(jcl):
                return {"success": False, "error": f"JCL file not found: '{jcl}'"}
            try:
                with open(jcl, 'r') as f:
                    jcl_content = f.read()
            except Exception as e:
                return {"success": False, "error": f"Cannot read JCL file '{jcl}': {str(e)}"}
        
        try:
            with ZosFtpClient(config) as client:
                job = client.submit_job(jcl_content)
                
                return {
                    "success": True,
                    "jobid": job.jobid,
                    "jobname": job.jobname,
                    "status": job.status,
                    "spool_files": job.spool_files
                }
        except Exception as e:
            if config.debug:
                import traceback
                import sys
                traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}


@mcp.tool(description="List jobs from JES spool with pagination support")
def list_jes_jobs(jobmask: str = '', owner: str = '', status: str = 'ALL', limit: Optional[int] = None, offset: int = 0) -> dict:
    """Lists jobs from JES spool matching the criteria.
    
    Args:
        jobmask: Job name pattern with wildcards (e.g., 'USER123J', 'USER*', 'JOB*')
                 Use * to match any characters, ? to match single character
        owner: Job owner (defaults to current user if empty)
        status: Job status - 'ALL' (default), 'OUTPUT', 'ACTIVE', 'INPUT'
        limit: Maximum number of jobs to return (default: None = all)
        offset: Number of jobs to skip (default: 0)
    
    Returns:
        Dictionary with list of jobs, count, total, offset, and has_more
    
    Examples:
        list_jes_jobs()                           # All your jobs
        list_jes_jobs(jobmask='USER*')           # Jobs starting with USER
        list_jes_jobs(status='OUTPUT', limit=20) # First 20 completed jobs
        list_jes_jobs(limit=20, offset=20)       # Next 20 jobs
        
    IMPORTANT - JESINTERFACELEVEL=1 Limitation:
        With JESINTERFACELEVEL=1, server-side filtering may not work.
        The tool will retrieve all jobs and filter client-side, which
        may be slower. The jobmask parameter is always applied client-side
        for reliability.
    """
    config = _get_connection_config()
    error = _validate_config(config)
    if error:
        return {"success": False, "error": error}
    
    try:
        with ZosFtpClient(config) as client:
            jobs = client.list_jobs(jobmask, owner, status)
            
            # Convert Job objects to dicts
            all_results = []
            for job in jobs:
                all_results.append({
                    "jobname": job.jobname,
                    "jobid": job.jobid,
                    "status": job.status,
                    "spool_files": job.spool_files
                })
            
            # Sort by jobid descending (latest first)
            all_results.sort(key=lambda x: x['jobid'], reverse=True)
            
            total = len(all_results)
            
            # Apply pagination
            if limit is not None:
                result = all_results[offset:offset + limit]
                has_more = (offset + limit) < total
            else:
                result = all_results[offset:]
                has_more = False
            
            return {
                "success": True,
                "jobs": result,
                "count": len(result),
                "total": total,
                "offset": offset,
                "has_more": has_more
            }
    except Exception as e:
        if config.debug:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


@mcp.tool(description="Get job information and spool files for a specific job ID")
def get_job_info(jobid: str, jobmask: str = '*') -> dict:
    """Retrieves detailed information about a job including spool files.
    
    Args:
        jobid: Job ID (e.g., 'JOB12345')
        jobmask: Job name mask to filter (default '*' for all)
    
    Returns:
        Dictionary with job details including jobname, status, and spool file count
    
    Examples:
        get_job_info('JOB12345')
        get_job_info('JOB12345', jobmask='USER*')
    """
    config = _get_connection_config()
    error = _validate_config(config)
    if error:
        return {"success": False, "error": error}
    
    try:
        with ZosFtpClient(config) as client:
            job = client.get_job_info(jobid)
            
            return {
                "success": True,
                "jobid": job.jobid,
                "job_info": {
                    "jobname": job.jobname,
                    "jobid": job.jobid,
                    "status": job.status,
                    "spool_files": job.spool_files
                }
            }
    except JobNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        if config.debug:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


@mcp.tool(description="Download spool output for a specific job")
def download_job_spool(jobid: str, target_file: Optional[str] = None) -> dict:
    """Downloads all spool output for a job to a local file.
    
    Args:
        jobid: Job ID (e.g., 'JOB12345')
        target_file: Optional target file path (defaults to download_path/jobid.txt)
    
    Returns:
        Dictionary with success status, target file, line count, and return code
        Return code is automatically extracted from job output (e.g., "0000", "0004", "ABEND S0C4")
    
    Examples:
        download_job_spool('JOB12345')
        download_job_spool('JOB12345', '/tmp/job_output.txt')
    
    IMPORTANT - JESINTERFACELEVEL=1 Limitation:
        With JESINTERFACELEVEL=1, jobs may be purged quickly from the spool.
        If you get "Job not found" errors, the job may have been purged by
        the system. Download spool output immediately after job completion.
    """
    config = _get_connection_config()
    error = _validate_config(config)
    if error:
        return {"success": False, "error": error}
    
    # Determine target file path
    if not target_file:
        target_file = os.path.join(config.download_path, f"{jobid}.txt")
    elif os.path.isdir(target_file):
        target_file = os.path.join(target_file, f"{jobid}.txt")
    
    try:
        with ZosFtpClient(config) as client:
            target_path, return_code = client.download_job_spool(jobid, Path(target_file))
            
            # Get line count
            with open(target_path, 'r') as f:
                lines = len(f.readlines())
            
            result = {
                "success": True,
                "jobid": jobid,
                "target_file": str(target_path),
                "lines_retrieved": lines
            }
            
            # Add return code if found
            if return_code:
                result["return_code"] = return_code
                result["job_status"] = "SUCCESS" if return_code == "0000" else "WARNING/ERROR"
            
            return result
            
    except JobNotFoundError as e:
        return {"success": False, "error": str(e), 
                "note": "Job may be purged or inaccessible with JESINTERFACELEVEL=1"}
    except Exception as e:
        if config.debug:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


# ========== VSAM Operations (conditional on ZFTP_ALLOW_WRITE) ==========

# VSAM info tool requires job submission
if os.environ.get('ZFTP_ALLOW_WRITE', 'false').lower() in ('true', '1', 'yes'):
    
    # REXX template for getting VSAM info
    _VSAM_INFO_REXX = ''' /*REXX - Get VSAM Info - supports LEVEL pattern and lists */
 PARSE ARG dsn_input
 IF dsn_input = '' THEN dsn_input = '{DSN_INPUT}'
 SAY '@@VSAM_INFO_START@@'
 /* Check if it looks like a HLQ pattern (no .VSAM or .KSDS) */
 IF POS('.VSAM',dsn_input) = 0 & POS('.KSDS',dsn_input) = 0,
    & POS('.ESDS',dsn_input) = 0 & POS('.RRDS',dsn_input) = 0 THEN DO
   CALL process_level dsn_input
 END
 ELSE DO
   DO WHILE dsn_input <> ''
     PARSE VAR dsn_input dataset_name dsn_input
     dataset_name = STRIP(dataset_name)
     IF dataset_name = '' THEN ITERATE
     CALL get_vsam_info dataset_name
   END
 END
 SAY '@@VSAM_INFO_END@@'
 EXIT 0
 process_level:
   PARSE ARG pattern
   /* First get CLUSTER info */
   Q = OUTTRAP(CAT.)
   "LISTC LEVEL("||pattern||") CLUSTER"
   cat_rc = RC
   Q = OUTTRAP(OFF)
   IF cat_rc = 0 THEN DO
     DO j = 1 TO CAT.0
       line = CAT.j
       IF POS('CLUSTER -------',line) > 0 THEN DO
         PARSE VAR line . '-------' dsname .
         dsname = STRIP(dsname)
         IF dsname <> '' THEN CALL get_vsam_info dsname
       END
     END
   END
   /* Then get AIX info */
   Q = OUTTRAP(AIX.)
   "LISTC LEVEL("||pattern||") AIX"
   aix_rc = RC
   Q = OUTTRAP(OFF)
   IF aix_rc = 0 THEN DO
     DO j = 1 TO AIX.0
       line = AIX.j
       IF POS('AIX -----------',line) > 0 THEN DO
         PARSE VAR line . '-----------' aixname .
         aixname = STRIP(aixname)
         IF aixname <> '' THEN CALL get_aix_info aixname
       END
     END
   END
   RETURN
 get_vsam_info:
   PARSE ARG dsname
   Q = OUTTRAP(DATA.)
   "LISTC ENT('"||dsname||"') ALL"
   listcat_rc = RC
   Q = OUTTRAP(OFF)
   IF listcat_rc <> 0 THEN DO
     SAY '@@VSAM:' dsname '|ERROR:LISTCAT_RC=' listcat_rc
     RETURN
   END
   keylen = ''; rkp = ''; maxlrecl = ''; avglrecl = ''
   shroptns = ''; dstype = 'KSDS'; rec_total = ''
   in_data = 0
   DO i = 1 TO DATA.0
     line = DATA.i
     IF POS('DATA -------',line) > 0 THEN in_data = 1
     IF POS('INDEX ------',line) > 0 THEN in_data = 0
     IF in_data = 0 THEN ITERATE
     val = getkey('KEYLEN',line)
     IF val <> '' THEN keylen = val
     val = getkey('RKP',line)
     IF val <> '' THEN rkp = val
     val = getkey('MAXLRECL',line)
     IF val <> '' THEN maxlrecl = val
     val = getkey('AVGLRECL',line)
     IF val <> '' THEN avglrecl = val
     val = getkey('REC-TOTAL',line)
     IF val <> '' THEN rec_total = val
     position = POS('SHROPTNS(',line)
     IF position <> 0 THEN DO
       position = position + LENGTH('SHROPTNS(')
       shroptns = SUBSTR(line,position,3)
     END
     IF WORDPOS('NONINDEXED',line) <> 0 THEN dstype = 'ESDS'
     IF WORDPOS('NUMBERED',line) <> 0 THEN dstype = 'RRDS'
     IF WORDPOS('LINEAR',line) <> 0 THEN dstype = 'LDS'
   END
   SAY '@@VSAM:' dsname '|TYPE:' dstype '|KEYLEN:' keylen,
       '|RKP:' rkp '|AVGLRECL:' avglrecl '|MAXLRECL:' maxlrecl,
       '|RECORDS:' rec_total '|SHROPT:' shroptns
   RETURN
 get_aix_info:
   PARSE ARG aixname
   Q = OUTTRAP(DATA.)
   "LISTC ENT('"||aixname||"') ALL"
   listcat_rc = RC
   Q = OUTTRAP(OFF)
   IF listcat_rc <> 0 THEN RETURN
   keylen = ''; rkp = ''; base_cluster = ''; path_name = ''
   is_unique = 'N'; is_upgrade = 'N'
   in_data = 0; in_assoc = 0
   DO i = 1 TO DATA.0
     line = DATA.i
     IF POS('DATA -------',line) > 0 THEN in_data = 1
     IF POS('INDEX ------',line) > 0 THEN in_data = 0
     IF POS('ASSOCIATIONS',line) > 0 THEN in_assoc = 1
     IF POS('ATTRIBUTES',line) > 0 THEN in_assoc = 0
     IF in_assoc = 1 THEN DO
       IF POS('CLUSTER--',line) > 0 THEN DO
         PARSE VAR line . 'CLUSTER--' base_cluster .
         base_cluster = STRIP(base_cluster)
       END
       IF POS('PATH-----',line) > 0 THEN DO
         PARSE VAR line . 'PATH-----' path_name .
         path_name = STRIP(path_name)
       END
     END
     IF in_data = 1 THEN DO
       val = getkey('KEYLEN',line)
       IF val <> '' THEN keylen = val
       val = getkey('RKP',line)
       IF val <> '' THEN rkp = val
       IF WORDPOS('UNIQKEY',line) <> 0 THEN is_unique = 'Y'
       IF WORDPOS('NONUNIQKEY',line) <> 0 THEN is_unique = 'N'
     END
     IF WORDPOS('UPGRADE',line) <> 0 THEN is_upgrade = 'Y'
   END
   SAY '@@AIX:' aixname '|BASE:' base_cluster
   SAY '@@AIXD:' aixname '|PATH:' path_name '|KL:' keylen,
       '|RKP:' rkp '|UNQ:' is_unique '|UPG:' is_upgrade
   RETURN
 getkey: PROCEDURE
   PARSE ARG keyword, str
   ret_str = ''
   position = POS(keyword,str)
   IF position <> 0 THEN DO
     len = LENGTH(keyword)
     position = position + len
     len = 24 - len
     ret_str = STRIP(STRIP(SUBSTR(str,position,len)),,'-')
     IF ret_str = '(NULL)' THEN ret_str = ''
   END
   RETURN ret_str
'''

    def _generate_vsam_jcl(userid: str, dsn_input: str) -> str:
        """Generate JCL for VSAM info REXX execution."""
        # Ensure jobname follows JESINTERFACELEVEL=1 rules
        jobname = userid[:7] + 'V' if len(userid) >= 7 else userid + 'V'
        rexx_content = _VSAM_INFO_REXX.replace('{DSN_INPUT}', dsn_input)
        
        # Split REXX into lines for JCL (max 71 chars per line for SYSUT1)
        jcl_lines = [
            f"//{jobname} JOB CLASS=A,MSGCLASS=H,NOTIFY=&SYSUID",
            "//REXLIB1 EXEC PGM=IEFBR14",
            "//REXXLIB DD DSN=&&REXXLIB,DISP=(,PASS),",
            "// DCB=(LRECL=80,RECFM=FB,DSORG=PO,BLKSIZE=0),",
            "// SPACE=(80,(100,50,1),RLSE)",
            "//*",
            "//REXXCOPY EXEC PGM=IEBGENER",
            "//SYSUT2 DD DSN=&&REXXLIB(VSAMINFO),DISP=(SHR,PASS)",
            "//SYSPRINT DD SYSOUT=*",
            "//SYSIN    DD DUMMY",
            "//SYSUT1 DD *",
        ]
        
        # Add REXX content
        for line in rexx_content.split('\n'):
            jcl_lines.append(line[:71] if len(line) > 71 else line)
        
        jcl_lines.extend([
            "/*",
            "//STEP0 EXEC PGM=IKJEFT01,PARM='VSAMINFO'",
            "//SYSPROC DD DSN=&&REXXLIB,DISP=(SHR,PASS)",
            "//SYSTSIN DD DUMMY",
            "//SYSTSPRT DD SYSOUT=*",
            "//"
        ])
        
        return '\n'.join(jcl_lines)

    def _parse_vsam_output(spool_content: str) -> tuple:
        """Parse VSAM info from job spool output.
        
        Returns:
            Tuple of (vsam_datasets, alternate_indexes)
        """
        vsam_datasets = []
        alternate_indexes = []
        in_vsam_section = False
        
        for line in spool_content.split('\n'):
            line = line.strip()
            
            if '@@VSAM_INFO_START@@' in line:
                in_vsam_section = True
                continue
            if '@@VSAM_INFO_END@@' in line:
                in_vsam_section = False
                continue
            
            if not in_vsam_section:
                continue
            
            if line.startswith('@@ERROR:'):
                # Handle error messages
                continue
            
            if line.startswith('@@VSAM:'):
                # Parse VSAM dataset info
                # Format: @@VSAM: dsname |TYPE: type |KEYLEN: len ...
                rest = line[7:].strip()
                parts = rest.split('|')
                vsam_info = {}
                
                # First part is the dataset name (before first |)
                if parts:
                    dsname = parts[0].strip()
                    if dsname:
                        vsam_info['name'] = dsname
                    parts = parts[1:]  # Process remaining parts
                
                for part in parts:
                    part = part.strip()
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if value and value != '':
                            vsam_info[key] = value
                
                if vsam_info:
                    # Convert numeric fields
                    for field in ['keylen', 'rkp', 'avglrecl', 'maxlrecl', 'records']:
                        if field in vsam_info:
                            try:
                                vsam_info[field] = int(vsam_info[field])
                            except ValueError:
                                pass
                    
                    vsam_datasets.append(vsam_info)
            
            elif line.startswith('@@AIX:'):
                # Parse AIX (Alternate Index) basic info - first line
                # Format: @@AIX: aixname |BASE: cluster
                rest = line[6:].strip()
                parts = rest.split('|')
                aix_info = {}
                
                # First part is the AIX name
                if parts:
                    aixname = parts[0].strip()
                    if aixname:
                        aix_info['name'] = aixname
                    parts = parts[1:]
                
                for part in parts:
                    part = part.strip()
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if value and value != '':
                            if key == 'base':
                                aix_info['base_cluster'] = value
                
                if aix_info and 'name' in aix_info:
                    alternate_indexes.append(aix_info)
            
            elif line.startswith('@@AIXD:'):
                # Parse AIX detail info - second line
                # Format: @@AIXD: aixname |PATH: path |KL: keylen |RKP: rkp |UNQ: Y/N |UPG: Y/N
                rest = line[7:].strip()
                parts = rest.split('|')
                
                # First part is the AIX name - find matching entry
                aixname = ''
                if parts:
                    aixname = parts[0].strip()
                    parts = parts[1:]
                
                # Find the matching AIX entry and update it
                for aix_info in alternate_indexes:
                    if aix_info.get('name') == aixname:
                        for part in parts:
                            part = part.strip()
                            if ':' in part:
                                key, value = part.split(':', 1)
                                key = key.strip().lower()
                                value = value.strip()
                                if value and value != '':
                                    # Map abbreviated field names
                                    if key == 'kl':
                                        try:
                                            aix_info['keylen'] = int(value)
                                        except ValueError:
                                            aix_info['keylen'] = value
                                    elif key == 'unq':
                                        aix_info['unique'] = (value == 'Y')
                                    elif key == 'upg':
                                        aix_info['upgrade'] = (value == 'Y')
                                    elif key == 'rkp':
                                        try:
                                            aix_info['rkp'] = int(value)
                                        except ValueError:
                                            aix_info['rkp'] = value
                                    else:
                                        aix_info[key] = value
                        break
        
        return vsam_datasets, alternate_indexes

    def _filter_for_modernization(vsam_datasets: list) -> list:
        """Filter VSAM dataset info to only essential fields for modernization."""
        modernization_fields = ['name', 'type', 'keylen', 'rkp', 'avglrecl', 'maxlrecl', 'records', 'shropt']
        filtered = []
        for ds in vsam_datasets:
            filtered_ds = {k: v for k, v in ds.items() if k in modernization_fields}
            filtered.append(filtered_ds)
        return filtered

    @mcp.tool(description="Get VSAM dataset information including key length, record size, CI size, and more with pagination support")
    def get_vsam_info(dataset: str, limit: Optional[int] = None, offset: int = 0) -> dict:
        """Retrieves VSAM dataset information essential for modernization/migration.
        
        Args:
            dataset: Either a specific VSAM cluster name (e.g., 'USER.DATA.VSAM.KSDS')
                     or a high-level qualifier to find all VSAM clusters under it
                     (e.g., 'USER.DATA' will find all VSAM clusters starting with USER.DATA)
            limit: Maximum number of VSAM datasets to return (default: None = all)
            offset: Number of VSAM datasets to skip (default: 0)
        
        Returns:
            Dictionary with:
                - success: True if operation succeeded
                - vsam_datasets: List of VSAM dataset info objects containing:
                    - name: Dataset name
                    - type: KSDS, ESDS, RRDS, or LDS
                    - keylen: Key length (KSDS only)
                    - rkp: Relative key position (KSDS only)
                    - avglrecl: Average record length
                    - maxlrecl: Maximum record length
                    - records: Total record count
                    - shropt: Share options (e.g., "1,3")
                    - alternate_indexes: List of AIX objects for this VSAM (if any):
                        - name: AIX name
                        - keylen: Alternate key length
                        - rkp: Alternate key position in base record
                        - unique: True if keys must be unique
                        - upgrade: True if AIX auto-updates when base changes
                        - path: Path dataset name
                - count: Number of VSAM datasets returned
                - total: Total number of VSAM datasets found
                - offset: Current offset
                - has_more: True if more VSAM datasets available
                - jobid: Job ID used for LISTCAT
                - return_code: Job return code
        
        Examples:
            get_vsam_info('USER.PROD.CUSTOMER.VSAM.KSDS')  # Single dataset
            get_vsam_info('USER.PROD')  # All VSAM under USER.PROD
            get_vsam_info('USER.PROD', limit=50)  # First 50 VSAM datasets
            get_vsam_info('USER.PROD', limit=50, offset=50)  # Next 50 VSAM datasets
            
        Note:
            This tool submits a batch job to run LISTCAT via REXX.
            Requires ZFTP_ALLOW_WRITE=true to be set.
            
            Returns only fields needed for schema design: type (determines table 
            structure), keylen/rkp (primary key definition), recsize (row layout),
            records (capacity planning), and shropt (concurrency patterns).
        """
        import time
        
        config = _get_connection_config()
        error = _validate_config(config)
        if error:
            return {"success": False, "error": error}
        
        try:
            with ZosFtpClient(config) as client:
                # Generate and submit JCL
                jcl = _generate_vsam_jcl(config.user, dataset)
                job = client.submit_job(jcl)
                
                # Wait for job completion (poll status)
                max_wait = 60  # seconds
                poll_interval = 2
                waited = 0
                
                while waited < max_wait:
                    try:
                        job_info = client.get_job_info(job.jobid)
                        if job_info.status == 'OUTPUT':
                            break
                    except JobNotFoundError:
                        # Job may have completed and been purged
                        break
                    
                    time.sleep(poll_interval)
                    waited += poll_interval
                
                # Download spool output
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    temp_file = f.name
                
                try:
                    target_path, return_code = client.download_job_spool(job.jobid, Path(temp_file))
                    
                    # Read and parse output
                    with open(target_path, 'r') as f:
                        spool_content = f.read()
                    
                    vsam_datasets, alternate_indexes = _parse_vsam_output(spool_content)
                    
                    # Always filter for modernization fields
                    vsam_datasets = _filter_for_modernization(vsam_datasets)
                    
                    # Nest alternate indexes inside their base VSAM datasets
                    for vsam_ds in vsam_datasets:
                        aix_list = []
                        for aix in alternate_indexes:
                            if aix.get('base_cluster') == vsam_ds.get('name'):
                                # Remove base_cluster from AIX since it's now nested
                                aix_copy = {k: v for k, v in aix.items() if k != 'base_cluster'}
                                aix_list.append(aix_copy)
                        # Only add alternate_indexes field if there are AIXs
                        if aix_list:
                            vsam_ds['alternate_indexes'] = aix_list
                    
                    # Store total before pagination
                    total_vsam = len(vsam_datasets)
                    
                    # Apply pagination to VSAM datasets
                    if limit is not None:
                        vsam_datasets = vsam_datasets[offset:offset + limit]
                        has_more = (offset + limit) < total_vsam
                    else:
                        vsam_datasets = vsam_datasets[offset:]
                        has_more = False
                    
                    # Build result with data first, metadata at bottom
                    result = {
                        "success": True,
                        "vsam_datasets": vsam_datasets,
                        "count": len(vsam_datasets),
                        "total": total_vsam,
                        "offset": offset,
                        "has_more": has_more,
                        "jobid": job.jobid,
                        "return_code": return_code
                    }
                    
                    return result
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_file)
                    except Exception:
                        pass
                        
        except Exception as e:
            if config.debug:
                import traceback
                traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}


# ========== GDG Operations (conditional on ZFTP_ALLOW_WRITE) ==========

# GDG info tool requires job submission
if os.environ.get('ZFTP_ALLOW_WRITE', 'false').lower() in ('true', '1', 'yes'):
    
    # REXX template for getting GDG base attributes - supports wildcards
    _GDG_INFO_REXX = ''' /*REXX - Get GDG Info - supports wildcards */
 PARSE ARG gdg_input
 IF gdg_input = '' THEN gdg_input = '{GDG_INPUT}'
 SAY '@@GDG_INFO_START@@'
 /* Check if wildcard pattern */
 IF POS('*',gdg_input) > 0 THEN DO
   /* Has wildcard - remove trailing .* or * for LEVEL */
   pattern = gdg_input
   had_wildcard_suffix = 0
   IF RIGHT(pattern,2) = '.*' THEN DO
     pattern = SUBSTR(pattern,1,LENGTH(pattern)-2)
     had_wildcard_suffix = 1
   END
   ELSE IF RIGHT(pattern,1) = '*' THEN DO
     pattern = SUBSTR(pattern,1,LENGTH(pattern)-1)
     had_wildcard_suffix = 1
   END
   /* Use LEVEL if we stripped a wildcard suffix */
   IF had_wildcard_suffix = 1 THEN DO
     CALL process_level pattern
   END
   ELSE DO
     /* Wildcard in middle - not supported, try as-is */
     CALL get_gdg_info gdg_input
   END
 END
 ELSE DO
   /* No wildcard - exact match */
   CALL get_gdg_info gdg_input
 END
 SAY '@@GDG_INFO_END@@'
 EXIT 0
 process_level:
   PARSE ARG pattern
   Q = OUTTRAP(CAT.)
   "LISTC LEVEL("||pattern||") GDG"
   cat_rc = RC
   Q = OUTTRAP(OFF)
   IF cat_rc = 0 THEN DO
     DO j = 1 TO CAT.0
       line = CAT.j
       IF POS('GDG BASE',line) > 0 THEN DO
         /* Format: GDG BASE ------ USER.GDGBASE */
         PARSE VAR line 'GDG BASE' dashes gdgname .
         gdgname = STRIP(gdgname)
         IF gdgname <> '' & gdgname <> '---' THEN DO
           CALL get_gdg_info gdgname
         END
       END
     END
   END
   RETURN
 get_gdg_info:
   PARSE ARG gdg_base
   Q = OUTTRAP(DATA.)
   "LISTC ENT('"||gdg_base||"') GDG ALL"
   listcat_rc = RC
   Q = OUTTRAP(OFF)
   IF listcat_rc <> 0 THEN DO
     SAY '@@ERROR:' gdg_base '|LISTCAT_RC=' listcat_rc
     RETURN
   END
   limit = ''; scratch = ''; empty = ''; order = ''; purge = ''
   extended = 'N'
   DO i = 1 TO DATA.0
     line = DATA.i
     val = getkey('LIMIT',line)
     IF val <> '' THEN limit = val
     IF POS('NOSCRATCH',line) <> 0 THEN scratch = 'NOSCRATCH'
     ELSE IF POS('SCRATCH',line) <> 0 THEN scratch = 'SCRATCH'
     IF POS('NOEMPTY',line) <> 0 THEN empty = 'NOEMPTY'
     ELSE IF POS('EMPTY',line) <> 0 THEN empty = 'EMPTY'
     IF POS('LIFO',line) <> 0 THEN order = 'LIFO'
     ELSE IF POS('FIFO',line) <> 0 THEN order = 'FIFO'
     IF POS('NOPURGE',line) <> 0 THEN purge = 'NOPURGE'
     ELSE IF POS('PURGE',line) <> 0 THEN purge = 'PURGE'
     IF POS('NOEXTENDED',line) <> 0 THEN extended = 'N'
     ELSE IF POS('EXTENDED',line) <> 0 THEN extended = 'Y'
     IF POS('NONVSAM--',line) <> 0 THEN DO
       PARSE VAR line . 'NONVSAM--' genname .
       genname = STRIP(genname)
       IF genname <> '' THEN SAY '@@GEN:' gdg_base '|' genname
     END
   END
   SAY '@@GDG:' gdg_base '|LIMIT:' limit '|SCRATCH:' scratch,
       '|EMPTY:' empty '|ORDER:' order '|PURGE:' purge,
       '|EXTENDED:' extended
   RETURN
 getkey: PROCEDURE
   PARSE ARG keyword, str
   ret_str = ''
   position = POS(keyword,str)
   IF position <> 0 THEN DO
     len = LENGTH(keyword)
     position = position + len
     len = 24 - len
     ret_str = STRIP(STRIP(SUBSTR(str,position,len)),,'-')
     IF ret_str = '(NULL)' THEN ret_str = ''
   END
   RETURN ret_str
'''

    def _generate_gdg_jcl(userid: str, gdg_input: str) -> str:
        """Generate JCL for GDG info REXX execution."""
        # Ensure jobname follows JESINTERFACELEVEL=1 rules
        jobname = userid[:7] + 'G' if len(userid) >= 7 else userid + 'G'
        rexx_content = _GDG_INFO_REXX.replace('{GDG_INPUT}', gdg_input)
        
        jcl_lines = [
            f"//{jobname} JOB CLASS=A,MSGCLASS=H,NOTIFY=&SYSUID",
            "//REXLIB1 EXEC PGM=IEFBR14",
            "//REXXLIB DD DSN=&&REXXLIB,DISP=(,PASS),",
            "// DCB=(LRECL=80,RECFM=FB,DSORG=PO,BLKSIZE=0),",
            "// SPACE=(80,(100,50,1),RLSE)",
            "//*",
            "//REXXCOPY EXEC PGM=IEBGENER",
            "//SYSUT2 DD DSN=&&REXXLIB(GDGINFO),DISP=(SHR,PASS)",
            "//SYSPRINT DD SYSOUT=*",
            "//SYSIN    DD DUMMY",
            "//SYSUT1 DD *",
        ]
        
        # Add REXX content
        for line in rexx_content.split('\n'):
            jcl_lines.append(line[:71] if len(line) > 71 else line)
        
        jcl_lines.extend([
            "/*",
            "//STEP0 EXEC PGM=IKJEFT01,PARM='GDGINFO'",
            "//SYSPROC DD DSN=&&REXXLIB,DISP=(SHR,PASS)",
            "//SYSTSIN DD DUMMY",
            "//SYSTSPRT DD SYSOUT=*",
            "//"
        ])
        
        return '\n'.join(jcl_lines)

    def _parse_gdg_output(spool_content: str) -> list:
        """Parse GDG info from job spool output.
        
        Returns:
            List of GDG base dictionaries, each with base info and generations
        """
        import re
        gdg_bases = {}  # Use dict to collect by name
        in_gdg_section = False
        gen_pattern = re.compile(r'\.G(\d{4})V\d{2}$')
        
        for line in spool_content.split('\n'):
            line = line.strip()
            
            if '@@GDG_INFO_START@@' in line:
                in_gdg_section = True
                continue
            if '@@GDG_INFO_END@@' in line:
                in_gdg_section = False
                continue
            
            if not in_gdg_section:
                continue
            
            if line.startswith('@@ERROR:'):
                # Extract error info - format: @@ERROR: gdgname |LISTCAT_RC=...
                rest = line[8:].strip()
                if '|' in rest:
                    gdgname, error_msg = rest.split('|', 1)
                    gdgname = gdgname.strip()
                    if gdgname not in gdg_bases:
                        gdg_bases[gdgname] = {'name': gdgname, 'error': error_msg.strip()}
                continue
            
            if line.startswith('@@GEN:'):
                # Parse generation name - format: @@GEN: gdgbase |genname
                rest = line[6:].strip()
                if '|' in rest:
                    gdgbase, genname = rest.split('|', 1)
                    gdgbase = gdgbase.strip()
                    genname = genname.strip()
                    
                    if gdgbase not in gdg_bases:
                        gdg_bases[gdgbase] = {'name': gdgbase, 'generations': []}
                    
                    if 'generations' not in gdg_bases[gdgbase]:
                        gdg_bases[gdgbase]['generations'] = []
                    
                    match = gen_pattern.search(genname)
                    if match:
                        gen_num = int(match.group(1))
                        gdg_bases[gdgbase]['generations'].append({
                            'name': genname,
                            'generation': gen_num
                        })
                continue
            
            if line.startswith('@@GDG:'):
                # Parse GDG base info
                # Format: @@GDG: name |LIMIT: n |SCRATCH: x |EMPTY: x |ORDER: x |PURGE: x |EXTENDED: x
                rest = line[6:].strip()
                parts = rest.split('|')
                
                # First part is the GDG base name
                gdg_name = ''
                if parts:
                    gdg_name = parts[0].strip()
                    parts = parts[1:]
                
                if gdg_name:
                    if gdg_name not in gdg_bases:
                        gdg_bases[gdg_name] = {'name': gdg_name, 'generations': []}
                    
                    for part in parts:
                        part = part.strip()
                        if ':' in part:
                            key, value = part.split(':', 1)
                            key = key.strip().lower()
                            value = value.strip()
                            if value and value != '':
                                if key == 'limit':
                                    try:
                                        gdg_bases[gdg_name]['limit'] = int(value)
                                    except ValueError:
                                        gdg_bases[gdg_name]['limit'] = value
                                elif key == 'extended':
                                    gdg_bases[gdg_name]['extended'] = (value == 'Y')
                                else:
                                    gdg_bases[gdg_name][key] = value
        
        # Convert dict to list and sort generations within each GDG
        result = []
        for gdg_base in gdg_bases.values():
            if 'generations' in gdg_base:
                # Sort generations by generation number (descending - newest first)
                gdg_base['generations'].sort(key=lambda x: x.get('generation', 0), reverse=True)
            else:
                gdg_base['generations'] = []
            result.append(gdg_base)
        
        # Sort GDG bases by name
        result.sort(key=lambda x: x.get('name', ''))
        
        return result

    @mcp.tool(description="Get GDG (Generation Data Group) base attributes and list all generations with pagination support")
    def get_gdg_info(gdg_pattern: str, limit: Optional[int] = None, offset: int = 0) -> dict:
        """Retrieves GDG base attributes and lists current generations with pagination.
        
        Args:
            gdg_pattern: GDG base name or pattern (e.g., 'USER.DAILY.BACKUP' or 'AWS.M2.*')
                         Use * to match multiple GDG bases
                         Do NOT include generation suffix (G0001V00)
            limit: Maximum number of GDG bases to return (default: None = all)
            offset: Number of GDG bases to skip (default: 0)
        
        Returns:
            Dictionary with:
                - success: True if operation succeeded
                - gdg_bases: List of GDG base objects, each containing:
                    - name: GDG base name
                    - limit: Maximum number of generations
                    - scratch: NOSCRATCH or SCRATCH (delete data when rolled off)
                    - empty: NOEMPTY or EMPTY (allow empty GDG)
                    - order: LIFO or FIFO (generation ordering)
                    - purge: NOPURGE or PURGE (purge behavior)
                    - extended: True if extended format GDG
                    - generations: List of ALL generation datasets (newest first):
                        - name: Full dataset name with generation suffix
                        - generation: Generation number (e.g., 1, 2, 3)
                    - generation_count: Number of generations for this GDG base
                - count: Number of GDG bases returned
                - total: Total number of GDG bases found
                - offset: Current offset
                - has_more: True if more GDG bases available
                - jobid: Job ID used for LISTCAT
                - return_code: Job return code
        
        Examples:
            get_gdg_info('USER.DAILY.BACKUP')  # Single GDG with all generations
            get_gdg_info('AWS.M2.*')  # All GDG bases under AWS.M2
            get_gdg_info('AWS.M2.*', limit=10)  # First 10 GDG bases
            get_gdg_info('AWS.M2.*', limit=10, offset=10)  # Next 10 GDG bases
            
        Note:
            This tool uses LISTCAT (via batch job) for GDG base attributes.
            Requires ZFTP_ALLOW_WRITE=true to be set.
            
            Pagination applies to GDG bases, not generations. Each GDG base
            returned will include ALL of its generations.
        """
        import time
        
        config = _get_connection_config()
        error = _validate_config(config)
        if error:
            return {"success": False, "error": error}
        
        try:
            with ZosFtpClient(config) as client:
                # Get GDG base attributes via LISTCAT job
                jcl = _generate_gdg_jcl(config.user, gdg_pattern)
                job = client.submit_job(jcl)
                
                # Wait for job completion (poll status)
                max_wait = 60  # seconds
                poll_interval = 2
                waited = 0
                
                while waited < max_wait:
                    try:
                        job_info = client.get_job_info(job.jobid)
                        if job_info.status == 'OUTPUT':
                            break
                    except JobNotFoundError:
                        break
                    
                    time.sleep(poll_interval)
                    waited += poll_interval
                
                # Download spool output for GDG base attributes
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    temp_file = f.name
                
                try:
                    target_path, return_code = client.download_job_spool(job.jobid, Path(temp_file))
                    
                    with open(target_path, 'r') as f:
                        spool_content = f.read()
                    
                    gdg_bases = _parse_gdg_output(spool_content)
                    
                    # Check for errors
                    if not gdg_bases:
                        return {
                            "success": True,
                            "gdg_bases": [],
                            "count": 0,
                            "total": 0,
                            "offset": offset,
                            "has_more": False,
                            "jobid": job.jobid,
                            "return_code": return_code
                        }
                    
                    # Add generation_count to each GDG base
                    for gdg_base in gdg_bases:
                        gdg_base['generation_count'] = len(gdg_base.get('generations', []))
                    
                    # Store total before pagination
                    total_gdg_bases = len(gdg_bases)
                    
                    # Apply pagination to GDG bases (not generations!)
                    if limit is not None:
                        gdg_bases = gdg_bases[offset:offset + limit]
                        has_more = (offset + limit) < total_gdg_bases
                    else:
                        gdg_bases = gdg_bases[offset:]
                        has_more = False
                    
                    # Build result
                    return {
                        "success": True,
                        "gdg_bases": gdg_bases,
                        "count": len(gdg_bases),
                        "total": total_gdg_bases,
                        "offset": offset,
                        "has_more": has_more,
                        "jobid": job.jobid,
                        "return_code": return_code
                    }
                finally:
                    try:
                        os.unlink(temp_file)
                    except Exception:
                        pass
                        
        except Exception as e:
            if config.debug:
                import traceback
                traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}


# ========== Consolidated Export Operations (conditional on ZFTP_ALLOW_WRITE) ==========

# Export tool requires job submission for VSAM/GDG info
if os.environ.get('ZFTP_ALLOW_WRITE', 'false').lower() in ('true', '1', 'yes'):
    
    @mcp.tool(description="Export consolidated dataset catalog with enriched VSAM and GDG information to JSONL file")
    def export_catalog_jsonl(pattern: str = '*', target_file: Optional[str] = None, 
                            include_vsam: bool = True, include_gdg: bool = True) -> dict:
        """Exports a consolidated catalog of datasets with enriched VSAM and GDG information.
        
        This tool combines list_catalog, get_vsam_info, and get_gdg_info to create a 
        comprehensive dataset inventory in JSONL format (one JSON object per line).
        
        Args:
            pattern: Dataset name pattern (default: '*' for all datasets)
            target_file: Output JSONL file path (default: download_path/catalog_export.jsonl)
            include_vsam: Enrich VSAM datasets with detailed info (default: True)
            include_gdg: Enrich GDG bases with generation info (default: True)
        
        Returns:
            Dictionary with:
                - success: True if operation succeeded
                - target_file: Path to generated JSONL file
                - total_datasets: Total number of datasets exported
                - vsam_enriched: Number of VSAM datasets enriched
                - gdg_enriched: Number of GDG bases enriched
                - processing_time: Time taken in seconds
        
        Output JSONL Format:
            Each line is a JSON object. For regular datasets and VSAM:
            - name: Dataset name
            - catalog_info: Basic catalog information (volume, recfm, lrecl, dsorg, etc.)
            - vsam_info: (if VSAM) Detailed VSAM attributes
            
            For GDG bases, creates multiple records:
            1. GDG base record:
               - name: GDG base name
               - catalog_info: Catalog info with dsorg='GDG'
               - gdg_base_info: Base attributes (limit, scratch, empty, order, purge, extended, generation_count)
            2. One record per generation:
               - name: Generation dataset name (e.g., USER.BACKUP.G0001V00)
               - catalog_info: Catalog info with dsorg='NONVSAM'
               - gdg_generation_info: {gdg_base: base name, generation: number}
        
        Examples:
            export_catalog_jsonl('USER.*')  # Export all USER datasets
            export_catalog_jsonl('AWS.M2.*', '/tmp/aws_catalog.jsonl')
            export_catalog_jsonl('PROD.*', include_vsam=True, include_gdg=False)
            
        Note:
            This tool requires ZFTP_ALLOW_WRITE=true because it uses get_vsam_info
            and get_gdg_info which submit batch jobs.
            
            Large catalogs may take time to process. The tool processes datasets
            in batches and provides progress information.
        """
        import time
        import json
        
        start_time = time.time()
        
        config = _get_connection_config()
        error = _validate_config(config)
        if error:
            return {"success": False, "error": error}
        
        # Determine target file path
        if not target_file:
            target_file = os.path.join(config.download_path, "catalog_export.jsonl")
        
        try:
            with ZosFtpClient(config) as client:
                # Step 1: Get all datasets from catalog
                datasets = client.list_datasets(pattern)
                
                if not datasets:
                    return {
                        "success": True,
                        "target_file": target_file,
                        "total_datasets": 0,
                        "vsam_enriched": 0,
                        "gdg_enriched": 0,
                        "processing_time": time.time() - start_time
                    }
                
                # Categorize datasets for enrichment
                vsam_datasets = []
                gdg_bases = []
                
                for ds in datasets:
                    if ds.dsorg == 'VSAM' or ds.dsorg == 'VS':  # VSAM
                        vsam_datasets.append(ds)
                    elif ds.dsorg == 'GDG':  # GDG base
                        gdg_bases.append(ds)
                
                # Step 2: Enrich VSAM datasets
                vsam_info_map = {}
                if include_vsam and vsam_datasets:
                    # Strip trailing .* from pattern for VSAM LEVEL search
                    vsam_pattern = pattern
                    if vsam_pattern.endswith('.*'):
                        vsam_pattern = vsam_pattern[:-2]
                    
                    # Get VSAM info for the pattern (will get all VSAM under pattern)
                    vsam_result = get_vsam_info(vsam_pattern)
                    if vsam_result.get('success'):
                        for vsam in vsam_result.get('vsam_datasets', []):
                            vsam_info_map[vsam['name']] = vsam
                
                # Step 3: Enrich GDG bases
                gdg_info_map = {}
                if include_gdg and gdg_bases:
                    # Strip trailing .* from pattern for GDG LEVEL search
                    gdg_pattern = pattern
                    if gdg_pattern.endswith('.*'):
                        gdg_pattern = gdg_pattern[:-2]
                    
                    # Try wildcard pattern first for efficiency
                    gdg_result = get_gdg_info(gdg_pattern)
                    if gdg_result.get('success') and gdg_result.get('gdg_bases'):
                        for gdg_info in gdg_result.get('gdg_bases', []):
                            gdg_name = gdg_info.get('name')
                            if gdg_name:
                                gdg_info_map[gdg_name] = gdg_info
                    
                    # For any GDG bases not enriched, call individually
                    for gdg_ds in gdg_bases:
                        if gdg_ds.name not in gdg_info_map:
                            gdg_result = get_gdg_info(gdg_ds.name)
                            if gdg_result.get('success') and gdg_result.get('gdg_bases'):
                                gdg_bases_list = gdg_result.get('gdg_bases', [])
                                if gdg_bases_list:
                                    gdg_info = gdg_bases_list[0]
                                    gdg_info_map[gdg_ds.name] = gdg_info
                
                # Step 4: Write JSONL file
                # First, build a map of generation datasets from catalog for merging
                generation_catalog_map = {}
                for ds in datasets:
                    # Check if this looks like a GDG generation (has .GnnnnVnn pattern)
                    if '.G' in ds.name and ds.dsorg == 'PS':
                        generation_catalog_map[ds.name] = ds
                
                def clean_dict(d):
                    """Remove keys with None values from dictionary."""
                    return {k: v for k, v in d.items() if v is not None}
                
                with open(target_file, 'w') as f:
                    for ds in datasets:
                        # Skip generation datasets - they'll be written with GDG base
                        if ds.name in generation_catalog_map:
                            continue
                        
                        record = {
                            'name': ds.name,
                            'catalog_info': clean_dict({
                                'volume': ds.volume,
                                'unit': ds.unit,
                                'referred': ds.referred,
                                'ext': ds.ext,
                                'used': ds.used,
                                'recfm': ds.recfm,
                                'lrecl': ds.lrecl,
                                'blksz': ds.blksz,
                                'dsorg': ds.dsorg
                            })
                        }
                        
                        # Add enriched VSAM info if available
                        if ds.name in vsam_info_map:
                            record['vsam_info'] = vsam_info_map[ds.name]
                        
                        # Handle GDG bases - write base info and separate generation records
                        if ds.name in gdg_info_map:
                            gdg_info = gdg_info_map[ds.name]
                            # Write GDG base record with base attributes only
                            record['gdg_base_info'] = {
                                'limit': gdg_info.get('limit'),
                                'scratch': gdg_info.get('scratch'),
                                'empty': gdg_info.get('empty'),
                                'order': gdg_info.get('order'),
                                'purge': gdg_info.get('purge'),
                                'extended': gdg_info.get('extended'),
                                'generation_count': gdg_info.get('generation_count', 0)
                            }
                            f.write(json.dumps(record) + '\n')
                            
                            # Write separate record for each generation with merged info
                            for gen in gdg_info.get('generations', []):
                                gen_name = gen['name']
                                # Get catalog info if available
                                if gen_name in generation_catalog_map:
                                    gen_ds = generation_catalog_map[gen_name]
                                    gen_record = {
                                        'name': gen_name,
                                        'catalog_info': clean_dict({
                                            'volume': gen_ds.volume,
                                            'unit': gen_ds.unit,
                                            'referred': gen_ds.referred,
                                            'ext': gen_ds.ext,
                                            'used': gen_ds.used,
                                            'recfm': gen_ds.recfm,
                                            'lrecl': gen_ds.lrecl,
                                            'blksz': gen_ds.blksz,
                                            'dsorg': gen_ds.dsorg
                                        }),
                                        'gdg_generation_info': {
                                            'gdg_base': ds.name,
                                            'generation': gen['generation']
                                        }
                                    }
                                else:
                                    # No catalog info available (shouldn't happen but handle it)
                                    gen_record = {
                                        'name': gen_name,
                                        'catalog_info': {
                                            'dsorg': 'PS'
                                        },
                                        'gdg_generation_info': {
                                            'gdg_base': ds.name,
                                            'generation': gen['generation']
                                        }
                                    }
                                f.write(json.dumps(gen_record) + '\n')
                        else:
                            # Regular dataset or VSAM without GDG
                            f.write(json.dumps(record) + '\n')
                
                processing_time = time.time() - start_time
                
                return {
                    "success": True,
                    "target_file": target_file,
                    "total_datasets": len(datasets),
                    "vsam_enriched": len(vsam_info_map),
                    "gdg_enriched": len(gdg_info_map),
                    "processing_time": round(processing_time, 2)
                }
                
        except Exception as e:
            if config.debug:
                import traceback
                traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}


# ========== Utility Operations ==========

@mcp.tool(description="Get current connection information for the mainframe")
def get_connection_info() -> dict:
    """Returns the current connection information from environment variables.
    
    Returns:
        Dictionary with connection details including:
            - host, port, user
            - timeout, download_path
            - encoding and line ending settings
            - JES interface level (detected at runtime)
            - connection status
    
    Examples:
        get_connection_info()  # Check current settings and connection status
    
    Note:
        Password is never returned, only a boolean indicating if it's set.
        Use this tool to verify your environment configuration and check
        which JESINTERFACELEVEL your mainframe is using.
    """
    config = _get_connection_config()
    
    try:
        with ZosFtpClient(config) as client:
            info = client.get_connection_info()
            return {
                "success": True,
                **info
            }
    except Exception:
        # Return config even if connection fails
        return {
            "success": False,
            "host": config.host,
            "port": config.port,
            "user": config.user,
            "timeout": config.timeout,
            "download_path": config.download_path,
            "default_encoding": config.default_encoding or "none",
            "default_line_ending": config.default_line_ending or "none",
            "preserve_trailing_spaces": config.preserve_trailing_spaces,
            "password_set": bool(config.password),
            "connected": False
        }


def run_server():
    """Start the MCP server.
    
    Initializes and runs the FastMCP server for z/OS FTP operations.
    The server reads configuration from environment variables and
    exposes tools for dataset operations, job management, and more.
    
    Environment Variables:
        ZFTP_HOST: Mainframe hostname (required)
        ZFTP_PORT: FTP port (default: 21)
        ZFTP_USER: FTP username (required)
        ZFTP_PASSWORD: FTP password (required)
        ZFTP_TIMEOUT: Connection timeout in seconds (default: 600.0)
        ZFTP_DOWNLOAD_PATH: Local download directory (default: /tmp/mainframe-downloads)
        ZFTP_DEFAULT_ENCODING: Default encoding for text transfers (e.g., 'IBM-037,UTF-8')
        ZFTP_DEFAULT_LINE_ENDING: Default line ending (CRLF, LF, CR, NONE)
        ZFTP_PRESERVE_TRAILING_SPACES: Preserve trailing spaces (true/false, default: false)
        ZFTP_DEBUG: Enable debug logging (true/false, default: false)
        ZFTP_ALLOW_WRITE: Enable write operations (true/false, default: false)
    
    The server will detect JESINTERFACELEVEL at connection time and adapt
    job operations accordingly. JESINTERFACELEVEL=1 has limitations on
    job filtering and requires specific jobname patterns.
    """
    config = _get_connection_config()
    
    print("Starting MainframeZOS MCP server...")
    print("Current connection settings:")
    print(f"  Host: {config.host or 'Not set'}")
    print(f"  Port: {config.port}")
    print(f"  User: {config.user or 'Not set'}")
    print(f"  Password: {'Set' if config.password else 'Not set'}")
    print(f"  Timeout: {config.timeout} seconds")
    print(f"  Download path: {config.download_path}")
    print("Configure connection using set_connection_params tool or environment variables")
    
    mcp.run()


if __name__ == "__main__":
    run_server()
