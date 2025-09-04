# app/schemas/general_response.py
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """
    Standardized error response format.
    """
    error_code: str = Field(..., description="Stable application-specific error code.")
    message: str = Field(..., description="A human-readable error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details, if any.")
    path: Optional[str] = Field(None, description="The request path where error occurred.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp when the error occurred.")
    request_id: Optional[str] = Field(None, description="Correlation/Request ID for tracing.")

    @field_serializer("timestamp")
    def _serialize_ts(self, ts: datetime) -> str:
        # Standardize as ISO-8601; add 'Z' to indicate UTC if naive
        if ts.tzinfo is None:
            return ts.isoformat() + "Z"
        return ts.astimezone().isoformat()

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "RESOURCE_3001",
                "message": "The requested resource was not found.",
                "details": {"resource": "user_info", "id": 123},
                "path": "/api/eva/user-info/123",
                "timestamp": "2025-01-01T12:00:00.000000Z",
                "request_id": "c3f1a572-2bb8-4f86-9a3e-3a9921efbd0d",
            }
        }


class SuccessResponse(BaseModel):
    """Standardized success response format for non-entity endpoints."""
    message: str = Field(..., description="A human-readable success message.")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional additional data.")
    success: bool = Field(default=True, description="Always true for success responses.")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully.",
                "data": {"id": 123, "status": "deleted"},
                "success": True,
            }
        }