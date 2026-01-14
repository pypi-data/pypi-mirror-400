"""
Flat, user-friendly absence (time element) model for Alight SDK.
"""

import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field, BaseModel

from .utils import add_to_nested_path, convert_datetime_to_xml, post_process_nested_data


class Absence(BaseModel):
    """
    Simplified time element mapping to PayServEmpTimeElements.time_element[0].
    """
    model_config = {
        "populate_by_name": True
    }

    # Core identifiers and reason
    id: Optional[str] = Field(default=None, alias="time_element[0].id[0]")
    absence_reason: Optional[str] = Field(default=None, alias="time_element[0].absence_reason")

    # Quantities
    units: Optional[str] = Field(default=None, alias="time_element[0].units")
    unit_type: Optional[str] = Field(default=None, alias="time_element[0].unit_type")

    # Dates
    valid_from: Optional[datetime.date] = Field(default=None, alias="time_element[0].valid_from")
    valid_to: Optional[datetime.date] = Field(default=None, alias="time_element[0].valid_to")

    # Easy additional fields
    comments: Optional[str] = Field(default=None, alias="time_element[0].comments")
    absence_post: Optional[str] = Field(default=None, alias="time_element[0].absence_post")

    def to_nested_dict(self) -> Dict[str, Any]:
        flat = self.model_dump(exclude_none=True, by_alias=True)
        nested: Dict[str, Any] = {}
        for k, v in flat.items():
            add_to_nested_path(nested, k, v)
        # Convert dates to XML compatible
        for key in ("valid_from", "valid_to"):
            if key in nested and isinstance(nested[key], (datetime.date, datetime.datetime)):
                nested[key] = convert_datetime_to_xml(nested[key], None)
        return nested


class Absences(BaseModel):
    """
    Wrapper for multiple Absence items mapping to time_element[*].
    """
    absences: Optional[List[Absence]] = Field(default=None, description="List of absence time elements")

    def to_nested_dict(self) -> Dict[str, Any]:
        nested: Dict[str, Any] = {}
        if not self.absences:
            return nested
        # Merge each absence into time_element list
        time_elements: List[Dict[str, Any]] = []
        for idx, item in enumerate(self.absences):
            data = item.to_nested_dict()
            # Convert indexed paths from [0] to [idx]
            remapped: Dict[str, Any] = {}
            for k, v in data.items():
                remapped[k.replace("time_element[0]", f"time_element[{idx}]")] = v
            # Build nested for this item and then merge
            item_nested: Dict[str, Any] = {}
            for k, v in remapped.items():
                add_to_nested_path(item_nested, k, v)
            # Collect the single time_element dict
            if "time_element" in item_nested and isinstance(item_nested["time_element"], list):
                time_elements.extend(item_nested["time_element"])
        if time_elements:
            nested["time_element"] = time_elements
        # Post-process using the XSD model to wrap units and convert dates
        try:
            from ..schemas.generated_envelope_xsd_schema.process_pay_serv_emp import (
                PayServEmpTimeElements as XsdPayServEmpTimeElements,
            )
            post_process_nested_data(nested, XsdPayServEmpTimeElements)
        except Exception:
            pass
        return nested
