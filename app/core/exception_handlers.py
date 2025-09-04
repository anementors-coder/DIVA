# app/core/exception_handlers.py
import logging
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any

from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.core.errors import ErrorCode, OnboardingException
from app.schemas.general_response import ErrorResponse

logger = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str:
    rid = getattr(request.state, "request_id", None)
    if rid:
        return rid
    return request.headers.get("x-request-id") or request.headers.get("X-Request-ID") or str(uuid.uuid4())


def _headers_with_context(request: Request) -> Dict[str, str]:
    rid = _get_request_id(request)
    start_time = getattr(request.state, "start_time", None)
    duration_ms = None
    if start_time is not None:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
    headers = {"X-Request-ID": rid}
    if duration_ms is not None:
        headers["X-Response-Time"] = f"{duration_ms}ms"
    return headers


async def onboarding_exception_handler(request: Request, exc: OnboardingException) -> JSONResponse:
    logger.error(f"OnboardingException: {exc.error_code.value} - {exc.message} - details={exc.details}")

    status_code_map = {
        ErrorCode.INVALID_TOKEN: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.MISSING_USER_ID: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.UNAUTHORIZED_ACCESS: status.HTTP_403_FORBIDDEN,

        ErrorCode.INVALID_INPUT: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.MISSING_REQUIRED_FIELD: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.INVALID_URL_FORMAT: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.INVALID_JSON_FORMAT: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.FIELD_TOO_LONG: status.HTTP_422_UNPROCESSABLE_ENTITY,

        ErrorCode.RESOURCE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.QUESTION_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.USER_INFO_NOT_FOUND: status.HTTP_404_NOT_FOUND,

        ErrorCode.RESOURCE_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.USER_INFO_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.RESOURCE_CONFLICT: status.HTTP_409_CONFLICT,

        ErrorCode.DATABASE_CONNECTION_ERROR: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.DATABASE_CONSTRAINT_VIOLATION: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.DATABASE_TRANSACTION_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,

        ErrorCode.INVALID_ONBOARDING_DATA: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.QUESTION_CREATION_FAILED: status.HTTP_500_INTERNAL_SERVER_ERROR,

        # File upload errors
        ErrorCode.FILE_TOO_LARGE: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        ErrorCode.INVALID_FILE_TYPE: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        ErrorCode.INVALID_FILE_CONTENT: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.FILE_UPLOAD_FAILED: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.FILE_NOT_FOUND: status.HTTP_404_NOT_FOUND,

        ErrorCode.INTERNAL_SERVER_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.SERVICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    }

    http_status = status_code_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    error_response = ErrorResponse(
        error_code=exc.error_code.value,
        message=exc.message,
        details=exc.details,
        path=str(request.url.path),
        request_id=_get_request_id(request),
        timestamp=datetime.utcnow(),
    )

    return JSONResponse(
        status_code=http_status,
        content=jsonable_encoder(error_response),
        headers=_headers_with_context(request),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.error(f"Validation error: {exc.errors()}")

    error_details: List[Dict[str, Any]] = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", ""),
            "type": error.get("type", "")
        })

    error_response = ErrorResponse(
        error_code=ErrorCode.INVALID_INPUT.value,
        message="Input validation failed",
        details={"validation_errors": error_details},
        path=str(request.url.path),
        request_id=_get_request_id(request),
        timestamp=datetime.utcnow(),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(error_response),
        headers=_headers_with_context(request),
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.error(f"Pydantic validation error: {exc.errors()}")

    error_details: List[Dict[str, Any]] = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", ""),
            "type": error.get("type", "")
        })

    error_response = ErrorResponse(
        error_code=ErrorCode.INVALID_INPUT.value,
        message="Data validation failed",
        details={"validation_errors": error_details},
        path=str(request.url.path),
        request_id=_get_request_id(request),
        timestamp=datetime.utcnow(),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(error_response),
        headers=_headers_with_context(request),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")

    error_code_map = {
        status.HTTP_400_BAD_REQUEST: ErrorCode.INVALID_INPUT,
        status.HTTP_401_UNAUTHORIZED: ErrorCode.INVALID_TOKEN,
        status.HTTP_403_FORBIDDEN: ErrorCode.UNAUTHORIZED_ACCESS,
        status.HTTP_404_NOT_FOUND: ErrorCode.RESOURCE_NOT_FOUND,
        status.HTTP_409_CONFLICT: ErrorCode.RESOURCE_CONFLICT,
        status.HTTP_422_UNPROCESSABLE_ENTITY: ErrorCode.INVALID_INPUT,
        status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorCode.INTERNAL_SERVER_ERROR,
        status.HTTP_503_SERVICE_UNAVAILABLE: ErrorCode.SERVICE_UNAVAILABLE,
    }
    error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)

    error_response = ErrorResponse(
        error_code=error_code.value,
        message=str(exc.detail),
        details={"status_code": exc.status_code},
        path=str(request.url.path),
        request_id=_get_request_id(request),
        timestamp=datetime.utcnow(),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response),
        headers=_headers_with_context(request),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.error(f"Database error: {str(exc)}")

    error_response = ErrorResponse(
        error_code=ErrorCode.DATABASE_CONNECTION_ERROR.value,
        message="A database error occurred",
        details={"error": str(exc)},
        path=str(request.url.path),
        request_id=_get_request_id(request),
        timestamp=datetime.utcnow(),
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=jsonable_encoder(error_response),
        headers=_headers_with_context(request),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    error_response = ErrorResponse(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        message="An unexpected error occurred",
        details={"error": str(exc)},
        path=str(request.url.path),
        request_id=_get_request_id(request),
        timestamp=datetime.utcnow(),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(error_response),
        headers=_headers_with_context(request),
    )


def register_exception_handlers(app):
    app.add_exception_handler(OnboardingException, onboarding_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)