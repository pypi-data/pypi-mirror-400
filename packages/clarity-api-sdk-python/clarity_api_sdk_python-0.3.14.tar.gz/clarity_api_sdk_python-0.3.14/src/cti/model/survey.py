"""Pydantic models for survey data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SurveyBase(BaseModel):
    """Base model for survey data.

    Attributes:
        name: Survey name.
        description: Survey description.
        geodesy_srid: Geodesy spatial reference identifier.
        timezone_name: Timezone name for the survey.
        updated_by: User who last updated the survey.
    """

    name: str
    description: str | None = None
    geodesy_srid: str
    timezone_name: str


class SurveyCreate(SurveyBase):
    """Model for creating survey data.

    Attributes:
        project_id: Foreign key reference to Project.
    """

    project_id: UUID


class SurveyUpdate(SurveyBase):
    """Model for updating survey data.

    Attributes:
        name: Survey name.
        description: Survey description.
        geodesy_srid: Geodesy spatial reference identifier.
        timezone_name: Timezone name for the survey.
        updated_by: User who last updated the survey.
    """


class Survey(SurveyBase):
    """Model for survey data with database fields.

    Attributes:
        survey_id: Unique identifier for the survey.
        project_id: Foreign key reference to Project.
        created_date: Date when the survey was created.
        updated_date: Date when the survey was last updated.
    """

    survey_id: UUID
    project_id: UUID
    created_date: datetime
    updated_date: datetime
    updated_by: str

    model_config = ConfigDict(from_attributes=True)


class Surveys(BaseModel):
    """Model for a collection of surveys."""

    surveys: list[Survey]
