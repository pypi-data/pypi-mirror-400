class SNPClientError(Exception):
    """Raised when there is a general error in the SNP client."""
    pass

class AuthenticationError(SNPClientError):
    """Raised when there is an authentication error."""
    pass

class UploadError(SNPClientError):
    """Raised when there is an error during file upload."""
    pass

class FolderNotFoundError(SNPClientError):
    """Raised when a specified folder is not found."""
    pass

