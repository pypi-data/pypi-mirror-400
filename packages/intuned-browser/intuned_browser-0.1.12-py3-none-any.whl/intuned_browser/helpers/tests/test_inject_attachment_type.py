"""
Comprehensive tests for the _inject_attachment_type function.

Tests cover:
- Basic attachment injection
- Nested object attachment injection
- Array attachment injection
- Complex mixed scenarios
- Edge cases
- Attachment definition structure
"""

from typing import Any

import pytest

from intuned_browser.helpers.validate_data_using_schema import _inject_attachment_type


@pytest.mark.asyncio
async def test_replace_simple_attachment_type_with_ref() -> None:
    """Test that simple attachment type is replaced with $ref."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
    }

    result = _inject_attachment_type(schema)

    # Should have $defs with attachment definition
    assert "$defs" in result
    assert "attachment" in result["$defs"]
    assert result["$defs"]["attachment"]["type"] == "object"

    # Should replace attachment type with $ref
    assert result["properties"]["file"] == {"$ref": "#/$defs/attachment"}
    # Other properties should remain unchanged
    assert result["properties"]["name"] == {"type": "string"}


@pytest.mark.asyncio
async def test_handle_multiple_attachment_fields_in_same_object() -> None:
    """Test handling of multiple attachment fields in the same object."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "document": {"type": "attachment"},
            "image": {"type": "attachment"},
            "video": {"type": "attachment"},
            "title": {"type": "string"},
            "count": {"type": "integer"},
        },
        "required": ["document", "title"],
    }

    result = _inject_attachment_type(schema)

    # All attachment types should be replaced
    assert result["properties"]["document"] == {"$ref": "#/$defs/attachment"}
    assert result["properties"]["image"] == {"$ref": "#/$defs/attachment"}
    assert result["properties"]["video"] == {"$ref": "#/$defs/attachment"}

    # Non-attachment properties should remain unchanged
    assert result["properties"]["title"] == {"type": "string"}
    assert result["properties"]["count"] == {"type": "integer"}

    # Required array should remain unchanged
    assert result["required"] == ["document", "title"]

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_replace_attachments_in_deeply_nested_objects() -> None:
    """Test replacing attachments in deeply nested object structures."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "object",
                        "properties": {
                            "avatar": {"type": "attachment"},
                            "resume": {"type": "attachment"},
                            "name": {"type": "string"},
                        },
                    },
                    "settings": {
                        "type": "object",
                        "properties": {
                            "theme": {"type": "string"},
                        },
                    },
                },
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "banner": {"type": "attachment"},
                },
            },
        },
    }

    result = _inject_attachment_type(schema)

    # Check deeply nested attachments are replaced
    assert result["properties"]["user"]["properties"]["profile"]["properties"]["avatar"] == {
        "$ref": "#/$defs/attachment"
    }
    assert result["properties"]["user"]["properties"]["profile"]["properties"]["resume"] == {
        "$ref": "#/$defs/attachment"
    }
    assert result["properties"]["metadata"]["properties"]["banner"] == {"$ref": "#/$defs/attachment"}

    # Non-attachment properties should remain unchanged
    assert result["properties"]["user"]["properties"]["profile"]["properties"]["name"] == {"type": "string"}
    assert result["properties"]["user"]["properties"]["settings"]["properties"]["theme"] == {"type": "string"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_handle_attachments_in_complex_nested_structures() -> None:
    """Test handling attachments in objects with complex nested structures."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "object",
                        "properties": {
                            "primary": {"type": "attachment"},
                            "secondary": {
                                "type": "object",
                                "properties": {
                                    "backup": {"type": "attachment"},
                                    "archive": {"type": "attachment"},
                                },
                            },
                        },
                    },
                },
            },
        },
    }

    result = _inject_attachment_type(schema)

    # All nested attachments should be replaced
    assert result["properties"]["data"]["properties"]["files"]["properties"]["primary"] == {
        "$ref": "#/$defs/attachment"
    }
    assert result["properties"]["data"]["properties"]["files"]["properties"]["secondary"]["properties"]["backup"] == {
        "$ref": "#/$defs/attachment"
    }
    assert result["properties"]["data"]["properties"]["files"]["properties"]["secondary"]["properties"]["archive"] == {
        "$ref": "#/$defs/attachment"
    }

    # Attachment definition should exist
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_replace_attachments_in_array_items() -> None:
    """Test replacing attachments in array items."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "file": {"type": "attachment"},
                "description": {"type": "string"},
            },
        },
    }

    result = _inject_attachment_type(schema)

    # Attachment in array items should be replaced
    assert result["items"]["properties"]["file"] == {"$ref": "#/$defs/attachment"}
    assert result["items"]["properties"]["description"] == {"type": "string"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_handle_arrays_of_arrays_with_attachments() -> None:
    """Test handling arrays of arrays with attachments."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "media": {"type": "attachment"},
                    "caption": {"type": "string"},
                },
            },
        },
    }

    result = _inject_attachment_type(schema)

    # Nested array attachments should be replaced
    assert result["items"]["items"]["properties"]["media"] == {"$ref": "#/$defs/attachment"}
    assert result["items"]["items"]["properties"]["caption"] == {"type": "string"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_handle_object_with_array_of_objects_containing_attachments() -> None:
    """Test handling object with array of objects containing attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "documents": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "attachment"},
                        "metadata": {
                            "type": "object",
                            "properties": {
                                "thumbnail": {"type": "attachment"},
                                "title": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "title": {"type": "string"},
        },
    }

    result = _inject_attachment_type(schema)

    # Array item attachment should be replaced
    assert result["properties"]["documents"]["items"]["properties"]["file"] == {"$ref": "#/$defs/attachment"}
    # Nested object attachment in array should be replaced
    assert result["properties"]["documents"]["items"]["properties"]["metadata"]["properties"]["thumbnail"] == {
        "$ref": "#/$defs/attachment"
    }
    # Non-attachment properties should remain unchanged
    assert result["properties"]["documents"]["items"]["properties"]["metadata"]["properties"]["title"] == {
        "type": "string"
    }
    assert result["properties"]["title"] == {"type": "string"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_handle_oneof_anyof_with_attachments() -> None:
    """Test handling oneOf/anyOf schemas with attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "content": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                        },
                    },
                    {
                        "type": "object",
                        "properties": {
                            "file": {"type": "attachment"},
                        },
                    },
                ],
            },
            "fallback": {
                "anyOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "properties": {
                            "backup": {"type": "attachment"},
                        },
                    },
                ],
            },
        },
    }

    result = _inject_attachment_type(schema)

    # Attachments in oneOf should be replaced
    assert result["properties"]["content"]["oneOf"][0]["properties"]["text"] == {"type": "string"}
    assert result["properties"]["content"]["oneOf"][1]["properties"]["file"] == {"$ref": "#/$defs/attachment"}

    # Attachments in anyOf should be replaced
    assert result["properties"]["fallback"]["anyOf"][0] == {"type": "string"}
    assert result["properties"]["fallback"]["anyOf"][1]["properties"]["backup"] == {"$ref": "#/$defs/attachment"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_handle_allof_with_attachments() -> None:
    """Test handling allOf schemas with attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "allOf": [
            {
                "type": "object",
                "properties": {
                    "base_file": {"type": "attachment"},
                    "id": {"type": "string"},
                },
            },
            {
                "type": "object",
                "properties": {
                    "extended_file": {"type": "attachment"},
                    "metadata": {"type": "object"},
                },
            },
        ],
    }

    result = _inject_attachment_type(schema)

    # Attachments in allOf should be replaced
    assert result["allOf"][0]["properties"]["base_file"] == {"$ref": "#/$defs/attachment"}
    assert result["allOf"][1]["properties"]["extended_file"] == {"$ref": "#/$defs/attachment"}

    # Non-attachment properties should remain unchanged
    assert result["allOf"][0]["properties"]["id"] == {"type": "string"}
    assert result["allOf"][1]["properties"]["metadata"] == {"type": "object"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_handle_schema_without_attachments() -> None:
    """Test handling schema without any attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "active": {"type": "boolean"},
        },
    }

    result = _inject_attachment_type(schema)

    # Schema should remain mostly unchanged except for $defs
    assert result["properties"]["name"] == {"type": "string"}
    assert result["properties"]["age"] == {"type": "integer"}
    assert result["properties"]["active"] == {"type": "boolean"}

    # Should still have $defs with attachment definition (added proactively)
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_not_modify_original_schema_immutability() -> None:
    """Test that the function does not modify the original schema (immutability)."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
    }

    # Deep copy to compare later
    import copy

    original_schema = copy.deepcopy(schema)

    result = _inject_attachment_type(schema)

    # Original schema should be unchanged
    assert schema == original_schema
    assert schema["properties"]["file"] == {"type": "attachment"}
    assert "$defs" not in schema

    # Result should be modified
    assert result["properties"]["file"] == {"$ref": "#/$defs/attachment"}
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_handle_schema_with_existing_defs() -> None:
    """Test handling schema with existing $defs."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "custom_field": {"$ref": "#/$defs/customType"},
        },
        "$defs": {
            "customType": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                },
            },
        },
    }

    result = _inject_attachment_type(schema)

    # Should preserve existing $defs
    assert "customType" in result["$defs"]
    assert result["$defs"]["customType"]["properties"]["value"] == {"type": "string"}

    # Should add attachment definition
    assert "attachment" in result["$defs"]

    # Should replace attachment type
    assert result["properties"]["file"] == {"$ref": "#/$defs/attachment"}

    # Should preserve existing $ref
    assert result["properties"]["custom_field"] == {"$ref": "#/$defs/customType"}


@pytest.mark.asyncio
async def test_handle_schema_with_attachment_in_definitions() -> None:
    """Test handling schema that references definitions with attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "document": {"$ref": "#/$defs/Document"},
        },
        "$defs": {
            "Document": {
                "type": "object",
                "properties": {
                    "file": {"type": "attachment"},
                    "title": {"type": "string"},
                },
            },
        },
    }

    result = _inject_attachment_type(schema)

    # Should preserve the $ref
    assert result["properties"]["document"] == {"$ref": "#/$defs/Document"}

    # Should replace attachment type in the definition
    assert result["$defs"]["Document"]["properties"]["file"] == {"$ref": "#/$defs/attachment"}
    assert result["$defs"]["Document"]["properties"]["title"] == {"type": "string"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_attachment_definition_structure() -> None:
    """Test that the attachment definition has the proper structure."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
        },
    }

    result = _inject_attachment_type(schema)

    # Verify attachment definition structure
    assert "attachment" in result["$defs"]
    assert result["$defs"]["attachment"]["type"] == "object"

    # Check for required Attachment fields in properties
    attachment_props = result["$defs"]["attachment"]["properties"]
    assert "file_name" in attachment_props
    assert "bucket" in attachment_props
    assert "region" in attachment_props
    assert "key" in attachment_props
    assert "suggested_file_name" in attachment_props

    # Check required fields
    assert "required" in result["$defs"]["attachment"]
    required_fields = result["$defs"]["attachment"]["required"]
    assert "file_name" in required_fields
    assert "bucket" in required_fields
    assert "region" in required_fields
    assert "key" in required_fields
    assert "suggested_file_name" in required_fields


