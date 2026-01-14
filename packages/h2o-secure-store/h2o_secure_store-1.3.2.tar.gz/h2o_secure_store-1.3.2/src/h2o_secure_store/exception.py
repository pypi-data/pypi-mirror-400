import json

from h2o_secure_store.gen import ApiException


class TimeoutException(Exception):
    """Exception raised when timeout is exceeded."""

    def __init__(self):
        super().__init__("Timeout exceeded")


class CustomApiException(ApiException):
    """ApiException with simplified error message.
    """

    def __init__(self, e: ApiException):
        self.status = e.status
        self.reason = e.reason
        self.body = e.body
        self.headers = e.headers

    def __str__(self):
        status_reason = f"{self.status} ({self.reason})"
        message = self.body

        if message is None:
            return status_reason

        try:
            body_json = json.loads(self.body)
            message = body_json["message"]
        except (ValueError, KeyError):
            pass

        return f"{status_reason}: {message}"
