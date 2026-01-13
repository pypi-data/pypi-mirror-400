import logging
from datetime import datetime, timezone
from typing import Annotated, Dict, Optional

from bson import ObjectId
from bson import errors as bson_errors
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
)

logger = logging.getLogger(__name__)


def validate_object_id(value: str) -> str:
    """
    Validate and convert ObjectId to string.

    Args:
        value: ObjectId string or ObjectId instance

    Returns:
        String representation of ObjectId

    Raises:
        ValueError: If value is not a valid ObjectId
    """
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, str):
        try:
            # Validate format
            ObjectId(value)
            return value
        except (bson_errors.InvalidId, TypeError) as e:
            raise ValueError(f"Invalid ObjectId format: {value}") from e
    raise TypeError(f"Expected str or ObjectId, got {type(value).__name__}")


# Convert MongoDB ObjectId to string for GraphQL compatibility
PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]


class BaseDBModel(BaseModel):
    """
    Base model for all MongoDB documents with built-in audit fields.
    Uses _id alias for MongoDB compatibility.

    Provides automatic tracking of:
    - Creation and update timestamps
    - User who created/updated the document
    - Soft delete support via deleted_at
    """

    id: Optional[PyObjectId] = Field(
        alias="_id", default=None, description="Document unique identifier"
    )

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when document was created",
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when document was last updated",
    )
    deleted_at: Optional[datetime] = Field(
        default=None, description="Timestamp when document was soft-deleted"
    )

    created_by: str = Field(
        default="system", description="User who created the document"
    )
    updated_by: str = Field(
        default="system", description="User who last updated the document"
    )

    @field_validator("created_by", "updated_by")
    @classmethod
    def validate_user_not_empty(cls, value: str) -> str:
        """Validate that user identifier is not empty."""
        if not value or not isinstance(value, str):
            raise ValueError("User identifier must be a non-empty string")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


class TimeSeriesDBModel(BaseModel):
    """
    Base model for MongoDB Time Series collections.

    Time Series collections are optimized for time-stamped data like:
    - Sensor readings
    - Logs
    - Metrics
    - Events

    Required fields:
    - time_field: The timestamp field (default: 'timestamp')
    - meta_field: Optional metadata field for grouping

    Usage:
        class SensorReading(TimeSeriesDBModel):
            timestamp: datetime  # Required time field
            sensor_id: str       # Metadata field
            temperature: float
            humidity: float

            class TimeSeriesConfig:
                time_field = "timestamp"
                meta_field = "sensor_id"
                granularity = "seconds"  # or "minutes", "hours"
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class TimeSeriesConfig:
        """Configuration for Time Series collection."""

        time_field: str = "timestamp"
        meta_field: Optional[str] = None
        granularity: str = "seconds"  # "seconds", "minutes", or "hours"

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class AuditLogModel(BaseModel):
    """
    Model for audit log entries stored in Time Series collection.

    Tracks all CRUD operations with detailed change information.
    """

    id: Optional[PyObjectId] = Field(
        alias="_id", default=None, description="Audit log entry identifier"
    )
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the audited action",
    )
    user: str = Field(description="User who performed the action")
    action: str = Field(
        description="Action type: CREATE, UPDATE, DELETE, RESTORE, HARD_DELETE"
    )
    collection: str = Field(
        description="Collection name where action occurred"
    )
    doc_id: str = Field(description="Document ID that was affected")
    changes: Optional[Dict] = Field(
        default=None, description="Detailed changes (for UPDATE/DELETE)"
    )

    @field_validator("action")
    @classmethod
    def validate_action(cls, value: str) -> str:
        """Validate action is one of the allowed values."""
        allowed_actions = {
            "CREATE",
            "UPDATE",
            "DELETE",
            "RESTORE",
            "HARD_DELETE",
        }
        if value not in allowed_actions:
            raise ValueError(
                f"Action must be one of {allowed_actions}, got {value}"
            )
        return value

    @field_validator("user", "collection", "doc_id")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        """Validate that string fields are not empty."""
        if not value or not isinstance(value, str):
            raise ValueError("Field must be a non-empty string")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )
