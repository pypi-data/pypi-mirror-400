"""Pydantic models for hierarchy operations."""

from uuid import UUID

from pydantic import BaseModel


class Organization(BaseModel):
    """Pydantic model for organization data."""

    organization_id: UUID
    organization_name: str


class Project(Organization):
    """Pydantic model for project data."""

    project_id: UUID
    project_name: str


class Survey(Project):
    """Pydantic model for survey data."""

    survey_id: UUID
    survey_name: str


class Source(Survey):
    """Pydantic model for source data."""

    source_id: UUID
    source_file_name: str
