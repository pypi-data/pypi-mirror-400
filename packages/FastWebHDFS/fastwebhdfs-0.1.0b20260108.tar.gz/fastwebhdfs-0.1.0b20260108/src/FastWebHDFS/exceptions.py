from httpx import Response


class WebHDFSException(Exception):
    
    def __init__(self, response: Response):
        
        self.status_code = response.status_code
        try:
            remote = response.json().get("RemoteException", {})
        except Exception:
            remote = {}
        
        self.exception = remote.get("exception", "UnknownException")
        self.java_class = remote.get("javaClassName")
        self.message = remote.get("message", "No message provided")
        
        super().__init__(f"{self.status_code} {self.exception}: {self.message}")

class FileAlreadyExistsException(WebHDFSException):
    """Raised when a file or directory already exists.

    403 Forbidden
    """
    pass

class ParentNotDirectoryException(WebHDFSException):
    """Raised when the parent path is not a directory.
    
    403 Forbidden
    """
    pass

class FileNotFoundException(WebHDFSException):
    """Raised when a required file or directory does not exist.
    
    404 Not Found
    """
    pass
