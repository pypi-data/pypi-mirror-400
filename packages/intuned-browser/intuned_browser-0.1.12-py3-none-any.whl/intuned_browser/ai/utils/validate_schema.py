from typing import Any

from jsonschema import Draft7Validator
from pydantic import BaseModel


def validate_schema(data_schema: type[BaseModel] | dict[str, Any]) -> dict[str, Any]:
    """
    Validate and convert a Pydantic model or dictionary to a JSON schema dict.

    Args:
        data_schema: Either a Pydantic BaseModel class or a dictionary representing a JSON schema

    Returns:
        A dictionary representing the JSON schema
    """
    # Handle Pydantic BaseModel class
    if isinstance(data_schema, type) and issubclass(data_schema, BaseModel):
        # It's a Pydantic model class - convert to JSON schema
        return data_schema.model_json_schema()

    # Handle dictionary
    if isinstance(data_schema, dict):
        # Validate it's a proper schema dict
        schema_type = data_schema.get("type")
        if schema_type not in ["string", "number", "integer", "boolean", "array", "object"]:
            raise ValueError(f"Invalid or missing schema type: {schema_type}")
        return data_schema

    raise ValueError("Data schema must be a Pydantic BaseModel class or a dictionary.")


def validate_tool_call_schema(*, instance: Any, schema: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Validate an instance against a JSON schema and collect all validation errors.

    Unlike the standard jsonschema.validate function, this function collects all
    validation errors instead of raising an exception on the first error.

    Args:
        instance: The instance to validate
        schema: The JSON schema to validate against

    Returns:
        A list of validation errors, each containing:
        - path: The JSON path to the invalid property
        - message: The validation error message
        - value: The invalid value
        - schema_path: The path in the schema that was violated
    """
    validator = Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(instance):
        # Format the path as a string (e.g., "root.items[0].name")
        path_string = ".".join(str(path_part) for path_part in error.path) if error.path else "root"

        # Format the schema path
        schema_path_string = (
            ".".join(str(path_part) for path_part in error.schema_path) if error.schema_path else "schema"
        )

        # Add the error to the list
        errors.append(
            {"path": path_string, "message": error.message, "value": error.instance, "schema_path": schema_path_string}
        )

    return errors


def check_all_types_are_strings(schema: dict[str, Any]) -> bool:
    """
    Check if all types in the schema are strings.

    Args:
        schema: The JSON schema dictionary to check

    Returns:
        True if all types are strings, False otherwise
    """
    schema_type = schema.get("type")

    if schema_type == "string":
        return True
    elif schema_type == "array":
        items = schema.get("items")
        if items is None:
            return True  # No items constraint means it could be strings

        # Handle both single schema and list of schemas
        if isinstance(items, list):
            return all(check_all_types_are_strings(item) for item in items)
        else:
            return check_all_types_are_strings(items)

    elif schema_type == "object":
        properties = schema.get("properties")
        if properties is None:
            return True  # No properties constraint means it could be strings

        return all(check_all_types_are_strings(prop) for prop in properties.values())

    # For number, integer, boolean, or other types
    return False
