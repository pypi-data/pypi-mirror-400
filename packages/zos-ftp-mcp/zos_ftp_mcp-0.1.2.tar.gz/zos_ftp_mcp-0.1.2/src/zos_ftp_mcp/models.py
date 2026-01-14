"""
Data models for z/OS FTP operations.
"""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class ConnectionConfig:
    """FTP connection configuration."""
    host: str
    port: int = 21
    user: str = ""
    password: str = ""
    timeout: float = 600.0
    download_path: str = "/tmp"
    default_encoding: Optional[str] = None  # e.g., '(IBM-037,UTF-8)'
    default_line_ending: Optional[str] = None  # e.g., 'CRLF', 'LF'
    preserve_trailing_spaces: bool = False  # Preserve trailing blanks in text transfers
    debug: bool = False  # Enable FTP protocol debugging
    allow_write: bool = False  # Allow write operations (upload, delete)
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.host:
            raise ValueError("Host is required")
        
        # Validate line ending format
        if self.default_line_ending and self.default_line_ending.upper() not in ('CRLF', 'LF', 'CR', 'NONE'):
            raise ValueError(f"Invalid line ending: {self.default_line_ending}. Must be CRLF, LF, CR, or NONE")


@dataclass
class Dataset:
    """Mainframe dataset information."""
    name: str
    volume: Optional[str] = None
    unit: Optional[str] = None
    referred: Optional[str] = None
    ext: Optional[str] = None
    used: Optional[str] = None
    recfm: Optional[str] = None
    lrecl: Optional[str] = None
    blksz: Optional[str] = None
    dsorg: Optional[str] = None
    
    @property
    def is_pds(self) -> bool:
        """Check if dataset is partitioned."""
        return self.dsorg == "PO"
    
    @property
    def is_vsam(self) -> bool:
        """Check if dataset is VSAM."""
        return self.dsorg == "VSAM"


@dataclass
class Job:
    """JES job information."""
    jobid: str
    jobname: str
    status: str
    spool_files: int = 0
    owner: Optional[str] = None
    job_class: Optional[str] = None
    return_code: Optional[str] = None
    
    @property
    def is_active(self) -> bool:
        """Check if job is currently executing."""
        return self.status == "ACTIVE"
    
    @property
    def is_complete(self) -> bool:
        """Check if job has completed."""
        return self.status in ("OUTPUT", "COMPLETED")


@dataclass
class SpoolFile:
    """Individual spool file information."""
    jobid: str
    spool_id: str
    ddname: str
    step_name: Optional[str] = None
    proc_step: Optional[str] = None
    record_count: int = 0


@dataclass
class PDSMember:
    """PDS member information."""
    name: str
    pds_name: str
    version: Optional[str] = None
    created: Optional[str] = None
    changed: Optional[str] = None
    size: Optional[int] = None
    init: Optional[str] = None
    mod: Optional[str] = None