@pytest.mark.asyncio
async def test_handle_complex_real_world_schema() -> None:
    """Test handling a complex real-world schema with nested structures and mixed types."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "profile": {
                "type": "object",
                "properties": {
                    "avatar": {"type": "attachment"},
                    "documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "file": {"type": "attachment"},
                                "type": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "settings": {
                "oneOf": [
                    {"type": "null"},
                    {
                        "type": "object",
                        "properties": {
                            "theme": {"type": "string"},
                            "background": {"type": "attachment"},
                        },
                    },
                ],
            },
        },
        "required": ["user_id"],
    }

    result = _inject_attachment_type(schema)

    # All attachments should be replaced
    assert result["properties"]["profile"]["properties"]["avatar"] == {"$ref": "#/$defs/attachment"}
    assert result["properties"]["profile"]["properties"]["documents"]["items"]["properties"]["file"] == {
        "$ref": "#/$defs/attachment"
    }
    assert result["properties"]["settings"]["oneOf"][1]["properties"]["background"] == {"$ref": "#/$defs/attachment"}

    # Non-attachment properties should remain unchanged
    assert result["properties"]["user_id"] == {"type": "string"}
    assert result["properties"]["profile"]["properties"]["documents"]["items"]["properties"]["type"] == {
        "type": "string"
    }
    assert result["properties"]["settings"]["oneOf"][0] == {"type": "null"}
    assert result["properties"]["settings"]["oneOf"][1]["properties"]["theme"] == {"type": "string"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]


@pytest.mark.asyncio
async def test_handle_attachment_with_additional_properties() -> None:
    """Test handling schema with additionalProperties and attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
        },
        "additionalProperties": {
            "type": "object",
            "properties": {
                "extra_file": {"type": "attachment"},
            },
        },
    }

    result = _inject_attachment_type(schema)

    # Attachment in properties should be replaced
    assert result["properties"]["file"] == {"$ref": "#/$defs/attachment"}

    # Attachment in additionalProperties should be replaced
    assert result["additionalProperties"]["properties"]["extra_file"] == {"$ref": "#/$defs/attachment"}

    # Should have attachment definition
    assert "attachment" in result["$defs"]
