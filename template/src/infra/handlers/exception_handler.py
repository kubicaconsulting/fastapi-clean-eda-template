from fastapi import Request, status as HTTPStatus
from fastapi.responses import JSONResponse

from infra.logging import get_logger
from template.src.infra.errors.operational_exception import OperationalException

logger = get_logger(__name__)


async def app_exception_handler(
    request: Request, exc: OperationalException | Exception
):
    status = exc.status if exc.status else exc.status_code
    message = exc.message if exc.message else exc.detail

    try:
        logger.error(f"[UNHANDELED_EXCEPTION]: {message}")
        return JSONResponse(status_code=status, content={"error": message})
    except Exception as e:
        logger.error(f"[UNHANDELED_EXCEPTION]: {e}")
        return JSONResponse(
            status_code=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": message},
        )
