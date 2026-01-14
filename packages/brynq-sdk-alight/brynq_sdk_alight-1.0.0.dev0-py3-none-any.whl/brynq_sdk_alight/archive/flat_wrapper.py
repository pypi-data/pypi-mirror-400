"""
Flat wrapper for XSD schemas.
Provides a simple interface that automatically maps flat dictionaries to complex XSD schemas.
"""

from typing import Any, Dict, Optional, Type, get_origin, get_args
from pydantic import BaseModel
from xsdata.models.datatype import XmlDate
from xsdata_pydantic.bindings import XmlSerializer


class SchemaWrapper:
    """
    Generic wrapper for any XSD schema.
    Converts flat dictionaries to proper XSD format without field duplication.
    
    Usage:
        employee_data = {
            "person_id": "12345",
            "given_name": "John",
            "family_name": "Smith",
            "birth_date": "1990-01-01",
            # ... any other fields matching the schema
        }
        
        # Create wrapper with the flat data and schema class
        wrapper = SchemaWrapper(employee_data, IndicativeDataType)
        
        # Get XML directly
        xml = wrapper.to_xml()
    """
    
    def __init__(self, data: Dict[str, Any], schema_class: Type[BaseModel]):
        """
        Initialize with flat data and target schema class.
        
        Args:
            data: Flat dictionary with field names matching schema fields
            schema_class: XSD-generated schema class to use (e.g. IndicativeDataType)
        """
        self.data = data
        self.schema_class = schema_class
    
    def _xsd_flat_to_nested(self, flat_dict: Dict[str, Any], model: Type[BaseModel]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using schema introspection.
        Uses the model's field types to determine how to structure the data.
        """
        nested = {}
        
        for name, field in model.model_fields.items():
            key_in_input = name  # Original model field name as key in flat_dict
            alias = field.alias or name
            
            # Handle nested BaseModel fields (recursively) 
            if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
                nested[alias] = self._xsd_flat_to_nested(flat_dict, field.annotation)
            
            # Handle Union types with BaseModel (like Optional[SomeModel])
            elif any(isinstance(item, type) and issubclass(item, BaseModel) 
                    for item in get_args(field.annotation) if isinstance(item, type)):
                # Get the BaseModel class from the Union
                nested_model = next((item for item in get_args(field.annotation) 
                                   if isinstance(item, type) and issubclass(item, BaseModel)), None)
                if nested_model:
                    nested[alias] = self._xsd_flat_to_nested(flat_dict, nested_model)
            
            # Handle primitive fields - PURE schema introspection, NO hardcoding!
            else:
                if key_in_input in flat_dict:
                    value = flat_dict[key_in_input]
                    
                    # XSD enhancement: Check if this field type needs {"value": ...} wrapping
                    field_type = self._unwrap_optional_and_list(field.annotation)
                    if (hasattr(field_type, 'model_fields') and
                        'value' in getattr(field_type, 'model_fields', {})):
                        # Automatic XmlDate conversion for date fields (minimal logic)
                        if 'date' in key_in_input.lower() and isinstance(value, str):
                            nested[alias] = {"value": XmlDate.from_string(value)}
                        else:
                            nested[alias] = {"value": value}
                    else:
                        nested[alias] = value
        
        return nested
    
    def _unwrap_optional_and_list(self, field_type):
        """Helper to unwrap Optional and List types to get the core type."""
        # Handle Optional[T] (Union[T, None])
        origin = get_origin(field_type)
        if origin is type(None) or str(origin) == 'typing.Union':
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
    
    def to_nested_dict(self) -> Dict[str, Any]:
        """Convert flat data to nested dictionary structure using schema introspection."""
        return self._xsd_flat_to_nested(self.data, self.schema_class)
    
    def to_model(self) -> BaseModel:
        """Convert flat data to proper schema model instance using introspection."""
        nested_data = self._xsd_flat_to_nested(self.data, self.schema_class)
        return self.schema_class.model_validate(nested_data)
    
    def to_xml(self, pretty_print: bool = True) -> str:
        """
        Generate XML output directly from flat data.
        
        Args:
            pretty_print: Whether to format the XML with proper indentation
            
        Returns:
            XML string representation of the data
        """
        from xml.dom import minidom
        
        model = self.to_model()
        serializer = XmlSerializer()
        xml_output = serializer.render(model)
        
        # Optional pretty printing
        if pretty_print:
            dom = minidom.parseString(xml_output)
            xml_output = dom.toprettyxml(indent="  ")
            xml_output = '\n'.join([line for line in xml_output.split('\n') if line.strip()])
        
        return xml_output

