"""Pydantic models for layback algorithm data."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LaybackAlgorithmBase(BaseModel):
    """Base model for layback algorithm data.

    Attributes:
        name: Algorithm name.
        description: Algorithm description.
    """

    name: str | None = None
    description: str | None = None


class LaybackAlgorithmCreate(LaybackAlgorithmBase):
    """Model for creating layback algorithm data.

    Attributes:
        name: Algorithm name.
        description: Algorithm description.
    """


class LaybackAlgorithmUpdate(LaybackAlgorithmBase):
    """Model for updating layback algorithm data.

    Attributes:
        name: Algorithm name.
        description: Algorithm description.
    """


class LaybackAlgorithm(LaybackAlgorithmBase):
    """Model for layback algorithm data with database fields.

    Attributes:
        layback_algorithm_id: Unique identifier for the layback algorithm.
    """

    layback_algorithm_id: UUID

    model_config = ConfigDict(from_attributes=True)
