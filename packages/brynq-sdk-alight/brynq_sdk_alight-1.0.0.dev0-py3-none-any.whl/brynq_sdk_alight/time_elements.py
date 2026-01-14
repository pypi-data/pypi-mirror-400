from typing import Any, Dict, List, Optional, Union

from .schemas.absence import Absence, Absences
from .schemas.payments import PayServEmpExtensionCreate


class TimeElements:
    """
    High-level Time Elements API. Sends Absences via PayServEmpExtension.

    Usage:
        alight = Alight()
        xml = alight.time_elements.create(absences=[...], person_id="35561", employee_id="35561ZZGB")
        xml = alight.time_elements.update(absences=[...], person_id="35561", employee_id="35561ZZGB")
    """

    def __init__(self, client: Any):
        self._client = client

    def _build_extension_with_time_elements(self, absences: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Transform raw absence dictionaries into the nested structure required by the Alight extension.

        Accepts either a single absence dict or a list; normalizes to the schema-backed
        `PayServEmpExtensionCreate` payload before handing off to XML generation.

        Example:
            >>> self._build_extension_with_time_elements(
            ...     {"absence_reason": "VAC", "valid_from": "2024-01-01", "units": "8"}
            ... )
        """
        # Normalize input to list of dicts
        if isinstance(absences, dict):
            normalized = [absences]
        else:
            normalized = absences
        # Let Pydantic accept native date types; XSD post-processing will wrap
        absence_models = [Absence(**dict(a)) for a in normalized]
        wrapper = Absences(absences=absence_models)
        extension_model = PayServEmpExtensionCreate(time_elements=wrapper)
        return extension_model.to_nested_dict()

    def create(
        self,
        *,
        absences: Union[Dict[str, Any], List[Dict[str, Any]]],
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Generate an ADD envelope that carries absence data through the extension channel.

        Useful when feeding single-day absences from a flat export—pass the dict directly and the helper
        will wrap it in the schema-specific containers.

        Example:
            >>> alight.time_elements.create(
            ...     absences={"absence_reason": "VAC", "valid_from": "2024-01-01", "units": "8"},
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        extension_data = self._build_extension_with_time_elements(absences)

        payload = {
            "person_id": person_id,
            "employee_id": employee_id,
        }

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
        *,
        absences: Union[Dict[str, Any], List[Dict[str, Any]]],
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Generate a CHANGE envelope for absence data using the same normalization pipeline as `create`.

        Downstream systems rely on the CHANGE action code to differentiate incremental corrections from
        brand-new entries.

        Example:
            >>> alight.time_elements.update(
            ...     absences=[
            ...         {"absence_reason": "VAC", "valid_from": "2024-01-01", "valid_to": "2024-01-02", "units": "16"}
            ...     ],
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        extension_data = self._build_extension_with_time_elements(absences)

        payload = {
            "person_id": person_id,
            "employee_id": employee_id,
        }

        return self._client.generate_employee_xml(
            employee=payload,
            action_code="CHANGE",
            logical_id=logical_id,
            extension_data=extension_data,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )
