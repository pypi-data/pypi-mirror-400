import base64
import re
import uuid
from datetime import datetime
from typing import Union, List, Optional, Literal, Dict, Any
from xml.dom import minidom
import pandas as pd
import requests
import os
from brynq_sdk_brynq import BrynQ
from .schemas.employee import EmployeeCreate
from .schemas.payments import PayServEmpExtensionCreate
from xsdata.models.datatype import XmlDate, XmlDateTime
from xsdata_pydantic.bindings import XmlSerializer as PydanticXmlSerializer
from .schemas.utils import construct_model

from .schemas.generated_xsd_schemas.hrxml_indicative_data import IndicativeDataType, IndicativeData
from .schemas.generated_envelope_xsd_schema.process_pay_serv_emp import (
    ProcessPayServEmp,
    DataArea,
    PayServEmp,
    PayServEmpExtension,
    PayServEmpPayElements,
    PayServEmpTimeElements,
    PayServEmpTimeQuotas,
)
from .schemas.generated_xsd_schemas.openapplications_bod import ApplicationArea, Sender
from .employee import Employee
from .salary import Salary


class Alight(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, sandbox: bool = False, debug: bool = False):
        super().__init__()
        self.timeout = 3600
        self.sandbox = sandbox
        self.data_interface_id = os.getenv("DATA_INTERFACE_ID")
        self.credentials = self.interfaces.credentials.get(system='alight', system_type=system_type)
        self.auth_url = "https://identity-qas.eu.hrx.alight.com/connect/token" if sandbox else "https://identity.eu.hrx.alight.com/connect/token"
        self.base_url = "https://apigateway.stradaglobal.com/extwebmethods"
        self.session = requests.Session()
        self.headers = self._get_request_headers()
        self.session.headers.update(self.headers)
        self.debug = debug
        self.gcc = self.credentials.get('data').get('gcc').upper()
        # Top-level API instances
        self._employee: Optional[Employee] = None
        self._salary: Optional[Salary] = None
        self._address: Optional["Address"] = None
        self._job: Optional["Job"] = None
        self._leave: Optional["Leave"] = None
        self._termination: Optional["Termination"] = None
        self._pay_elements: Optional["PayElements"] = None
        self._time_elements: Optional["TimeElements"] = None
        self._time_quotas: Optional["TimeQuotas"] = None

    def _get_request_headers(self):
        """
        Exchange the configured client credentials for an OAuth bearer token and build session headers.

        Called during initialization so the shared `requests.Session` carries the correct GCC, environment,
        subscription key, and freshly minted token before any outbound requests fire.
        """
        body = {
            'grant_type': 'client_credentials',
            'client_id': self.credentials.get('data').get('client_id'),
            'client_secret': self.credentials.get('data').get('client_secret')
        }
        resp = requests.post(self.auth_url, data=body)
        resp.raise_for_status()
        return {
            "gcc": self.credentials.get('data').get('gcc'),
            "env": "qas" if self.sandbox else "prod",
            'Authorization': f"Bearer {resp.json()['access_token']}",
            "Ocp-Apim-Subscription-Key": self.credentials.get('data').get('subscription_key')
        }

    @property
    def employee(self) -> Employee:
        """Access employee operations (create/update)."""
        if self._employee is None:
            self._employee = Employee(self)
        return self._employee

    @property
    def salary(self) -> Salary:
        """Access salary operations (update)."""
        if self._salary is None:
            self._salary = Salary(self)
        return self._salary

    @property
    def address(self) -> "Address":
        """Access address operations (update)."""
        if self._address is None:
            from .address import Address
            self._address = Address(self)
        return self._address

    @property
    def job(self) -> "Job":
        """Access job operations (create/update)."""
        if self._job is None:
            from .job import Job
            self._job = Job(self)
        return self._job

    @property
    def leave(self) -> "Leave":
        """Access leave operations (create/update)."""
        if self._leave is None:
            from .leave import Leave
            self._leave = Leave(self)
        return self._leave

    @property
    def termination(self) -> "Termination":
        """Access termination operations (create/update)."""
        if self._termination is None:
            from .termination import Termination
            self._termination = Termination(self)
        return self._termination

    @property
    def pay_elements(self) -> "PayElements":
        """Access pay elements operations (create/update)."""
        if self._pay_elements is None:
            from .pay_elements import PayElements
            self._pay_elements = PayElements(self)
        return self._pay_elements

    @property
    def time_elements(self) -> "TimeElements":
        """Access time elements operations via extension (create/update)."""
        if self._time_elements is None:
            from .time_elements import TimeElements
            self._time_elements = TimeElements(self)
        return self._time_elements

    @property
    def time_quotas(self) -> "TimeQuotas":
        """Access time quotas operations via extension (create/update)."""
        if self._time_quotas is None:
            from .time_quotas import TimeQuotas
            self._time_quotas = TimeQuotas(self)
        return self._time_quotas

    def create_hrxml_from_data(self, person_data: Dict[str, Any]) -> IndicativeDataType:
        """
        Create HR-XML IndicativeDataType from person data dictionary.

        Args:
            person_data: Dictionary containing person, employee, employment, deployment, and remuneration data

        Returns:
            IndicativeDataType: Validated XSData model instance

        Example:
            >>> alight.create_hrxml_from_data(
            ...     {
            ...         "indicative_person_dossier": {
            ...             "indicative_person": [
            ...                 {
            ...                     "person_id": [{"value": "35561"}],
            ...                     "person_name": [{"given_name": [{"value": "Alex"}]}],
            ...                 }
            ...             ]
            ...         }
            ...     }
            ... )
        """
        try:
            return construct_model(IndicativeDataType, person_data)
        except Exception as e:
            try:
                indicative_data = IndicativeDataType.model_validate(person_data)
                return indicative_data
            except Exception as e2:
                raise ValueError(f"Failed to create HR-XML from data: {e2}")

    def create_extension_from_data(self, extension_data: Dict[str, Any]) -> PayServEmpExtension:
        """
        Create PayServEmpExtension from extension data dictionary.

        Args:
            extension_data: Dictionary containing payment instructions, cost assignments, etc.

        Returns:
            PayServEmpExtension: Validated XSData model instance

        Example:
            >>> alight.create_extension_from_data(
            ...     {"bank_accounts": {"bank_account": [{"iban": {"value": "GB00BARC20201530093459"}}]}}
            ... )
        """
        try:
            # Always route through flat builder to ensure schema-driven wrappers
            if isinstance(extension_data, PayServEmpExtensionCreate):
                model = extension_data
            else:
                model = PayServEmpExtensionCreate(**dict(extension_data))
            nested = model.to_nested_dict()
            # Final generic normalization: coerce lists/wrappers/XML dates to XSD expectations
            try:
                from .schemas.utils import post_process_nested_data
                from .schemas.generated_envelope_xsd_schema.process_pay_serv_emp import PayServEmpExtension as XsdPayServEmpExtension
                post_process_nested_data(nested, XsdPayServEmpExtension)
            except Exception:
                pass
            # Defensive fix: ensure approver date attributes are XmlDate/XmlDateTime instances
            try:
                from xsdata.models.datatype import XmlDate, XmlDateTime
                import datetime as _dt
                appr = nested.get("approvers")
                if isinstance(appr, dict):
                    approver_items = appr.get("approver")
                    if isinstance(approver_items, list):
                        for item in approver_items:
                            if isinstance(item, dict):
                                v_from = item.get("valid_from")
                                if isinstance(v_from, _dt.datetime):
                                    item["valid_from"] = XmlDateTime(
                                        v_from.year, v_from.month, v_from.day, v_from.hour, v_from.minute, v_from.second, v_from.microsecond // 1000
                                    )
                                elif isinstance(v_from, _dt.date):
                                    item["valid_from"] = XmlDate(v_from.year, v_from.month, v_from.day)
                                v_to = item.get("valid_to")
                                if isinstance(v_to, _dt.datetime):
                                    item["valid_to"] = XmlDateTime(
                                        v_to.year, v_to.month, v_to.day, v_to.hour, v_to.minute, v_to.second, v_to.microsecond // 1000
                                    )
                                elif isinstance(v_to, _dt.date):
                                    item["valid_to"] = XmlDate(v_to.year, v_to.month, v_to.day)
            except Exception:
                pass
            try:
                return construct_model(PayServEmpExtension, nested)
            except Exception:
                return PayServEmpExtension.model_validate(nested)
        except Exception as e:
            raise ValueError(f"Failed to create extension from data: {e}")

    def create_pay_elements_from_data(self, pay_elements_data: Dict[str, Any]) -> PayServEmpPayElements:
        """
        Create PayServEmpPayElements from pay elements data dictionary.

        Args:
            pay_elements_data: Dictionary containing pay elements

        Returns:
            PayServEmpPayElements: Validated XSData model instance

        Example:
            >>> alight.create_pay_elements_from_data(
            ...     {
            ...         "pay_element": [
            ...             {"id": [{"value": "0010"}], "amount": {"value": "1200"}, "currency_code": {"value": "GBP"}}
            ...         ]
            ...     }
            ... )
        """
        try:
            # Coerce flat/simple values into XSD wrapper structures and XML dates
            from xsdata.models.datatype import XmlDate

            def coerce_wrapper(value: Any) -> Dict[str, Any]:
                if isinstance(value, dict) and "value" in value:
                    return value
                return {"value": value}

            def coerce_date(value: Any) -> Any:
                if isinstance(value, datetime):
                    return XmlDate.from_datetime(value)  # type: ignore
                if hasattr(value, "toordinal"):
                    return XmlDate.from_date(value)  # type: ignore
                return value

            normalized: Dict[str, Any] = dict(pay_elements_data or {})
            items = list((normalized.get("pay_element") or []))
            coerced_items: list[Dict[str, Any]] = []
            for item in items:
                if not isinstance(item, dict):
                    coerced_items.append(item)
                    continue
                tmp = dict(item)
                # Dates
                if "valid_from" in tmp:
                    tmp["valid_from"] = coerce_date(tmp["valid_from"])
                if "end_date" in tmp:
                    # end_date is a wrapper in XSD
                    end_val = tmp["end_date"]
                    if isinstance(end_val, dict) and "value" in end_val:
                        end_val["value"] = coerce_date(end_val["value"])
                        tmp["end_date"] = end_val
                    else:
                        tmp["end_date"] = {"value": coerce_date(end_val)}

                # id must be a list of wrapper dicts
                if "id" in tmp:
                    id_val = tmp["id"]
                    if isinstance(id_val, list):
                        new_list = []
                        for iv in id_val:
                            if isinstance(iv, dict) and "value" in iv:
                                new_list.append(iv)
                            else:
                                new_list.append({"value": iv})
                        tmp["id"] = new_list
                    else:
                        if isinstance(id_val, dict) and "value" in id_val:
                            tmp["id"] = [id_val]
                        else:
                            tmp["id"] = [{"value": id_val}]

                # Simple wrappers
                for key in (
                    "pay_element_type",
                    "amount",
                    "currency_code",
                    "rate",
                    "units",
                    "unit_type",
                    "reference_number",
                    "cost_center_code",
                    "premium_id",
                ):
                    if key in tmp and not (isinstance(tmp[key], dict) and "value" in tmp[key]):
                        tmp[key] = coerce_wrapper(tmp[key])

                coerced_items.append(tmp)

            normalized["pay_element"] = coerced_items

            try:
                return construct_model(PayServEmpPayElements, normalized)
            except Exception:
                return PayServEmpPayElements.model_validate(normalized)
        except Exception as e:
            raise ValueError(f"Failed to create pay elements from data: {e}")

    def create_complete_alight_envelope(
        self,
        indicative_data: IndicativeDataType,
        extension: Optional[PayServEmpExtension] = None,
        pay_elements: Optional[PayServEmpPayElements] = None,
        time_elements: Optional[PayServEmpTimeElements] = None,
        time_quotas: Optional[PayServEmpTimeQuotas] = None,
        action_code: str = "ADD",
        logical_id: str = "TST-GB003-1001",
        language_code: str = "en-US",
        system_environment_code: str = "TST NF",
        release_id: str = "DEFAULT",
        *,
        creation_datetime: Optional[datetime] = None,
        bod_id: Optional[str] = None,
        application_sender_component_id: str = "PAYROLL",
        application_sender_reference_id: str = "hrisxml",
        application_sender_confirmation_code: str = "Always",
        application_bodid: Optional[str] = None,
        application_language_code: Optional[str] = None,
        application_system_environment_code: Optional[str] = None,
        application_release_id: Optional[str] = None,
        data_area_language_code: Optional[str] = None,
        data_area_system_environment_code: Optional[str] = None,
        data_area_release_id: Optional[str] = None,
        exclude_bod_fields: bool = False,
    ) -> ProcessPayServEmp:
        """
        Create the complete Alight XML envelope using XSData models.

        Args:
            indicative_data: The HR-XML indicative data
            extension: Optional Alight-specific extensions
            pay_elements: Optional pay elements
            action_code: Action code for the process (default: "ADD")
            logical_id: Logical ID for the sender (default: "TST-GB003-1001")
            language_code: Language code (default: "en-US")
            system_environment_code: System environment (default: "TST NF")
            release_id: Release ID (default: "DEFAULT")

        Returns:
            ProcessPayServEmp: Complete envelope ready for serialization

        Example:
            >>> envelope = alight.create_complete_alight_envelope(
            ...     indicative_data=alight.create_hrxml_from_data({...}),
            ...     pay_elements=alight.create_pay_elements_from_data({"pay_element": [{"id": [{"value": "0010"}]}]}),
            ...     action_code="CHANGE",
            ... )
        """
        # Create timestamp and BODID
        timestamp = creation_datetime or datetime.now()
        bod_id_value = (bod_id or str(uuid.uuid4())).upper()
        app_bodid_value = (application_bodid or bod_id_value).upper()

        try:
            # Create Sender
            sender_data = {
                "logical_id": {"value": logical_id},
                "component_id": {"value": application_sender_component_id},
                "reference_id": {"value": application_sender_reference_id},
                "confirmation_code": {"value": application_sender_confirmation_code}
            }
            try:
                sender = construct_model(Sender, sender_data)
            except Exception:
                sender = Sender.model_validate(sender_data)

            # Create ApplicationArea
            app_area_data = {
                "sender": sender,
            }
            # BOD REMOVAL: Always include creation_date_time and bodid for model validation (required fields)
            # We'll remove them from XML output later if exclude_bod_fields is True
            app_area_data["creation_date_time"] = {"value": XmlDateTime.from_datetime(timestamp)}
            # BOD REMOVAL: Only include bodid if not excluding BOD fields
            if not exclude_bod_fields:
                app_area_data["bodid"] = {"value": app_bodid_value}
            if application_language_code:
                app_area_data["language_code"] = application_language_code
            if application_system_environment_code:
                app_area_data["system_environment_code"] = application_system_environment_code
            if application_release_id:
                app_area_data["release_id"] = application_release_id

            try:
                application_area = construct_model(ApplicationArea, app_area_data)
            except Exception:
                application_area = ApplicationArea.model_validate(app_area_data)

            # Create PayServEmp (contains our IndicativeData + Extensions)
            # Need to create IndicativeData wrapper (not IndicativeDataType)
            # Copy all relevant fields from indicative_data to preserve employer_identifiers etc.
            indicative_data_wrapper = IndicativeData(
                document_id=indicative_data.document_id,
                document_sequence=indicative_data.document_sequence,
                alternate_document_id=indicative_data.alternate_document_id,
                employer_identifiers=indicative_data.employer_identifiers,
                indicative_person_dossier=indicative_data.indicative_person_dossier,
                user_area=indicative_data.user_area,
                language_code=indicative_data.language_code,
                valid_from=indicative_data.valid_from,
                valid_to=indicative_data.valid_to
            )

            pay_serv_emp_data = {
                "indicative_data": indicative_data_wrapper
            }

            # Add optional components if provided
            if extension:
                pay_serv_emp_data["pay_serv_emp_extension"] = extension
            if pay_elements:
                pay_serv_emp_data["pay_serv_emp_pay_elements"] = pay_elements
            if time_elements:
                pay_serv_emp_data["pay_serv_emp_time_elements"] = time_elements
            if time_quotas:
                pay_serv_emp_data["pay_serv_emp_time_quotas"] = time_quotas

            try:
                pay_serv_emp = construct_model(PayServEmp, pay_serv_emp_data)
            except Exception:
                pay_serv_emp = PayServEmp.model_validate(pay_serv_emp_data)

            # Create Process with ActionExpression
            process_data = {
                "action_criteria": [{
                    "action_expression": [{
                        "action_code": action_code
                    }]
                }]
            }

            # Create DataArea
            data_area_data = {
                "process": process_data,
                "pay_serv_emp": [pay_serv_emp]
            }
            try:
                data_area = construct_model(DataArea, data_area_data)
            except Exception:
                data_area = DataArea.model_validate(data_area_data)

            # Create the complete ProcessPayServEmp envelope
            envelope_data = {
                "application_area": application_area,
                "data_area": data_area,
                "language_code": language_code,
                "system_environment_code": system_environment_code,
                "release_id": release_id
            }
            if data_area_language_code:
                envelope_data["language_code"] = data_area_language_code
            if data_area_system_environment_code:
                envelope_data["system_environment_code"] = data_area_system_environment_code
            if data_area_release_id:
                envelope_data["release_id"] = data_area_release_id

            try:
                complete_envelope = construct_model(ProcessPayServEmp, envelope_data)
            except Exception:
                complete_envelope = ProcessPayServEmp.model_validate(envelope_data)
            return complete_envelope

        except Exception as e:
            raise ValueError(f"Failed to create complete Alight envelope: {e}")

    def serialize_with_namespaces(
        self,
        envelope: ProcessPayServEmp,
        pretty_print: bool = True,
        custom_namespaces: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Serialize ProcessPayServEmp envelope to XML with proper namespace handling.

        Args:
            envelope: The ProcessPayServEmp envelope to serialize
            pretty_print: Whether to format the XML with indentation (default: True)
            custom_namespaces: Custom namespace mappings (prefix -> namespace URI)

        Returns:
            str: Serialized XML string

        Example:
            >>> xml = alight.serialize_with_namespaces(envelope, custom_namespaces={"cust": "http://example.com"})
        """
        # Default namespace mappings for Alight standard prefixes
        namespace_map = custom_namespaces or {
            "nga": "http://www.ngahr.com/ngapexxml/1",
            "oa": "http://www.openapplications.org/oagis/9",
            "hr": "http://www.hr-xml.org/3"
        }

        try:
            # Use ns_map parameter for clean namespace mapping
            pydantic_serializer = PydanticXmlSerializer()
            raw_xml = pydantic_serializer.render(envelope, ns_map=namespace_map)

            # BOD REMOVAL: Remove BOD fields from XML if exclude_bod_fields was set (for new hires)
            # Check if we should exclude by looking at the envelope's application_area
            # When exclude_bod_fields is True, bodid is not set, so it will be None
            if envelope.application_area and envelope.application_area.bodid is None:
                # Remove CreationDateTime and BODID elements from XML for new hires
                # Handle both single-line and multi-line XML formatting
                raw_xml = re.sub(r'<oa:CreationDateTime>.*?</oa:CreationDateTime>\s*', '', raw_xml, flags=re.DOTALL)
                raw_xml = re.sub(r'<oa:BODID>.*?</oa:BODID>\s*', '', raw_xml, flags=re.DOTALL)
                # Also handle self-closing tags if they exist
                raw_xml = re.sub(r'<oa:CreationDateTime\s*/>\s*', '', raw_xml)
                raw_xml = re.sub(r'<oa:BODID\s*/>\s*', '', raw_xml)

            if pretty_print:
                # Pretty print the XML
                dom = minidom.parseString(raw_xml)
                pretty_xml = dom.toprettyxml(indent="  ", encoding=None)

                # Clean up extra blank lines
                lines = [line for line in pretty_xml.split('\n') if line.strip()]
                return '\n'.join(lines)
            else:
                return raw_xml

        except Exception as e:
            # Fallback without ns_map if it fails
            try:
                pydantic_serializer = PydanticXmlSerializer()
                raw_xml = pydantic_serializer.render(envelope)

                if pretty_print:
                    dom = minidom.parseString(raw_xml)
                    pretty_xml = dom.toprettyxml(indent="  ", encoding=None)
                    lines = [line for line in pretty_xml.split('\n') if line.strip()]
                    return '\n'.join(lines)
                else:
                    return raw_xml

            except Exception as e2:
                raise ValueError(f"Failed to serialize envelope: {e2}")

    def generate_complete_hrxml(
        self,
        indicative_data: Dict[str, Any],
        extension_data: Optional[Dict[str, Any]] = None,
        pay_elements_data: Optional[Dict[str, Any]] = None,
        action_code: str = "ADD",
        logical_id: str = "TST-GB003-1001",
        pretty_print: bool = True
    ) -> str:
        """
        High-level function to generate complete Alight HR-XML from data dictionaries.

        Args:
            person_data: Dictionary containing person/employee/employment data
            extension_data: Optional dictionary containing Alight extensions
            pay_elements_data: Optional dictionary containing pay elements
            action_code: Action code for the process (default: "ADD")
            logical_id: Logical ID for the sender (default: "TST-GB003-1001")
            pretty_print: Whether to format the XML with indentation (default: True)

        Returns:
            str: Complete Alight HR-XML string

        Example:
            >>> xml = alight.generate_complete_hrxml(
            ...     indicative_data=alight.create_hrxml_from_data({...}).model_dump(by_alias=True),
            ...     extension_data={"bank_accounts": {"bank_account": [{"iban": {"value": "GB00..."}}]}},
            ...     pay_elements_data={"pay_element": [{"id": [{"value": "0010"}], "amount": {"value": "1200"}}]},
            ...     action_code="CHANGE",
            ... )
        """
        try:
            # Create optional components
            extension = None
            pay_elements = None

            if extension_data:
                extension = self.create_extension_from_data(extension_data)

            if pay_elements_data:
                pay_elements = self.create_pay_elements_from_data(pay_elements_data)

            # Create complete envelope
            envelope = self.create_complete_alight_envelope(
                indicative_data=indicative_data,
                extension=extension,
                pay_elements=pay_elements,
                action_code=action_code,
                logical_id=logical_id
            )

            # Serialize to XML
            xml_string = self.serialize_with_namespaces(envelope, pretty_print=pretty_print)

            return xml_string

        except Exception as e:
            raise ValueError(f"Failed to generate complete HR-XML: {e}")

    def generate_newhire_xml(
        self,
        indicative_data: Dict[str, Any],
        extension_data: Optional[Dict[str, Any]] = None,
        pay_elements_data: Optional[Dict[str, Any]] = None,
        logical_id: Optional[str] = None,
        pretty_print: bool = True
    ) -> str:
        """
        Generate a complete NewHire HR-XML document for Alight integration.

        Args:
            person_data: Dictionary containing person, employee, employment, deployment, and remuneration data
            extension_data: Optional dictionary containing Alight-specific extensions (payment instructions, etc.)
            pay_elements_data: Optional dictionary containing pay elements
            logical_id: Optional logical ID for the sender (should be: GCC-LCC-generated ID where GCC is the client identifier and LCC is a legal entity identifier)
            pretty_print: Whether to format the XML with indentation (default: True)

        Returns:
            str: Complete Alight HR-XML string ready for transmission

        Example:
            >>> alight = Alight()
            >>> person_data = {
            ...     "indicative_person_dossier": {
            ...         "indicative_person": [{
            ...             "person_id": [{"value": "12345"}],
            ...             "person_name": [{"given_name": [{"value": "John"}], "family_name": [{"value": "Doe"}]}]
            ...         }]
            ...     }
            ... }
            >>> xml = alight.generate_newhire_xml(person_data)
        """
        if self.debug:
            print(f"🔄 Generating NewHire XML for logical_id: {logical_id}")

        try:
            xml_string = self.generate_complete_hrxml(
                indicative_data=indicative_data,
                extension_data=extension_data,
                pay_elements_data=pay_elements_data,
                action_code="ADD",
                logical_id=logical_id,
                pretty_print=pretty_print
            )

            if self.debug:
                print("✅ Successfully generated NewHire XML")

            return xml_string

        except Exception as e:
            if self.debug:
                print(f"❌ Failed to generate NewHire XML: {e}")
            raise ValueError(f"Failed to generate NewHire XML: {e}")

    def generate_employee_change_xml(
        self,
        indicative_data: Dict[str, Any],
        extension_data: Optional[Dict[str, Any]] = None,
        pay_elements_data: Optional[Dict[str, Any]] = None,
        logical_id: Optional[str] = None,
        pretty_print: bool = True
    ) -> str:
        """
        Generate a complete Employee Change HR-XML document for Alight integration.

        Args:
            person_data: Dictionary containing person, employee, employment, deployment, and remuneration data
            extension_data: Optional dictionary containing Alight-specific extensions
            pay_elements_data: Optional dictionary containing pay elements
            logical_id: Optional logical ID for the sender (defaults to TST-GB003-1001)
            pretty_print: Whether to format the XML with indentation (default: True)

        Returns:
            str: Complete Alight HR-XML string ready for transmission

        Example:
            >>> xml = alight.generate_employee_change_xml(
            ...     indicative_data=alight.create_hrxml_from_data({...}).model_dump(by_alias=True),
            ...     pay_elements_data={"pay_element": [{"id": [{"value": "0010"}], "amount": {"value": "45000"}}]},
            ...     logical_id="GCC-LEGAL-0001",
            ... )
        """
        if self.debug:
            print(f"🔄 Generating Employee Change XML for logical_id: {logical_id or 'TST-GB003-1001'}")

        try:
            xml_string = self.generate_complete_hrxml(
                indicative_data=indicative_data,
                extension_data=extension_data,
                pay_elements_data=pay_elements_data,
                action_code="CHANGE",
                logical_id=logical_id or "ADT-NL001-1001",
                pretty_print=pretty_print
            )

            if self.debug:
                print("✅ Successfully generated Employee Change XML")

            return xml_string

        except Exception as e:
            if self.debug:
                print(f"❌ Failed to generate Employee Change XML: {e}")
            raise ValueError(f"Failed to generate Employee Change XML: {e}")

    def save_xml_to_file(self, xml_content: str, filename: str) -> str:
        """
        Save XML content to a file.

        Args:
            xml_content: The XML string to save
            filename: The filename to save to

        Returns:
            str: The full path to the saved file

        Example:
            >>> path = alight.save_xml_to_file(xml_content, "exports/newhire.xml")
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_content)

            if self.debug:
                print(f"💾 XML saved to: {filename}")

            return filename

        except Exception as e:
            if self.debug:
                print(f"❌ Failed to save XML to file: {e}")
            raise ValueError(f"Failed to save XML to file: {e}")

    def validate_person_data(self, person_data: Dict[str, Any]) -> bool:
        """
        Validate person data structure before generating XML.

        Args:
            person_data: Dictionary containing person data

        Returns:
            bool: True if valid, raises ValueError if not

        Example:
            >>> alight.validate_person_data({"indicative_person_dossier": {"indicative_person": []}})
        """
        try:
            # Try to create HR-XML from the data to validate structure
            self.create_hrxml_from_data(person_data)
            return True
        except Exception as e:
            raise ValueError(f"Invalid person data structure: {e}")

    def upload_to_strada(self, xml_content: str):
        """
        Submit a base64-encoded BOD payload to the Strada gateway.

        The endpoint expects raw XML wrapped in JSON; returning UUID lets callers poll for status later on.

        Example:
            >>> bod_id = alight.upload_to_strada(xml_content)
        """
        data = base64.b64encode(xml_content.encode('utf-8')).decode('utf-8')

        # Print curl command equivalent
        env = "qas" if self.sandbox else "prod"
        auth_token = self.session.headers.get('Authorization', 'Bearer <TOKEN>')
        subscription_key = self.session.headers.get('Ocp-Apim-Subscription-Key', '<SUBSCRIPTION_KEY>')

        print(f'curl {self.base_url}/bods/submit -X POST -H "Content-Type: application/json" -H "gcc: {self.gcc}" -H "env: {env}" -H "Authorization: {auth_token}" -H "Ocp-Apim-Subscription-Key: {subscription_key}" -d \'{{"bod": "{data}"}}\'')

        resp = self.session.post(url=f"{self.base_url}/bods/submit", json={"bod": data})
        resp.raise_for_status()
        return resp.json().get("UUID")

    def get_bods_status(self, bods_id: str):
        """
        Fetch the payroll processing status for a previously submitted BOD.

        Mirrors the Strada UI status check so long-running jobs can be monitored programmatically.

        Example:
            >>> status = alight.get_bods_status("123E4567-E89B-12D3-A456-426614174000")
        """
        resp = self.session.get(url=f"https://apigateway.stradaglobal.com/extwebmethods/bods/{bods_id}/gccs/{self.gcc}/payroll-status")
        resp.raise_for_status()
        return resp.json()

    def generate_employee_xml(
        self,
        employee: Union[EmployeeCreate, Dict[str, Any]],
        action_code: str = "ADD",
        logical_id: Optional[str] = None,
        extension_data: Optional[Dict[str, Any]] = None,
        pay_elements_data: Optional[Dict[str, Any]] = None,
        time_elements_data: Optional[Dict[str, Any]] = None,
        time_quotas_data: Optional[Dict[str, Any]] = None,
        envelope_options: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> str:
        """
        Generate XML directly from an Employee instance.
        This method streamlines the process of creating XML from a flat employee model.

        Args:
            employee: A valid Employee instance
            action_code: The action code for the XML ("ADD" for new hire, "CHANGE" for updates)
            logical_id: Optional logical ID for the sender
            extension_data: Optional extension data dictionary
            pay_elements_data: Optional pay elements data dictionary
            pretty_print: Whether to format the XML with indentation

        Returns:
            str: Complete Alight HR-XML string ready for transmission

        Example:
            >>> alight = Alight()
            >>> employee = Employee(person_id="12345", given_name="John", family_name="Doe", birth_date="1980-01-01")
            >>> xml = alight.generate_employee_xml(employee)
        """
        if self.debug:
            print(f"🔄 Generating {'NewHire' if action_code == 'ADD' else 'Change'} XML from Employee object")

        try:
            # Convert Employee to IndicativeDataType model
            employee_model = employee if isinstance(employee, EmployeeCreate) else EmployeeCreate(**employee)
            indicative_data = employee_model.to_model()

            # Process optional extensions
            extension = None
            pay_elements = None

            extension_dict: Optional[Dict[str, Any]] = None
            if extension_data:
                extension_dict = dict(extension_data)
            if time_elements_data:
                extension_dict = extension_dict or {}
                extension_dict.setdefault("pay_serv_emp_time_elements", {})
                extension_dict["pay_serv_emp_time_elements"].update(time_elements_data)
            if time_quotas_data:
                extension_dict = extension_dict or {}
                extension_dict.setdefault("pay_serv_emp_time_quotas", {})
                extension_dict["pay_serv_emp_time_quotas"].update(time_quotas_data)

            time_elements_model = None
            time_quotas_model = None
            if extension_dict:
                # Build extension first (without time elements/quotas keys)
                ext_only = dict(extension_dict)
                ext_only.pop("pay_serv_emp_time_elements", None)
                ext_only.pop("pay_serv_emp_time_quotas", None)
                if ext_only:
                    extension = self.create_extension_from_data(ext_only)
                # Build time elements/quotas models if provided
                te = extension_dict.get("pay_serv_emp_time_elements")
                if te:
                    # Coerce wrapper types expected by XSD
                    from xsdata.models.datatype import XmlDate
                    items = te.get("time_element", []) or []
                    for item in items:
                        if isinstance(item.get("valid_from"), (datetime,)):
                            item["valid_from"] = XmlDate.from_datetime(item["valid_from"])  # type: ignore
                        elif hasattr(item.get("valid_from"), "toordinal"):
                            item["valid_from"] = XmlDate.from_date(item["valid_from"])  # type: ignore
                        if isinstance(item.get("valid_to"), (datetime,)):
                            item["valid_to"] = XmlDate.from_datetime(item["valid_to"])  # type: ignore
                        elif hasattr(item.get("valid_to"), "toordinal"):
                            item["valid_to"] = XmlDate.from_date(item["valid_to"])  # type: ignore
                        if "units" in item and isinstance(item.get("units"), (str, int, float)):
                            units_str = str(item["units"])
                            if units_str.endswith(".00"):
                                units_str = units_str[:-3]
                            elif units_str.endswith(".0"):
                                units_str = units_str[:-2]
                            item["units"] = {"value": units_str}
                        if "unit_type" in item and isinstance(item.get("unit_type"), str):
                            item["unit_type"] = {"value": item["unit_type"]}
                        # id may be a list of wrappers in XSD
                        if "id" in item:
                            id_val = item.get("id")
                            if isinstance(id_val, list):
                                new_list = []
                                for iv in id_val:
                                    if isinstance(iv, dict) and "value" in iv:
                                        new_list.append(iv)
                                    else:
                                        new_list.append({"value": iv})
                                item["id"] = new_list
                            elif isinstance(id_val, str):
                                item["id"] = [{"value": id_val}]
                        if "absence_reason" in item and isinstance(item.get("absence_reason"), str):
                            item["absence_reason"] = {"value": item["absence_reason"]}
                    try:
                        time_elements_model = construct_model(PayServEmpTimeElements, te)
                    except Exception:
                        time_elements_model = PayServEmpTimeElements.model_validate(te)
                tq = extension_dict.get("pay_serv_emp_time_quotas")
                if tq:
                    try:
                        time_quotas_model = construct_model(PayServEmpTimeQuotas, tq)
                    except Exception:
                        time_quotas_model = PayServEmpTimeQuotas.model_validate(tq)

            if pay_elements_data:
                pay_elements = self.create_pay_elements_from_data(pay_elements_data)

            # Create complete envelope
            envelope_kwargs: Dict[str, Any] = {}
            if logical_id is not None:
                envelope_kwargs["logical_id"] = logical_id

            if envelope_options:
                envelope_kwargs.update(dict(envelope_options))

            envelope_kwargs.setdefault("creation_datetime", datetime.now())
            envelope_kwargs.setdefault("bod_id", str(uuid.uuid4()).upper())
            envelope_kwargs.setdefault("logical_id", logical_id or "TST-GB003-1001")

            # BOD REMOVAL: Exclude BOD fields for new hires (action_code="ADD")
            if action_code == "ADD":
                envelope_kwargs["exclude_bod_fields"] = True

            envelope = self.create_complete_alight_envelope(
                indicative_data=indicative_data,
                extension=extension,
                pay_elements=pay_elements,
                time_elements=time_elements_model,
                time_quotas=time_quotas_model,
                action_code=action_code,
                **envelope_kwargs,
            )

            # Serialize to XML
            xml_string = self.serialize_with_namespaces(envelope, pretty_print=pretty_print)

            if self.debug:
                print("✅ Successfully generated XML from Employee object")

            return xml_string

        except Exception as e:
            if self.debug:
                print(f"❌ Failed to generate XML from Employee: {e}")
            raise ValueError(f"Failed to generate XML from Employee: {e}")

    def generate_newhire_from_employee(
        self,
        employee: EmployeeCreate,
        logical_id: Optional[str] = None,
        extension_data: Optional[Dict[str, Any]] = None,
        pay_elements_data: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True
    ) -> str:
        """
        Generate a NewHire XML document directly from an Employee instance.
        Convenience method for generate_employee_xml with action_code="ADD".

        Args:
            employee: A valid Employee instance
            logical_id: Optional logical ID for the sender
            extension_data: Optional extension data dictionary
            pay_elements_data: Optional pay elements data dictionary
            pretty_print: Whether to format the XML with indentation

        Returns:
            str: Complete NewHire HR-XML string

        Example:
            >>> xml = alight.generate_newhire_from_employee(
            ...     employee=EmployeeCreate(person_id="35561", employee_id="35561ZZGB"),
            ...     pay_elements_data={"pay_element": [{"id": [{"value": "0010"}], "amount": {"value": "42000"}}]},
            ... )
        """
        return self.generate_employee_xml(
            employee=employee,
            action_code="ADD",
            logical_id=logical_id,
            extension_data=extension_data,
            pay_elements_data=pay_elements_data,
            pretty_print=pretty_print
        )

    def generate_change_from_employee(
        self,
        employee: EmployeeCreate,
        logical_id: Optional[str] = None,
        extension_data: Optional[Dict[str, Any]] = None,
        pay_elements_data: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True
    ) -> str:
        """
        Generate an Employee Change XML document directly from an Employee instance.
        Convenience method for generate_employee_xml with action_code="CHANGE".

        Args:
            employee: A valid Employee instance
            logical_id: Optional logical ID for the sender
            extension_data: Optional extension data dictionary
            pay_elements_data: Optional pay elements data dictionary
            pretty_print: Whether to format the XML with indentation

        Returns:
            str: Complete Employee Change HR-XML string

        Example:
            >>> xml = alight.generate_change_from_employee(
            ...     employee=EmployeeCreate(person_id="35561", employee_id="35561ZZGB"),
            ...     extension_data={"bank_accounts": {"bank_account": [{"iban": {"value": "GB00..."}}]}},
            ... )
        """
        return self.generate_employee_xml(
            employee=employee,
            action_code="CHANGE",
            logical_id=logical_id,
            extension_data=extension_data,
            pay_elements_data=pay_elements_data,
            pretty_print=pretty_print
        )
