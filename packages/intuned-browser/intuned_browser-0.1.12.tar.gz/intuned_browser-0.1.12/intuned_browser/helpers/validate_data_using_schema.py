from copy import deepcopy
from typing import Any

from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import BaseModel

from intuned_browser.helpers.types import Attachment
from intuned_browser.helpers.types import ValidationError


def _inject_attachment_type(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Inject the attachment type definition into the schema.

    Converts any property with "type": "attachment" to use a $ref to the attachment definition.
    Also ensures the attachment definition exists in the schema's $defs.

    Args:
        schema: The JSON schema to modify

    Returns:
        Modified schema with attachment type support
    """
    # Deep copy to avoid modifying the original schema
    schema = deepcopy(schema)

    # Get the attachment schema from the Pydantic model
    attachment_json_schema = Attachment.model_json_schema()

    # Ensure $defs exist in the schema
    if "$defs" not in schema:
        schema["$defs"] = {}

    # If the attachment schema has $defs, we need to move them to the root level
    # and update references accordingly
    if "$defs" in attachment_json_schema:
        # Move $defs to root level $defs with a prefix to avoid conflicts
        for def_name, def_schema in attachment_json_schema["$defs"].items():
            schema["$defs"][f"Attachment_{def_name}"] = def_schema

        # Update references in the attachment schema from #/$defs/X to #/$defs/Attachment_X
        def update_refs(node: Any) -> Any:
            if isinstance(node, dict):
                if "$ref" in node and node["$ref"].startswith("#/$defs/"):
                    ref_name = node["$ref"].split("/")[-1]
                    return {"$ref": f"#/$defs/Attachment_{ref_name}"}
                return {key: update_refs(value) for key, value in node.items()}
            elif isinstance(node, list):
                return [update_refs(item) for item in node]
            return node

        attachment_definition = update_refs(attachment_json_schema)
        # Remove $defs from the attachment definition as they're now at root level
        if "$defs" in attachment_definition:
            del attachment_definition["$defs"]
    else:
        attachment_definition = attachment_json_schema

    # Set the attachment definition
    schema["$defs"]["attachment"] = attachment_definition

    # Recursively find and replace "type": "attachment" with $ref
    def replace_attachment_type(node: Any) -> Any:
        if isinstance(node, dict):
            node_type = node.get("type")
            # If this node has "type": "attachment" (case-insensitive), replace it with a $ref
            if isinstance(node_type, str) and node_type.lower() == "attachment":
                return {"$ref": "#/$defs/attachment"}
            # If this node has "type": ["attachment", ...], convert to oneOf
            elif isinstance(node_type, list):
                # Check if any type in the list is "attachment" (case-insensitive)
                has_attachment = any(isinstance(t, str) and t.lower() == "attachment" for t in node_type)
                if has_attachment:
                    one_of_schemas = []
                    for type_item in node_type:
                        if isinstance(type_item, str) and type_item.lower() == "attachment":
                            one_of_schemas.append({"$ref": "#/$defs/attachment"})
                        else:
                            one_of_schemas.append({"type": type_item})

                    new_node = {key: value for key, value in node.items() if key != "type"}
                    new_node["oneOf"] = one_of_schemas
                    return new_node
            # Otherwise, recursively process all values
            return {key: replace_attachment_type(value) for key, value in node.items()}
        elif isinstance(node, list):
            return [replace_attachment_type(item) for item in node]
        return node

    schema = replace_attachment_type(schema)

    return schema


def _convert_pydantic_to_dict(data: Any) -> Any:
    if isinstance(data, BaseModel):
        # Convert Pydantic model to dict, excluding None values for optional fields
        return _convert_pydantic_to_dict(data.model_dump(mode="json", exclude_none=False))
    elif isinstance(data, dict):
        return {key: _convert_pydantic_to_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_pydantic_to_dict(item) for item in data]
    else:
        return data


def _resolve_schema(schema: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    """Resolve $ref and schema combinators to get actual schema of a field."""
    if not isinstance(schema, dict):
        return schema

    # Handle $ref
    if "$ref" in schema:
        ref_path = schema["$ref"]
        if ref_path.startswith("#/definitions/"):
            def_name = ref_path.split("/")[-1]
            definitions = root_schema.get("definitions", {})
            return definitions.get(def_name, schema)
        elif ref_path.startswith("#/$defs/"):
            def_name = ref_path.split("/")[-1]
            defs = root_schema.get("$defs", {})
            return defs.get(def_name, schema)

    # Handle oneOf/anyOf - find the object schema (not null)
    for combinator in ["oneOf", "anyOf"]:
        if combinator in schema:
            for option in schema[combinator]:
                resolved = _resolve_schema(option, root_schema)
                if resolved.get("type") == "object":
                    return resolved

    return schema


def _remove_none_from_optional_fields(data: Any, schema: dict[str, Any], root_schema: dict[str, Any]) -> Any:
    """Recursively remove None from non-required fields."""
    if isinstance(data, dict) and isinstance(schema, dict):
        # Resolve schema first (handle $ref, oneOf, etc.)
        resolved_schema = _resolve_schema(schema, root_schema)

        required_fields = set(resolved_schema.get("required", []))
        properties = resolved_schema.get("properties", {})

        cleaned = {}
        for key, value in data.items():
            field_schema = properties.get(key, {})

            if key in required_fields:
                cleaned[key] = _remove_none_from_optional_fields(value, field_schema, root_schema)
            elif value is not None:
                cleaned[key] = _remove_none_from_optional_fields(value, field_schema, root_schema)

        return cleaned

    elif isinstance(data, list):
        items_schema = schema.get("items", {})
        return [_remove_none_from_optional_fields(item, items_schema, root_schema) for item in data if item is not None]

    else:
        return data


# Export for testing
__all__ = ["validate_data_using_schema", "_inject_attachment_type", "_convert_pydantic_to_dict"]


def validate_data_using_schema(data: dict[str, Any] | list[dict[str, Any]], schema: dict[str, Any]):
    """
    Validates data against a JSON schema using the AJV validator.
    This function can validate any given data against a given schema. It supports validating custom data types such as the [Attachment](../type-references/Attachment) type.

    Args:
        data (dict[str, Any] | list[dict[str, Any]]): The data to validate. Can be a single data object or an array of data objects.
        schema (dict[str, Any]): JSON schema object defining validation rules

    Returns:
        None: Returns nothing if validation passes, raises ValidationError if it fails
    Raises:
        ValidationError: If validation fails
    Examples:
        ```python Basic Validation
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import validate_data_using_schema
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            upload_data = {
                "file": {
                    "file_name": "documents/report.pdf",
                    "bucket": "my-bucket",
                    "region": "us-east-1",
                    "key": "documents/report.pdf",
                    "endpoint": None,
                    "suggested_file_name": "Monthly Report.pdf",
                    "file_type": "document"
                },
                "name": "Test File Upload"
            }

            upload_schema = {
                "type": "object",
                "required": ["file", "name"],
                "properties": {
                    "file": {"type": "attachment"},
                    "name": {"type": "string"}
                }
            }

            validate_data_using_schema(upload_data, upload_schema)
            # Validation passes with Attachment type
            print("Validation passed")
            return "Validation passed"
        ```

        ```python Invalid Data Validation
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import validate_data_using_schema
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            user_data = {
                "name": "John Doe",
                "email": "john@example.com",
            }

            user_schema = {
                "type": "object",
                "required": ["name", "email", "age"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "number", "minimum": 0}
                }
            }

            validate_data_using_schema(user_data, user_schema)  # this will throw
            # Validation fails, throws ValidationError
            print("Never reached")
            return "Never reached"
        ```
    """
    try:
        # Convert any Pydantic model instances (like Attachment) to dicts first
        data = _convert_pydantic_to_dict(data)
        transformed_schema = _inject_attachment_type(schema)
        cleaned_data = _remove_none_from_optional_fields(data, transformed_schema, transformed_schema)

        validator = Draft7Validator(transformed_schema)
        errors = list(validator.iter_errors(cleaned_data))

        if errors:
            error_messages = []
            for error in errors:
                # Convert deque path to a readable string
                if error.path:
                    path_str = ".".join(str(p) for p in error.path)
                else:
                    path_str = "root"
                error_messages.append(f"  - {path_str}: {error.message}")

            full_message = "Validation failed with {} error(s):\n{}".format(len(errors), "\n".join(error_messages))

            raise ValidationError(full_message, data)

    except JsonSchemaValidationError as e:
        raise ValidationError(f"Validation failed: {e.message}", data) from e
