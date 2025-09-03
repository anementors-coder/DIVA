from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import logging
from datetime import datetime

from app.core.errors import ErrorCode, ErrorMessage, OnboardingException
from app.schemas.general_response import ErrorResponse

logger = logging.getLogger(__name__)


async def onboarding_exception_handler(request: Request, exc: OnboardingException) -> JSONResponse:
    """
    Handle OnboardingException globally
    """
    logger.error(f"OnboardingException: {exc.error_code.value} - {exc.message}")
    
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
        ErrorCode.INTERNAL_SERVER_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.SERVICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    }
    
    http_status = status_code_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    error_response = ErrorResponse(
        error_code=exc.error_code.value,
        message=exc.message,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=http_status,
        content=error_response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle FastAPI validation errors
    """
    logger.error(f"Validation error: {exc.errors()}")
    
    # Extract validation errors
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        error_code=ErrorCode.INVALID_INPUT.value,
        message="Input validation failed",
        details={"validation_errors": error_details}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.dict()
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors
    """
    logger.error(f"Pydantic validation error: {exc.errors()}")
    
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        error_code=ErrorCode.INVALID_INPUT.value,
        message="Data validation failed",
        details={"validation_errors": error_details}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions
    """
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    # Map HTTP status codes to our error codes
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
        details={"status_code": exc.status_code}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle SQLAlchemy database errors
    """
    logger.error(f"Database error: {str(exc)}")
    
    error_response = ErrorResponse(
        error_code=ErrorCode.DATABASE_CONNECTION_ERROR.value,
        message="A database error occurred",
        details={"error": str(exc)}
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error_response.dict()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle any other unexpected exceptions
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    error_response = ErrorResponse(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        message="An unexpected error occurred",
        details={"error": str(exc)}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app
    """
    app.add_exception_handler(OnboardingException, onboarding_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)