"""Unit tests for s3_delete_object operation."""

import pytest
from moto import mock_s3
import boto3
import json

from s3_mcp.s3.operations import delete_object_operation
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
    bucket_name = "test-delete-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    # Create test objects
    test_objects = [
        ("file1.txt", b"content1"),
        ("file2.txt", b"content2"),
        ("folder/file3.txt", b"content3"),
    ]

    for key, body in test_objects:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=body)

    return bucket_name


@pytest.fixture
def versioned_bucket(s3_client):
    """Create a versioned test bucket with objects."""
    bucket_name = "test-versioned-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    # Enable versioning
    s3_client.put_bucket_versioning(
        Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
    )

    # Create test object
    s3_client.put_object(Bucket=bucket_name, Key="versioned-file.txt", Body=b"version 1")

    # Update to create version 2
    response = s3_client.put_object(Bucket=bucket_name, Key="versioned-file.txt", Body=b"version 2")

    version_id = response["VersionId"]

    return bucket_name, version_id


@pytest.mark.asyncio
async def test_delete_object(test_bucket_with_objects, s3_client, aws_credentials):
    """Test deleting an object from a bucket."""
    # Verify object exists
    objects = s3_client.list_objects_v2(Bucket=test_bucket_with_objects)
    assert "Contents" in objects
    initial_count = len(objects["Contents"])

    # Delete object
    result = await delete_object_operation(
        bucket_name=test_bucket_with_objects, key="file1.txt", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["success"] is True
    assert data["bucket"] == test_bucket_with_objects
    assert data["key"] == "file1.txt"

    # Verify object was deleted
    objects_after = s3_client.list_objects_v2(Bucket=test_bucket_with_objects)
    if "Contents" in objects_after:
        assert len(objects_after["Contents"]) == initial_count - 1
        assert not any(obj["Key"] == "file1.txt" for obj in objects_after["Contents"])


@pytest.mark.asyncio
async def test_delete_nested_object(test_bucket_with_objects, s3_client, aws_credentials):
    """Test deleting an object with nested path."""
    result = await delete_object_operation(
        bucket_name=test_bucket_with_objects,
        key="folder/file3.txt",
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert data["success"] is True
    assert data["key"] == "folder/file3.txt"

    # Verify deletion
    try:
        s3_client.head_object(Bucket=test_bucket_with_objects, Key="folder/file3.txt")
        pytest.fail("Object should have been deleted")
    except Exception as e:
        # Expected - object should not exist
        assert "404" in str(e) or "Not Found" in str(e) or "NoSuchKey" in str(e)


@pytest.mark.asyncio
async def test_delete_nonexistent_object(test_bucket_with_objects, aws_credentials):
    """Test deleting a non-existent object (idempotent)."""
    result = await delete_object_operation(
        bucket_name=test_bucket_with_objects,
        key="nonexistent-file.txt",
        response_format=ResponseFormat.JSON,
    )

    # Delete operation is idempotent in S3
    # Deleting non-existent object succeeds without error
    data = json.loads(result)
    assert data["success"] is True


@pytest.mark.asyncio
async def test_delete_from_versioned_bucket(versioned_bucket, s3_client, aws_credentials):
    """Test deleting object from versioned bucket creates delete marker."""
    bucket_name, version_id = versioned_bucket

    result = await delete_object_operation(
        bucket_name=bucket_name, key="versioned-file.txt", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["success"] is True
    # In versioned bucket, delete creates a delete marker
    assert data.get("delete_marker") is True or data.get("version_id") is not None


@pytest.mark.asyncio
async def test_delete_specific_version(versioned_bucket, s3_client, aws_credentials):
    """Test deleting a specific version from versioned bucket."""
    bucket_name, version_id = versioned_bucket

    result = await delete_object_operation(
        bucket_name=bucket_name,
        key="versioned-file.txt",
        version_id=version_id,
        response_format=ResponseFormat.JSON,
    )

    data = json.loads(result)
    assert data["success"] is True
    # When deleting specific version, no delete marker is created
    assert data.get("version_id") == version_id


@pytest.mark.asyncio
async def test_markdown_format(test_bucket_with_objects, aws_credentials):
    """Test markdown output format."""
    result = await delete_object_operation(
        bucket_name=test_bucket_with_objects,
        key="file2.txt",
        response_format=ResponseFormat.MARKDOWN,
    )

    assert isinstance(result, str)
    assert test_bucket_with_objects in result
    assert "file2.txt" in result
    assert "deleted" in result.lower() or "success" in result.lower()


@pytest.mark.asyncio
async def test_delete_nonexistent_bucket(aws_credentials):
    """Test deleting from non-existent bucket."""
    result = await delete_object_operation(
        bucket_name="nonexistent-bucket", key="file.txt", response_format=ResponseFormat.MARKDOWN
    )

    # Should return error message
    assert "failed" in result.lower() or "error" in result.lower()


@pytest.mark.asyncio
async def test_multiple_deletes_same_object(test_bucket_with_objects, aws_credentials):
    """Test that deleting same object multiple times is idempotent."""
    key = "file1.txt"

    # First delete
    result1 = await delete_object_operation(
        bucket_name=test_bucket_with_objects, key=key, response_format=ResponseFormat.JSON
    )

    data1 = json.loads(result1)
    assert data1["success"] is True

    # Second delete (object already deleted)
    result2 = await delete_object_operation(
        bucket_name=test_bucket_with_objects, key=key, response_format=ResponseFormat.JSON
    )

    data2 = json.loads(result2)
    # Should still succeed (idempotent operation)
    assert data2["success"] is True


@pytest.mark.asyncio
async def test_delete_all_objects_in_bucket(test_bucket_with_objects, s3_client, aws_credentials):
    """Test deleting all objects in a bucket."""
    # List all objects
    response = s3_client.list_objects_v2(Bucket=test_bucket_with_objects)
    objects = response.get("Contents", [])

    # Delete all objects
    for obj in objects:
        result = await delete_object_operation(
            bucket_name=test_bucket_with_objects,
            key=obj["Key"],
            response_format=ResponseFormat.JSON,
        )

        data = json.loads(result)
        assert data["success"] is True

    # Verify bucket is empty
    response_after = s3_client.list_objects_v2(Bucket=test_bucket_with_objects)
    assert "Contents" not in response_after or len(response_after.get("Contents", [])) == 0


@pytest.mark.asyncio
async def test_delete_response_structure(test_bucket_with_objects, aws_credentials):
    """Test that delete response has all required fields."""
    result = await delete_object_operation(
        bucket_name=test_bucket_with_objects, key="file1.txt", response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert "success" in data
    assert "bucket" in data
    assert "key" in data
    assert isinstance(data["success"], bool)
    assert isinstance(data["bucket"], str)
    assert isinstance(data["key"], str)


@pytest.mark.asyncio
async def test_delete_object_with_special_characters(s3_client, aws_credentials):
    """Test deleting object with special characters in key."""
    bucket_name = "test-special-chars-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    # Create object with special characters
    special_key = "folder/file with spaces & special!chars.txt"
    s3_client.put_object(Bucket=bucket_name, Key=special_key, Body=b"content")

    result = await delete_object_operation(
        bucket_name=bucket_name, key=special_key, response_format=ResponseFormat.JSON
    )

    data = json.loads(result)
    assert data["success"] is True
    assert data["key"] == special_key
