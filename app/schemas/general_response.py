from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# =============================
# Common API Response Schemas
# =============================

class ErrorResponse(BaseModel):
    """
    Standardized error response format, reflecting FastAPI's default for HTTPException.
    """
    detail: str = Field(..., description="A human-readable description of the error.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "User info not found.",
            }
        }

class SuccessResponse(BaseModel):
    """Standardized success response format for the API."""
    message: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully.",
                "data": {"id": 123, "status": "created"}
            }
        }

# =============================
# Pagination Schemas (Inactive)
# =============================
# Note: Pagination was removed from endpoints and CRUD functions.
# These schemas are kept for potential future use but are not currently active.

class PaginationParams(BaseModel):
    """Schema for pagination query parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Generic schema for a paginated response."""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int