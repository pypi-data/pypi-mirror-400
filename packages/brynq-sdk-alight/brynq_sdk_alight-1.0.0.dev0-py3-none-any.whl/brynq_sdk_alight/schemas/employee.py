"""
Flat, user-friendly employee model for Alight SDK.
Automatically converts to complex nested HR-XML structure using schema introspection.
"""

import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import Field, model_validator, BaseModel

from .utils import add_to_nested_path, post_process_nested_data, construct_model
from .salary import Salary  # Import related models
from .address import Address
from .job import Job
from .leave import Leave
from .termination import Termination
from .generated_xsd_schemas.hrxml_indicative_data import IndicativeDataType


class EmployeeCreate(BaseModel):
    """
    Comprehensive employee model for Alight integration.
    Automatically converts to complex nested HR-XML structure using pure schema introspection.
    """
    model_config = {
        "populate_by_name": True  # Allow populating by field name in addition to alias
    }

    # Document Level Fields - Use aliases to map directly to XSD fields
    document_id: Optional[str] = Field(
        default=None,
        description="Document identifier",
        alias="document_id"
    )
    document_sequence: Optional[str] = Field(
        default=None,
        description="Document sequence number",
        alias="document_sequence"
    )
    alternate_document_id: Optional[List[str]] = Field(
        default=None,
        description="Alternate document identifier (list in XSD)",
        alias="alternate_document_id"
    )

    # Core Identity - Use aliases to map directly to XSD fields
    person_id: str = Field(
        description="Unique person identifier",
        alias="indicative_person_dossier.indicative_person.person_id"
    )
    person_legal_id: Optional[str] = Field(
        default=None,
        description="Legal ID (SSN/NI number)",
        alias="indicative_person_dossier.indicative_person.person_legal_id"
    )
    person_legal_id_scheme_name: Optional[str] = Field(
        default=None,
        description="Legal ID scheme (GB-NI/US-SSN)",
        alias="indicative_person_dossier.indicative_person.person_legal_id.scheme_name"
    )
    employee_id: Optional[str] = Field(
        default=None,
        description="Employee ID (defaults to person_id)",
        alias="indicative_person_dossier.indicative_employee.employee_id"
    )
    employee_group_code: Optional[str] = Field(
        default=None,
        description="Employee group classification",
        alias="indicative_person_dossier.indicative_employee.employee_group_code"
    )

    # Name Information - Use aliases to map directly to XSD fields
    given_name: Optional[str] = Field(
        default=None,
        description="First name",
        alias="indicative_person_dossier.indicative_person.person_name.given_name"
    )
    middle_name: Optional[str] = Field(
        default=None,
        description="Middle name",
        alias="indicative_person_dossier.indicative_person.person_name.middle_name"
    )
    preferred_name: Optional[str] = Field(
        default=None,
        description="Preferred or nick name",
        alias="indicative_person_dossier.indicative_person.person_name.preferred_name"
    )
    family_name: Optional[str] = Field(
        default=None,
        description="Last name/surname",
        alias="indicative_person_dossier.indicative_person.person_name.family_name"
    )
    former_family_name: Optional[str] = Field(
        default=None,
        description="Maiden name",
        alias="indicative_person_dossier.indicative_person.person_name.former_family_name"
    )
    preferred_salutation_code: Optional[str] = Field(
        default=None,
        description="Mr/Ms/Dr etc.",
        alias="indicative_person_dossier.indicative_person.person_name.preferred_salutation_code"
    )
    generation_affix_code: Optional[str] = Field(
        default=None,
        description="Generation suffix (Sr., Jr., III, etc.)",
        alias="indicative_person_dossier.indicative_person.person_name.generation_affix_code"
    )
    qualification_affix_code: Optional[str] = Field(
        default=None,
        description="Qualification code (e.g., MBA, PhD)",
        alias="indicative_person_dossier.indicative_person.person_name.qualification_affix_code"
    )
    title_affix_code: Optional[List[str]] = Field(
        default=None,
        description="Title affix codes (e.g., Lord, Sir)",
        alias="indicative_person_dossier.indicative_person.person_name.title_affix_code"
    )
    person_name_initials: Optional[str] = Field(
        default=None,
        description="Initials derived from person name",
        alias="indicative_person_dossier.indicative_person.person_name.person_name_initials"
    )
    formatted_name: Optional[str] = Field(
        default=None,
        description="Formatted display name",
        alias="indicative_person_dossier.indicative_person.person_name.formatted_name"
    )

    # Personal Details - Use aliases to map directly to XSD fields
    birth_date: Optional[datetime.date] = Field(
        default=None,
        description="Birth date",
        alias="indicative_person_dossier.indicative_person.birth_date"
    )
    gender_code: Optional[str] = Field(
        default=None,
        description="Male/Female/Other",
        alias="indicative_person_dossier.indicative_person.gender_code"
    )
    # Birth Place - nested under indicative_person.birth_place
    birth_place_city_name: Optional[str] = Field(
        default=None,
        description="City of birth",
        alias="indicative_person_dossier.indicative_person.birth_place.city_name"
    )
    birth_place_country_sub_division_code: Optional[str] = Field(
        default=None,
        description="State/region code of birth",
        alias="indicative_person_dossier.indicative_person.birth_place.country_sub_division_code"
    )
    birth_place_country_code: Optional[str] = Field(
        default=None,
        description="Country code of birth",
        alias="indicative_person_dossier.indicative_person.birth_place.country_code"
    )
    marital_status_code: Optional[str] = Field(
        default=None,
        description="Married/Unmarried/etc.",
        alias="indicative_person_dossier.indicative_person.certified_marital_status.marital_status_code"
    )
    marital_status_certified_date: Optional[datetime.date] = Field(
        default=None,
        description="Certified marital status date",
        alias="indicative_person_dossier.indicative_person.certified_marital_status.certified_date"
    )
    primary_language_code: Optional[str] = Field(
        default=None,
        description="Primary language code",
        alias="indicative_person_dossier.indicative_person.primary_language_code"
    )
    citizenship_country_code: Optional[str] = Field(
        default=None,
        description="Citizenship country code",
        alias="indicative_person_dossier.indicative_person.citizenship_country_code"
    )

    # Employment Status - Use aliases to map directly to XSD fields
    employed_indicator: Optional[bool] = Field(
        default=None,
        description="Employment status indicator",
        alias="indicative_person_dossier.indicative_employment.employed_indicator"
    )
    expected_duty_entry_date: Optional[datetime.date] = Field(
        default=None,
        description="Expected start date",
        alias="indicative_person_dossier.indicative_employment.proposed_hire.expected_duty_entry_date"
    )
    hire_type_code: Optional[str] = Field(
        default=None,
        description="NewHire/Rehire/Transfer",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.hire.hire_type_code"
    )
    hire_date: Optional[datetime.date] = Field(
        default=None,
        description="Hire date",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.hire.hire_date"
    )
    original_hire_date: Optional[datetime.date] = Field(
        default=None,
        description="Original hire date",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.hire.original_hire_date"
    )

    # Contact Information - Use index-aware aliases to map items into communication list
    mobile_phone: Optional[str] = Field(
        default=None,
        description="Mobile phone number",
        alias="indicative_person_dossier.indicative_person.communication[0].dial_number"
    )
    mobile_phone_use_code: Optional[str] = Field(
        default=None,
        description="Mobile phone use context",
        alias="indicative_person_dossier.indicative_person.communication[0].use_code"
    )
    mobile_phone_channel_code: Optional[str] = Field(
        default=None,
        description="Communication channel code for phone",
        alias="indicative_person_dossier.indicative_person.communication[0].channel_code"
    )
    country_dialing: Optional[str] = Field(
        default=None,
        description="Country dialing code for phone",
        alias="indicative_person_dossier.indicative_person.communication[0].country_dialing"
    )
    area_dialing: Optional[str] = Field(
        default=None,
        description="Area/region dialing code for phone",
        alias="indicative_person_dossier.indicative_person.communication[0].area_dialing"
    )
    dial_number: Optional[str] = Field(
        default=None,
        description="Dialable phone number",
        alias="indicative_person_dossier.indicative_person.communication[0].dial_number"
    )
    extension: Optional[str] = Field(
        default=None,
        description="Phone extension",
        alias="indicative_person_dossier.indicative_person.communication[0].extension"
    )
    access: Optional[str] = Field(
        default=None,
        description="Phone access code",
        alias="indicative_person_dossier.indicative_person.communication[0].access"
    )

    email: Optional[str] = Field(
        default=None,
        description="Email address",
        alias="indicative_person_dossier.indicative_person.communication[1].uri"
    )
    email_use_code: Optional[str] = Field(
        default=None,
        description="Email use context",
        alias="indicative_person_dossier.indicative_person.communication[1].use_code"
    )
    email_channel_code: Optional[str] = Field(
        default=None,
        description="Communication channel code for email",
        alias="indicative_person_dossier.indicative_person.communication[1].channel_code"
    )

    # Relation to Address model
    address: Optional[Address] = Field(default=None, description="Employee's home address")
    address_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Valid from date applied to primary home address",
        alias="indicative_person_dossier.indicative_person.communication[2].address.valid_from"
    )
    address_use_code: Optional[str] = Field(
        default=None,
        description="Address use context (HOME/WORK)",
        alias="indicative_person_dossier.indicative_person.communication[2].use_code"
    )
    address_type: Optional[str] = Field(
        default=None,
        description="Address type attribute",
        alias="indicative_person_dossier.indicative_person.communication[2].address.type_value"
    )
    # Flat person address fields (HOME address in communication[2])
    line_1: Optional[str] = Field(
        default=None,
        description="Primary address line",
        alias="indicative_person_dossier.indicative_person.communication[2].address.line_one"
    )
    city: Optional[str] = Field(
        default=None,
        description="City name",
        alias="indicative_person_dossier.indicative_person.communication[2].address.city_name"
    )
    state_province: Optional[str] = Field(
        default=None,
        description="State/Province code",
        alias="indicative_person_dossier.indicative_person.communication[2].address.country_sub_division_code"
    )
    postal_code: Optional[str] = Field(
        default=None,
        description="Postal code",
        alias="indicative_person_dossier.indicative_person.communication[2].address.postal_code"
    )
    country: Optional[str] = Field(
        default=None,
        description="Country code",
        alias="indicative_person_dossier.indicative_person.communication[2].address.country_code"
    )
    person_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for indicative person",
        alias="indicative_person_dossier.indicative_person.valid_from"
    )
    employee_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for indicative employee",
        alias="indicative_person_dossier.indicative_employee.valid_from"
    )
    employment_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for indicative employment",
        alias="indicative_person_dossier.indicative_employment.valid_from"
    )
    employment_lifecycle_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for employment lifecycle",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.valid_from"
    )
    hire_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for hire node",
        alias="indicative_person_dossier.indicative_employment.employment_lifecycle.hire.valid_from"
    )
    deployment_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for indicative deployment",
        alias="indicative_person_dossier.indicative_deployment.valid_from"
    )
    pay_cycle_remuneration_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for pay cycle remuneration",
        alias="indicative_person_dossier.pay_cycle_remuneration.valid_from"
    )

    # Employer/Organization Information - Use aliases to map directly to XSD fields
    employer_organization_id: Optional[str] = Field(
        default=None,
        description="Employer organization ID (flat input; coerced to XSD list)",
        alias="employer_identifiers.organization_id"
    )
    employer_organization_name: Optional[str] = Field(
        default=None,
        description="Employer organization name",
        alias="employer_identifiers.organization_name"
    )
    employer_organization_tax_id: Optional[List[str]] = Field(
        default=None,
        description="Employer organization tax ID (list in XSD)",
        alias="employer_identifiers.organization_tax_id"
    )
    employer_organization_legal_id: Optional[List[str]] = Field(
        default=None,
        description="Employer organization legal ID (list in XSD)",
        alias="employer_identifiers.organization_legal_id"
    )

    # Deployment Organization - Use aliases to map directly to XSD fields
    deployment_organization_id: Optional[str] = Field(
        default=None,
        description="Deployment organization ID",
        alias="indicative_person_dossier.indicative_deployment.deployment_organization.organization_identifiers.organization_id"
    )
    deployment_organization_name: Optional[str] = Field(
        default=None,
        description="Deployment organization name",
        alias="indicative_person_dossier.indicative_deployment.deployment_organization.organization_identifiers.organization_name"
    )
    deployment_organization_valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for deployment organization",
        alias="indicative_person_dossier.indicative_deployment.deployment_organization.valid_from"
    )

    # Work Location (flat) -> IndicativeDeployment.WorkLocation.Address
    work_location_city_name: Optional[str] = Field(
        default=None,
        description="Work location city",
        alias="indicative_person_dossier.indicative_deployment.work_location.address.city_name"
    )
    work_location_country_sub_division_code: Optional[str] = Field(
        default=None,
        description="Work location subdivision/state",
        alias="indicative_person_dossier.indicative_deployment.work_location.address.country_sub_division_code"
    )
    work_location_postal_code: Optional[str] = Field(
        default=None,
        description="Work location postal code",
        alias="indicative_person_dossier.indicative_deployment.work_location.address.postal_code"
    )

    # Legacy job fields (maintain backwards compatibility with flat payloads)
    title: Optional[str] = Field(
        default=None,
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
        description="Work location identifier",
        alias="indicative_person_dossier.indicative_deployment.work_location.location_id"
    )
    manager_id: Optional[str] = Field(
        default=None,
        description="Manager employee ID",
        alias="indicative_person_dossier.indicative_deployment.manager_id.id"
    )
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
        description="Work level code",
        alias="indicative_person_dossier.indicative_deployment.work_level_code"
    )

    # Work Location and Job Information fields removed - these belong in Job model
    # Access these through the job relation

    # Relation to Job model (replaces job fields)
    job: Optional[Job] = Field(default=None, description="Employee's job information")
    leave: Optional[Leave] = Field(default=None, description="Employee's leave information")
    termination: Optional[Termination] = Field(default=None, description="Employee's termination information")

    # Schedule Information and Work Level fields removed - these belong in Job model
    # Access these through the job relation

    # Pay Information - Use aliases to map directly to XSD fields
    pay_group_code: Optional[str] = Field(
        default=None,
        description="Pay group classification",
        alias="indicative_person_dossier.pay_cycle_remuneration.pay_group_code"
    )

    # Payment Instructions - Use aliases to map directly to XSD fields
    payment_type: Optional[str] = Field(
        default=None,
        description="Payment type (MAIN/etc.)",
        alias="payment_instruction.payment_type"
    )
    payment_method: Optional[str] = Field(
        default=None,
        description="Payment method (BANK_DOM/etc.)",
        alias="payment_instruction.payment_method"
    )
    account_type_code: Optional[str] = Field(
        default=None,
        description="Account type (DDA/etc.)",
        alias="payment_instruction.account_type_code"
    )
    name_on_account: Optional[str] = Field(
        default=None,
        description="Name on bank account",
        alias="payment_instruction.name_on_account"
    )
    bank_routing_id: Optional[str] = Field(
        default=None,
        description="Bank routing number",
        alias="payment_instruction.bank_routing_id"
    )
    account_id: Optional[str] = Field(
        default=None,
        description="Bank account number",
        alias="payment_instruction.account_id"
    )
    iban: Optional[str] = Field(
        default=None,
        description="IBAN",
        alias="payment_instruction.iban"
    )
    bank_country_code: Optional[str] = Field(
        default=None,
        description="Bank country code",
        alias="payment_instruction.bank_country_code"
    )

    # Relation to Salary model
    salary: Optional[Salary] = Field(default=None, description="Employee's salary information")

    # Legacy Pay Elements - Use aliases to map directly to XSD fields
    pay_element_id: Optional[str] = Field(
        default=None,
        description="Pay element ID",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.pay_element.id"
    )
    pay_element_type: Optional[str] = Field(
        default=None,
        description="Pay element type",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.pay_element.type_code"
    )
    pay_amount: Optional[str] = Field(
        default=None,
        description="Pay amount",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.amount.value"
    )
    pay_currency_code: Optional[str] = Field(
        default=None,
        description="Pay currency code",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.amount.currency_code"
    )

    # Common Dates - Use aliases to map to specific XSD fields
    valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Valid from date",
        # Map to specific fields in the XSD schema
        alias="indicative_person_dossier.valid_from"
    )

    # Additional fields - Use aliases to map directly to XSD fields
    compensation_change_reason: Optional[str] = Field(
        default=None,
        description="Reason for compensation change",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.compensation_change_reason"
    )
    effective_date: Optional[datetime.date] = Field(
        default=None,
        description="Effective date for changes",
        alias="indicative_person_dossier.indicative_deployment.effective_date"
    )

    def to_nested_dict(self) -> Dict[str, Any]:
        """
        Convert flat employee data to nested HR-XML structure using PURE schema-driven conversion.
        Uses alias dot-paths expanded to nested dict to align with XSD structure.
        """
        if IndicativeDataType is None:
            raise ImportError("IndicativeDataType not available - cannot perform schema-driven conversion")

        # Dump current model using aliases to get dot-path keys
        flat_alias: Dict[str, Any] = self.model_dump(
            exclude={"salary", "address", "job"}, exclude_none=True, by_alias=True
        )
        # print("[EMP] flat_alias keys:", list(flat_alias.keys())[:40])

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
            if value_path not in flat_alias and basis_path in flat_alias:
                del flat_alias[basis_path]

        # Minimal business logic
        if not flat_alias.get('indicative_person_dossier.indicative_employee.employee_id') and self.person_id:
            # Mirror employee_id default to person_id if missing
            flat_alias['indicative_person_dossier.indicative_employee.employee_id'] = self.person_id

        # Merge related models (they already dump with by_alias in their to_nested_dict)
        if self.salary is not None:
            for k, v in (self.salary.to_nested_dict() or {}).items():
                flat_alias[k] = v
        if self.address is not None:
            for k, v in (self.address.to_nested_dict() or {}).items():
                flat_alias[k] = v
        if self.job is not None:
            job_data = self.job.to_nested_dict() or {}
            for k, v in job_data.items():
                flat_alias[k] = v
        if self.leave is not None:
            for k, v in (self.leave.to_nested_dict() or {}).items():
                flat_alias[k] = v
        if self.termination is not None:
            for k, v in (self.termination.to_nested_dict() or {}).items():
                flat_alias[k] = v

        # No ad-hoc communication aggregation; indices in aliases will build lists
        # Delegate to generic converter (now dot-path aware)
        # Build nested structure from dot-path aliases generically
        nested: Dict[str, Any] = {}
        for k, v in flat_alias.items():
            add_to_nested_path(nested, k, v)

        post_process_nested_data(nested, IndicativeDataType)
        # print("[EMP] nested top-level keys:", list(nested.keys()))
        return nested

    def to_model(self) -> IndicativeDataType:
        """
        Convert flat employee data directly to validated IndicativeDataType model.
        Uses dot-separated aliases to map fields directly to the right places in the schema.

        Returns:
            IndicativeDataType: A validated model ready for XML serialization
        """
        # Get the nested structure with only non-empty fields
        nested_data = self.to_nested_dict()

        try:
            return construct_model(IndicativeDataType, nested_data)
        except Exception:
            # Fallback to full validation if fast-path construction fails
            return IndicativeDataType.model_validate(nested_data)
