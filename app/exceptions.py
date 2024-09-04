from enum import Enum

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any
from app.common.core.logger import get_logger
# from app.exceptions import MCException
from app.schemas.response_schemas import MCResponse

logger = get_logger(__name__)


class MCException(HTTPException):
    def __init__(self, status_code: Enum, detail: Any, headers: Any = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(MCException)
    async def mc_exception_handler(request: Request, exc: MCException):
        logger.warning(f"MCException: {exc.status_code.value[0]} {exc.status_code.value[1]}")

        return JSONResponse(
            status_code=200,
            content=MCResponse(
                code=exc.status_code.value[0],
                error_code=exc.status_code.value[0],
                error_message=exc.status_code.value[1],
                payload={"detail": exc.detail}
            ).dict(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        logger.warning(f"HTTPException: {exc.status_code} {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=MCResponse(
                code=exc.status_code,
                error_code=exc.status_code,
                error_message=str(exc.detail),
                payload={}
            ).dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        logger.warning(f"RequestValidationError: 422 {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content=MCResponse(
                code=422,
                error_code=422,
                error_message="Unprocessable Entity",
                payload={"detail": str(exc.errors.__str__())}
            ).dict(),
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc: ValidationError):
        logger.error(f"ValidationError: 500 {exc.json()}")
        return JSONResponse(
            status_code=500,
            content=MCResponse(
                code=500,
                error_code=500,
                error_message="Internal Server Error",
                payload={}
            ).dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"Exception: 500 {exc}")
        return JSONResponse(
            status_code=500,
            content=MCResponse(
                code=500,
                error_code=500,
                error_message=str(exc),
                payload={}
            ).dict(),
        )
