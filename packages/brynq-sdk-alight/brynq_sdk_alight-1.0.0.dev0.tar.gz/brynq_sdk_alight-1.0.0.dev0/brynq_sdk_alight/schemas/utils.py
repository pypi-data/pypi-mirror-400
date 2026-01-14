"""
Shared conversion and nesting utilities for flat -> nested XSD mapping.
Composition-first alternative to inheriting a custom BaseModel.
"""

import datetime
from typing import Any, Dict, Optional, Type, get_args, get_origin, Annotated

from pydantic import BaseModel as PydanticBaseModel
from pydantic.fields import FieldInfo
from xsdata.models.datatype import XmlDate, XmlDateTime, XmlTime, XmlPeriod


class _FieldMeta:
    __slots__ = ("name", "field")

    def __init__(self, name: str, field: FieldInfo):
        self.name = name
        self.field = field


_MODEL_FIELD_CACHE: Dict[Type[PydanticBaseModel], Dict[str, _FieldMeta]] = {}
_IS_LIST_CACHE: Dict[int, bool] = {}
_LIST_ITEM_TYPE_CACHE: Dict[int, Optional[Type[Any]]] = {}


def add_to_nested_path(nested: Dict[str, Any], path: str, value: Any) -> None:
    """Add a value to a nested dict at a dot-separated path with optional list indices."""
    parts = path.split('.')
    current = nested

    # Navigate to parent
    for part in parts[:-1]:
        name = part
        index: Optional[int] = None
        if '[' in part and part.endswith(']'):
            name = part[: part.index('[')]
            try:
                index = int(part[part.index('[') + 1 : -1])
            except Exception:
                index = None

        if name not in current:
            current[name] = [] if index is not None else {}
        else:
            if index is None and not isinstance(current[name], dict):
                current[name] = {"value": current[name]}
            if index is not None and not isinstance(current[name], list):
                current[name] = []

        if index is None:
            current = current[name]
        else:
            while len(current[name]) <= index:
                current[name].append(None)
            if not isinstance(current[name][index], dict):
                existing_value = current[name][index]
                current[name][index] = {"value": existing_value} if existing_value is not None else {}
            current = current[name][index]

    # Leaf
    leaf = parts[-1]
    name = leaf
    index: Optional[int] = None
    if '[' in leaf and leaf.endswith(']'):
        name = leaf[: leaf.index('[')]
        try:
            index = int(leaf[leaf.index('[') + 1 : -1])
        except Exception:
            index = None

    if index is None:
        current[name] = value
    else:
        if name not in current or not isinstance(current[name], list):
            current[name] = []
        while len(current[name]) <= index:
            current[name].append(None)
        current[name][index] = value


def _unwrap_annotated(t):
    while get_origin(t) is Annotated:
        args = get_args(t)
        if args:
            t = args[0]
        else:
            break
    return t


def is_wrapper_model(model_type) -> bool:
    return (
        isinstance(model_type, type)
        and issubclass(model_type, PydanticBaseModel)
        and hasattr(model_type, "model_fields")
        and "value" in getattr(model_type, "model_fields", {})
    )


def is_list_field(field_type) -> bool:
    cache_key = id(field_type)
    if cache_key in _IS_LIST_CACHE:
        return _IS_LIST_CACHE[cache_key]

    field_type = _unwrap_annotated(field_type)
    origin = get_origin(field_type)
    if origin is list or str(origin) == 'typing.List':
        _IS_LIST_CACHE[cache_key] = True
        return True
    # Optional[List[T]] / Union[List[T], None]
    if str(origin) == 'typing.Union':
        for arg in get_args(field_type) or []:
            arg = _unwrap_annotated(arg)
            inner_origin = get_origin(arg)
            if inner_origin is list or str(inner_origin) == 'typing.List':
                _IS_LIST_CACHE[cache_key] = True
                return True
    _IS_LIST_CACHE[cache_key] = False
    return False


def get_list_item_type(field_type):
    cache_key = id(field_type)
    if cache_key in _LIST_ITEM_TYPE_CACHE:
        return _LIST_ITEM_TYPE_CACHE[cache_key]

    field_type = _unwrap_annotated(field_type)
    if get_origin(field_type) is list:
        args = get_args(field_type)
        if args:
            value = _unwrap_annotated(args[0])
            _LIST_ITEM_TYPE_CACHE[cache_key] = value
            return value
    # Optional[List[T]]
    origin = get_origin(field_type)
    if str(origin) == 'typing.Union':
        for arg in get_args(field_type) or []:
            arg = _unwrap_annotated(arg)
            if get_origin(arg) is list:
                inner = get_args(arg)
                if inner:
                    value = _unwrap_annotated(inner[0])
                    _LIST_ITEM_TYPE_CACHE[cache_key] = value
                    return value
    _LIST_ITEM_TYPE_CACHE[cache_key] = None
    return None


def unwrap_optional_and_list(field_type):
    field_type = _unwrap_annotated(field_type)
    origin = get_origin(field_type)
    if origin is type(Optional[str]) or str(origin) == 'typing.Union':
        args = get_args(field_type)
        if args:
            for arg in args:
                if arg is not type(None):  # noqa: E721
                    field_type = _unwrap_annotated(arg)
                    break
    if get_origin(field_type) is list:
        args = get_args(field_type)
        if args:
            field_type = _unwrap_annotated(args[0])
    return field_type


