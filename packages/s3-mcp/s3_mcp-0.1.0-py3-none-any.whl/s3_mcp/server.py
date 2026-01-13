"""FastMCP server for AWS S3 operations."""

from typing import Optional, Dict
from fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .s3.operations import (
    list_objects_operation,
    get_object_operation,
    put_object_operation,
    delete_object_operation,
)
from .s3.utils import ResponseFormat


# Initialize FastMCP server with correct naming convention
mcp = FastMCP("s3_mcp")


# Pydantic models for input validation


class S3ListObjectsInput(BaseModel):
    """Input model for listing S3 objects."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    bucket_name: str = Field(
        ...,
        description="S3 bucket name (e.g., 'my-data-bucket')",
        min_length=3,
        max_length=63,
        pattern=r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
    )
    prefix: str = Field(
        default="", description="Object key prefix to filter results (e.g., 'logs/2024/')"
    )
    limit: int = Field(
        default=20, description="Maximum number of objects to return (1-1000)", ge=1, le=1000
    )
    continuation_token: Optional[str] = Field(
        default=None, description="Pagination token from previous response"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Response format: 'markdown' or 'json'"
    )


class S3GetObjectInput(BaseModel):
    """Input model for generating presigned GET URL."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    bucket_name: str = Field(
        ...,
        description="S3 bucket name",
        min_length=3,
        max_length=63,
        pattern=r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
    )
    key: str = Field(
        ...,
        description="Object key (path within bucket, e.g., 'data/file.txt')",
        min_length=1,
        max_length=1024,
    )
    expires_in: int = Field(
        default=3600,
        description="URL expiration in seconds (default: 3600 = 1 hour, max: 604800 = 7 days)",
        ge=1,
        le=604800,
    )
    response_content_disposition: Optional[str] = Field(
        default=None,
        description="Override Content-Disposition header (e.g., 'attachment; filename=file.txt')",
    )
    response_content_type: Optional[str] = Field(
        default=None, description="Override Content-Type header (e.g., 'application/json')"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Response format: 'markdown' or 'json'"
    )


class S3PutObjectInput(BaseModel):
    """Input model for generating presigned PUT URL."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    bucket_name: str = Field(
        ...,
        description="S3 bucket name",
        min_length=3,
        max_length=63,
        pattern=r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
    )
    key: str = Field(
        ...,
        description="Object key (destination path, e.g., 'uploads/image.png')",
        min_length=1,
        max_length=1024,
    )
    expires_in: int = Field(
        default=3600,
        description="URL expiration in seconds (default: 3600 = 1 hour, max: 604800 = 7 days)",
        ge=1,
        le=604800,
    )
    content_type: Optional[str] = Field(
        default=None, description="MIME type of the object (e.g., 'image/png', 'application/pdf')"
    )
    server_side_encryption: Optional[str] = Field(
        default=None, description="Server-side encryption algorithm ('AES256' or 'aws:kms')"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None, description="Custom metadata as key-value pairs"
    )
    acl: Optional[str] = Field(
        default=None, description="Canned ACL ('private', 'public-read', 'public-read-write', etc.)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Response format: 'markdown' or 'json'"
    )

    @field_validator("server_side_encryption")
    @classmethod
    def validate_encryption(cls, v: Optional[str]) -> Optional[str]:
        """Validate encryption algorithm."""
        if v is not None and v not in ["AES256", "aws:kms"]:
            raise ValueError("server_side_encryption must be 'AES256' or 'aws:kms'")
        return v

    @field_validator("acl")
    @classmethod
    def validate_acl(cls, v: Optional[str]) -> Optional[str]:
        """Validate ACL value."""
        valid_acls = [
            "private",
            "public-read",
            "public-read-write",
            "authenticated-read",
            "aws-exec-read",
            "bucket-owner-read",
            "bucket-owner-full-control",
        ]
        if v is not None and v not in valid_acls:
            raise ValueError(f"acl must be one of: {', '.join(valid_acls)}")
        return v


class S3DeleteObjectInput(BaseModel):
    """Input model for deleting S3 object."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    bucket_name: str = Field(
        ...,
        description="S3 bucket name",
        min_length=3,
        max_length=63,
        pattern=r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
    )
    key: str = Field(
        ...,
        description="Object key to delete (e.g., 'old-files/deprecated.txt')",
        min_length=1,
        max_length=1024,
    )
    version_id: Optional[str] = Field(
        default=None, description="Specific version to delete (for versioned buckets)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Response format: 'markdown' or 'json'"
    )


