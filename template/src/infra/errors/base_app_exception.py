from fastapi import HTTPException


class BaseAppException(HTTPException):
    """Base exception for our application"""

    def __init__(self, status: int, message: str):
        super().__init__(status_code=status, detail=message)
