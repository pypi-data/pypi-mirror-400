from typing import Any, Dict, List, Optional

from .schemas.payments import PayElementCreate
from .schemas.generated_envelope_xsd_schema.process_pay_serv_emp import (
    PayServEmpPayElements as XsdPayServEmpPayElements,
)


class PayElements:
    """
    High-level PayElements API. Builds PayServEmpPayElements from a list of PayElementCreate.

    Usage:
        alight = Alight()
        xml = alight.pay_elements.create(elements=[{...}], person_id="35561", employee_id="35561ZZGB")
        xml = alight.pay_elements.update(elements=[{...}], person_id="35561", employee_id="35561ZZGB")
    """

    def __init__(self, client: Any):
        self._client = client

    def _build_pay_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize incoming pay elements and validate them against the generated XSD model.

        Accepts plain dictionaries and returns the nested payload expected by `generate_employee_xml`.

        Example:
            >>> self._build_pay_elements([
            ...     {"element_code": "0010", "amount": 1200, "currency_code": "GBP"},
            ... ])
        """
        normalized: List[Dict[str, Any]] = []
        for item in elements:
            model = item if isinstance(item, PayElementCreate) else PayElementCreate(**item)
            normalized.append(model.to_nested_dict())
        payload = {"pay_element": normalized}
        XsdPayServEmpPayElements.model_validate(payload)
        return payload

    def create(
        self,
        *,
        elements: List[Dict[str, Any]],
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Generate an ADD envelope for pay elements using the minimal person identifiers.

        Example:
            >>> alight.pay_elements.create(
            ...     elements=[{"element_code": "0010", "amount": "1200", "currency_code": "GBP"}],
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        pay_elements_data = self._build_pay_elements(elements)

        return self._client.generate_employee_xml(
            employee={"person_id": person_id, "employee_id": employee_id},
            action_code="ADD",
            logical_id=logical_id,
            pay_elements_data=pay_elements_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )

    def update(
        self,
        *,
        elements: List[Dict[str, Any]],
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Generate a CHANGE envelope for existing pay elements while keeping identifiers flat.

        Mirrors `create` but reuses the CHANGE action code so downstream consumers can differ updates
        from new allocations without rebuilding envelopes manually.
        """
        pay_elements_data = self._build_pay_elements(elements)

        return self._client.generate_employee_xml(
            employee={"person_id": person_id, "employee_id": employee_id},
            action_code="CHANGE",
            logical_id=logical_id,
            pay_elements_data=pay_elements_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )
