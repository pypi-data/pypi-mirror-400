"""
Flat, user-friendly job/deployment model for Alight SDK.
"""

import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field, BaseModel

from .utils import add_to_nested_path  # not used here; kept for parity if needed


class Job(BaseModel):
    """
    Simplified job/deployment model.
    Uses PURE schema-driven conversion - NO hardcoded structure mappings.
    Uses aliases to match expected field names in Employee model.
    """
    model_config = {
        "populate_by_name": True  # Allow populating by field name in addition to alias
    }

    title: str = Field(
        description="Job title",
        alias="indicative_person_dossier.indicative_deployment.job.job_title"
    )
    department: Optional[str] = Field(
        default=None,
        description="Department name",
        alias="indicative_person_dossier.indicative_deployment.department_name"
    )
    position_id: Optional[str] = Field(
        default=None,
        description="Position identifier",
        alias="indicative_person_dossier.indicative_deployment.position_id"
    )
    position_title: Optional[str] = Field(
        default=None,
        description="Position title",
        alias="indicative_person_dossier.indicative_deployment.position_title"
    )
    location_code: Optional[str] = Field(
        default=None,
        description="Work location code",
        alias="indicative_person_dossier.indicative_deployment.work_location.location_id"
    )
    work_location_city_name: Optional[str] = Field(
        default=None,
        description="Work location city name",
        alias="indicative_person_dossier.indicative_deployment.work_location.address.city_name"
    )
    work_location_country_sub_division_code: Optional[str] = Field(
        default=None,
        description="Work location country subdivision/state code",
        alias="indicative_person_dossier.indicative_deployment.work_location.address.country_sub_division_code"
    )
    work_location_postal_code: Optional[str] = Field(
        default=None,
        description="Work location postal code",
        alias="indicative_person_dossier.indicative_deployment.work_location.address.postal_code"
    )
    manager_id: Optional[str] = Field(
        default=None,
        description="Manager employee ID",
        alias="indicative_person_dossier.indicative_deployment.manager_id.id"
    )

    # Schedule
    weekly_hours: Optional[float] = Field(
        default=None,
        description="Weekly working hours",
        alias="indicative_person_dossier.indicative_deployment.schedule.scheduled_hours[0].value"
    )
    weekly_hours_basis: Optional[str] = Field(
        default="Week",
        description="Schedule basis for weekly hours",
        alias="indicative_person_dossier.indicative_deployment.schedule.scheduled_hours[0].schedule_basis"
    )
    pay_cycle_hours: Optional[float] = Field(
        default=None,
        description="Hours per pay cycle",
        alias="indicative_person_dossier.indicative_deployment.schedule.scheduled_hours[1].value"
    )
    pay_cycle_hours_basis: Optional[str] = Field(
        default=None,
        description="Schedule basis for pay cycle hours",
        alias="indicative_person_dossier.indicative_deployment.schedule.scheduled_hours[1].schedule_basis"
    )
    scheduled_days_per_week: Optional[float] = Field(
        default=None,
        description="Scheduled days per week",
        alias="indicative_person_dossier.indicative_deployment.schedule.scheduled_days[0].value"
    )
    scheduled_days_basis: Optional[str] = Field(
        default=None,
        description="Schedule basis for scheduled days",
        alias="indicative_person_dossier.indicative_deployment.schedule.scheduled_days[0].schedule_basis"
    )
    day_schedule_id: Optional[str] = Field(
        default=None,
        description="Day schedule ID",
        alias="indicative_person_dossier.indicative_deployment.schedule.day_schedule[0].id"
    )
    fte_ratio: Optional[str] = Field(
        default=None,
        description="Full-time equivalent ratio",
        alias="indicative_person_dossier.indicative_deployment.full_time_equivalent_ratio"
    )
    work_level_code: Optional[str] = Field(
        default="FullTime",
        description="FullTime/PartTime",
        alias="indicative_person_dossier.indicative_deployment.work_level_code"
    )

    # Organization fields removed - these belong in Employee model

    # Dates - employment lifecycle dates moved to Employee model
    valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Valid from date",
        alias="indicative_person_dossier.indicative_deployment.valid_from"
    )

    def to_nested_dict(self) -> Dict[str, Any]:
        """
        Convert to nested structure compatible with employee job fields.
        Rely on index-aware aliases.
        """
        data = self.model_dump(exclude_none=True, by_alias=True)

        # Clean up orphan schedule_basis fields when corresponding value fields are None
        # This prevents malformed ScheduledHours objects missing required attributes
        schedule_paths = [
            ('indicative_person_dossier.indicative_deployment.schedule.scheduled_hours[0].value',
             'indicative_person_dossier.indicative_deployment.schedule.scheduled_hours[0].schedule_basis'),
            ('indicative_person_dossier.indicative_deployment.schedule.scheduled_hours[1].value',
             'indicative_person_dossier.indicative_deployment.schedule.scheduled_hours[1].schedule_basis'),
            ('indicative_person_dossier.indicative_deployment.schedule.scheduled_days[0].value',
             'indicative_person_dossier.indicative_deployment.schedule.scheduled_days[0].schedule_basis'),
        ]
        for value_path, basis_path in schedule_paths:
            # If value is missing but basis exists, remove the basis to avoid malformed objects
            if value_path not in data and basis_path in data:
                del data[basis_path]

        return data
