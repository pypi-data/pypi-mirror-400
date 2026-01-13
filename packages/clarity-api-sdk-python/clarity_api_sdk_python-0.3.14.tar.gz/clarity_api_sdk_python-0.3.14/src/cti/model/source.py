"""Pydantic models for source data."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class SourceStatus(str, Enum):
    """Status of a source file upload."""

    UPLOADING = "uploading"
    READY = "ready"
    ERROR = "error"


class SourceBase(BaseModel):
    """Base model for source data.

    Attributes:
        survey_id: Foreign key reference to Survey.
        file_name: Name of the external source file.
        file_size: Size of the external source file in bytes.
    """

    survey_id: UUID
    file_name: str
    file_size: int

    @field_validator("file_name")
    @classmethod
    def validate_file_name(cls, value: str) -> str:
        """Validate that file_name has a '.xtf' or '.jsf' extension.

        Args:
            value: Name of the external source file.

        Returns:
            The validated file_name.

        Raises:
            ValueError: If file_name does not have a '.xtf' or '.jsf' extension.
        """
        if not value.lower().endswith((".xtf", ".jsf")):
            raise ValueError("file_name must have a '.xtf' or '.jsf' extension")
        return value


class SourceCreate(SourceBase):
    """Model for creating source data (with survey_id in body)."""


class SourceUpdate(SourceBase):
    """Model for updating source data.

    Attributes:
    """


class Source(SourceBase):
    """Model for source data with database fields.

    Attributes:
        source_id: Unique identifier for the source.
        status: Upload status (uploading, ready, error).
        uri: uri for source, will allow AWS S3, Google Cloud Storage, NFS, URL, or Azure Blob URI (set after upload initiated).
        meta_data: meta data for the uri
        upload_id: S3 multipart upload ID (present while uploading, cleared when complete).
    """

    source_id: UUID
    status: SourceStatus = SourceStatus.UPLOADING
    uri: str | None = None
    meta_data: dict
    upload_id: str | None = None
    created_date: datetime
    updated_date: datetime
    updated_by: str

    model_config = ConfigDict(from_attributes=True)


class SourceWithUpload(Source):
    """Source response including upload information.

    Overrides optional fields from Source to be required for upload responses.
    """
