from typing import Any, Dict, Optional

from .schemas import Termination as TerminationModel


class Termination:
    """
    High-level Termination API.

    Usage:
        alight = Alight()
        xml = alight.termination.create(data={...}, person_id="35561", employee_id="35561ZZGB")
        xml = alight.termination.update(data={...}, person_id="35561", employee_id="35561ZZGB")
    """

    def __init__(self, client: Any):
        self._client = client

    def create(
        self,
        data: Dict[str, Any],
        *,
        person_id: str,
        employee_id: str,
        extension_data: Optional[Dict[str, Any]] = None,
        employee_data: Optional[Dict[str, Any]] = None,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Create termination entry (actionCode=ADD). Returns XML string.
        Requires both person_id and employee_id.

        Example:
            >>> alight.termination.create(
            ...     data={"termination_reason": "RESIGNATION", "termination_date": "2024-06-30"},
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ...     extension_data={"last_day_worked": "2024-06-28"},
            ... )
        """
        termination_model = TerminationModel(**data)
        payload: Dict[str, Any] = {
            "person_id": person_id,
            "employee_id": employee_id,
            "termination": termination_model.model_dump(exclude_none=True, by_alias=True),
        }

        if employee_data:
            payload.update(employee_data)

        return self._client.generate_employee_xml(
            employee=payload,
            action_code="ADD",
            logical_id=logical_id,
            extension_data=extension_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )

    def update(
        self,
        data: Dict[str, Any],
        *,
        person_id: str,
        employee_id: str,
        extension_data: Optional[Dict[str, Any]] = None,
        employee_data: Optional[Dict[str, Any]] = None,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Update termination entry (actionCode=CHANGE). Returns XML string.
        Requires both person_id and employee_id.

        Example:
            >>> alight.termination.update(
            ...     data={"termination_reason": "DISMISSAL", "termination_date": "2024-07-15"},
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ...     employee_data={"last_day_worked": "2024-07-10"},
            ... )
        """
        termination_model = TerminationModel(**data)
        payload: Dict[str, Any] = {
            "person_id": person_id,
            "employee_id": employee_id,
            "termination": termination_model.model_dump(exclude_none=True, by_alias=True),
        }

        if employee_data:
            payload.update(employee_data)

        return self._client.generate_employee_xml(
            employee=payload,
            action_code="CHANGE",
            logical_id=logical_id,
            extension_data=extension_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )
