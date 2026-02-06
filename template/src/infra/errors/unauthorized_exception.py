from fastapi import status as HTTPStatus

from .operational_exception import OperationalException


class UnauthorizedException(OperationalException):
    def __init__(
        self,
        status: int = HTTPStatus.HTTP_401_UNAUTHORIZED,
        message: str = "Unauthorized Action",
    ):
        super().__init__(status=status, message=message)
