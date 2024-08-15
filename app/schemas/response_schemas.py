from pydantic import BaseModel, ValidationError
from typing import Any, Optional, Type
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from functools import wraps
import json
from app.common.core.logger import get_logger

logger = get_logger(__name__)


class MCResponse(BaseModel):
    code: int = 0
    error_code: int = 0
    error_message: str = ""
    payload: Optional[Any] = None


def response_model(response_model: Optional[Type[BaseModel]] = None):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            result = await f(*args, **kwargs)

            if response_model is not None:
                try:
                    result = response_model.model_validate(result, from_attributes=True)
                except Exception as e:
                    logger.error(f"Error occurred during {f.__name__}, response_model validate error : {e}")
                    raise e

            return JSONResponse(
                status_code=200,
                content=MCResponse(
                    code=0,
                    error_code=0,
                    error_message="",
                    payload=result,
                ).model_dump(mode='json'),
            )

        return wrapper

    return decorator