"""
Flat, user-friendly leave model for Alight SDK.
"""

import datetime
from typing import Optional, Dict, Any
from pydantic import Field, BaseModel

from .utils import add_to_nested_path  # not used here


class Leave(BaseModel):
    """
    Simplified leave model.
    Uses PURE schema-driven conversion - NO hardcoded structure mappings.
    Uses aliases to match expected field names in Employee model.
    Maps to IndicativeEmployment.employment_lifecycle.leave[0].
    """
    model_config = {
        "populate_by_name": True
    }

    leave_reason_code: Optional[str] = Field(
        default=None,
        description="Reason for leave",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.leave[0].leave_reason_code"
    )
    leave_status_code: Optional[str] = Field(
        default=None,
        description="Current leave status",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.leave[0].leave_status_code"
    )
    leave_start_date: Optional[datetime.date] = Field(
        default=None,
        description="Leave start date",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.leave[0].leave_start_date"
    )
    last_paid_date: Optional[datetime.date] = Field(
        default=None,
        description="Last paid date during leave",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.leave[0].last_paid_date"
    )
    scheduled_work_return_date: Optional[datetime.date] = Field(
        default=None,
        description="Scheduled work return date",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.leave[0].scheduled_work_return_date"
    )
    work_return_date: Optional[datetime.date] = Field(
        default=None,
        description="Actual work return date",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.leave[0].work_return_date"
    )

    def to_nested_dict(self) -> Dict[str, Any]:
        """
        Convert to nested structure compatible with employee model.
        """
        return self.model_dump(exclude_none=True, by_alias=True)
