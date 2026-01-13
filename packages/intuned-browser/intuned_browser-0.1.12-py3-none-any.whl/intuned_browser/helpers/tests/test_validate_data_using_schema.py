import logging
from typing import Any

import pytest

from intuned_browser import validate_data_using_schema
from intuned_browser.helpers.types import Attachment
from intuned_browser.helpers.types import AttachmentType
from intuned_browser.helpers.types import ValidationError


@pytest.mark.asyncio
async def test_validate_data_using_schema_valid() -> None:
    """Test validation with valid data."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    data: dict[str, Any] = {
        "name": "John Doe",
        "age": 30,
        "extra_field": "allowed",
    }

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_invalid() -> None:
    """Test validation with invalid data (missing required field)."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    invalid_data: dict[str, Any] = {"name": "John Doe"}  # Missing required 'age' field

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Validation failed with" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_list() -> None:
    """Test validation with list of valid objects."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }

    data: list[dict[str, Any]] = [
        {"name": "John Doe", "age": 30, "extra": "field"},
        {"name": "Jane Doe", "age": 25, "other": "value"},
    ]

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_list_invalid() -> None:
    """Test validation with list containing invalid object."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }

    invalid_data: list[dict[str, Any]] = [
        {"name": "John Doe", "age": 30},
        {"name": "Jane Doe", "age": "25"},  # age should be integer, not string
    ]

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    logging.debug(f"exc_info: {exc_info}")
    assert "Validation failed with" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_type() -> None:
    """Test validation with Attachment custom type."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Valid data that matches Attachment structure
    valid_data: dict[str, Any] = {
        "file": {
            "file_name": "documents/report.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "documents/report.pdf",
            "endpoint": None,
            "suggested_file_name": "Monthly Report.pdf",
            "file_type": "document",
        },
        "name": "Test File Upload",
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_type_invalid() -> None:
    """Test validation with invalid Attachment data."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Invalid data - missing required Attachment fields
    invalid_data: dict[str, Any] = {
        "file": {
            "file_name": "documents/report.pdf",
            # Missing required fields: bucket, region, suggested_file_name
        },
        "name": "Test File Upload",
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Validation failed with" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_minimal_fields() -> None:
    """Test validation with Attachment containing only required fields."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
        },
        "required": ["file"],
    }

    # Valid data with only required fields
    valid_data: dict[str, Any] = {
        "file": {
            "file_name": "report.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/report.pdf",
            "suggested_file_name": "Report.pdf",
        },
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_array() -> None:
    """Test validation with array of Attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "attachments": {
                "type": "array",
                "items": {"type": "attachment"},
            },
        },
        "required": ["attachments"],
    }

    # Valid data with array of attachments
    valid_data: dict[str, Any] = {
        "attachments": [
            {
                "file_name": "doc1.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/doc1.pdf",
                "suggested_file_name": "Document 1.pdf",
                "endpoint": None,
                "file_type": "document",
            },
            {
                "file_name": "doc2.pdf",
                "bucket": "my-bucket",
                "region": "us-west-2",
                "key": "files/doc2.pdf",
                "suggested_file_name": "Document 2.pdf",
            },
        ],
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_array_invalid() -> None:
    """Test validation with array containing invalid Attachment."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "attachments": {
                "type": "array",
                "items": {"type": "attachment"},
            },
        },
        "required": ["attachments"],
    }

    # Invalid data - second attachment missing required fields
    invalid_data: dict[str, Any] = {
        "attachments": [
            {
                "file_name": "doc1.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/doc1.pdf",
                "suggested_file_name": "Document 1.pdf",
            },
            {
                "file_name": "doc2.pdf",
                # Missing bucket, region, key, suggested_file_name
            },
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Validation failed with" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_empty_array() -> None:
    """Test validation with empty array of Attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "attachments": {
                "type": "array",
                "items": {"type": "attachment"},
            },
        },
        "required": ["attachments"],
    }

    # Valid data with empty array
    valid_data: dict[str, Any] = {
        "attachments": [],
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_optional_attachment() -> None:
    """Test validation with optional Attachment field."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
        "required": ["name"],  # file is optional
    }

    # Valid data without the optional attachment field
    valid_data: dict[str, Any] = {
        "name": "Test Without File",
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_multiple_attachments() -> None:
    """Test validation with multiple Attachment fields."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "primary_file": {"type": "attachment"},
            "backup_file": {"type": "attachment"},
            "title": {"type": "string"},
        },
        "required": ["primary_file", "title"],
    }

    # Valid data with multiple attachments
    valid_data: dict[str, Any] = {
        "primary_file": {
            "file_name": "main.pdf",
            "bucket": "primary-bucket",
            "region": "us-east-1",
            "key": "files/main.pdf",
            "suggested_file_name": "Main Document.pdf",
        },
        "backup_file": {
            "file_name": "backup.pdf",
            "bucket": "backup-bucket",
            "region": "us-west-2",
            "key": "files/backup.pdf",
            "suggested_file_name": "Backup Document.pdf",
        },
        "title": "Important Documents",
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_wrong_field_type() -> None:
    """Test validation with Attachment having wrong field type."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
        },
        "required": ["file"],
    }

    # Invalid data - bucket should be string, not integer
    invalid_data: dict[str, Any] = {
        "file": {
            "file_name": "report.pdf",
            "bucket": 12345,  # Should be string
            "region": "us-east-1",
            "key": "files/report.pdf",
            "suggested_file_name": "Report.pdf",
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Validation failed with" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_with_endpoint() -> None:
    """Test validation with Attachment having custom endpoint."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
        },
        "required": ["file"],
    }

    # Valid data with custom endpoint (e.g., for R2/custom S3)
    valid_data: dict[str, Any] = {
        "file": {
            "file_name": "report.pdf",
            "bucket": "my-bucket",
            "region": "auto",
            "key": "files/report.pdf",
            "suggested_file_name": "Report.pdf",
            "endpoint": "https://custom-s3.example.com",
            "file_type": "document",
        },
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_nullable() -> None:
    """Test validation with nullable attachment type (can be attachment or null)."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": ["attachment", "null"]},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Valid data with attachment
    valid_data_with_attachment: dict[str, Any] = {
        "file": {
            "file_name": "report.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/report.pdf",
            "suggested_file_name": "Report.pdf",
        },
        "name": "Test With File",
    }
    validate_data_using_schema(valid_data_with_attachment, schema)

    # Valid data with null
    valid_data_with_null: dict[str, Any] = {
        "file": None,
        "name": "Test Without File",
    }
    validate_data_using_schema(valid_data_with_null, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_nullable_invalid() -> None:
    """Test validation with nullable attachment type receiving invalid value."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": ["attachment", "null"]},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Invalid data - wrong type (string instead of attachment or null)
    invalid_data: dict[str, Any] = {
        "file": "not-an-attachment",
        "name": "Test",
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Validation failed with" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_filters_nested_empty_values() -> None:
    """Test that nested empty values are filtered before validation."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "email": {"type": "string"},  # Optional
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "notes": {"type": "string"},  # Optional
                        },
                    },
                },
                "required": ["name", "age"],
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},  # Optional
                    },
                    "required": ["title"],
                },
            },
        },
        "required": ["user", "items"],
    }

    # Data with nested empty values
    data_with_nested_empty: dict[str, Any] = {
        "user": {
            "name": "John Doe",
            "age": 30,
            "email": "",  # Empty string - should be filtered
            "metadata": {
                "notes": None,  # None - should be filtered
            },
        },
        "items": [
            {"title": "Item 1", "description": ""},  # Empty description - should be filtered
            {"title": "Item 2", "description": "   "},  # Whitespace - should be filtered
        ],
    }

    # Should pass validation because nested empty values are filtered
    validate_data_using_schema(data_with_nested_empty, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_empty_values_in_arrays() -> None:
    """Test that empty values in arrays are filtered before validation."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "string"},  # Optional
            },
            "required": ["name"],
        },
    }

    # Array with items containing empty values
    data_with_empty_in_array: list[dict[str, Any]] = [
        {"name": "Item 1", "value": ""},  # Empty value - should be filtered
        {"name": "Item 2", "value": None},  # None - should be filtered
        {"name": "Item 3"},  # No empty value
    ]

    # Should pass validation because empty values are filtered
    validate_data_using_schema(data_with_empty_in_array, schema)


