from pydantic import ValidationError


class UnprocessableContent(Exception):
    def __init__(
            self,
            error: ValidationError,
            message: str = "Unprocessable Content",
            status_code: int = 422,
    ):
        super().__init__(error)
        self.error = error
        self.message = message
        self.status_code = status_code
        self.error_details = self.get_error_details()

    def get_error_details(self):
        error_messages = []
        for error in self.error.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            error_messages.append(f"{field} {error['msg']}")
        return error_messages
