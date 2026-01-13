"""Pydantic models for layback type data."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LaybackTypeBase(BaseModel):
    """Base model for layback type data.

    Attributes:
        name: Name of the layback type.
        description: Description of the layback type.
    """

    name: str | None = None
    description: str | None = None


class LaybackTypeCreate(LaybackTypeBase):
    """Model for creating layback type data.

    Attributes:
        name: Name of the layback type.
        description: Description of the layback type.
    """


class LaybackTypeUpdate(LaybackTypeBase):
    """Model for updating layback type data.

    Attributes:
        name: Name of the layback type.
        description: Description of the layback type.
    """


class LaybackType(LaybackTypeBase):
    """Model for layback type data with database fields.

    Attributes:
        layback_type_id: Unique identifier for the layback type.
    """

    layback_type_id: UUID

    model_config = ConfigDict(from_attributes=True)
