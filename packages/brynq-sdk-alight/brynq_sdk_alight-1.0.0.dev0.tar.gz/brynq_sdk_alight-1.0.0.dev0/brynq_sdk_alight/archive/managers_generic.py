"""
Fully generic manager for the Alight SDK.
Pure XSD schema-driven transformations - zero hardcoded mappings.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING, List, get_origin, get_args
from pydantic import BaseModel

from .schemas.hrxml_indicative_data import IndicativeDataType

if TYPE_CHECKING:
    from . import Alight


class EmployeeManager:
    """Fully generic employee manager - pure XSD schema-driven conversion."""

    def __init__(self, alight_sdk: 'Alight'):
        self.alight_sdk = alight_sdk

    def create_newhire_simple(self, flat_data: Dict[str, Any],
                             logical_id: Optional[str] = None,
                             pretty_print: bool = True,
                             save_to_file: bool = False,
                             filename: Optional[str] = None) -> str:
        """
        Create NewHire XML from flat dictionary using pure XSD schema conversion.
        """
        nested_data = self._flat_to_nested(flat_data)
        return self.alight_sdk.generate_newhire_xml(
            person_data=nested_data,
            logical_id=logical_id,
            pretty_print=pretty_print
        )

    def create_employee_change_simple(self, flat_data: Dict[str, Any],
                                     logical_id: Optional[str] = None,
                                     pretty_print: bool = True,
                                     save_to_file: bool = False,
                                     filename: Optional[str] = None) -> str:
        """
        Create Employee Change XML from flat dictionary using pure XSD schema conversion.
        """
        nested_data = self._flat_to_nested(flat_data)
        return self.alight_sdk.generate_employee_change_xml(
            person_data=nested_data,
            logical_id=logical_id,
            pretty_print=pretty_print
        )

    def _flat_to_nested(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat data to nested using PURE XSD schema inspection.
        Zero hardcoded mappings - everything is generic and schema-driven.
        """
        # Use the generic XSD-aware conversion directly on the main schema
        return self._xsd_flat_to_nested(flat_data, IndicativeDataType)

    def _xsd_flat_to_nested(self, flat_dict: Dict[str, Any], model: BaseModel) -> Dict[str, Any]:
        """
        Generic XSD-aware version exactly like your Functions.flat_dict_to_nested_dict.
        Recursively processes the schema and handles XSD {"value": ...} format automatically.
        """
        nested = {}

        for name, field in model.model_fields.items():
            key_in_input = name  # Original model field name as key in flat_dict
            alias = field.alias or name

            # Handle nested BaseModel fields (recursively) - exact same logic as your function
            if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
                nested[alias] = self._xsd_flat_to_nested(flat_dict, field.annotation)

            # Handle Union types with BaseModel (like Optional[SomeModel]) - exact same logic
            elif any(isinstance(item, type) and issubclass(item, BaseModel) for item in get_args(field.annotation)):
                # Get the BaseModel class from the Union
                nested_model = next(item for item in get_args(field.annotation)
                                   if isinstance(item, type) and issubclass(item, BaseModel))
                nested[alias] = self._xsd_flat_to_nested(flat_dict, nested_model)

            # Handle primitive fields - your logic + XSD value wrapping
            else:
                if key_in_input in flat_dict:
                    value = flat_dict[key_in_input]

                    # XSD enhancement: Check if this field type needs {"value": ...} wrapping
                    field_type = self._unwrap_optional_and_list(field.annotation)
                    if (hasattr(field_type, 'model_fields') and
                        'value' in getattr(field_type, 'model_fields', {})):
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
