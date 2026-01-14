from typing import Optional, Dict, Any
import datetime
from pydantic import Field, BaseModel

from .utils import add_to_nested_path, post_process_nested_data, convert_datetime_to_xml, construct_model
from .absence import Absences
from .timequota import TimeQuotas
from ..schemas.generated_envelope_xsd_schema.process_pay_serv_emp import PayServEmpExtension as XsdPayServEmpExtension
from ..schemas.generated_envelope_xsd_schema.process_pay_serv_emp import PayServEmpPayElements as XsdPayServEmpPayElements


class PayServEmpExtensionCreate(BaseModel):
    """
    Alias-driven flat model for NGA PayServEmpExtension (index-aware paths, no custom logic).
    """
    model_config = {
        "populate_by_name": True
    }
    # Payment Instructions [0]
    payment_valid_from: Optional[datetime.date] = Field(default=None, alias="payment_instructions[0].valid_from")
    payment_type: Optional[str] = Field(default=None, alias="payment_instructions[0].payment_type")
    payment_method: Optional[str] = Field(default=None, alias="payment_instructions[0].payment_method")
    payment_type_code: Optional[str] = Field(default=None, alias="payment_instructions[0].payment_type_code")
    local_payment_method: Optional[str] = Field(default=None, alias="payment_instructions[0].local_payment_method")
    amount: Optional[list[str]] = Field(default=None, alias="payment_instructions[0].amount")
    currency_code: Optional[str] = Field(default=None, alias="payment_instructions[0].currency_code")
    payment_percentage: Optional[list[str]] = Field(default=None, alias="payment_instructions[0].payment_percentage")
    name_on_account: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.name_on_account")
    account_type_code: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.type_code[0]")
    bank_routing_id: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.bank_routing_id[0]")
    bank_routing_id_swift: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.bank_routing_id[1]")
    bank_routing_id_swift_scheme_name: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.bank_routing_id[1].scheme_name")
    account_id: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.account_id[0]")
    iban: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.iban")
    account_country_code: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.country_code[0]")
    account_currency_code: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.currency_code")
    additional_account_id: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.additional_account_id")
    account_postal_code: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.postal_code")
    account_city_name: Optional[str] = Field(default=None, alias="payment_instructions[0].direct_deposit_account.city_name")

    # Payment Instructions [1] (second instruction, e.g., OTHER)
    payment2_valid_from: Optional[datetime.date] = Field(default=None, alias="payment_instructions[1].valid_from")
    payment2_type: Optional[str] = Field(default=None, alias="payment_instructions[1].payment_type")
    payment2_method: Optional[str] = Field(default=None, alias="payment_instructions[1].payment_method")
    payment2_type_code: Optional[str] = Field(default=None, alias="payment_instructions[1].payment_type_code")
    payment2_amount: Optional[str] = Field(default=None, alias="payment_instructions[1].amount")
    name_on_account2: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.name_on_account")
    account_type_code_2: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.type_code[0]")
    bank_routing_id2: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.bank_routing_id[0]")
    bank_routing_id2_swift: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.bank_routing_id[1]")
    bank_routing_id2_swift_scheme_name: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.bank_routing_id[1].scheme_name")
    account_id2: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.account_id[0]")
    additional_account_id2: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.additional_account_id")
    iban2: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.iban")
    account_country_code2: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.country_code[0]")
    account_currency_code2: Optional[str] = Field(default=None, alias="payment_instructions[1].direct_deposit_account.currency_code")

    # Cost Assignment [0]
    cost_valid_from: Optional[datetime.date] = Field(default=None, alias="cost_assignment[0].valid_from")
    cost_center_code: Optional[str] = Field(default=None, alias="cost_assignment[0].cost_center_code")
    cost_center_name: Optional[str] = Field(default=None, alias="cost_assignment[0].cost_center_name")
    percentage: Optional[int] = Field(default=None, alias="cost_assignment[0].percentage")

    # Pay Scales (single)
    pay_scales_valid_from: Optional[datetime.date] = Field(default=None, alias="pay_scales.valid_from")
    pay_scale_type: Optional[str] = Field(default=None, alias="pay_scales.pay_scale_type")
    pay_scale_group: Optional[str] = Field(default=None, alias="pay_scales.pay_scale_group")
    pay_scale_level: Optional[str] = Field(default=None, alias="pay_scales.pay_scale_level")

    # Date Specifications (indices)
    date_active_status_type: Optional[str] = Field(default=None, alias="date_specifications.date[0].date_type")
    date_active_status: Optional[datetime.date] = Field(default=None, alias="date_specifications.date[0].value")
    date_hire_type: Optional[str] = Field(default=None, alias="date_specifications.date[1].date_type")
    date_hire: Optional[datetime.date] = Field(default=None, alias="date_specifications.date[1].value")
    date_continuous_service_type: Optional[str] = Field(default=None, alias="date_specifications.date[2].date_type")
    date_continuous_service: Optional[datetime.date] = Field(default=None, alias="date_specifications.date[2].value")
    date_seniority_type: Optional[str] = Field(default=None, alias="date_specifications.date[3].date_type")
    date_seniority: Optional[datetime.date] = Field(default=None, alias="date_specifications.date[3].value")
    date_benefits_service_type: Optional[str] = Field(default=None, alias="date_specifications.date[4].date_type")
    date_benefits_service: Optional[datetime.date] = Field(default=None, alias="date_specifications.date[4].value")
    date_company_service_type: Optional[str] = Field(default=None, alias="date_specifications.date[5].date_type")
    date_company_service: Optional[datetime.date] = Field(default=None, alias="date_specifications.date[5].value")
    date_first_day_type: Optional[str] = Field(default=None, alias="date_specifications.date[6].date_type")
    date_first_day_of_work: Optional[datetime.date] = Field(default=None, alias="date_specifications.date[6].value")

    # Approvers [0]
    approver_valid_from: Optional[datetime.date] = Field(default=None, alias="approvers.approver[0].valid_from")
    approver_value: Optional[str] = Field(default=None, alias="approvers.approver[0].value")
    approver_type: Optional[str] = Field(default=None, alias="approvers.approver[0].type_value")

    # Contract Elements [0]
    contract_valid_from: Optional[datetime.date] = Field(default=None, alias="contract_elements[0].valid_from")
    contract_type: Optional[str] = Field(default=None, alias="contract_elements[0].contract_type")
    contract_start_date: Optional[datetime.date] = Field(default=None, alias="contract_elements[0].contract_start_date")
    contract_end_date: Optional[datetime.date] = Field(default=None, alias="contract_elements[0].contract_end_date")

    # Payroll Specific Groupings (single object)
    psg_valid_from: Optional[datetime.date] = Field(default=None, alias="payroll_specific_groupings.valid_from")
    psg1: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping1")
    psg2: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping2")
    psg3: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping3")
    psg4: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping4")
    psg5: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping5")
    psg6: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping6")
    psg7: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping7")
    psg8: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping8")
    psg9: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping9")
    psg10: Optional[str] = Field(default=None, alias="payroll_specific_groupings.payroll_specific_grouping10")

    # Alternate Identifiers
    payroll_exchange_id: Optional[str] = Field(default=None, alias="alternate_identifiers.payroll_exchange_id")
    alternate_id: Optional[str] = Field(default=None, alias="alternate_identifiers.alternate_id[0]")
    alternate_id_type: Optional[str] = Field(default=None, alias="alternate_identifiers.alternate_id[0].type_value")
    pay_serv_id: Optional[str] = Field(default=None, alias="alternate_identifiers.pay_serv_id")
    prior_incorrect_pay_serv_id: Optional[str] = Field(default=None, alias="alternate_identifiers.prior_incorrect_pay_serv_id")

    # Alternate Descriptions
    alt_desc_valid_from: Optional[datetime.date] = Field(default=None, alias="alternate_descriptions.valid_from")
    alt_desc_1: Optional[str] = Field(default=None, alias="alternate_descriptions.description[0]")
    alt_desc_1_type: Optional[str] = Field(default=None, alias="alternate_descriptions.description[0].type_value")
    alt_desc_2: Optional[str] = Field(default=None, alias="alternate_descriptions.description[1]")
    alt_desc_2_type: Optional[str] = Field(default=None, alias="alternate_descriptions.description[1].type_value")
    alt_desc_3: Optional[str] = Field(default=None, alias="alternate_descriptions.description[2]")
    alt_desc_3_type: Optional[str] = Field(default=None, alias="alternate_descriptions.description[2].type_value")

    # Time Elements
    time_elements: Optional[Absences] = None
    time_quotas: Optional[TimeQuotas] = None

    def to_nested_dict(self) -> Dict[str, Any]:
        flat = self.model_dump(exclude_none=True, by_alias=True)
        nested: Dict[str, Any] = {}
        for k, v in flat.items():
            add_to_nested_path(nested, k, v)
        # Merge time elements
        if self.time_elements is not None:
            te = self.time_elements.to_nested_dict()
            if te:
                # Wrap into container
                nested.setdefault("pay_serv_emp_time_elements", {})
                nested["pay_serv_emp_time_elements"].update({"time_element": te.get("time_element", [])})
        # Merge time quotas
        if self.time_quotas is not None:
            tq = self.time_quotas.to_nested_dict()
            if tq:
                nested.setdefault("pay_serv_emp_time_quotas", {})
                nested["pay_serv_emp_time_quotas"].update({"time_quota": tq.get("time_quota", [])})
        post_process_nested_data(nested, XsdPayServEmpExtension)
        return nested

    def to_model(self) -> XsdPayServEmpExtension:
        nested = self.to_nested_dict()
        try:
            return construct_model(XsdPayServEmpExtension, nested)
        except Exception:
            return XsdPayServEmpExtension.model_validate(nested)


class PayElementCreate(BaseModel):
    """
    Alias-driven flat model for a single PayElement item.
    """
    model_config = {
        "populate_by_name": True
    }
    valid_from: Optional[datetime.date] = Field(default=None, alias="valid_from")
    id: Optional[str] = Field(default=None, alias="id[0].value")
    pay_element_type: Optional[str] = Field(default=None, alias="pay_element_type.value")
    amount: Optional[str] = Field(default=None, alias="amount.value")
    currency_code: Optional[str] = Field(default=None, alias="currency_code.value")
    rate: Optional[str] = Field(default=None, alias="rate.value")
    units: Optional[str] = Field(default=None, alias="units.value")
    unit_type: Optional[str] = Field(default=None, alias="unit_type.value")
    reference_number: Optional[str] = Field(default=None, alias="reference_number.value")
    cost_center_code: Optional[str] = Field(default=None, alias="cost_center_code.value")
    end_date: Optional[datetime.date] = Field(default=None, alias="end_date.value")
    premium_id: Optional[str] = Field(default=None, alias="premium_id.value")
    different_valuation: Optional[str] = Field(default=None, alias="different_valuation.value")
    off_cycle_indicator: Optional[bool] = Field(default=None, alias="off_cycle_indicator.value")

    def to_nested_dict(self) -> Dict[str, Any]:
        flat = self.model_dump(exclude_none=True, by_alias=True)
        nested: Dict[str, Any] = {}
        for k, v in flat.items():
            add_to_nested_path(nested, k, v)
        # Ensure required wrappers and types explicitly (schema nuances)
        # id must be a list of wrapper dicts
        if "id" in nested:
            if isinstance(nested["id"], list):
                nested["id"] = [item if isinstance(item, dict) and "value" in item else {"value": item} for item in nested["id"]]
            else:
                nested["id"] = [{"value": nested["id"]}]
        # Wrap simple fields (only those not already aliased as .value)
        for key in ("pay_element_type", "amount", "currency_code"):
            if key in nested and not (isinstance(nested[key], dict) and "value" in nested[key]):
                nested[key] = {"value": nested[key]}
        # Convert dates
        if "valid_from" in nested and isinstance(nested["valid_from"], (datetime.date, datetime.datetime)):
            nested["valid_from"] = convert_datetime_to_xml(nested["valid_from"], None)
        if "end_date" in nested and isinstance(nested["end_date"], dict) and "value" in nested["end_date"]:
            inner = nested["end_date"]["value"]
            if isinstance(inner, (datetime.date, datetime.datetime)):
                nested["end_date"]["value"] = convert_datetime_to_xml(inner, None)
        # Final pass through schema container to catch any remaining wrappers
        container = {"pay_element": [nested]}
        post_process_nested_data(container, XsdPayServEmpPayElements)
        return container["pay_element"][0]
