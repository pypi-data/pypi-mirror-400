"""Pydantic models for processing log data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProcessingLogBase(BaseModel):
    """Base model for processing log data.

    Attributes:
        processing_step: Name of the processing step.
        processor_name: Name of the processor.
        processing_parameters: Processing parameters in JSON format.
        start_timestamp: Start timestamp of processing.
        end_timestamp: End timestamp of processing.
        status: Status of the processing step.
        error_details: Error details if processing failed.
    """

    processing_step: str
    processor_name: str | None = None
    processing_parameters: dict | None = None
    start_timestamp: datetime
    end_timestamp: datetime
    status: str
    error_details: str | None = None


class ProcessingLogCreate(ProcessingLogBase):
    """Model for creating processing log data.

    Attributes:
        survey_id: Foreign key reference to Survey.
        source_id: Foreign key reference to Source.
    """

    survey_id: UUID
    source_id: UUID


class ProcessingLogUpdate(ProcessingLogBase):
    """Model for updating processing log data.

    Attributes:
        processing_step: Name of the processing step.
        processor_name: Name of the processor.
        processing_parameters: Processing parameters in JSON format.
        start_timestamp: Start timestamp of processing.
        end_timestamp: End timestamp of processing.
        status: Status of the processing step.
        error_details: Error details if processing failed.
    """


class ProcessingLog(ProcessingLogBase):
    """Model for processing log data with database fields.

    Attributes:
        processing_log_id: Unique identifier for the processing log.
        survey_id: Foreign key reference to Survey.
        source_id: Foreign key reference to Source.
    """

    processing_log_id: UUID
    survey_id: UUID
    source_id: UUID

    model_config = ConfigDict(from_attributes=True)