@pytest.mark.asyncio
async def test_existing_nullable_optional_is_valid() -> None:
    """Test that existing nullable optional fields are valid."""
    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
            },
        },
    }

    data = {"name": None}

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_capital_attachment_type() -> None:
    """Test validation with Attachment type using capital 'A'."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "Attachment"},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Valid data that matches Attachment structure
    valid_data: dict[str, Any] = {
        "file": {
            "file_name": "documents/report.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "documents/report.pdf",
            "endpoint": None,
            "suggested_file_name": "Monthly Report.pdf",
            "file_type": "document",
        },
        "name": "Test File Upload",
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_capital_attachment_comprehensive() -> None:
    """Comprehensive test for capital Attachment with various type combinations."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            # Single required Attachment
            "required_file": {"type": "Attachment"},
            # Optional Attachment (not in required)
            "optional_file": {"type": "Attachment"},
            # Nullable Attachment (can be Attachment or null)
            "nullable_file": {"type": ["Attachment", "null"]},
            # Array of Attachments
            "files_array": {
                "type": "array",
                "items": {"type": "Attachment"},
            },
            # Union of 3 types (Attachment, string, or null)
            "flexible_field": {"type": ["Attachment", "string", "null"]},
        },
        "required": ["required_file", "nullable_file", "files_array", "flexible_field"],
    }

    # Test data with all variations
    valid_data: dict[str, Any] = {
        # Required attachment present
        "required_file": {
            "file_name": "required.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/required.pdf",
            "suggested_file_name": "Required.pdf",
        },
        # Optional attachment not provided (valid)
        # Nullable attachment set to null
        "nullable_file": None,
        # Array with multiple attachments
        "files_array": [
            {
                "file_name": "file1.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/file1.pdf",
                "suggested_file_name": "File 1.pdf",
            },
            {
                "file_name": "file2.pdf",
                "bucket": "my-bucket",
                "region": "us-west-2",
                "key": "files/file2.pdf",
                "suggested_file_name": "File 2.pdf",
            },
        ],
        # Flexible field as string
        "flexible_field": "just a string",
    }

    validate_data_using_schema(valid_data, schema)

    # Test with flexible_field as Attachment
    valid_data_with_attachment: dict[str, Any] = {
        "required_file": {
            "file_name": "required.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/required.pdf",
            "suggested_file_name": "Required.pdf",
        },
        "nullable_file": {
            "file_name": "nullable.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/nullable.pdf",
            "suggested_file_name": "Nullable.pdf",
        },
        "files_array": [],  # Empty array is valid
        "flexible_field": {
            "file_name": "flexible.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/flexible.pdf",
            "suggested_file_name": "Flexible.pdf",
        },
    }

    validate_data_using_schema(valid_data_with_attachment, schema)

    # Test with flexible_field as null
    valid_data_with_null: dict[str, Any] = {
        "required_file": {
            "file_name": "required.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/required.pdf",
            "suggested_file_name": "Required.pdf",
        },
        "nullable_file": None,
        "files_array": [],
        "flexible_field": None,
    }

    validate_data_using_schema(valid_data_with_null, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_nested_attachment_in_objects() -> None:
    """Test validation with Attachment fields inside nested objects within arrays."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "documents": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "metadata": {
                            "type": "object",
                            "properties": {
                                "file": {"type": "Attachment"},
                                "name": {"type": "string"},
                            },
                            "required": ["file", "name"],
                        },
                    },
                    "required": ["metadata"],
                },
            },
        },
        "required": ["documents"],
    }

    valid_data: dict[str, Any] = {
        "documents": [
            {
                "metadata": {
                    "file": {
                        "file_name": "doc1.pdf",
                        "bucket": "my-bucket",
                        "region": "us-east-1",
                        "key": "files/doc1.pdf",
                        "suggested_file_name": "Document 1.pdf",
                    },
                    "name": "First Document",
                },
            },
            {
                "metadata": {
                    "file": {
                        "file_name": "doc2.pdf",
                        "bucket": "my-bucket",
                        "region": "us-west-2",
                        "key": "files/doc2.pdf",
                        "suggested_file_name": "Document 2.pdf",
                    },
                    "name": "Second Document",
                },
            },
        ],
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_deeply_nested_attachment() -> None:
    """Test validation with Attachments 3-4 levels deep with mixed required/optional fields."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "level1": {
                "type": "object",
                "properties": {
                    "level2": {
                        "type": "object",
                        "properties": {
                            "level3": {
                                "type": "object",
                                "properties": {
                                    "required_file": {"type": "Attachment"},
                                    "optional_file": {"type": "Attachment"},
                                    "level4": {
                                        "type": "object",
                                        "properties": {
                                            "deep_file": {"type": "ATTACHMENT"},
                                        },
                                    },
                                },
                                "required": ["required_file"],
                            },
                        },
                        "required": ["level3"],
                    },
                },
                "required": ["level2"],
            },
        },
        "required": ["level1"],
    }

    valid_data: dict[str, Any] = {
        "level1": {
            "level2": {
                "level3": {
                    "required_file": {
                        "file_name": "level3.pdf",
                        "bucket": "my-bucket",
                        "region": "us-east-1",
                        "key": "files/level3.pdf",
                        "suggested_file_name": "Level 3.pdf",
                    },
                    # optional_file omitted
                    "level4": {
                        "deep_file": {
                            "file_name": "level4.pdf",
                            "bucket": "my-bucket",
                            "region": "us-east-1",
                            "key": "files/level4.pdf",
                            "suggested_file_name": "Level 4.pdf",
                        },
                    },
                },
            },
        },
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_with_oneof() -> None:
    """Test validation with oneOf combinator containing Attachment type."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "content": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "type": {"const": "text"},
                            "value": {"type": "string"},
                        },
                        "required": ["type", "value"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "type": {"const": "file"},
                            "file": {"type": "Attachment"},
                        },
                        "required": ["type", "file"],
                    },
                ],
            },
        },
        "required": ["content"],
    }

    # Test with text content
    valid_text_data: dict[str, Any] = {
        "content": {
            "type": "text",
            "value": "Some text content",
        },
    }
    validate_data_using_schema(valid_text_data, schema)

    # Test with file content
    valid_file_data: dict[str, Any] = {
        "content": {
            "type": "file",
            "file": {
                "file_name": "document.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/document.pdf",
                "suggested_file_name": "Document.pdf",
            },
        },
    }
    validate_data_using_schema(valid_file_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_with_anyof() -> None:
    """Test validation with anyOf combinator containing Attachment type."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "resource": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "Attachment"},
                ],
            },
        },
        "required": ["resource"],
    }

    valid_string_data: dict[str, Any] = {
        "resource": "https://example.com/file.pdf",
    }
    validate_data_using_schema(valid_string_data, schema)

    valid_attachment_data: dict[str, Any] = {
        "resource": {
            "file_name": "file.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/file.pdf",
            "suggested_file_name": "File.pdf",
        },
    }
    validate_data_using_schema(valid_attachment_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_array_with_constraints() -> None:
    """Test validation with min/max items constraints on Attachment arrays."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {"type": "Attachment"},
                "minItems": 1,
                "maxItems": 3,
            },
        },
        "required": ["files"],
    }

    valid_data: dict[str, Any] = {
        "files": [
            {
                "file_name": "file1.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/file1.pdf",
                "suggested_file_name": "File 1.pdf",
            },
            {
                "file_name": "file2.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/file2.pdf",
                "suggested_file_name": "File 2.pdf",
            },
        ],
    }
    validate_data_using_schema(valid_data, schema)

    invalid_data_empty: dict[str, Any] = {
        "files": [],
    }
    with pytest.raises(ValidationError):
        validate_data_using_schema(invalid_data_empty, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_cross_field_dependencies() -> None:
    """Test validation with cross-field dependencies involving Attachment."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "has_attachment": {"type": "boolean"},
            "file": {"type": ["Attachment", "null"]},
        },
        "required": ["has_attachment", "file"],
        "if": {
            "properties": {
                "has_attachment": {"const": True},
            },
        },
        "then": {
            "properties": {
                "file": {"type": "Attachment"},
            },
        },
    }

    valid_with_file: dict[str, Any] = {
        "has_attachment": True,
        "file": {
            "file_name": "document.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/document.pdf",
            "suggested_file_name": "Document.pdf",
        },
    }
    validate_data_using_schema(valid_with_file, schema)

    valid_without_file: dict[str, Any] = {
        "has_attachment": False,
        "file": None,
    }
    validate_data_using_schema(valid_without_file, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_in_definitions() -> None:
    """Test validation with Attachment referenced through $ref in definitions."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "document": {"$ref": "#/definitions/Document"},
        },
        "required": ["document"],
        "definitions": {
            "Document": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "file": {"type": "Attachment"},
                    "attachments": {
                        "type": "array",
                        "items": {"type": "ATTACHMENT"},
                    },
                },
                "required": ["title", "file"],
            },
        },
    }

    valid_data: dict[str, Any] = {
        "document": {
            "title": "Important Document",
            "file": {
                "file_name": "main.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/main.pdf",
                "suggested_file_name": "Main.pdf",
            },
            "attachments": [
                {
                    "file_name": "attachment1.pdf",
                    "bucket": "my-bucket",
                    "region": "us-east-1",
                    "key": "files/attachment1.pdf",
                    "suggested_file_name": "Attachment 1.pdf",
                },
            ],
        },
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_error_messages() -> None:
    """Test that error messages are helpful for Attachment validation failures."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "Attachment"},
        },
        "required": ["file"],
    }

    invalid_data: dict[str, Any] = {
        "file": {
            "file_name": "incomplete.pdf",
            # Missing bucket, region, key, suggested_file_name
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)

    error_message = str(exc_info.value)
    assert "Validation failed" in error_message
    # The error should mention the attachment validation failure
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_mixed_casing_in_array() -> None:
    """Test that array with mixed case Attachment types works correctly."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "field1": {"type": ["Attachment", "string", "null"]},
            "field2": {"type": ["ATTACHMENT", "number", "null"]},
            "field3": {"type": ["attachment", "boolean", "null"]},
            "field4": {"type": ["AtTaChMeNt", "null"]},
        },
        "required": ["field1", "field2", "field3", "field4"],
    }

    valid_data: dict[str, Any] = {
        "field1": "string value",
        "field2": 42,
        "field3": True,
        "field4": None,
    }
    validate_data_using_schema(valid_data, schema)

    # Test with actual Attachments
    valid_with_attachments: dict[str, Any] = {
        "field1": {
            "file_name": "file1.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/file1.pdf",
            "suggested_file_name": "File 1.pdf",
        },
        "field2": {
            "file_name": "file2.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/file2.pdf",
            "suggested_file_name": "File 2.pdf",
        },
        "field3": {
            "file_name": "file3.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/file3.pdf",
            "suggested_file_name": "File 3.pdf",
        },
        "field4": {
            "file_name": "file4.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/file4.pdf",
            "suggested_file_name": "File 4.pdf",
        },
    }
    validate_data_using_schema(valid_with_attachments, schema)


@pytest.mark.asyncio
async def test_pydantic_model_with_attachment() -> None:
    """Test validation with pydantic model with attachment."""
    data = {
        "name": "P-R2-B3RX",
        "manufacturer": "GracePorts®",
        "description": "PANEL INTERFACE CONNECTOR WITH RJ45; UL TYPE 4, NO OUTLET",
        "price": 176.0,
        "product_url": "https://www.mc-mc.com/Product/graceports-p-r2-b3rx",
        "part_number": "P-R2-B3RX",
        "upc": "842864101475",
        "images": [
            "https://res.cloudinary.com/mcrey/image/upload/f_auto,q_auto/w_350/v1655877314/Products/GRENPR2B3RX/IMG_50387534_GracePorts_P_R2_B3RX_1.jpg",
            "https://res.cloudinary.com/mcrey/image/upload/f_auto,q_auto/w_100/v1655877314/Products/GRENPR2B3RX/IMG_50387534_GracePorts_P_R2_B3RX_1.jpg",
            "https://res.cloudinary.com/mcrey/image/upload/f_auto,q_auto/w_100/v1655877306/Products/GRENPR2B3RX/IMG_50387535_GracePorts_P_R2_B3RX.jpg",
        ],
        "attributes": {
            "Brand": "GracePorts®",
            "Type": "Bulkhead",
            "Mounting Type": "Panel",
            "Voltage Rating": "30 VDC",
            "Connector Type": "Cat 5e Ethernet RJ45 F/F",
            "Housing Material": "Plastic",
            "Dimensions": "3.15 in L x 1.65 in W x 1.72 in H",
        },
        "features": [
            "Extension cable interfaces consist of fully shielded cable assemblies panel-mounted to the housing allowing a direct and cost effective method of interfacing to computers, printers, modems and networks",
            "Bulkhead interface method permits standard cable connections on both the front and the rear of the graceport unit",
            "Connections are made to and from the interface by way of user supplied computer cable assemblies, printed circuit assembly",
            "Low-profile circuit board interfaces simplify installation where backplane clearance is limited",
            "The compact design features a data connector on the front and terminal block connections on the rear for easy wiring",
            "Low voltage (data), limited to 30 VDC, high voltage supply (for computer use only)",
            "1 port",
            "6 point, NEMA 12/4, IP65, cast alloy base enclosure",
        ],
        "normally_stocked": True,
        "docs": [
            Attachment(
                file_name="123e1829-300b-4c34-9b58-19fa764c2e6b/SPEC_48757191_SpecificationSheet.pdf",
                bucket="intuned-poc",
                region="us-west-2",
                key="123e1829-300b-4c34-9b58-19fa764c2e6b/SPEC_48757191_SpecificationSheet.pdf",
                endpoint=None,
                suggested_file_name="SPEC_48757191_SpecificationSheet.pdf",
                file_type=AttachmentType.DOCUMENT,
            )
        ],
        "spec_sheet": Attachment(
            file_name="123e1829-300b-4c34-9b58-19fa764c2e6b/SPEC_48757191_SpecificationSheet.pdf",
            bucket="intuned-poc",
            region="us-west-2",
            key="123e1829-300b-4c34-9b58-19fa764c2e6b/SPEC_48757191_SpecificationSheet.pdf",
            endpoint=None,
            suggested_file_name="SPEC_48757191_SpecificationSheet.pdf",
            file_type=AttachmentType.DOCUMENT,
        ),
    }
    schema = {
        "type": "object",
        "description": "Industrial interface connector product with technical specifications and optional documentation",
        "properties": {
            "name": {"type": "string", "description": "Product name/model number"},
            "manufacturer": {
                "type": "string",
                "description": "Product manufacturer (GracePorts)",
            },
            "description": {
                "type": "string",
                "description": "Detailed product description",
            },
            "price": {"type": "number", "description": "Product price in USD"},
            "product_url": {
                "type": "string",
                "description": "URL of the product details page",
            },
            "part_number": {"type": "string", "description": "Manufacturer part number"},
            "upc": {"type": "string", "description": "Universal Product Code"},
            "images": {
                "type": "array",
                "description": "Product images including main image and thumbnails",
            },
            "attributes": {
                "type": "object",
                "description": "Technical specifications and product attributes",
            },
            "features": {
                "type": "array",
                "description": "Product features and functionality descriptions",
            },
            "normally_stocked": {
                "type": "boolean",
                "description": "Whether the product is normally stocked (true) or special order item (false)",
            },
            "docs": {
                "type": "array",
                "items": {"type": "Attachment"},
                "description": "Optional downloadable documents like installation manuals",
            },
            "spec_sheet": {
                "type": "Attachment",
                "description": "Optional product specification sheet document",
            },
        },
        "required": [
            "name",
            "manufacturer",
            "description",
            "price",
            "product_url",
            "part_number",
            "upc",
            "images",
            "attributes",
            "features",
            "normally_stocked",
        ],
    }

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_pydantic_model_array_of_attachments() -> None:
    """Test validation with array of Attachment pydantic model instances."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "documents": {
                "type": "array",
                "items": {"type": "Attachment"},
            },
        },
        "required": ["title", "documents"],
    }

    # Data with array of Attachment instances
    data: dict[str, Any] = {
        "title": "Project Documents",
        "documents": [
            Attachment(
                file_name="doc1.pdf",
                bucket="my-bucket",
                region="us-east-1",
                key="files/doc1.pdf",
                endpoint=None,
                suggested_file_name="Document 1.pdf",
                file_type=AttachmentType.DOCUMENT,
            ),
            Attachment(
                file_name="doc2.pdf",
                bucket="another-bucket",
                region="us-west-2",
                key="files/doc2.pdf",
                endpoint="https://custom-s3.example.com",
                suggested_file_name="Document 2.pdf",
                file_type=AttachmentType.DOCUMENT,
            ),
            Attachment(
                file_name="doc3.pdf",
                bucket="third-bucket",
                region="eu-west-1",
                key="files/doc3.pdf",
                suggested_file_name="Document 3.pdf",
                file_type=AttachmentType.DOCUMENT,
            ),
        ],
    }

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_pydantic_model_mixed_with_dicts_nested() -> None:
    """Test validation with deeply nested structure mixing dicts and Attachment pydantic models."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "project": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "section_name": {"type": "string"},
                                "primary_file": {"type": "Attachment"},
                                "backup_files": {
                                    "type": "array",
                                    "items": {"type": "ATTACHMENT"},
                                },
                                "metadata": {
                                    "type": "object",
                                    "properties": {
                                        "description": {"type": "string"},
                                        "optional_attachment": {"type": ["attachment", "null"]},
                                    },
                                },
                            },
                            "required": ["section_name", "primary_file"],
                        },
                    },
                },
                "required": ["name", "sections"],
            },
            "archived_files": {
                "type": "array",
                "items": {"type": "Attachment"},
            },
        },
        "required": ["project"],
    }

    # Complex nested data mixing dicts and Attachment instances
    data: dict[str, Any] = {
        "project": {
            "name": "Complex Project",
            "sections": [
                {
                    "section_name": "Introduction",
                    "primary_file": Attachment(
                        file_name="intro.pdf",
                        bucket="project-bucket",
                        region="us-east-1",
                        key="sections/intro.pdf",
                        suggested_file_name="Introduction.pdf",
                        file_type=AttachmentType.DOCUMENT,
                    ),
                    "backup_files": [
                        Attachment(
                            file_name="intro_backup1.pdf",
                            bucket="backup-bucket",
                            region="us-west-2",
                            key="backups/intro_backup1.pdf",
                            suggested_file_name="Intro Backup 1.pdf",
                        ),
                    ],
                    "metadata": {
                        "description": "Project introduction section",
                        "optional_attachment": Attachment(
                            file_name="intro_notes.pdf",
                            bucket="notes-bucket",
                            region="us-east-1",
                            key="notes/intro_notes.pdf",
                            suggested_file_name="Intro Notes.pdf",
                        ),
                    },
                },
                {
                    "section_name": "Conclusion",
                    "primary_file": Attachment(
                        file_name="conclusion.pdf",
                        bucket="project-bucket",
                        region="us-east-1",
                        key="sections/conclusion.pdf",
                        suggested_file_name="Conclusion.pdf",
                    ),
                    "backup_files": [],
                    "metadata": {
                        "description": "Project conclusion section",
                        "optional_attachment": None,
                    },
                },
            ],
        },
        "archived_files": [
            Attachment(
                file_name="archive1.pdf",
                bucket="archive-bucket",
                region="us-east-1",
                key="archives/archive1.pdf",
                suggested_file_name="Archive 1.pdf",
                endpoint="https://archive.s3.example.com",
            ),
            Attachment(
                file_name="archive2.pdf",
                bucket="archive-bucket",
                region="us-east-1",
                key="archives/archive2.pdf",
                suggested_file_name="Archive 2.pdf",
            ),
        ],
    }

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_error_message_multiple_errors() -> None:
    """Test that error messages collect and format multiple errors correctly."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string"},
        },
        "required": ["name", "age", "email"],
    }

    invalid_data: dict[str, Any] = {
        "name": 123,  # Wrong type - should be string
        "age": "not-a-number",  # Wrong type - should be integer
        # Missing required 'email' field
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)

    error_message = str(exc_info.value)
    # Should indicate multiple errors
    assert "Validation failed with" in error_message
    assert "error(s):" in error_message
    # Should list multiple errors (check for bullet points or field names)
    assert error_message.count("-") >= 2 or error_message.count("error") >= 2
    # Should contain field names
    assert "name" in error_message or "age" in error_message or "email" in error_message
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_error_message_nested_field() -> None:
    """Test that error messages correctly format nested field paths."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
                "required": ["name", "age"],
            },
        },
        "required": ["user"],
    }

    invalid_data: dict[str, Any] = {
        "user": {
            "name": "John Doe",
            # Missing required 'age' field
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)

    error_message = str(exc_info.value)
    # Should contain nested field path
    assert "user" in error_message or "age" in error_message
    assert "Validation failed with" in error_message
    assert exc_info.value.data == invalid_data
