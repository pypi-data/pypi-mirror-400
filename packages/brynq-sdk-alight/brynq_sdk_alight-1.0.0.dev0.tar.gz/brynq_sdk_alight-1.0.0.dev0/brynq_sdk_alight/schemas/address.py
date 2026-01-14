"""
Flat, user-friendly address model for Alight SDK.
"""

from typing import Optional, Dict, Any, List
from pydantic import Field, BaseModel

# Composition approach: plain Pydantic BaseModel; conversion handled by callers


class Address(BaseModel):
    """
    Simplified address model.
    Uses PURE schema-driven conversion - NO hardcoded structure mappings.
    Uses aliases to match expected field names in Employee model.
    """
    model_config = {
        "populate_by_name": True  # Allow populating by field name in addition to alias
    }

    line_1: str = Field(
        description="Street address line 1",
        alias="indicative_person_dossier.indicative_person.communication[2].address.line_one"
    )
    line_2: Optional[str] = Field(
        default=None,
        description="Street address line 2",
        alias="indicative_person_dossier.indicative_person.communication[2].address.line_two"
    )
    line_3: Optional[str] = Field(
        default=None,
        description="Street address line 3",
        alias="indicative_person_dossier.indicative_person.communication[2].address.line_three"
    )
    line_4: Optional[str] = Field(
        default=None,
        description="Street address line 4",
        alias="indicative_person_dossier.indicative_person.communication[2].address.line_four"
    )
    line_5: Optional[str] = Field(
        default=None,
        description="Street address line 5",
        alias="indicative_person_dossier.indicative_person.communication[2].address.line_five"
    )
    building_number: Optional[str] = Field(
        default=None,
        description="Building number",
        alias="indicative_person_dossier.indicative_person.communication[2].address.building_number"
    )
    building_name: Optional[str] = Field(
        default=None,
        description="Building name",
        alias="indicative_person_dossier.indicative_person.communication[2].address.building_name"
    )
    street_name: Optional[str] = Field(
        default=None,
        description="Street name",
        alias="indicative_person_dossier.indicative_person.communication[2].address.street_name"
    )
    unit: Optional[str] = Field(
        default=None,
        description="Unit or apartment identifier",
        alias="indicative_person_dossier.indicative_person.communication[2].address.unit"
    )
    floor: Optional[str] = Field(
        default=None,
        description="Floor number",
        alias="indicative_person_dossier.indicative_person.communication[2].address.floor"
    )
    post_office_box: Optional[str] = Field(
        default=None,
        description="P.O. Box",
        alias="indicative_person_dossier.indicative_person.communication[2].address.post_office_box"
    )
    city: str = Field(
        description="City name",
        alias="indicative_person_dossier.indicative_person.communication[2].address.city_name"
    )
    state_province: Optional[str] = Field(
        default=None,
        description="State/province",
        alias="indicative_person_dossier.indicative_person.communication[2].address.country_sub_division_code"
    )
    delivery_point_code: Optional[List[str]] = Field(
        default=None,
        description="Delivery point code(s)",
        alias="indicative_person_dossier.indicative_person.communication[2].address.delivery_point_code"
    )
    postal_code: str = Field(
        description="ZIP/postal code",
        alias="indicative_person_dossier.indicative_person.communication[2].address.postal_code"
    )
    country: str = Field(
        description="Country code (GB/US/etc.)",
        alias="indicative_person_dossier.indicative_person.communication[2].address.country_code"
    )
    city_sub_division_name: Optional[List[str]] = Field(
        default=None,
        description="Neighborhood or city subdivision name(s)",
        alias="indicative_person_dossier.indicative_person.communication[2].address.city_sub_division_name"
    )
    use_code: Optional[str] = Field(
        default=None,
        description="Address use context (HOME/WORK)",
        alias="indicative_person_dossier.indicative_person.communication[2].use_code"
    )

    def to_nested_dict(self) -> Dict[str, Any]:
        """
        Convert to nested structure compatible with employee address fields.
        """
        # Convert to dictionary with aliases - will directly map to employee fields
        return self.model_dump(exclude_none=True, by_alias=True)
