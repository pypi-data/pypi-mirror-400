from typing import Any, Dict, Optional

from .schemas import Address as AddressModel


class Address:
    """
    High-level Address API. Address changes are updates to IndicativeData.

    Usage:
        alight = Alight()
        xml = alight.address.update(
            data={...},
            person_id="35561",
            employee_id="35561ZZGB",
        )
    """

    def __init__(self, client: Any):
        self._client = client

    def update(
        self,
        data: Dict[str, Any],
        *,
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        employee_data: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Update address (actionCode=CHANGE). Returns XML string.
        Requires both person_id and employee_id per integration constraints.

        Example:
            >>> alight.address.update(
            ...     data={
            ...         "address_line_1": "10 Downing Street",
            ...         "town": "London",
            ...         "postal_code": "SW1A 2AA",
            ...         "address_valid_from": "2024-01-01",
            ...     },
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        payload: dict[str, Any] = {
            "person_id": person_id,
            "employee_id": employee_id,
        }

        # build from flat fields
        address_model = AddressModel(**data)
        payload["address"] = address_model.model_dump(exclude_none=True, by_alias=True)

        if "address_valid_from" in data:
            payload["address_valid_from"] = data["address_valid_from"]
        if "address_valid_to" in data:
            payload["address_valid_to"] = data["address_valid_to"]

        if employee_data:
            payload.update(employee_data)

        return self._client.generate_employee_xml(
            employee=payload,
            action_code="CHANGE",
            logical_id=logical_id,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )
