from typing import Any, Dict, Optional, Mapping

from .schemas import Job as JobModel


class Job:
    """
    High-level Job/Deployment API.

    Usage:
        alight = Alight()
        xml = alight.job.create(data={...}, person_id="35561", employee_id="35561ZZGB")
        xml = alight.job.update(data={...}, person_id="35561", employee_id="35561ZZGB")
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
        Create job/deployment data (actionCode=ADD). Returns XML string.
        Requires both person_id and employee_id.

        Example:
            >>> alight.job.create(
            ...     data={"job_code": "FIN-MGR", "department": "Finance"},
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        job_model = JobModel(**data)
        payload = {
            "person_id": person_id,
            "employee_id": employee_id,
            "job": job_model.model_dump(exclude_none=True, by_alias=True),
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
        data: Mapping[str, Any],
        *,
        person_id: str,
        employee_id: str,
        logical_id: Optional[str] = None,
        envelope_options: Optional[dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Update job/deployment data (actionCode=CHANGE). Returns XML string.
        Requires both person_id and employee_id.

        Example:
            >>> alight.job.update(
            ...     data={"job": {"job_code": "FIN-DIR", "effective_date": "2024-04-01"}},
            ...     person_id="35561",
            ...     employee_id="35561ZZGB",
            ... )
        """
        job_model = JobModel(**dict(data))
        payload = {
            "person_id": person_id,
            "employee_id": employee_id,
            "job": job_model.model_dump(exclude_none=True, by_alias=True),
        }

        return self._client.generate_employee_xml(
            employee=payload,
            action_code="CHANGE",
            logical_id=logical_id,
            envelope_options=envelope_options,
            pretty_print=pretty_print,
        )
