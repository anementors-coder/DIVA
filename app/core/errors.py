# app/core/errors.py
from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(Enum):
    """Enumeration of error codes for the application"""

    # Authentication & Authorization Errors (1000-1999)
    INVALID_TOKEN = "AUTH_1001"
    MISSING_USER_ID = "AUTH_1002"
    UNAUTHORIZED_ACCESS = "AUTH_1003"

    # Validation Errors (2000-2999)
    INVALID_INPUT = "VALIDATION_2001"
    MISSING_REQUIRED_FIELD = "VALIDATION_2002"
    INVALID_URL_FORMAT = "VALIDATION_2003"
    INVALID_JSON_FORMAT = "VALIDATION_2004"
    FIELD_TOO_LONG = "VALIDATION_2005"

    # Resource Errors (3000-3999)
    RESOURCE_NOT_FOUND = "RESOURCE_3001"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_3002"
    RESOURCE_CONFLICT = "RESOURCE_3003"

    # Database Errors (4000-4999)
    DATABASE_CONNECTION_ERROR = "DB_4001"
    DATABASE_CONSTRAINT_VIOLATION = "DB_4002"
    DATABASE_TRANSACTION_ERROR = "DB_4003"

    # Onboarding Specific Errors (5000-5999)
    QUESTION_NOT_FOUND = "ONBOARD_5001"
    USER_INFO_NOT_FOUND = "ONBOARD_5002"
    USER_INFO_ALREADY_EXISTS = "ONBOARD_5003"
    INVALID_ONBOARDING_DATA = "ONBOARD_5004"
    QUESTION_CREATION_FAILED = "ONBOARD_5005"

    # File Upload Errors (6000-6999)
    FILE_TOO_LARGE = "UPLOAD_6001"
    INVALID_FILE_TYPE = "UPLOAD_6002"
    INVALID_FILE_CONTENT = "UPLOAD_6003"
    FILE_UPLOAD_FAILED = "UPLOAD_6004"
    FILE_NOT_FOUND = "UPLOAD_6005"

    # Server Errors (9000-9999)
    INTERNAL_SERVER_ERROR = "SERVER_9001"
    SERVICE_UNAVAILABLE = "SERVER_9002"


class ErrorMessage:
    """Class containing error messages for different error codes"""

    ERROR_MESSAGES: Dict[ErrorCode, str] = {
        # Authentication & Authorization Messages
        ErrorCode.INVALID_TOKEN: "The provided authentication token is invalid or expired.",
        ErrorCode.MISSING_USER_ID: "User ID is missing from the authentication token.",
        ErrorCode.UNAUTHORIZED_ACCESS: "You are not authorized to access this resource.",

        # Validation Messages
        ErrorCode.INVALID_INPUT: "The provided input data is invalid.",
        ErrorCode.MISSING_REQUIRED_FIELD: "One or more required fields are missing.",
        ErrorCode.INVALID_URL_FORMAT: "The provided URL format is invalid.",
        ErrorCode.INVALID_JSON_FORMAT: "The JSON data format is invalid.",
        ErrorCode.FIELD_TOO_LONG: "One or more fields exceed the maximum allowed length.",

        # Resource Messages
        ErrorCode.RESOURCE_NOT_FOUND: "The requested resource was not found.",
        ErrorCode.RESOURCE_ALREADY_EXISTS: "The resource already exists.",
        ErrorCode.RESOURCE_CONFLICT: "There is a conflict with the existing resource.",

        # Database Messages
        ErrorCode.DATABASE_CONNECTION_ERROR: "Unable to establish database connection.",
        ErrorCode.DATABASE_CONSTRAINT_VIOLATION: "Database constraint violation occurred.",
        ErrorCode.DATABASE_TRANSACTION_ERROR: "Database transaction failed.",

        # Onboarding Specific Messages
        ErrorCode.QUESTION_NOT_FOUND: "The requested onboarding question was not found.",
        ErrorCode.USER_INFO_NOT_FOUND: "User onboarding information was not found.",
        ErrorCode.USER_INFO_ALREADY_EXISTS: "User onboarding information already exists.",
        ErrorCode.INVALID_ONBOARDING_DATA: "The onboarding data provided is invalid.",
        ErrorCode.QUESTION_CREATION_FAILED: "Failed to create the onboarding question.",

        # File Upload Messages
        ErrorCode.FILE_TOO_LARGE: "The uploaded file exceeds the maximum allowed size.",
        ErrorCode.INVALID_FILE_TYPE: "Invalid file type. Only PDF is allowed.",
        ErrorCode.INVALID_FILE_CONTENT: "The uploaded file content is invalid or corrupted.",
        ErrorCode.FILE_UPLOAD_FAILED: "Failed to upload the file.",
        ErrorCode.FILE_NOT_FOUND: "The requested file was not found.",

        # Server Messages
        ErrorCode.INTERNAL_SERVER_ERROR: "An unexpected server error occurred.",
        ErrorCode.SERVICE_UNAVAILABLE: "The service is temporarily unavailable.",
    }

    @classmethod
    def get_message(cls, error_code: ErrorCode, custom_message: Optional[str] = None) -> str:
        """
        Get error message for a given error code.

        Args:
            error_code: The error code enum
            custom_message: Optional custom message to override default

        Returns:
            Error message string
        """
        if custom_message:
            return custom_message
        return cls.ERROR_MESSAGES.get(error_code, "An unknown error occurred.")


class OnboardingException(Exception):
    """Custom exception class for onboarding-related errors"""

    def __init__(
        self,
        error_code: ErrorCode,
        custom_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = ErrorMessage.get_message(error_code, custom_message)
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }