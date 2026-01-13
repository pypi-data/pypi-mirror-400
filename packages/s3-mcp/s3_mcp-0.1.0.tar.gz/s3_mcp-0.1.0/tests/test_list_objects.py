"""Unit tests for s3_list_objects operation."""

import pytest
from moto import mock_s3
import boto3
import json

from s3_mcp.s3.operations import list_objects_operation
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
    """Create a test bucket with sample objects."""
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    # Create test objects
    test_objects = [
        ("file1.txt", b"content1", "text/plain"),
        ("file2.txt", b"content2", "text/plain"),
        ("images/photo1.jpg", b"image1", "image/jpeg"),
        ("images/photo2.jpg", b"image2", "image/jpeg"),
        ("logs/2024/jan.log", b"log1", "text/plain"),
        ("logs/2024/feb.log", b"log2", "text/plain"),
    ]

    for key, body, content_type in test_objects:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=body, ContentType=content_type)

    return bucket_name


@pytest.mark.asyncio
async def test_list_all_objects(test_bucket, aws_credentials):
    """Test listing all objects in a bucket."""
    result = await list_objects_operation(
        bucket_name=test_bucket, response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["bucket"] == test_bucket
    assert data["prefix"] == ""
    assert data["total_count"] == 6  # All 6 test objects
    assert len(data["objects"]) == 6
    assert not data["has_more"]


@pytest.mark.asyncio
async def test_list_with_prefix(test_bucket, aws_credentials):
    """Test listing objects with prefix filter."""
    result = await list_objects_operation(
        bucket_name=test_bucket, prefix="images/", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["prefix"] == "images/"
    assert data["total_count"] == 2
    assert all("images/" in obj["Key"] for obj in data["objects"])


@pytest.mark.asyncio
async def test_list_with_limit(test_bucket, aws_credentials):
    """Test pagination with limit."""
    result = await list_objects_operation(
        bucket_name=test_bucket, limit=3, response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["total_count"] == 3
    assert len(data["objects"]) == 3


@pytest.mark.asyncio
async def test_list_with_continuation(test_bucket, s3_client, aws_credentials):
    """Test pagination with continuation token."""
    # First request with limit
    result1 = await list_objects_operation(
        bucket_name=test_bucket, limit=3, response_format=ResponseFormat.JSON
    )

    data1 = json.loads(result1)

    # If there are more results, test continuation
    if data1.get("has_more"):
        result2 = await list_objects_operation(
            bucket_name=test_bucket,
            limit=3,
            continuation_token=data1["next_continuation_token"],
            response_format=ResponseFormat.JSON,
        )

        data2 = json.loads(result2)
        # Ensure we got different objects
        keys1 = {obj["Key"] for obj in data1["objects"]}
        keys2 = {obj["Key"] for obj in data2["objects"]}
        assert keys1.isdisjoint(keys2)


@pytest.mark.asyncio
async def test_list_markdown_format(test_bucket, aws_credentials):
    """Test markdown output format."""
    result = await list_objects_operation(
        bucket_name=test_bucket, prefix="images/", response_format=ResponseFormat.MARKDOWN
    )

    assert isinstance(result, str)
    assert "test-bucket" in result
    assert "images/" in result
    assert "photo1.jpg" in result or "photo2.jpg" in result


@pytest.mark.asyncio
async def test_empty_bucket(s3_client, aws_credentials):
    """Test listing objects in an empty bucket."""
    bucket_name = "empty-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    result = await list_objects_operation(
        bucket_name=bucket_name, response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["total_count"] == 0
    assert data["objects"] == []


@pytest.mark.asyncio
async def test_nonexistent_bucket(aws_credentials):
    """Test error handling for non-existent bucket."""
    result = await list_objects_operation(
        bucket_name="nonexistent-bucket", response_format=ResponseFormat.MARKDOWN
    )

    # Should return error message
    assert "failed" in result.lower() or "error" in result.lower()


@pytest.mark.asyncio
async def test_prefix_with_no_matches(test_bucket, aws_credentials):
    """Test prefix that matches no objects."""
    result = await list_objects_operation(
        bucket_name=test_bucket, prefix="nonexistent-prefix/", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["total_count"] == 0
    assert data["objects"] == []


@pytest.mark.asyncio
async def test_object_metadata_structure(test_bucket, aws_credentials):
    """Test that object metadata has all required fields."""
    result = await list_objects_operation(
        bucket_name=test_bucket, limit=1, response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert len(data["objects"]) == 1

    obj = data["objects"][0]
    assert "Key" in obj
    assert "Size" in obj
    assert "LastModified" in obj
    assert "ETag" in obj
    assert isinstance(obj["Key"], str)
    assert isinstance(obj["Size"], int)


@pytest.mark.asyncio
async def test_limit_validation(test_bucket, aws_credentials):
    """Test that limit is properly validated and capped."""
    # Test with limit > 1000 (should be capped to 1000)
    result = await list_objects_operation(
        bucket_name=test_bucket, limit=2000, response_format=ResponseFormat.JSON
    )

    # Should not error, limit should be capped
    data = json.loads(result)
    assert "objects" in data

    # Test with limit < 1 (should be set to 1)
    result = await list_objects_operation(
        bucket_name=test_bucket, limit=0, response_format=ResponseFormat.JSON
    )

    # Should not error, limit should be set to at least 1
    data = json.loads(result)
    assert "objects" in data


@pytest.mark.asyncio
async def test_nested_prefix(test_bucket, aws_credentials):
    """Test listing with nested prefix."""
    result = await list_objects_operation(
        bucket_name=test_bucket, prefix="logs/2024/", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["prefix"] == "logs/2024/"
    assert data["total_count"] == 2
    assert all("logs/2024/" in obj["Key"] for obj in data["objects"])
