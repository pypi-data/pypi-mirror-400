"""S3 client wrapper with error handling and presigned URL generation."""

import os
from typing import Optional, Dict, Any, cast
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError


class S3Client:
    """
    Wrapper around boto3 S3 client with error handling and presigned URL generation.

    This client provides a clean interface for S3 operations used by the MCP server,
    with consistent error handling and configuration.
    """

    def __init__(self, region_name: Optional[str] = None):
        """
        Initialize S3 client with AWS configuration.

        Args:
            region_name: AWS region (defaults to AWS_REGION env var or 'us-east-1')

        Raises:
            NoCredentialsError: If AWS credentials are not configured
        """
        self.region = region_name or os.getenv("AWS_REGION", "us-east-1")

        # Configure boto3 client with signature version 4 and retries
        config = Config(
            region_name=self.region,
            signature_version="s3v4",  # Required for presigned URLs
            retries={"max_attempts": 3, "mode": "standard"},
        )

        try:
            self.client = boto3.client("s3", config=config)
        except NoCredentialsError:
            # Re-raise with more context
            raise RuntimeError(
                "AWS credentials not found. Please configure AWS credentials via "
                "environment variables, AWS CLI, or IAM role."
            )

    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000,
        continuation_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List objects in an S3 bucket.

        Args:
            bucket: S3 bucket name
            prefix: Object key prefix to filter results
            max_keys: Maximum number of objects to return
            continuation_token: Token for pagination

        Returns:
            Dictionary with:
                - Contents: List of object metadata
                - IsTruncated: Whether more results exist
                - NextContinuationToken: Token for next page (if truncated)

        Raises:
            ClientError: If S3 operation fails
        """
        try:
            params: Dict[str, Any] = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": max_keys}

            if continuation_token:
                params["ContinuationToken"] = continuation_token

            response = self.client.list_objects_v2(**params)
            return cast(Dict[str, Any], response)

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))

            if error_code == "NoSuchBucket":
                raise ValueError(f"Bucket '{bucket}' does not exist") from e
            elif error_code == "AccessDenied":
                raise PermissionError(
                    f"Access denied to bucket '{bucket}'. Check IAM permissions."
                ) from e
            else:
                raise RuntimeError(f"Failed to list objects in '{bucket}': {error_msg}") from e

    def generate_presigned_url(
        self, client_method: str, params: Dict[str, Any], expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL for S3 operations.

        Args:
            client_method: S3 client method name ('get_object' or 'put_object')
            params: Parameters for the S3 operation
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL string

        Raises:
            ClientError: If URL generation fails
        """
        try:
            url = self.client.generate_presigned_url(
                ClientMethod=client_method, Params=params, ExpiresIn=expires_in
            )
            return url

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))

            if error_code == "NoSuchBucket":
                bucket = params.get("Bucket", "unknown")
                raise ValueError(f"Bucket '{bucket}' does not exist") from e
            elif error_code == "AccessDenied":
                raise PermissionError(
                    f"Access denied. Check IAM permissions for {client_method}."
                ) from e
            else:
                raise RuntimeError(f"Failed to generate presigned URL: {error_msg}") from e

    def delete_object(
        self, bucket: str, key: str, version_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete an object from S3.

        Args:
            bucket: S3 bucket name
            key: Object key to delete
            version_id: Specific version to delete (for versioned buckets)

        Returns:
            Dictionary with deletion response (DeleteMarker, VersionId)

        Raises:
            ClientError: If deletion fails
        """
        try:
            params: Dict[str, Any] = {"Bucket": bucket, "Key": key}
            if version_id:
                params["VersionId"] = version_id

            response = self.client.delete_object(**params)
            return cast(Dict[str, Any], response)

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))

            if error_code == "NoSuchBucket":
                raise ValueError(f"Bucket '{bucket}' does not exist") from e
            elif error_code == "AccessDenied":
                raise PermissionError(
                    f"Access denied to delete from bucket '{bucket}'. Check IAM permissions."
                ) from e
            else:
                raise RuntimeError(f"Failed to delete object '{key}': {error_msg}") from e
