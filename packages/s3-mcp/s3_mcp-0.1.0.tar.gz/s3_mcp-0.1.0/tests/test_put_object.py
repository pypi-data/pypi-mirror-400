"""Unit tests for s3_put_object operation."""

import pytest
from moto import mock_s3
import boto3
import json

from s3_mcp.s3.operations import put_object_operation
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
def test_bucket(s3_client):
    """Create a test bucket."""
    bucket_name = "test-upload-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    return bucket_name


@pytest.mark.asyncio
async def test_generate_presigned_upload_url(test_bucket, aws_credentials):
    """Test generating a presigned PUT URL."""
    result = await put_object_operation(
        bucket_name=test_bucket, key="uploads/file.txt", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["operation"] == "PUT"
    assert data["bucket"] == test_bucket
    assert data["key"] == "uploads/file.txt"
    assert "presigned_url" in data
    assert "expires_in" in data
    assert "expires_at" in data
    assert isinstance(data["presigned_url"], str)
    assert data["presigned_url"].startswith("https://")


@pytest.mark.asyncio
async def test_custom_expiration(test_bucket, aws_credentials):
    """Test presigned URL with custom expiration time."""
    custom_expiry = 7200  # 2 hours

    result = await put_object_operation(
        bucket_name=test_bucket,
        key="file.txt",
        expires_in=custom_expiry,
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert data["expires_in"] == custom_expiry


@pytest.mark.asyncio
async def test_with_content_type(test_bucket, aws_credentials):
    """Test presigned URL with Content-Type header."""
    result = await put_object_operation(
        bucket_name=test_bucket,
        key="document.pdf",
        content_type="application/pdf",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert "presigned_url" in data
    assert "required_headers" in data
    assert data["required_headers"]["Content-Type"] == "application/pdf"


@pytest.mark.asyncio
async def test_with_encryption_aes256(test_bucket, aws_credentials):
    """Test presigned URL with AES256 encryption."""
    result = await put_object_operation(
        bucket_name=test_bucket,
        key="encrypted-file.txt",
        server_side_encryption="AES256",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert "presigned_url" in data
    assert "required_headers" in data
    assert data["required_headers"]["x-amz-server-side-encryption"] == "AES256"


@pytest.mark.asyncio
async def test_with_encryption_kms(test_bucket, aws_credentials):
    """Test presigned URL with KMS encryption."""
    result = await put_object_operation(
        bucket_name=test_bucket,
        key="encrypted-file.txt",
        server_side_encryption="aws:kms",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert "presigned_url" in data
    assert "required_headers" in data
    assert data["required_headers"]["x-amz-server-side-encryption"] == "aws:kms"


@pytest.mark.asyncio
async def test_with_metadata(test_bucket, aws_credentials):
    """Test presigned URL with custom metadata."""
    metadata = {"user": "test-user", "environment": "testing"}

    result = await put_object_operation(
        bucket_name=test_bucket,
        key="file-with-metadata.txt",
        metadata=metadata,
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert "presigned_url" in data
    # Metadata is handled by S3 client automatically


@pytest.mark.asyncio
async def test_with_acl_private(test_bucket, aws_credentials):
    """Test presigned URL with private ACL."""
    result = await put_object_operation(
        bucket_name=test_bucket,
        key="private-file.txt",
        acl="private",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert "presigned_url" in data


@pytest.mark.asyncio
async def test_with_acl_public_read(test_bucket, aws_credentials):
    """Test presigned URL with public-read ACL."""
    result = await put_object_operation(
        bucket_name=test_bucket,
        key="public-file.txt",
        acl="public-read",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert "presigned_url" in data


@pytest.mark.asyncio
async def test_combined_parameters(test_bucket, aws_credentials):
    """Test presigned URL with multiple parameters combined."""
    result = await put_object_operation(
        bucket_name=test_bucket,
        key="uploads/document.pdf",
        content_type="application/pdf",
        server_side_encryption="AES256",
        metadata={"author": "test", "version": "1.0"},
        acl="private",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert "presigned_url" in data
    assert "required_headers" in data
    assert data["required_headers"]["Content-Type"] == "application/pdf"
    assert data["required_headers"]["x-amz-server-side-encryption"] == "AES256"


@pytest.mark.asyncio
async def test_markdown_format(test_bucket, aws_credentials):
    """Test markdown output format."""
    result = await put_object_operation(
        bucket_name=test_bucket,
        key="file.txt",
        content_type="text/plain",
        response_format=ResponseFormat.MARKDOWN,
    )

    assert isinstance(result, str)
    assert test_bucket in result
    assert "file.txt" in result
    assert "https://" in result
    assert "Upload URL" in result or "upload" in result.lower()


@pytest.mark.asyncio
async def test_nonexistent_bucket(aws_credentials):
    """Test generating URL for non-existent bucket."""
    result = await put_object_operation(
        bucket_name="nonexistent-bucket", key="file.txt", response_format=ResponseFormat.JSON
    )

    # S3 allows presigned URLs for non-existent buckets
    # The check happens when the URL is used
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_expiration_validation(test_bucket, aws_credentials):
    """Test that expiration is properly validated and capped."""
    # Test with expiration > max (should be capped)
    result = await put_object_operation(
        bucket_name=test_bucket,
        key="file.txt",
        expires_in=700000,  # > 604800 (7 days)
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    # Should be capped to max (604800 or configured max)
    assert data["expires_in"] <= 604800

    # Test with expiration < 1 (should be set to 1)
    result = await put_object_operation(
        bucket_name=test_bucket, key="file.txt", expires_in=0, response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    # Should be at least 1 second
    assert data["expires_in"] >= 1


@pytest.mark.asyncio
async def test_nested_object_path(test_bucket, aws_credentials):
    """Test presigned URL for object with nested path."""
    nested_key = "uploads/2024/january/file.txt"

    result = await put_object_operation(
        bucket_name=test_bucket, key=nested_key, response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["key"] == nested_key
    assert "presigned_url" in data


@pytest.mark.asyncio
async def test_url_contains_signature(test_bucket, aws_credentials):
    """Test that generated URL contains AWS signature parameters."""
    result = await put_object_operation(
        bucket_name=test_bucket, key="file.txt", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    url = data["presigned_url"]

    # Check for AWS signature query parameters
    assert "X-Amz-Algorithm" in url or "AWSAccessKeyId" in url
    assert "Signature" in url or "X-Amz-Signature" in url


@pytest.mark.asyncio
async def test_different_content_types(test_bucket, aws_credentials):
    """Test presigned URLs with different content types."""
    content_types = {
        "document.pdf": "application/pdf",
        "image.png": "image/png",
        "data.json": "application/json",
        "video.mp4": "video/mp4",
    }

    for key, content_type in content_types.items():
        result = await put_object_operation(
            bucket_name=test_bucket,
            key=key,
            content_type=content_type,
            response_format=ResponseFormat.JSON,
        )

        data = json.loads(result)
        assert data["key"] == key
        assert "required_headers" in data
        assert data["required_headers"]["Content-Type"] == content_type


@pytest.mark.asyncio
async def test_no_required_headers_when_none_specified(test_bucket, aws_credentials):
    """Test that required_headers is None when no headers specified."""
    result = await put_object_operation(
        bucket_name=test_bucket, key="file.txt", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    # When no content_type or encryption specified, required_headers should be None or empty
    assert data.get("required_headers") is None or data["required_headers"] == {}
