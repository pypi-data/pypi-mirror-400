from typing import Optional

class SdkError(Exception):
    """Base class for all SDK errors"""


class HttpStatusError(SdkError):

    def __init__(self, status_code: int, message: str, body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class TimeoutError(SdkError):
    pass

class NetworkError(SdkError):
    pass

class InvalidResponseError(SdkError):
    pass
