from typing import Any, Dict, Optional


class Employee:
    """
    High-level Employee API (no manager layer).

    Usage:
        alight = Alight()
        xml = alight.employee.create({...})
        xml = alight.employee.update(EmployeeModel(...))
    """

    def __init__(self, client: Any):
        self._client = client

    def create(
        self,
        data: Dict[str, Any],
        *,
        logical_id: Optional[str] = None,
        extension_data: Optional[Dict[str, Any]] = None,
        pay_elements_data: Optional[Dict[str, Any]] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Create a New Hire XML document (actionCode=ADD).
        Returns XML string.

        Example:
            >>> alight.employee.create(
            ...     {
            ...         "person_id": "35561",
            ...         "employee_id": "35561ZZGB",
            ...         "given_name": "Alex",
            ...         "family_name": "Mason",
            ...     },
            ...     extension_data={"bank_accounts": [{"iban": "GB00BARC20201530093459"}]},
            ... )
        """
        return self._client.generate_employee_xml(
            employee=data,
            action_code="ADD",
            logical_id=logical_id,
            extension_data=extension_data,
            pay_elements_data=pay_elements_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )

    def update(
        self,
        data: Dict[str, Any],
        *,
        logical_id: Optional[str] = None,
        extension_data: Optional[Dict[str, Any]] = None,
        pay_elements_data: Optional[Dict[str, Any]] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Create an Employee Change XML document (actionCode=CHANGE).
        Returns XML string.

        Example:
            >>> alight.employee.update(
            ...     {"person_id": "35561", "employee_id": "35561ZZGB", "email": "alex@example.com"},
            ...     extension_data={"bank_accounts": [{"iban": "GB00BARC20201530093459"}]},
            ...     pay_elements_data={"pay_element": [{"id": [{"value": "0010"}], "amount": {"value": "45000"}}]},
            ... )
        """
        return self._client.generate_employee_xml(
            employee=data,
            action_code="CHANGE",
            logical_id=logical_id,
            extension_data=extension_data,
            pay_elements_data=pay_elements_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )
