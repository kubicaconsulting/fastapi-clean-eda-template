from fastapi import status as HTTPStatus

from .operational_exception import OperationalException


class ResourceNotFoundException(OperationalException):
    def __init__(
        self,
        status: int = HTTPStatus.HTTP_404_NOT_FOUND,
        message: str = "Entity Not Found",
    ):
        super().__init__(status=status, message=message)
