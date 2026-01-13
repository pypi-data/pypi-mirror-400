"""Pydantic models for raw depth data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RawDepthBase(BaseModel):
    """Base model for raw depth data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the depth measurement.
        value: Depth value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int
    time: datetime
    value: float
    quality: float | None = None
    qc_flags: dict | None = None


class RawDepthCreate(RawDepthBase):
    """Model for creating raw depth data.

    Attributes:
        depth_source_id: Foreign key reference to DepthSource.
    """

    depth_source_id: UUID


class RawDepthUpdate(BaseModel):
    """Model for updating raw depth data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the depth measurement.
        value: Depth value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int | None = None
    time: datetime | None = None
    value: float | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class RawDepth(RawDepthBase):
    """Model for raw depth data with database fields.

    Attributes:
        raw_depth_id: Unique identifier for the raw depth.
        depth_source_id: Foreign key reference to DepthSource.
    """

    raw_depth_id: UUID
    depth_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
