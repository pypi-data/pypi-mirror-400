"""Schemas for entries on the "template" tag of TemplateModellerConfig schemas."""

from dataclasses import dataclass
from typing import Any, Literal, Optional

import desert
from marshmallow import RAISE, ValidationError, fields
from marshmallow.validate import Equal, OneOf
from marshmallow_union import Union as M_Union

from bitfount.data.types import _SemanticTypeValue


def validate_extension(value: Optional[str]) -> None:
    """Validate that extension is either None or a string that does not start with '.'.

    For instance, should be "csv", _not_ ".csv".
    """
    if value is None:
        return

    if not isinstance(value, str):
        raise ValidationError("Extension must be a string if provided.")

    if value.startswith("."):
        raise ValidationError("Extension must not start with '.' if provided.")


########
# Base #
########
@dataclass(kw_only=True)
class _TemplateVariablesEntryCommon:
    """Common fields for all template variable entries."""

    label: str = desert.field(
        fields.String(required=True),
    )
    tooltip: Optional[str] = desert.field(
        fields.String(required=False, allow_none=True),
        default=None,
    )


##########
# String #
##########
@dataclass(kw_only=True)
class TemplateVariablesEntryString(_TemplateVariablesEntryCommon):
    """Represents a "type: string" template variable entry."""

    type: Literal["string"] = desert.field(
        fields.String(validate=Equal("string"), required=True)
    )
    pattern: Optional[str] = None
    default: Optional[str] = None


@dataclass(kw_only=True)
class TemplateVariablesEntryBool(_TemplateVariablesEntryCommon):
    """Represents a "type: boolean" template variable entry."""

    type: Literal["boolean"] = desert.field(
        fields.String(validate=Equal("boolean"), required=True)
    )
    default: Optional[bool] = None


##########
# Number #
##########
@dataclass(kw_only=True)
class TemplateVariablesEntryNumber(_TemplateVariablesEntryCommon):
    """Represents a "type: number" template variable entry."""

    type: Literal["number"] = desert.field(
        fields.String(validate=Equal("number"), required=True)
    )
    minimum: Optional[int | float] = desert.field(
        M_Union([fields.Integer(), fields.Float()], allow_none=True),
        default=None,
    )
    default: Optional[int | float] = desert.field(
        M_Union([fields.Integer(), fields.Float()], allow_none=True),
        default=None,
    )


#########
# Array #
#########
@dataclass(kw_only=True)
class _TemplateArrayItemsDetails:
    """Details about the items in an array template variable entry."""

    # Currently only string items are supported in the array
    type: Literal["string"] = desert.field(
        fields.String(validate=Equal("string"), required=True)
    )


@dataclass(kw_only=True)
class TemplateVariablesEntryArray(_TemplateVariablesEntryCommon):
    """Represents a "type: array" template variable entry."""

    type: Literal["array"] = desert.field(
        fields.String(validate=Equal("array"), required=True)
    )
    items: _TemplateArrayItemsDetails = desert.field(
        fields.Nested(
            desert.schema_class(_TemplateArrayItemsDetails, meta={"unknown": RAISE}),
            required=True,
        )
    )
    minItems: Optional[int] = desert.field(
        fields.Integer(required=False, allow_none=True),
        default=None,
    )
    default: Optional[list[str]] = desert.field(
        fields.List(fields.String(), required=False, allow_none=True),
        default=None,
    )


#############
# File Path #
#############
@dataclass(kw_only=True)
class _TemplateFilePathTypeDetails:
    """Details about the file path template variable entry."""

    extension: Optional[str] = desert.field(
        fields.String(required=False, allow_none=True, validate=validate_extension),
        default=None,
    )


@dataclass(kw_only=True)
class _TemplateFilePathTypeEntry:
    """Entry for a file path template variable."""

    # This template corresponds to a file path with a particular extension
    file_path: _TemplateFilePathTypeDetails = desert.field(
        fields.Nested(
            desert.schema_class(_TemplateFilePathTypeDetails, meta={"unknown": RAISE}),
            required=True,
        )
    )


@dataclass(kw_only=True)
class TemplateVariablesEntryFilePath(_TemplateVariablesEntryCommon):
    """Represents a "type: file_path" template variable entry."""

    type: _TemplateFilePathTypeEntry = desert.field(
        fields.Nested(
            desert.schema_class(_TemplateFilePathTypeEntry, meta={"unknown": RAISE}),
            required=True,
        )
    )
    default: Optional[str] = None


##############
# Model Slug #
##############
@dataclass(kw_only=True)
class _TemplateModelSlugTypeDetails:
    """Details about the model slug template variable entry."""

    provider: str = desert.field(
        fields.String(required=True),
    )
    library: str = desert.field(
        fields.String(required=True),
    )
    pipeline_tag: Optional[str] = desert.field(
        fields.String(required=False, allow_none=True),
        default=None,
    )
    author: Optional[str] = desert.field(
        fields.String(required=False, allow_none=True),
        default=None,
    )


@dataclass(kw_only=True)
class _TemplateModelSlugTypeEntry:
    """Entry for a model slug template variable."""

    # This template corresponds to a model_id (and provides some
    # additional details to create it from)
    model_slug: _TemplateModelSlugTypeDetails = desert.field(
        fields.Nested(
            desert.schema_class(_TemplateModelSlugTypeDetails, meta={"unknown": RAISE}),
            required=True,
        )
    )


@dataclass(kw_only=True)
class TemplateVariablesEntryModelSlug(_TemplateVariablesEntryCommon):
    """Represents a "type: model_slug" template variable entry."""

    type: _TemplateModelSlugTypeEntry = desert.field(
        fields.Nested(
            desert.schema_class(_TemplateModelSlugTypeEntry, meta={"unknown": RAISE}),
            required=True,
        )
    )


###################################################
# Schema Column Name and Schema Column Name Array #
###################################################
@dataclass(kw_only=True)
class _TemplateSchemaColumnNameTypeDetails:
    """Details about the schema column name template variable entry."""

    semantic_type: _SemanticTypeValue = desert.field(
        fields.String(
            validate=OneOf(("categorical", "continuous", "image", "text")),
            required=True,
        )
    )


@dataclass(kw_only=True)
class _TemplateSchemaColumnNameTypeEntry:
    """Entry for a schema column name template variable."""

    # This template corresponds to a single column name in the schema (and the
    # semantic type to associate it with)
    schema_column_name: _TemplateSchemaColumnNameTypeDetails = desert.field(
        fields.Nested(
            desert.schema_class(
                _TemplateSchemaColumnNameTypeDetails, meta={"unknown": RAISE}
            ),
            required=True,
        )
    )


@dataclass(kw_only=True)
class TemplateVariablesEntrySchemaColumnName(_TemplateVariablesEntryCommon):
    """Represents a "type: schema_column_name" template variable entry."""

    type: _TemplateSchemaColumnNameTypeEntry = desert.field(
        fields.Nested(
            desert.schema_class(
                _TemplateSchemaColumnNameTypeEntry, meta={"unknown": RAISE}
            ),
            required=True,
        )
    )
    default: Optional[str] = None


@dataclass(kw_only=True)
class _TemplateSchemaColumnNameArrayTypeEntry:
    """Entry for a schema column name array template variable."""

    schema_column_name_array: _TemplateSchemaColumnNameTypeDetails = desert.field(
        fields.Nested(
            desert.schema_class(
                _TemplateSchemaColumnNameTypeDetails, meta={"unknown": RAISE}
            ),
            required=True,
        )
    )


@dataclass(kw_only=True)
class TemplateVariablesEntrySchemaColumnNameArray(_TemplateVariablesEntryCommon):
    """Represents a "type: schema_column_name_array" template variable entry."""

    type: _TemplateSchemaColumnNameArrayTypeEntry = desert.field(
        fields.Nested(
            desert.schema_class(
                _TemplateSchemaColumnNameArrayTypeEntry, meta={"unknown": RAISE}
            ),
            required=True,
        )
    )
    default: Optional[list[str]] = None


####################
# Combination Type #
####################
TemplateVariablesEntry = (
    TemplateVariablesEntryString
    | TemplateVariablesEntryNumber
    | TemplateVariablesEntryArray
    | TemplateVariablesEntryFilePath
    | TemplateVariablesEntryModelSlug
    | TemplateVariablesEntrySchemaColumnName
    | TemplateVariablesEntrySchemaColumnNameArray
    | TemplateVariablesEntryBool
)


