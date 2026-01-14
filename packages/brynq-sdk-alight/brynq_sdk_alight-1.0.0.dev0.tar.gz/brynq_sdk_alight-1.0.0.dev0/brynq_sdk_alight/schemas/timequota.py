"""
Flat, user-friendly time quota model for Alight SDK.
"""

import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field, BaseModel

from .utils import add_to_nested_path, convert_datetime_to_xml


class TimeQuota(BaseModel):
    """
    Maps to PayServEmpTimeQuotas.time_quota[0].
    """
    model_config = {"populate_by_name": True}

    id: Optional[str] = Field(default=None, alias="time_quota[0].id[0].value")
    units: Optional[str] = Field(default=None, alias="time_quota[0].units")
    units_taken: Optional[str] = Field(default=None, alias="time_quota[0].units_taken")
    units_remaining: Optional[str] = Field(default=None, alias="time_quota[0].units_remaining")
    unit_type: Optional[str] = Field(default=None, alias="time_quota[0].unit_type")
    accrued_to_date: Optional[str] = Field(default=None, alias="time_quota[0].accrued_to_date")
    deduction_start: Optional[datetime.date] = Field(default=None, alias="time_quota[0].deduction_start")
    deduction_end: Optional[datetime.date] = Field(default=None, alias="time_quota[0].deduction_end")
    valid_from: Optional[datetime.date] = Field(default=None, alias="time_quota[0].valid_from")
    valid_to: Optional[datetime.date] = Field(default=None, alias="time_quota[0].valid_to")

    def to_nested_dict(self) -> Dict[str, Any]:
        flat = self.model_dump(exclude_none=True, by_alias=True)
        nested: Dict[str, Any] = {}
        for k, v in flat.items():
            add_to_nested_path(nested, k, v)
        # Convert date/period values to XML-compatible
        for key in ("valid_from", "valid_to", "deduction_start", "deduction_end"):
            node = nested
            parts = key.split(".")
            if key in nested and isinstance(nested[key], (datetime.date, datetime.datetime)):
                nested[key] = convert_datetime_to_xml(nested[key], None)
        return nested


class TimeQuotas(BaseModel):
    """
    Wrapper for multiple TimeQuota items mapping to time_quota[*].
    """
    time_quotas: Optional[List[TimeQuota]] = Field(default=None, description="List of time quota items")

    def to_nested_dict(self) -> Dict[str, Any]:
        nested: Dict[str, Any] = {}
        if not self.time_quotas:
            return nested
        items: List[Dict[str, Any]] = []
        for idx, item in enumerate(self.time_quotas):
            data = item.to_nested_dict()
            remapped: Dict[str, Any] = {}
            for k, v in data.items():
                remapped[k.replace("time_quota[0]", f"time_quota[{idx}]")] = v
            item_nested: Dict[str, Any] = {}
            for k, v in remapped.items():
                add_to_nested_path(item_nested, k, v)
            if "time_quota" in item_nested and isinstance(item_nested["time_quota"], list):
                items.extend(item_nested["time_quota"])
        if items:
            nested["time_quota"] = items
        return nested
