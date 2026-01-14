from typing import Any, Dict, Optional, Union
from xsdata.models.datatype import XmlDate

from .schemas import Salary as SalaryModel, EmployeeCreate as EmployeeModel


class Salary:
    """
    High-level Salary API (no manager layer).

    Usage:
        alight = Alight()
        xml = alight.salary.update(salary={...}, identifiers={"person_id": "35561", "employee_id": "35561ZZGB"})
    """

    def __init__(self, client: Any):
        self._client = client

    def update(
        self,
        salary: Union[SalaryModel, Dict[str, Any]],
        *,
        identifiers: Optional[Dict[str, Any]] = None,
        employee: Optional[Union[EmployeeModel, Dict[str, Any]]] = None,
        logical_id: Optional[str] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Create an Employee Change XML with salary change as PayElements.
        Returns XML string.

        Example:
            >>> alight.salary.update(
            ...     salary={"base_salary": 42000, "currency_code": "GBP"},
            ...     identifiers={"person_id": "35561", "employee_id": "35561ZZGB"},
            ... )

        Passing `salary` as a plain dict is enough—the helper wraps it in the generated `Salary` schema
        and derives the recurring pay element payload automatically.
        """
        # Build or augment an EmployeeModel with identifiers and salary
        if employee is None:
            if not identifiers or "person_id" not in identifiers:
                raise ValueError("identifiers must include at least 'person_id' when no employee is provided")
            base: Dict[str, Any] = {
                "person_id": identifiers.get("person_id"),
            }
            if identifiers.get("employee_id"):
                base["employee_id"] = identifiers.get("employee_id")
            employee_model = EmployeeModel(**base)
        else:
            employee_model = employee if isinstance(employee, EmployeeModel) else EmployeeModel(**employee)

        # Normalize salary model
        salary_model = salary if isinstance(salary, SalaryModel) else SalaryModel(**salary)

        # Convert salary to alias-based nested dict compatible with to_model mapping
        # Alight expects a default pay element code/type even if upstream sources omit them,
        # so fall back to the recurring base salary identifiers that match standard setup.
        pay_elements_data = {
            "pay_element": [
                {
                    "id": [{"value": salary_model.element_code or "0010"}],
                    "pay_element_type": {"value": salary_model.element_type or "RECURRING"},
                    "amount": {"value": f"{salary_model.base_salary:.2f}"},
                    "currency_code": {"value": salary_model.currency_code},
                    "valid_from": (
                        XmlDate.from_string(salary_model.valid_from.isoformat())
                        if salary_model.valid_from
                        else None
                    ),
                }
            ]
        }

        # Clean None values in pay element
        for k in list(pay_elements_data["pay_element"][0].keys()):
            if pay_elements_data["pay_element"][0][k] is None:
                del pay_elements_data["pay_element"][0][k]

        # Also mirror salary on the Employee flat fields so IndicativeData contains identifiers
        # Employee.to_model handles wrapping; pay elements go via pay_elements_data
        return self._client.generate_employee_xml(
            employee=employee_model,
            action_code="CHANGE",
            logical_id=logical_id,
            pay_elements_data=pay_elements_data,
            pretty_print=pretty_print,
        )