def convert_datetime_to_xml(dt_value: datetime.date | datetime.datetime, target_type) -> Any:
    """Convert Python datetime/date to appropriate XML type."""
    if isinstance(dt_value, datetime.date) and not isinstance(dt_value, datetime.datetime):
        return XmlDate(dt_value.year, dt_value.month, dt_value.day)
    if isinstance(dt_value, datetime.datetime):
        return XmlDateTime(
            dt_value.year,
            dt_value.month,
            dt_value.day,
            dt_value.hour,
            dt_value.minute,
            dt_value.second,
            dt_value.microsecond // 1000,
        )
    return dt_value


def convert_date_string_to_xml(date_str: str, field_type, field_name: str) -> Any:
    target_type = get_xml_date_type_from_annotation(field_type)
    if target_type is None:
        lname = field_name.lower()
        if 'datetime' in lname or 'timestamp' in lname:
            target_type = XmlDateTime
        elif 'time' in lname and 'date' not in lname:
            target_type = XmlTime
        elif 'period' in lname:
            target_type = XmlPeriod
        else:
            target_type = XmlDate
    return convert_date_string_to_xml_for_type(date_str, target_type)


def convert_date_string_to_xml_for_type(date_str: str, target_type) -> Any:
    try:
        if target_type == XmlDate or str(target_type).endswith('XmlDate'):
            return XmlDate.from_string(date_str)
        if target_type == XmlDateTime or str(target_type).endswith('XmlDateTime'):
            return XmlDateTime.from_string(date_str)
        if target_type == XmlTime or str(target_type).endswith('XmlTime'):
            return XmlTime.from_string(date_str)
        if target_type == XmlPeriod or str(target_type).endswith('XmlPeriod'):
            return XmlPeriod.from_string(date_str)
        return date_str
    except Exception:
        return date_str


def get_xml_date_type_from_annotation(field_type) -> Optional[Type]:
    field_type = _unwrap_annotated(field_type)
    if field_type in (XmlDate, XmlDateTime, XmlTime, XmlPeriod):
        return field_type
    type_str = str(field_type)
    if 'XmlDate' in type_str and 'XmlDateTime' not in type_str:
        return XmlDate
    if 'XmlDateTime' in type_str:
        return XmlDateTime
    if 'XmlTime' in type_str:
        return XmlTime
    if 'XmlPeriod' in type_str:
        return XmlPeriod
    origin = getattr(field_type, '__origin__', None)
    if str(origin) == 'typing.Union':
        for arg in get_args(field_type) or []:
            arg = _unwrap_annotated(arg)
            if arg in (XmlDate, XmlDateTime, XmlTime, XmlPeriod):
                return arg
            elif hasattr(arg, '__name__'):
                name = arg.__name__
                if name == 'XmlDate':
                    return XmlDate
                if name == 'XmlDateTime':
                    return XmlDateTime
                if name == 'XmlTime':
                    return XmlTime
                if name == 'XmlPeriod':
                    return XmlPeriod
    return None


def looks_like_date(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) >= 10 and value[4] == '-' and value[7] == '-':
        try:
            year = int(value[0:4])
            month = int(value[5:7])
            day = int(value[8:10])
            if 1 <= month <= 12 and 1 <= day <= 31 and year >= 1900:
                return True
        except (ValueError, IndexError):
            pass
    return False


def post_process_nested_data(nested_data: Dict[str, Any], model: PydanticBaseModel) -> None:
    """Ensure wrapper/list structures and primitive coercions align with the schema model."""

    if not hasattr(model, 'model_fields'):
        return

    _normalize_node(nested_data, model, model.__name__ or "root")


def _normalize_node(node: Dict[str, Any], model: PydanticBaseModel, path: str) -> None:
    if not isinstance(node, dict) or not hasattr(model, 'model_fields'):
        return

    field_lookup = _get_model_field_cache(model)

    for key, value in list(node.items()):
        meta = field_lookup.get(key)
        if meta is None:
            continue

        field = meta.field
        raw_annotation = field.annotation
        current_path = f"{path}.{field.alias or meta.name}"

        if value is None:
            continue

        if is_list_field(raw_annotation):
            node[key] = _normalize_list(value, raw_annotation, current_path)
            continue

        base_annotation = unwrap_optional_and_list(_unwrap_annotated(raw_annotation))

        if isinstance(base_annotation, type) and issubclass(base_annotation, PydanticBaseModel):
            if is_wrapper_model(base_annotation):
                node[key] = _ensure_wrapper(value, base_annotation, current_path)
            else:
                if isinstance(value, dict):
                    _normalize_node(value, base_annotation, current_path)
            continue

        node[key] = _coerce_primitive_value(value, raw_annotation, current_path)


def _normalize_list(value: Any, annotation, path: str) -> list:
    items = value if isinstance(value, list) else [value]
    items = [item for item in items if item not in (None, {})]

    item_annotation = get_list_item_type(annotation)
    if item_annotation is None:
        return items

    base_item = unwrap_optional_and_list(_unwrap_annotated(item_annotation))

    if isinstance(base_item, type) and issubclass(base_item, PydanticBaseModel):
        normalized: list[Any] = []
        for idx, item in enumerate(items):
            item_path = f"{path}[{idx}]"
            if item is None:
                continue
            if is_wrapper_model(base_item):
                normalized.append(_ensure_wrapper(item, base_item, item_path))
            elif isinstance(item, dict):
                _normalize_node(item, base_item, item_path)
                normalized.append(item)
            else:
                normalized.append(item)
        return normalized

    return [_coerce_primitive_value(item, item_annotation, f"{path}[{idx}]") for idx, item in enumerate(items)]


def _ensure_wrapper(value: Any, wrapper_type: Type[PydanticBaseModel], path: str) -> Dict[str, Any]:
    value_field = wrapper_type.model_fields['value']
    value_annotation = value_field.annotation

    if isinstance(value, dict) and 'value' in value:
        coerced = _coerce_primitive_value(value['value'], value_annotation, f"{path}.value")
        value['value'] = coerced
        return value

    coerced = _coerce_primitive_value(value, value_annotation, f"{path}.value")
    return {"value": coerced}


def _coerce_primitive_value(value: Any, annotation, path: str) -> Any:
    target_annotation = unwrap_optional_and_list(_unwrap_annotated(annotation))

    if value is None:
        return None

    # Handle Union of XML date/time types explicitly (attributes like valid_from/valid_to)
    origin = get_origin(target_annotation)
    if str(origin) == 'typing.Union':
        union_args = [ _unwrap_annotated(a) for a in (get_args(target_annotation) or []) ]
        has_xml_date_union = any(a in (XmlDate, XmlDateTime, XmlTime, XmlPeriod) for a in union_args)
        if has_xml_date_union:
            if isinstance(value, (datetime.date, datetime.datetime)):
                # Prefer XmlDate for date, XmlDateTime for datetime
                return convert_datetime_to_xml(value, XmlDateTime if isinstance(value, datetime.datetime) else XmlDate)
            if isinstance(value, str) and looks_like_date(value):
                # Default to XmlDate for strings that look like dates
                return convert_date_string_to_xml_for_type(value, XmlDate)

    xml_target = get_xml_date_type_from_annotation(target_annotation)
    if xml_target is not None:
        if isinstance(value, (datetime.date, datetime.datetime)):
            return convert_datetime_to_xml(value, xml_target)
        if isinstance(value, str) and looks_like_date(value):
            return convert_date_string_to_xml_for_type(value, xml_target)

    if isinstance(value, (datetime.date, datetime.datetime)):
        return convert_datetime_to_xml(value, target_annotation)

    if isinstance(value, str) and looks_like_date(value):
        return convert_date_string_to_xml(value, target_annotation, path.split('.')[-1])

    if target_annotation is str and isinstance(value, bool):
        return "true" if value else "false"

    return value


def _get_model_field_cache(model: Type[PydanticBaseModel]) -> Dict[str, _FieldMeta]:
    cached = _MODEL_FIELD_CACHE.get(model)
    if cached is not None:
        return cached

    mapping: Dict[str, _FieldMeta] = {}
    for name, field in getattr(model, "model_fields", {}).items():
        meta = _FieldMeta(name=name, field=field)
        mapping[name] = meta
        alias = getattr(field, "alias", None)
        if alias:
            mapping[alias] = meta
    _MODEL_FIELD_CACHE[model] = mapping
    return mapping


def construct_model(model: Type[PydanticBaseModel], data: Dict[str, Any]) -> PydanticBaseModel:
    """
    Construct a Pydantic model instance without full validation by recursively
    instantiating only the fields present in the provided data dictionary.
    """
    if isinstance(data, model):
        return data
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict to construct {model.__name__}, got {type(data).__name__}")

    lookup = _get_model_field_cache(model)
    values: Dict[str, Any] = {}

    for key, value in data.items():
        if value is None:
            continue
        meta = lookup.get(key)
        if meta is None:
            continue
        if meta.name in values:
            continue
        field = meta.field
        values[meta.name] = _prepare_field_value(field.annotation, value)

    return model.model_construct(_fields_set=set(values.keys()), **values)


def _prepare_field_value(annotation, value: Any) -> Any:
    if value is None:
        return None

    if is_list_field(annotation):
        items = value if isinstance(value, list) else [value]
        item_type = get_list_item_type(annotation)
        if item_type is None:
            return items
        prepared = [_prepare_field_value(item_type, item) for item in items if item not in (None, {})]
        return prepared

    base_annotation = unwrap_optional_and_list(_unwrap_annotated(annotation))

    if isinstance(base_annotation, type) and issubclass(base_annotation, PydanticBaseModel):
        if isinstance(value, base_annotation):
            return value
        if isinstance(value, dict):
            return construct_model(base_annotation, value)
        if isinstance(value, list):
            return [
                construct_model(base_annotation, element) if isinstance(element, dict) else element
                for element in value
            ]

    return value
