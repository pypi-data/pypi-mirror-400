"""
Flat, user-friendly salary model for Alight SDK.
"""

import datetime
from typing import Optional, Dict, Any
from pydantic import Field, BaseModel

from .utils import add_to_nested_path  # not used directly; kept for parity if needed


class Salary(BaseModel):
    """
    Simplified salary/compensation model.
    Uses PURE schema-driven conversion - NO hardcoded structure mappings.
    Uses aliases to match expected field names in Employee model.
    """
    model_config = {
        "populate_by_name": True  # Allow populating by field name (base_salary) in addition to alias (pay_amount)
    }

    base_salary: float = Field(
        description="Base salary amount",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.amount.value"
    )
    currency_code: str = Field(
        default="USD",
        description="Currency code (USD/GBP/EUR)",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.amount.currency_code"
    )
    pay_frequency: Optional[str] = Field(
        default="Monthly",
        description="Monthly/Weekly/Hourly",
        alias="indicative_person_dossier.pay_cycle_remuneration.pay_cycle_interval_code"
    )

    # Pay Elements
    element_code: Optional[str] = Field(
        default="0010",
        description="Pay element code",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.pay_element.id"
    )
    element_type: Optional[str] = Field(
        default="RECURRING",
        description="RECURRING/BONUS/etc.",
        alias="indicative_person_dossier.pay_cycle_remuneration.remuneration.pay_element.type_code"
    )

    # Dates
    valid_from: Optional[datetime.date] = Field(
        default=None,
        description="Valid from date",
        alias="indicative_person_dossier.pay_cycle_remuneration.valid_from"
    )

    def to_nested_dict(self) -> Dict[str, Any]:
        """
        Convert salary data to format suitable for pay elements in the HR-XML.
        Using aliases for direct mapping to employee fields.
        """
        data = self.model_dump(exclude_none=True, by_alias=True)

        # Ensure amount is a string for XML compatibility
        if 'pay_amount' in data and isinstance(data['pay_amount'], (int, float)):
            data['pay_amount'] = str(data['pay_amount'])

        return data