@dataclass
class TemplatesMixin:
    """Schema for schemas having a `template` field."""

    template: Optional[dict[str, TemplateVariablesEntry]] = desert.field(
        fields.Dict(
            keys=fields.String(),
            values=M_Union(
                [
                    fields.Nested(
                        desert.schema_class(
                            TemplateVariablesEntryString, meta={"unknown": RAISE}
                        )
                    ),
                    fields.Nested(
                        desert.schema_class(
                            TemplateVariablesEntryBool, meta={"unknown": RAISE}
                        )
                    ),
                    fields.Nested(
                        desert.schema_class(
                            TemplateVariablesEntryNumber, meta={"unknown": RAISE}
                        )
                    ),
                    fields.Nested(
                        desert.schema_class(
                            TemplateVariablesEntryArray, meta={"unknown": RAISE}
                        )
                    ),
                    fields.Nested(
                        desert.schema_class(
                            TemplateVariablesEntryFilePath, meta={"unknown": RAISE}
                        )
                    ),
                    fields.Nested(
                        desert.schema_class(
                            TemplateVariablesEntryModelSlug, meta={"unknown": RAISE}
                        )
                    ),
                    fields.Nested(
                        desert.schema_class(
                            TemplateVariablesEntrySchemaColumnName,
                            meta={"unknown": RAISE},
                        )
                    ),
                    fields.Nested(
                        desert.schema_class(
                            TemplateVariablesEntrySchemaColumnNameArray,
                            meta={"unknown": RAISE},
                        )
                    ),
                ],
            ),
            allow_none=True,
        ),
        default=None,
    )


def _partition_template_entry_refs(
    any_of_entries: list[dict[str, Any]], components: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[tuple[list[str], dict[str, Any]]], list[str]]:
    """Categorise template entry schemas by the shape of their `type` field."""

    simple_refs: list[dict[str, Any]] = []
    object_entries: list[tuple[list[str], dict[str, Any]]] = []
    object_keys: list[str] = []

    for entry in any_of_entries:
        ref = entry.get("$ref")
        if not ref:
            continue
        schema_name = ref.split("/")[-1]
        schema = components.get(schema_name)
        if not schema:
            continue
        type_schema = schema.get("properties", {}).get("type")
        if not type_schema:
            continue
        if "$ref" in type_schema:
            nested_schema_name = type_schema["$ref"].split("/")[-1]
            nested_schema = components.get(nested_schema_name, {})
            nested_keys = list(nested_schema.get("properties", {}).keys())
            if not nested_keys:
                continue
            object_keys.extend(nested_keys)
            object_entries.append((nested_keys, entry))
        else:
            simple_refs.append(entry)

    return simple_refs, object_entries, sorted(set(object_keys))


def improve_template_variable_schema(spec_dict: dict[str, Any]) -> dict[str, Any]:
    """Annotate template variable field so editors surface better hints.

    This inspects the generated OpenAPI components and rewrites the `template`
    field definition to differentiate between scalar types (where `type` is a
    literal string) and nested types (where `type` is an object with a single key
    such as `model_slug`). The resulting `if/then/else` schema allows tools such
    as yaml-language-server to display the expected nested keys instead of only the
    scalar literals.
    """

    components = spec_dict.get("components", {}).get("schemas", {})
    for schema in components.values():
        template_property = schema.get("properties", {}).get("template")
        if not template_property:
            continue
        additional_properties = template_property.get("additionalProperties")
        if not isinstance(additional_properties, dict):
            continue
        any_of_entries = additional_properties.get("anyOf")
        if not isinstance(any_of_entries, list):
            continue
        simple_refs, object_entries, object_keys = _partition_template_entry_refs(
            any_of_entries, components
        )
        if not simple_refs or not object_entries:
            continue
        object_if_then = [
            {
                "if": {"properties": {"type": {"required": [key]}}},
                "then": entry_schema,
            }
            for keys, entry_schema in object_entries
            for key in keys
        ]
        template_property["additionalProperties"] = {
            "if": {
                "required": ["type"],
                "properties": {"type": {"type": "string"}},
            },
            "then": {"anyOf": simple_refs},
            "else": {
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "object",
                        "minProperties": 1,
                        "maxProperties": 1,
                        "propertyNames": {"enum": object_keys},
                    }
                },
                "allOf": object_if_then,
            },
        }
    return spec_dict
