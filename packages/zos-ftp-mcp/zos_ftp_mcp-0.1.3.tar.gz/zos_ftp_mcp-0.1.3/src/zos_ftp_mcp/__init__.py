"""
z/OS FTP MCP Server

A Model Context Protocol (MCP) server for interacting with z/OS mainframe systems via FTP.
Provides tools for listing datasets, downloading files, and managing PDS members.

Usage as MCP Server:
    Set ZFTP_* environment variables and run: zos-ftp-mcp

Environment Variables:
    ZFTP_HOST - z/OS mainframe hostname
    ZFTP_PORT - FTP port (default: 21)
    ZFTP_USER - FTP username
    ZFTP_PASSWORD - FTP password
    ZFTP_TIMEOUT - Connection timeout (default: 30.0)
    ZFTP_DOWNLOAD_PATH - Local download directory (default: /tmp)
"""

__version__ = "0.1.3"
__author__ = "Arunkumar Selvam"
__email__ = "aruninfy123@gmail.com"

from .server import run_server
from .zos_ftp import ZosFtpClient
from .models import ConnectionConfig, Dataset, Job, PDSMember, SpoolFile
from .exceptions import (
    ZosFtpError, ZosConnectionError, AuthenticationError,
    JobNotFoundError, DatasetNotFoundError, JesInterfaceLevelError,
    InvalidJobNameError, JclError, TransferError
)

def main() -> None:
    """Entry point for the MCP server."""
    run_server()

__all__ = [
    "main",
    "run_server",
    "ZosFtpClient",
    "ConnectionConfig",
    "Dataset",
    "Job",
    "PDSMember",
    "SpoolFile",
    "ZosFtpError",
    "ZosConnectionError",
    "AuthenticationError",
    "JobNotFoundError",
    "DatasetNotFoundError",
    "JesInterfaceLevelError",
    "InvalidJobNameError",
    "JclError",
    "TransferError",
]

