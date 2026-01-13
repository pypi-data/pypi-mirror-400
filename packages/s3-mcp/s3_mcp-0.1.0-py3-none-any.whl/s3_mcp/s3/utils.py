"""Shared utilities for S3 operations and response formatting."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json


class ResponseFormat(str, Enum):
    """Response format options for tool outputs."""

    MARKDOWN = "markdown"
    JSON = "json"


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes as human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string (e.g., "1.5 KB", "2.3 MB")
    """
    size_float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_float < 1024.0:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.1f} PB"


def format_timestamp(timestamp: datetime) -> str:
    """
    Format datetime as ISO 8601 string.

    Args:
        timestamp: Datetime object

    Returns:
        ISO 8601 formatted string
    """
    return timestamp.isoformat() + "Z"


def format_object_list_markdown(
    bucket: str,
    prefix: str,
    objects: List[Dict[str, Any]],
    total_count: int,
    has_more: bool,
    next_token: Optional[str] = None,
) -> str:
    """
    Format object list as Markdown table.

    Args:
        bucket: Bucket name
        prefix: Filter prefix used
        objects: List of object metadata
        total_count: Total objects in response
        has_more: Whether more results exist
        next_token: Continuation token for next page

    Returns:
        Markdown formatted string
    """
    lines = [f"# S3 Objects in `{bucket}`", ""]

    if prefix:
        lines.append(f"**Prefix:** `{prefix}`")
        lines.append("")

    lines.extend([f"**Total Objects:** {total_count}", ""])

    if not objects:
        lines.append("*No objects found*")
        return "\n".join(lines)

    # Table header
    lines.extend(
        [
            "| Key | Size | Last Modified | Storage Class |",
            "|-----|------|---------------|---------------|",
        ]
    )

    # Table rows
    for obj in objects:
        key = obj.get("Key", "")
        size = format_bytes(obj.get("Size", 0))
        last_mod = obj.get("LastModified", "")
        if isinstance(last_mod, datetime):
            last_mod = last_mod.strftime("%Y-%m-%d %H:%M:%S")
        storage_class = obj.get("StorageClass", "STANDARD")

        lines.append(f"| `{key}` | {size} | {last_mod} | {storage_class} |")

    # Pagination info
    if has_more:
        lines.extend(
            ["", "---", f"**More results available.** Use continuation token: `{next_token}`"]
        )

    return "\n".join(lines)


def format_object_list_json(
    bucket: str,
    prefix: str,
    objects: List[Dict[str, Any]],
    total_count: int,
    has_more: bool,
    next_token: Optional[str] = None,
) -> str:
    """
    Format object list as JSON.

    Args:
        bucket: Bucket name
        prefix: Filter prefix used
        objects: List of object metadata
        total_count: Total objects in response
        has_more: Whether more results exist
        next_token: Continuation token for next page

    Returns:
        JSON formatted string
    """
    # Convert datetime objects to ISO strings
    formatted_objects = []
    for obj in objects:
        formatted_obj = obj.copy()
        if "LastModified" in formatted_obj and isinstance(formatted_obj["LastModified"], datetime):
            formatted_obj["LastModified"] = format_timestamp(formatted_obj["LastModified"])
        formatted_objects.append(formatted_obj)

    result = {
        "bucket": bucket,
        "prefix": prefix,
        "total_count": total_count,
        "objects": formatted_objects,
        "has_more": has_more,
    }

    if next_token:
        result["next_continuation_token"] = next_token

    return json.dumps(result, indent=2)


