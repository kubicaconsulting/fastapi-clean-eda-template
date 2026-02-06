from abc import ABC
from fastapi import status as HTTPStatus

from .base_app_exception import BaseAppException


class OperationalException(BaseAppException, ABC):
    """Base exception for operational errors"""

    isOperational: bool = True
    data: dict = {}

    def __init__(
        self,
        status: int = HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str | None = "Unkown Error",
    ):
        self.status = status
        self.message = message

        super().__init__(status=self.status, message=self.message)

    def append_data(self, data: dict):
        self.data = {**self.data, **data}
        return self

    def set_is_operational(self, isOperational: bool):
        self.isOperational = isOperational
        return self

    def add_cause(self, cause: str | dict):
        self.cause = cause
        return self
