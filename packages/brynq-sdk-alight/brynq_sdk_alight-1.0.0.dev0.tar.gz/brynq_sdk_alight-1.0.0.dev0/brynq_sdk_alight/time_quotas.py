from typing import Any, Dict, List, Optional, Union

from .schemas.timequota import TimeQuota, TimeQuotas
from .schemas.payments import PayServEmpExtensionCreate
from .schemas import EmployeeCreate as EmployeeModel


class TimeQuotas:
    """
    High-level Time Quotas API. Sends TimeQuotas via PayServEmpExtension.

    Usage:
        alight = Alight()
        xml = alight.time_quotas.create(time_quotas=[...], person_id="35561", employee_id="35561ZZGB")
        xml = alight.time_quotas.update(time_quotas=[...], person_id="35561", employee_id="35561ZZGB")
    """

    def __init__(self, client: Any):
        self._client = client

    def _build_extension_with_time_quotas(self, time_quotas: List[Union[TimeQuota, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Wrap raw time quota dictionaries into the schema-backed extension payload.

        Running through `TimeQuota` and `TimeQuotas` ensures aliases (like unit/identifier wrappers)
        are applied before the data touches the XSD validation layer.

        Example:
            >>> self._build_extension_with_time_quotas(
            ...     [{"quota_code": "VAC", "balance": "40", "valid_from": "2024-01-01"}]
            ... )
        """
        quota_models = [q if isinstance(q, TimeQuota) else TimeQuota(**q) for q in time_quotas]
        wrapper = TimeQuotas(time_quotas=quota_models)
        ext = PayServEmpExtensionCreate(time_quotas=wrapper)  # type: ignore[arg-type]
        return ext.to_nested_dict()

    def create(
        self,
        *,
        time_quotas: List[Union[TimeQuota, Dict[str, Any]]],
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Generate an ADD envelope that pushes quota balances through the extension block.

        Example:
            >>> alight.time_quotas.create(
            ...     time_quotas=[{"quota_code": "VAC", "balance": "40"}],
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )

        Passing quota dictionaries directly keeps the calling code small—the helper expands wrappers like
        `quota_code.value` and runs schema validation before serializing to XML.
        """
        extension_data = self._build_extension_with_time_quotas(time_quotas)

        employee_model = EmployeeModel(
            person_id=person_id,
            employee_id=employee_id,
        )

        return self._client.generate_employee_xml(
            employee=employee_model,
            action_code="ADD",
            logical_id=logical_id,
            extension_data=extension_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )

    def update(
        self,
        *,
        time_quotas: List[Union[TimeQuota, Dict[str, Any]]],
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Generate a CHANGE envelope for quota adjustments using the same normalization flow as `create`.

        Keeps the employee identifiers consistent with the flat dictionary interface while ensuring the
        extension payload remains schema-valid.

        Example:
            >>> alight.time_quotas.update(
            ...     time_quotas=[{"quota_code": "VAC", "balance": "32"}],
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        extension_data = self._build_extension_with_time_quotas(time_quotas)

        employee_model = EmployeeModel(
            person_id=person_id,
            employee_id=employee_id,
        )

        return self._client.generate_employee_xml(
            employee=employee_model,
            action_code="CHANGE",
            logical_id=logical_id,
            extension_data=extension_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )
