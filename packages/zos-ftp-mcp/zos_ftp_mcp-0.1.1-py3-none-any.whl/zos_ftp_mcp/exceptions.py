"""
Custom exceptions for z/OS FTP operations.
"""


class ZosFtpError(Exception):
    """Base exception for z/OS FTP operations."""
    pass


class ZosConnectionError(ZosFtpError):
    """Connection-related errors."""
    pass


# Alias for backward compatibility
ConnectionError = ZosConnectionError


class AuthenticationError(ZosFtpError):
    """Authentication failures."""
    pass


class JobNotFoundError(ZosFtpError):
    """Job does not exist or is not accessible."""
    pass


class DatasetNotFoundError(ZosFtpError):
    """Dataset does not exist or is not accessible."""
    pass


class JesInterfaceLevelError(ZosFtpError):
    """Operation not supported with current JESINTERFACELEVEL."""
    
    def __init__(self, message: str, level: int = 1):
        self.level = level
        super().__init__(f"{message} (JESINTERFACELEVEL={level})")


class InvalidJobNameError(ZosFtpError):
    """Job name does not match required pattern for JESINTERFACELEVEL=1."""
    
    def __init__(self, jobname: str, userid: str):
        self.jobname = jobname
        self.userid = userid
        super().__init__(
            f"Job name '{jobname}' must start with user ID '{userid}' "
            f"plus one character (e.g., {userid}J) for JESINTERFACELEVEL=1"
        )


class JclError(ZosFtpError):
    """JCL syntax or execution errors."""
    pass


class TransferError(ZosFtpError):
    """File transfer errors."""
    pass
