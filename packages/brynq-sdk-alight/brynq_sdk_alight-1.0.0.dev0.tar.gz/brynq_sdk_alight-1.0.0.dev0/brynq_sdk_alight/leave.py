from typing import Any, Dict, Optional

from .schemas import Leave as LeaveModel


class Leave:
    """
    High-level Leave API.

    Usage:
        alight = Alight()
        xml = alight.leave.create(data={...}, person_id="35561", employee_id="35561ZZGB")
        xml = alight.leave.update(data={...}, person_id="35561", employee_id="35561ZZGB")
    """

    def __init__(self, client: Any):
        self._client = client

    def create(
        self,
        data: Dict[str, Any],
        *,
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Create leave entry (actionCode=ADD). Returns XML string.
        Requires both person_id and employee_id.

        Example:
            >>> alight.leave.create(
            ...     data={
            ...         "leave_type": "PARENTAL",
            ...         "start_date": "2024-02-01",
            ...         "end_date": "2024-02-15",
            ...     },
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        leave_model = LeaveModel(**data)
        payload = {
            "person_id": person_id,
            "employee_id": employee_id,
            "leave": leave_model.model_dump(exclude_none=True, by_alias=True),
        }

        return self._client.generate_employee_xml(
            employee=payload,
            action_code="ADD",
            logical_id=logical_id,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )

    def update(
        self,
        data: Dict[str, Any],
        *,
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Update leave entry (actionCode=CHANGE). Returns XML string.
        Requires both person_id and employee_id.

        Example:
            >>> alight.leave.update(
            ...     data={"leave": {"leave_type": "SICK", "status": "Cancelled"}},
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        if 'leave' in data and data['leave'] is not None:
            nested = data['leave']
            leave_model = nested if isinstance(nested, LeaveModel) else LeaveModel(**nested)
        else:
            leave_model = LeaveModel(**data)
        payload = {
            "person_id": person_id,
            "employee_id": employee_id,
            "leave": leave_model.model_dump(exclude_none=True, by_alias=True),
        }

        return self._client.generate_employee_xml(
            employee=payload,
            action_code="CHANGE",
            logical_id=logical_id,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )
