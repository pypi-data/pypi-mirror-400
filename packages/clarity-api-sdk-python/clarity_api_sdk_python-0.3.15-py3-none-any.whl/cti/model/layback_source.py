"""Pydantic models for layback source data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LaybackSourceBase(BaseModel):
    """Base model for layback source data.

    Attributes:
        input_timezone: Input timezone string.
        channels: Number of channels.
        start_time: Start timestamp.
        end_time: End timestamp.
    """

    input_timezone: str
    channels: int
    start_time: datetime
    end_time: datetime


class LaybackSourceCreate(LaybackSourceBase):
    """Model for creating layback source data.

    Attributes:
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
        layback_type_id: Foreign key reference to LaybackType.
        layback_algorithm_id: Foreign key reference to LaybackAlgorithm.
    """

    device_id: UUID
    source_id: UUID
    layback_type_id: UUID
    layback_algorithm_id: UUID


class LaybackSourceUpdate(LaybackSourceBase):
    """Model for updating layback source data.

    Attributes:
        input_timezone: Input timezone string.
        channels: Number of channels.
        start_time: Start timestamp.
        end_time: End timestamp.
    """


class LaybackSource(LaybackSourceBase):
    """Model for layback source data with database fields.

    Attributes:
        layback_source_id: Unique identifier for the layback source.
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
        layback_type_id: Foreign key reference to LaybackType.
        layback_algorithm_id: Foreign key reference to LaybackAlgorithm.
    """

    device_id: UUID
    source_id: UUID
    layback_type_id: UUID
    layback_algorithm_id: UUID

    model_config = ConfigDict(from_attributes=True)
