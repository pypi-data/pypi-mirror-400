"""S3 operations for MCP tools."""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from .client import S3Client
from .utils import (
    ResponseFormat,
    format_object_list_markdown,
    format_object_list_json,
    format_presigned_url_markdown,
    format_presigned_url_json,
    format_delete_response_markdown,
    format_delete_response_json,
    handle_error,
)


# Initialize S3 client (singleton pattern)
_s3_client: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    """Get or create S3 client singleton."""
    global _s3_client
    if _s3_client is None:
        _s3_client = S3Client()
    return _s3_client


async def list_objects_operation(
    bucket_name: str,
    prefix: str = "",
    limit: int = 20,
    continuation_token: Optional[str] = None,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """
    List objects in an S3 bucket.

    Args:
        bucket_name: S3 bucket name
        prefix: Object key prefix to filter results
        limit: Maximum number of objects to return (1-1000)
        continuation_token: Token for pagination
        response_format: Output format (markdown or json)

    Returns:
        Formatted string with object list

    Raises:
        ValueError: If bucket doesn't exist or inputs invalid
        PermissionError: If IAM permissions insufficient
        RuntimeError: If S3 operation fails
    """
    try:
        client = get_s3_client()

        # Validate limit
        limit = max(1, min(limit, 1000))

        response = client.list_objects(
            bucket=bucket_name, prefix=prefix, max_keys=limit, continuation_token=continuation_token
        )

        objects = response.get("Contents", [])
        is_truncated = response.get("IsTruncated", False)
        next_token = response.get("NextContinuationToken")

        # Format response based on requested format
        if response_format == ResponseFormat.JSON:
            return format_object_list_json(
                bucket=bucket_name,
                prefix=prefix,
                objects=objects,
                total_count=len(objects),
                has_more=is_truncated,
                next_token=next_token,
            )
        else:
            return format_object_list_markdown(
                bucket=bucket_name,
                prefix=prefix,
                objects=objects,
                total_count=len(objects),
                has_more=is_truncated,
                next_token=next_token,
            )

    except Exception as e:
        return handle_error(e)


async def get_object_operation(
    bucket_name: str,
    key: str,
    expires_in: int = 3600,
    response_content_disposition: Optional[str] = None,
    response_content_type: Optional[str] = None,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """
    Generate presigned URL for downloading an object.

    Args:
        bucket_name: S3 bucket name
        key: Object key
        expires_in: URL expiration in seconds (default: 3600, max: 604800)
        response_content_disposition: Override Content-Disposition header
        response_content_type: Override Content-Type header
        response_format: Output format (markdown or json)

    Returns:
        Formatted string with presigned URL

    Raises:
        ValueError: If bucket doesn't exist or inputs invalid
        PermissionError: If IAM permissions insufficient
        RuntimeError: If URL generation fails
    """
    try:
        client = get_s3_client()

        # Validate and cap expiration
        max_expiration = int(os.getenv("MAX_PRESIGNED_URL_EXPIRATION", "604800"))
        expires_in = max(1, min(expires_in, max_expiration))

        # Build parameters for presigned URL
        params: Dict[str, Any] = {"Bucket": bucket_name, "Key": key}

        if response_content_disposition:
            params["ResponseContentDisposition"] = response_content_disposition

        if response_content_type:
            params["ResponseContentType"] = response_content_type

        # Generate presigned URL
        url = client.generate_presigned_url(
            client_method="get_object", params=params, expires_in=expires_in
        )

        # Calculate expiration timestamp
        expires_at = (
            datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        ).isoformat().replace("+00:00", "Z")

        # Format response
        if response_format == ResponseFormat.JSON:
            return format_presigned_url_json(
                operation="GET",
                bucket=bucket_name,
                key=key,
                url=url,
                expires_in=expires_in,
                expires_at=expires_at,
            )
        else:
            return format_presigned_url_markdown(
                operation="GET",
                bucket=bucket_name,
                key=key,
                url=url,
                expires_in=expires_in,
                expires_at=expires_at,
            )

    except Exception as e:
        return handle_error(e)


async def put_object_operation(
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
    Generate presigned URL for uploading an object.

    Args:
        bucket_name: S3 bucket name
        key: Object key (destination path)
        expires_in: URL expiration in seconds (default: 3600, max: 604800)
        content_type: MIME type of the object
        server_side_encryption: Encryption algorithm ('AES256' or 'aws:kms')
        metadata: Custom metadata key-value pairs
        acl: Canned ACL ('private', 'public-read', etc.)
        response_format: Output format (markdown or json)

    Returns:
        Formatted string with presigned URL and required headers

    Raises:
        ValueError: If bucket doesn't exist or inputs invalid
        PermissionError: If IAM permissions insufficient
        RuntimeError: If URL generation fails
    """
    try:
        client = get_s3_client()

        # Validate and cap expiration
        max_expiration = int(os.getenv("MAX_PRESIGNED_URL_EXPIRATION", "604800"))
        expires_in = max(1, min(expires_in, max_expiration))

        # Build parameters for presigned URL
        params: Dict[str, Any] = {"Bucket": bucket_name, "Key": key}

        # Track required headers for the PUT request
        required_headers: Dict[str, str] = {}

        if content_type:
            params["ContentType"] = content_type
            required_headers["Content-Type"] = content_type

        if server_side_encryption:
            params["ServerSideEncryption"] = server_side_encryption
            required_headers["x-amz-server-side-encryption"] = server_side_encryption

        if metadata:
            params["Metadata"] = metadata
            # Metadata headers will be added by S3 client automatically

        if acl:
            params["ACL"] = acl

        # Generate presigned URL
        url = client.generate_presigned_url(
            client_method="put_object", params=params, expires_in=expires_in
        )

        # Calculate expiration timestamp
        expires_at = (
            datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        ).isoformat().replace("+00:00", "Z")

        # Format response
        if response_format == ResponseFormat.JSON:
            return format_presigned_url_json(
                operation="PUT",
                bucket=bucket_name,
                key=key,
                url=url,
                expires_in=expires_in,
                expires_at=expires_at,
                required_headers=required_headers if required_headers else None,
            )
        else:
            return format_presigned_url_markdown(
                operation="PUT",
                bucket=bucket_name,
                key=key,
                url=url,
                expires_in=expires_in,
                expires_at=expires_at,
                required_headers=required_headers if required_headers else None,
            )

    except Exception as e:
        return handle_error(e)


async def delete_object_operation(
    bucket_name: str,
    key: str,
    version_id: Optional[str] = None,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """
    Delete an object from S3.

    Args:
        bucket_name: S3 bucket name
        key: Object key to delete
        version_id: Specific version to delete (for versioned buckets)
        response_format: Output format (markdown or json)

    Returns:
        Formatted string with deletion confirmation

    Raises:
        ValueError: If bucket doesn't exist or inputs invalid
        PermissionError: If IAM permissions insufficient
        RuntimeError: If deletion fails
    """
    try:
        client = get_s3_client()

        response = client.delete_object(bucket=bucket_name, key=key, version_id=version_id)

        delete_marker = response.get("DeleteMarker", False)
        response_version_id = response.get("VersionId")

        # Format response
        if response_format == ResponseFormat.JSON:
            return format_delete_response_json(
                bucket=bucket_name,
                key=key,
                version_id=response_version_id,
                delete_marker=delete_marker,
            )
        else:
            return format_delete_response_markdown(
                bucket=bucket_name,
                key=key,
                version_id=response_version_id,
                delete_marker=delete_marker,
            )

    except Exception as e:
        return handle_error(e)
