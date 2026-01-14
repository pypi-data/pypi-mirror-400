"""
HR-XML Generator for Alight Integration

This module provides functions to generate HR-XML documents using XSData models
with proper Alight envelope structure and namespace handling.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from xml.dom import minidom

from xsdata.models.datatype import XmlDate, XmlDateTime
from xsdata_pydantic.bindings import XmlSerializer as PydanticXmlSerializer

from .schemas.hrxml_indicative_data import IndicativeDataType, IndicativeData
from .schemas.flattened_main_schemas.process_pay_serv_emp import (
    ProcessPayServEmp, DataArea, PayServEmp, PayServEmpExtension, PayServEmpPayElements
)
from .schemas.openapplications_bod import ApplicationArea, Sender


def create_hrxml_from_data(person_data: Dict[str, Any]) -> IndicativeDataType:
    """
    Create HR-XML IndicativeDataType from person data dictionary.
    
    Args:
        person_data: Dictionary containing person, employee, employment, deployment, and remuneration data
        
    Returns:
        IndicativeDataType: Validated XSData model instance
    """
    try:
        indicative_data = IndicativeDataType.model_validate(person_data)
        return indicative_data
    except Exception as e:
        raise ValueError(f"Failed to create HR-XML from data: {e}")


def create_extension_from_data(extension_data: Dict[str, Any]) -> PayServEmpExtension:
    """
    Create PayServEmpExtension from extension data dictionary.
    
    Args:
        extension_data: Dictionary containing payment instructions, cost assignments, etc.
        
    Returns:
        PayServEmpExtension: Validated XSData model instance
    """
    try:
        extension = PayServEmpExtension.model_validate(extension_data)
        return extension
    except Exception as e:
        raise ValueError(f"Failed to create extension from data: {e}")


def create_pay_elements_from_data(pay_elements_data: Dict[str, Any]) -> PayServEmpPayElements:
    """
    Create PayServEmpPayElements from pay elements data dictionary.
    
    Args:
        pay_elements_data: Dictionary containing pay elements
        
    Returns:
        PayServEmpPayElements: Validated XSData model instance
    """
    try:
        pay_elements = PayServEmpPayElements.model_validate(pay_elements_data)
        return pay_elements
    except Exception as e:
        raise ValueError(f"Failed to create pay elements from data: {e}")


def create_complete_alight_envelope(
    indicative_data: IndicativeDataType,
    extension: Optional[PayServEmpExtension] = None,
    pay_elements: Optional[PayServEmpPayElements] = None,
    action_code: str = "ADD",
    logical_id: str = "TST-GB003-1001",
    language_code: str = "en-US",
    system_environment_code: str = "TST NF",
    release_id: str = "DEFAULT"
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
    """
    # Create timestamp and BODID
    timestamp = datetime.now()
    bod_id = str(uuid.uuid4()).upper()

    try:
        # Create Sender
        sender_data = {
            "logical_id": {"value": logical_id},
            "component_id": {"value": "PAYROLL"},
            "reference_id": {"value": "hrisxml"},
            "confirmation_code": {"value": "Always"}
        }
        sender = Sender.model_validate(sender_data)

        # Create ApplicationArea
        app_area_data = {
            "sender": sender,
            "creation_date_time": {"value": XmlDateTime.from_datetime(timestamp)},
            "bodid": {"value": bod_id}
        }
        application_area = ApplicationArea.model_validate(app_area_data)

        # Create PayServEmp (contains our IndicativeData + Extensions)
        # Need to create IndicativeData wrapper (not IndicativeDataType)
        indicative_data_wrapper = IndicativeData(
            indicative_person_dossier=indicative_data.indicative_person_dossier
        )

        pay_serv_emp_data = {
            "indicative_data": indicative_data_wrapper
        }
        
        # Add optional components if provided
        if extension:
            pay_serv_emp_data["pay_serv_emp_extension"] = extension
        if pay_elements:
            pay_serv_emp_data["pay_serv_emp_pay_elements"] = pay_elements
            
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
        data_area = DataArea.model_validate(data_area_data)

        # Create the complete ProcessPayServEmp envelope
        envelope_data = {
            "application_area": application_area,
            "data_area": data_area,
            "language_code": language_code,
            "system_environment_code": system_environment_code,
            "release_id": release_id
        }

        complete_envelope = ProcessPayServEmp.model_validate(envelope_data)
        return complete_envelope

    except Exception as e:
        raise ValueError(f"Failed to create complete Alight envelope: {e}")


def serialize_with_namespaces(
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
    person_data: Dict[str, Any],
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
    """
    try:
        # Create HR-XML content
        indicative_data = create_hrxml_from_data(person_data)
        
        # Create optional components
        extension = None
        pay_elements = None
        
        if extension_data:
            extension = create_extension_from_data(extension_data)
            
        if pay_elements_data:
            pay_elements = create_pay_elements_from_data(pay_elements_data)
        
        # Create complete envelope
        envelope = create_complete_alight_envelope(
            indicative_data=indicative_data,
            extension=extension,
            pay_elements=pay_elements,
            action_code=action_code,
            logical_id=logical_id
        )
        
        # Serialize to XML
        xml_string = serialize_with_namespaces(envelope, pretty_print=pretty_print)
        
        return xml_string
        
    except Exception as e:
        raise ValueError(f"Failed to generate complete HR-XML: {e}") 