def format_presigned_url_markdown(
    operation: str,
    bucket: str,
    key: str,
    url: str,
    expires_in: int,
    expires_at: str,
    required_headers: Optional[Dict[str, str]] = None,
) -> str:
    """
    Format presigned URL response as Markdown.

    Args:
        operation: Operation type (GET or PUT)
        bucket: Bucket name
        key: Object key
        url: Presigned URL
        expires_in: Expiration in seconds
        expires_at: Expiration timestamp
        required_headers: Required headers for the request

    Returns:
        Markdown formatted string
    """
    lines = [
        f"# Presigned URL for {operation}",
        "",
        f"**Bucket:** `{bucket}`",
        f"**Key:** `{key}`",
        f"**Expires In:** {expires_in} seconds ({expires_in // 60} minutes)",
        f"**Expires At:** {expires_at}",
        "",
        "## URL",
        "```",
        url,
        "```",
    ]

    if required_headers:
        lines.extend(
            ["", "## Required Headers", "```json", json.dumps(required_headers, indent=2), "```"]
        )

    if operation == "PUT":
        lines.extend(["", "## Usage Example", "```bash", "curl -X PUT -T local-file.txt \\"])

        if required_headers:
            for header, value in required_headers.items():
                lines.append(f'  -H "{header}: {value}" \\')

        lines.extend([f'  "{url}"', "```"])
    else:  # GET
        lines.extend(["", "## Usage Example", "```bash", f'curl -o downloaded-file "{url}"', "```"])

    return "\n".join(lines)


def format_presigned_url_json(
    operation: str,
    bucket: str,
    key: str,
    url: str,
    expires_in: int,
    expires_at: str,
    required_headers: Optional[Dict[str, str]] = None,
) -> str:
    """
    Format presigned URL response as JSON.

    Args:
        operation: Operation type (GET or PUT)
        bucket: Bucket name
        key: Object key
        url: Presigned URL
        expires_in: Expiration in seconds
        expires_at: Expiration timestamp
        required_headers: Required headers for the request

    Returns:
        JSON formatted string
    """
    result = {
        "operation": operation,
        "bucket": bucket,
        "key": key,
        "presigned_url": url,
        "expires_in": expires_in,
        "expires_at": expires_at,
    }

    if required_headers:
        result["required_headers"] = required_headers

    return json.dumps(result, indent=2)


def format_delete_response_markdown(
    bucket: str, key: str, version_id: Optional[str] = None, delete_marker: bool = False
) -> str:
    """
    Format delete operation response as Markdown.

    Args:
        bucket: Bucket name
        key: Object key
        version_id: Version ID if versioning enabled
        delete_marker: Whether a delete marker was created

    Returns:
        Markdown formatted string
    """
    lines = ["# Object Deleted Successfully", "", f"**Bucket:** `{bucket}`", f"**Key:** `{key}`"]

    if version_id:
        lines.append(f"**Version ID:** `{version_id}`")

    if delete_marker:
        lines.extend(["", "*Note: A delete marker was created (versioned bucket)*"])

    return "\n".join(lines)


def format_delete_response_json(
    bucket: str, key: str, version_id: Optional[str] = None, delete_marker: bool = False
) -> str:
    """
    Format delete operation response as JSON.

    Args:
        bucket: Bucket name
        key: Object key
        version_id: Version ID if versioning enabled
        delete_marker: Whether a delete marker was created

    Returns:
        JSON formatted string
    """
    result = {"success": True, "bucket": bucket, "key": key, "delete_marker": delete_marker}

    if version_id:
        result["version_id"] = version_id

    return json.dumps(result, indent=2)


def handle_error(error: Exception) -> str:
    """
    Format error message for user-friendly display.

    Args:
        error: Exception that occurred

    Returns:
        User-friendly error message with guidance
    """
    if isinstance(error, ValueError):
        return f"❌ **Invalid Input:** {str(error)}\n\n💡 **Suggestion:** Check the bucket name and ensure it exists."

    elif isinstance(error, PermissionError):
        return (
            f"❌ **Permission Denied:** {str(error)}\n\n"
            "💡 **Suggestions:**\n"
            "- Verify IAM permissions for the operation\n"
            "- Check bucket policies\n"
            "- Ensure AWS credentials are configured correctly"
        )

    elif isinstance(error, RuntimeError):
        return f"❌ **Operation Failed:** {str(error)}\n\n💡 **Suggestion:** Check AWS service status and try again."

    else:
        return f"❌ **Unexpected Error:** {str(error)}\n\n💡 **Suggestion:** Check the error message and contact support if the issue persists."
