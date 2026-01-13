"""Pydantic models for processed depth data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProcessedDepthBase(BaseModel):
    """Base model for processed depth data.

    Attributes:
        time: Timestamp of the depth measurement.
        channel: Channel identifier.
        value: Depth value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    time: datetime
    channel: int | None = None
    value: float | None = None
    quality: float | None = None
    qc_flags: dict


class ProcessedDepthCreate(ProcessedDepthBase):
    """Model for creating processed depth data.

    Attributes:
        depth_source_id: Foreign key reference to DepthSource.
    """

    depth_source_id: UUID


class ProcessedDepthUpdate(BaseModel):
    """Model for updating processed depth data.

    Attributes:
        time: Timestamp of the depth measurement.
        channel: Channel identifier.
        value: Depth value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    time: datetime | None = None
    channel: int | None = None
    value: float | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class ProcessedDepth(ProcessedDepthBase):
    """Model for processed depth data with database fields.

    Attributes:
        processed_depth_id: Unique identifier for the processed depth.
        depth_source_id: Foreign key reference to DepthSource.
    """

    processed_depth_id: UUID
    depth_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