# Tool registrations with proper annotations


@mcp.tool(
    name="s3_list_objects",
    annotations={
        "title": "List S3 Bucket Objects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def s3_list_objects(
    bucket_name: str,
    prefix: str = "",
    limit: int = 20,
    continuation_token: Optional[str] = None,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """
    List objects in an S3 bucket with optional prefix filtering and pagination.

    This tool retrieves a list of objects (files) from an S3 bucket. Use it to:
    - Browse bucket contents
    - Find specific files by prefix
    - Paginate through large result sets

    Args:
        bucket_name: S3 bucket name (3-63 characters, lowercase, numbers, hyphens, dots)
        prefix: Filter objects by key prefix (e.g., 'logs/2024/' to find all logs from 2024)
        limit: Max objects to return per request (1-1000, default: 20)
        continuation_token: Token from previous response to get next page
        response_format: Output format - 'markdown' (default) or 'json'

    Returns:
        Formatted list of objects with key, size, last modified date, and storage class.
        If more results exist, includes continuation token for next page.

    Error Handling:
        - Bucket not found: Returns error with suggestion to verify bucket name
        - Access denied: Returns error with IAM permission suggestions
        - Invalid input: Returns validation error with specific field issues
    """
    # Validate input using Pydantic model
    validated_input = S3ListObjectsInput(
        bucket_name=bucket_name,
        prefix=prefix,
        limit=limit,
        continuation_token=continuation_token,
        response_format=response_format,
    )

    return await list_objects_operation(
        bucket_name=validated_input.bucket_name,
        prefix=validated_input.prefix,
        limit=validated_input.limit,
        continuation_token=validated_input.continuation_token,
        response_format=validated_input.response_format,
    )


@mcp.tool(
    name="s3_get_object",
    annotations={
        "title": "Generate Presigned URL for Download",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def s3_get_object(
    bucket_name: str,
    key: str,
    expires_in: int = 3600,
    response_content_disposition: Optional[str] = None,
    response_content_type: Optional[str] = None,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """
    Generate a time-limited presigned URL for downloading an S3 object.

    This tool creates a secure URL that allows downloading an object without AWS credentials.
    The URL is time-limited and automatically expires.

    Use cases:
    - Share files with users who don't have AWS access
    - Download objects in browser or HTTP client
    - Integrate S3 downloads in applications without AWS SDK

    Args:
        bucket_name: S3 bucket name
        key: Object key (path within bucket, e.g., 'data/report.pdf')
        expires_in: URL expiration in seconds (1-604800, default: 3600 = 1 hour)
        response_content_disposition: Override Content-Disposition (e.g., 'attachment; filename=report.pdf')
        response_content_type: Override Content-Type (e.g., 'application/pdf')
        response_format: Output format - 'markdown' (default) or 'json'

    Returns:
        Presigned URL with expiration details and usage example (curl command).

    Security Notes:
        - URLs are time-limited (max 7 days, default 1 hour)
        - Anyone with the URL can download during validity period
        - URLs cannot be revoked before expiration
        - Use shorter expiration for sensitive data

    Error Handling:
        - Bucket/object not found: Returns error with verification suggestions
        - Access denied: Returns error with IAM permission guidance
        - Invalid parameters: Returns validation error with field details
    """
    validated_input = S3GetObjectInput(
        bucket_name=bucket_name,
        key=key,
        expires_in=expires_in,
        response_content_disposition=response_content_disposition,
        response_content_type=response_content_type,
        response_format=response_format,
    )

    return await get_object_operation(
        bucket_name=validated_input.bucket_name,
        key=validated_input.key,
        expires_in=validated_input.expires_in,
        response_content_disposition=validated_input.response_content_disposition,
        response_content_type=validated_input.response_content_type,
        response_format=validated_input.response_format,
    )


@mcp.tool(
    name="s3_put_object",
    annotations={
        "title": "Generate Presigned URL for Upload",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def s3_put_object(
    bucket_name: str,
    key: str,
    expires_in: int = 3600,
    content_type: Optional[str] = None,
    server_side_encryption: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    acl: Optional[str] = None,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """
    Generate a time-limited presigned URL for uploading an object to S3.

    This tool creates a secure URL that allows uploading a file without AWS credentials.
    The URL is time-limited and enforces specified upload parameters (encryption, ACL, etc.).

    Use cases:
    - Allow users to upload files directly to S3 from browsers
    - Integrate uploads in applications without AWS SDK
    - Enforce upload policies (encryption, content type, etc.)

    Args:
        bucket_name: S3 bucket name
        key: Destination object key (path, e.g., 'uploads/document.pdf')
        expires_in: URL expiration in seconds (1-604800, default: 3600 = 1 hour)
        content_type: MIME type (e.g., 'image/png', 'application/pdf')
        server_side_encryption: Encryption algorithm ('AES256' or 'aws:kms')
        metadata: Custom metadata as key-value pairs
        acl: Access control ('private', 'public-read', 'public-read-write', etc.)
        response_format: Output format - 'markdown' (default) or 'json'

    Returns:
        Presigned URL with required headers and curl usage example.
        The response includes all headers that must be sent with the PUT request.

    Security Notes:
        - URLs are time-limited and scoped to specific object key
        - Enforce encryption with server_side_encryption parameter
        - Use 'private' ACL unless public access required
        - Consider bucket policies that require encryption

    Error Handling:
        - Bucket not found: Returns error with bucket verification guidance
        - Access denied: Returns error with IAM permission details
        - Invalid parameters: Returns validation errors with corrections
    """
    validated_input = S3PutObjectInput(
        bucket_name=bucket_name,
        key=key,
        expires_in=expires_in,
        content_type=content_type,
        server_side_encryption=server_side_encryption,
        metadata=metadata,
        acl=acl,
        response_format=response_format,
    )

    return await put_object_operation(
        bucket_name=validated_input.bucket_name,
        key=validated_input.key,
        expires_in=validated_input.expires_in,
        content_type=validated_input.content_type,
        server_side_encryption=validated_input.server_side_encryption,
        metadata=validated_input.metadata,
        acl=validated_input.acl,
        response_format=validated_input.response_format,
    )


@mcp.tool(
    name="s3_delete_object",
    annotations={
        "title": "Delete S3 Object",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def s3_delete_object(
    bucket_name: str,
    key: str,
    version_id: Optional[str] = None,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """
    Delete an object from an S3 bucket.

    ⚠️ WARNING: This is a DESTRUCTIVE operation. Deleted objects cannot be recovered
    unless versioning is enabled on the bucket.

    Use this tool to:
    - Remove unwanted or obsolete files
    - Clean up temporary uploads
    - Delete specific versions in versioned buckets

    Args:
        bucket_name: S3 bucket name
        key: Object key to delete (e.g., 'temp/old-file.txt')
        version_id: Specific version to delete (for versioned buckets only)
        response_format: Output format - 'markdown' (default) or 'json'

    Returns:
        Deletion confirmation with version information if applicable.
        For versioned buckets, indicates if a delete marker was created.

    Behavior:
        - Non-versioned buckets: Object is permanently deleted
        - Versioned buckets: Delete marker created (object can be recovered)
        - With version_id: Specific version permanently deleted

    Security Notes:
        - Requires s3:DeleteObject IAM permission
        - For versioned buckets, may need s3:DeleteObjectVersion
        - Consider enabling MFA Delete for added protection
        - Operation cannot be undone for non-versioned buckets

    Error Handling:
        - Bucket/object not found: Returns error (idempotent - safe to retry)
        - Access denied: Returns error with IAM permission guidance
        - Invalid parameters: Returns validation error with corrections
    """
    validated_input = S3DeleteObjectInput(
        bucket_name=bucket_name, key=key, version_id=version_id, response_format=response_format
    )

    return await delete_object_operation(
        bucket_name=validated_input.bucket_name,
        key=validated_input.key,
        version_id=validated_input.version_id,
        response_format=validated_input.response_format,
    )
