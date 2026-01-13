"""Pydantic models for final product data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FinalProductBase(BaseModel):
    """Base model for final product data.

    Attributes:
        product_type: Type of the product.
        file_path: Path to the GeoZarr or other file.
        geodesy_srid: Geodetic spatial reference system identifier.
        processing_parameters: Processing parameters in JSON format.
        processing_date: Date of processing.
    """

    product_type: str
    file_path: str
    geodesy_srid: str
    processing_parameters: dict | None = None
    processing_date: datetime


class FinalProductCreate(FinalProductBase):
    """Model for creating final product data.

    Attributes:
        survey_id: Foreign key reference to Survey.
    """

    survey_id: UUID


class FinalProductUpdate(BaseModel):
    """Model for updating final product data.

    Attributes:
        product_type: Type of the product.
        file_path: Path to the GeoZarr or other file.
        geodesy_srid: Geodetic spatial reference system identifier.
        processing_parameters: Processing parameters in JSON format.
        processing_date: Date of processing.
    """

    product_type: str | None = None
    file_path: str | None = None
    geodesy_srid: str | None = None
    processing_parameters: dict | None = None
    processing_date: datetime | None = None


class FinalProduct(FinalProductBase):
    """Model for final product data with database fields.

    Attributes:
        product_id: Unique identifier for the final product.
        survey_id: Foreign key reference to Survey.
    """

    product_id: UUID
    survey_id: UUID

    model_config = ConfigDict(from_attributes=True)
