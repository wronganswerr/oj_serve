from enum import Enum

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any


class MCException(HTTPException):
    def __init__(self, status_code: Enum, detail: Any, headers: Any = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
