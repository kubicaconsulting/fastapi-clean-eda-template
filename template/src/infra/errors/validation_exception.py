from fastapi import status as HTTPStatus

from .operational_exception import OperationalException


class ValidationException(OperationalException):
    def __init__(
        self,
        status: int = HTTPStatus.HTTP_400_BAD_REQUEST,
        message: str = "Invalid Entity",
    ):
        super().__init__(status=status, message=message)
