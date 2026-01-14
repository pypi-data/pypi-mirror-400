"""
Flat, user-friendly termination model for Alight SDK.
"""

import datetime
from typing import Optional, Dict, Any
from pydantic import Field, BaseModel

from .utils import add_to_nested_path  # not used here


class Termination(BaseModel):
    """
    Simplified termination model.
    Maps to IndicativeEmployment.employment_lifecycle.termination.
    """
    model_config = {
        "populate_by_name": True
    }

    voluntary_termination_indicator: Optional[bool] = Field(
        default=None,
        description="Voluntary termination indicator",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.termination.voluntary_termination_indicator"
    )
    termination_reason_code: Optional[str] = Field(
        default=None,
        description="Reason for termination",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.termination.termination_reason_code"
    )
    termination_date: Optional[datetime.date] = Field(
        default=None,
        description="Termination date",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.termination.termination_date"
    )
    last_worked_date: Optional[datetime.date] = Field(
        default=None,
        description="Last worked date",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.termination.last_worked_date"
    )
    last_paid_date: Optional[datetime.date] = Field(
        default=None,
        description="Last paid date",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.termination.last_paid_date"
    )

    def to_nested_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)
