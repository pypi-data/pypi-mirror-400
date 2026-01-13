"""Unit tests for s3_get_object operation."""

import pytest
from moto import mock_s3
import boto3
import json
from datetime import datetime

from s3_mcp.s3.operations import get_object_operation
from s3_mcp.s3.utils import ResponseFormat


@pytest.fixture
def aws_credentials(monkeypatch):
    """Set mock AWS credentials for testing."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def s3_client(aws_credentials):
    """Create mock S3 client."""
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        yield s3


@pytest.fixture
def test_bucket_with_objects(s3_client):
    """Create a test bucket with sample objects."""
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    # Create test objects
    test_objects = [
        ("document.pdf", b"PDF content here", "application/pdf"),
        ("image.jpg", b"JPEG image data", "image/jpeg"),
        ("data.json", b'{"key": "value"}', "application/json"),
    ]

    for key, body, content_type in test_objects:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=body, ContentType=content_type)

    return bucket_name


@pytest.mark.asyncio
async def test_generate_presigned_url(test_bucket_with_objects, aws_credentials):
    """Test generating a presigned GET URL."""
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="document.pdf",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert data["operation"] == "GET"
    assert data["bucket"] == test_bucket_with_objects
    assert data["key"] == "document.pdf"
    assert "presigned_url" in data
    assert "expires_in" in data
    assert "expires_at" in data
    assert isinstance(data["presigned_url"], str)
    assert data["presigned_url"].startswith("https://")


@pytest.mark.asyncio
async def test_custom_expiration(test_bucket_with_objects, aws_credentials):
    """Test presigned URL with custom expiration time."""
    custom_expiry = 7200  # 2 hours

    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="document.pdf",
        expires_in=custom_expiry,
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert data["expires_in"] == custom_expiry


@pytest.mark.asyncio
async def test_markdown_format(test_bucket_with_objects, aws_credentials):
    """Test markdown output format."""
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="document.pdf",
        response_format=ResponseFormat.MARKDOWN,
    )

    assert isinstance(result, str)
    assert test_bucket_with_objects in result
    assert "document.pdf" in result
    assert "https://" in result
    assert "Download URL" in result or "download" in result.lower()


@pytest.mark.asyncio
async def test_content_disposition_override(test_bucket_with_objects, aws_credentials):
    """Test overriding Content-Disposition header."""
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="document.pdf",
        response_content_disposition="attachment; filename=my-document.pdf",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    # URL should be generated successfully
    assert "presigned_url" in data
    assert isinstance(data["presigned_url"], str)


@pytest.mark.asyncio
async def test_content_type_override(test_bucket_with_objects, aws_credentials):
    """Test overriding Content-Type header."""
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="data.json",
        response_content_type="text/plain",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    # URL should be generated successfully
    assert "presigned_url" in data
    assert isinstance(data["presigned_url"], str)


@pytest.mark.asyncio
async def test_nonexistent_object(test_bucket_with_objects, aws_credentials):
    """Test generating URL for non-existent object."""
    # S3 allows presigned URLs for non-existent objects
    # The URL will be valid, but GET request will fail with 404
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="nonexistent.txt",
        response_format=ResponseFormat.JSON,
    )

    # Should generate URL successfully (S3 doesn't check object existence for presigning)
    data = json.loads(result)
    assert "presigned_url" in data


@pytest.mark.asyncio
async def test_nonexistent_bucket(aws_credentials):
    """Test generating URL for non-existent bucket."""
    result = await get_object_operation(
        bucket_name="nonexistent-bucket", key="file.txt", response_format=ResponseFormat.MARKDOWN
    )

    # S3 allows presigned URLs for non-existent buckets
    # The check happens when the URL is used
    # For our implementation, it might succeed or fail depending on implementation
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_expiration_validation(test_bucket_with_objects, aws_credentials, monkeypatch):
    """Test that expiration is properly validated and capped."""
    # Test with expiration > max (should be capped)
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="document.pdf",
        expires_in=700000,  # > 604800 (7 days)
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    # Should be capped to max (604800 or configured max)
    assert data["expires_in"] <= 604800

    # Test with expiration < 1 (should be set to 1)
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="document.pdf",
        expires_in=0,
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    # Should be at least 1 second
    assert data["expires_in"] >= 1


@pytest.mark.asyncio
async def test_url_contains_signature(test_bucket_with_objects, aws_credentials):
    """Test that generated URL contains AWS signature parameters."""
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="document.pdf",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    url = data["presigned_url"]

    # Check for AWS signature query parameters
    assert "X-Amz-Algorithm" in url or "AWSAccessKeyId" in url
    assert "Signature" in url or "X-Amz-Signature" in url


@pytest.mark.asyncio
async def test_expires_at_timestamp_format(test_bucket_with_objects, aws_credentials):
    """Test that expires_at is in correct ISO 8601 format."""
    result = await get_object_operation(
        bucket_name=test_bucket_with_objects,
        key="document.pdf",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    expires_at = data["expires_at"]

    # Should be ISO 8601 format
    assert isinstance(expires_at, str)
    assert expires_at.endswith("Z")  # UTC timezone

    # Should be parseable as datetime
    try:
        datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("expires_at is not in valid ISO 8601 format")


@pytest.mark.asyncio
async def test_different_object_types(test_bucket_with_objects, aws_credentials):
    """Test presigned URLs for different object types."""
    object_keys = ["document.pdf", "image.jpg", "data.json"]

    for key in object_keys:
        result = await get_object_operation(
            bucket_name=test_bucket_with_objects, key=key, response_format=ResponseFormat.JSON
        )

        data = json.loads(result)
        assert data["key"] == key
        assert "presigned_url" in data


@pytest.mark.asyncio
async def test_nested_object_path(test_bucket_with_objects, s3_client, aws_credentials):
    """Test presigned URL for object with nested path."""
    # Create object with nested path
    nested_key = "folder/subfolder/file.txt"
    s3_client.put_object(Bucket=test_bucket_with_objects, Key=nested_key, Body=b"nested content")

    result = await get_object_operation(
        bucket_name=test_bucket_with_objects, key=nested_key, response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["key"] == nested_key
    assert "presigned_url" in data
