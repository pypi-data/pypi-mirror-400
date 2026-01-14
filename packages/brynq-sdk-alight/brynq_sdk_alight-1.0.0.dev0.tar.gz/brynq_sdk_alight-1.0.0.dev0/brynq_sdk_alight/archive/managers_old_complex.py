"""
Simplified manager for the Alight SDK.
Pure dictionary transformations - no unnecessary classes or complexity.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING, List, get_origin, get_args
from pydantic import BaseModel

from .schemas.hrxml_indicative_data import IndicativeDataType, IndicativePerson

if TYPE_CHECKING:
    from . import Alight


class EmployeeManager:
    """Simple employee manager - just flat-to-nested dictionary conversion."""
    
    def __init__(self, alight_sdk: 'Alight'):
        self.alight_sdk = alight_sdk
    
        # Simple field categorization
        self.field_categories = {
            'extension': ['iban', 'bic', 'account_holder', 'notes'],
            'salary': ['base_salary', 'bonus_amount', 'salary_currency', 'pay_element_code'],
            'job': ['job_title', 'weekly_hours', 'country'],
        }

    def create_newhire_simple(self, flat_data: Dict[str, Any],
                      logical_id: Optional[str] = None, 
                      pretty_print: bool = True,
                      save_to_file: bool = False,
                      filename: Optional[str] = None) -> str:
        """
        Create NewHire XML from flat dictionary - that's it!
        
        Args:
            flat_data: Simple flat dictionary with snake_case keys
            logical_id: Optional logical ID
            pretty_print: Format XML nicely
            save_to_file: Save to file
            filename: Optional filename
            
        Returns:
            str: HR-XML ready for Alight
        """
        nested_data = self._flat_to_nested(flat_data)
        return self.alight_sdk.generate_newhire_xml(
            person_data=nested_data.get('person_data'),
            extension_data=nested_data.get('extension_data'),
            pay_elements_data=nested_data.get('salary_data'),
            logical_id=logical_id,
            pretty_print=pretty_print
        )
        
    def create_employee_change_simple(self, flat_data: Dict[str, Any],
                              logical_id: Optional[str] = None, 
                              pretty_print: bool = True,
                              save_to_file: bool = False,
                              filename: Optional[str] = None) -> str:
        """
        Create Employee Change XML from flat dictionary - that's it!
        """
        nested_data = self._flat_to_nested(flat_data)
        return self.alight_sdk.generate_employee_change_xml(
            person_data=nested_data.get('person_data'),
            extension_data=nested_data.get('extension_data'),
            pay_elements_data=nested_data.get('salary_data'),
            logical_id=logical_id,
            pretty_print=pretty_print
        )
    
    def _flat_to_nested(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat data to nested using PURE XSD schema inspection.
        No hardcoded field mappings - everything is generic and schema-driven.
        """
        result = {}
        
        # Use the generic XSD-aware conversion directly on the main schema
        nested_data = self._xsd_flat_to_nested(flat_data, IndicativeDataType)
        
        # The result should have the indicative_person_dossier structure
        if 'indicative_person_dossier' in nested_data:
            # Extract the person dossier data
            person_dossier = nested_data['indicative_person_dossier']
            
            # Map the XSD structure to our expected output format
            if person_dossier:
                result['person_data'] = person_dossier
        
        return result

    def _xsd_flat_to_nested(self, flat_dict: Dict[str, Any], model: BaseModel) -> Dict[str, Any]:
        """
        Generic XSD-aware version of flat_dict_to_nested_dict.
        Based on your Functions.flat_dict_to_nested_dict but handles XSD {"value": ...} format.
        """
        nested = {}
        
        for name, field in model.model_fields.items():
            key_in_input = name  # Original model field name as key in flat_dict
            alias = field.alias or name
            
            # Handle nested BaseModel fields (recursively)
            if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
                nested[alias] = self._xsd_flat_to_nested(flat_dict, field.annotation)
            
            # Handle Union types with BaseModel (like Optional[SomeModel])
            elif any(isinstance(item, type) and issubclass(item, BaseModel) for item in get_args(field.annotation)):
                # Get the BaseModel class from the Union
                nested_model = next(item for item in get_args(field.annotation) 
                                   if isinstance(item, type) and issubclass(item, BaseModel))
                nested[alias] = self._xsd_flat_to_nested(flat_dict, nested_model)
            
            # Handle List types with BaseModel elements
            elif get_origin(field.annotation) is list:
                args = get_args(field.annotation)
                if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                    # List of BaseModel - create single item with nested structure
                    nested_item = self._xsd_flat_to_nested(flat_dict, args[0])
                    if nested_item:  # Only add if there's actual data
                        nested[alias] = [nested_item]
                else:
                    # List of primitives - just wrap the value if present
                    if key_in_input in flat_dict:
                        nested[alias] = [flat_dict[key_in_input]]
            
            # Handle primitive fields (including XSD value wrappers)
            else:
                if key_in_input in flat_dict:
                    value = flat_dict[key_in_input]
                    
                    # Check if this is an XSD type that needs {"value": ...} wrapping
                    field_type = self._unwrap_optional_and_list(field.annotation)
                    if (hasattr(field_type, 'model_fields') and 
                        isinstance(field_type.model_fields.get('value'), type)):
                        nested[alias] = {"value": value}
                    else:
                        nested[alias] = value
        
        return nested
    
    def _unwrap_optional_and_list(self, field_type):
        """Helper to unwrap Optional and List types to get the core type."""
        # Handle Optional[T] (Union[T, None])
        origin = get_origin(field_type)
        if origin is type(Optional[str]) or str(origin) == 'typing.Union':
            args = get_args(field_type)
            if args:
                for arg in args:
                    if arg is not type(None):
                        field_type = arg
                        break
        
        # Handle List[T]
        if get_origin(field_type) is list:
            args = get_args(field_type)
            if args:
                field_type = args[0]
        
        return field_type

    def _build_person_data(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Build person data structure using XSD-based automatic wrapping."""
        person_data = {}
        person_section = {}
        employment_section = {}

        # XSD-based automatic field processing
        # These fields map directly to IndicativeDataType schema fields
        direct_person_fields = ['person_id', 'birth_date']
        direct_employment_fields = ['employee_id']

        # Process direct person fields using XSD schema inspection
        for field_name in direct_person_fields:
            if fields.get(field_name):
                wrapped_value = self._auto_wrap_field(field_name, fields[field_name], IndicativePerson)
                person_section[field_name] = wrapped_value

        # Process direct employment fields
        for field_name in direct_employment_fields:
            if fields.get(field_name):
                wrapped_value = self._auto_wrap_field(field_name, fields[field_name], IndicativeDataType)
                employment_section[field_name] = wrapped_value

        # Handle structured fields that don't map directly to schema
        # Names (complex nested structure)
        if fields.get('first_name') or fields.get('last_name'):
            person_section['person_name'] = [{}]
            if fields.get('first_name'):
                # Use XSD inspection for given_name wrapping
                person_section['person_name'][0]['given_name'] = self._auto_wrap_field('given_name', fields['first_name'], IndicativeDataType)
            if fields.get('last_name'):
                # Use XSD inspection for family_name wrapping
                person_section['person_name'][0]['family_name'] = self._auto_wrap_field('family_name', fields['last_name'], IndicativeDataType)

        # Communication (structured)
        communication = []
        if fields.get('email'):
            communication.append({
                "type": "Email",
                "uri": self._auto_wrap_field('uri', fields['email'], IndicativeDataType)
            })
        if fields.get('phone'):
            communication.append({
                "type": "Phone",
                "dial_number": self._auto_wrap_field('dial_number', fields['phone'], IndicativeDataType)
            })
        if communication:
            person_section['communication'] = communication

        # Employment dates
        hire_date = fields.get('hire_date')
        effective_date = fields.get('effective_date')
        actual_date = hire_date or effective_date

        if actual_date:
            employment_section['employment_lifecycle'] = [{
                "valid_from": actual_date,
                "hire": {
                    "hire_date": self._auto_wrap_field('hire_date', actual_date, IndicativeDataType),
                    "original_hire_date": self._auto_wrap_field('original_hire_date', actual_date, IndicativeDataType)
                }
            }]

        # Assemble
        if person_section:
            person_data['person'] = person_section
        if employment_section:
            person_data['employment'] = employment_section

        return person_data

    def _build_extension_data(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Build extension data (payment info, etc.)."""
        extension_data = {}

        # Payment instruction
        if any(fields.get(k) for k in ['iban', 'bic', 'account_holder']):
            extension_data['payment_instruction'] = {}
            if fields.get('iban'):
                extension_data['payment_instruction']['iban'] = fields['iban']
            if fields.get('bic'):
                extension_data['payment_instruction']['bic'] = fields['bic']
            if fields.get('account_holder'):
                extension_data['payment_instruction']['holder_name'] = fields['account_holder']

        if fields.get('notes'):
            extension_data['note'] = fields['notes']

        return extension_data

    def _build_salary_data(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Build salary data."""
        salary_data = {}
        pay_elements = []

        if fields.get('base_salary'):
            pay_elements.append({
                "code": "BASE",
                "amount": fields['base_salary'],
                "valid_from": fields.get('effective_date') or fields.get('hire_date')
            })

        if fields.get('bonus_amount'):
            pay_elements.append({
                "code": "BONUS",
                "amount": fields['bonus_amount'],
                "valid_from": fields.get('effective_date') or fields.get('hire_date')
            })

        if pay_elements:
            salary_data['pay_element'] = pay_elements

        return salary_data

    def _build_job_data(self, job_fields: Dict[str, Any], all_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Build job/deployment data."""
        job_data = {}

        actual_date = all_fields.get('hire_date') or all_fields.get('effective_date')
        if actual_date:
            job_data['valid_from'] = actual_date

        if job_fields.get('job_title'):
            job_data['job'] = {"title": job_fields['job_title']}

        if job_fields.get('weekly_hours'):
            job_data['schedule'] = {"weekly_hours": job_fields['weekly_hours']}

        if job_fields.get('country'):
            job_data['work_location'] = {"country": job_fields['country']}

        return job_data
