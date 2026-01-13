"""
Storage module for saving data to files and uploading to S3 bucket.

This module provides functions to:
1. Save data to local files (CSV/JSON)
2. Upload files to S3 buckets
3. Download files from S3 buckets
4. Check if files exist in S3
5. Combined save and upload operations
"""

import logging
import os
from typing import Optional, Union

import boto3
import pandas as pd
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def _get_s3_client(
    aws_access_key_id: Optional[str] = None, aws_secret_access_key: Optional[str] = None, region_name: Optional[str] = None
) -> boto3.client:
    """
    Create and return an S3 client with proper error handling.

    Args:
        aws_access_key_id: AWS access key ID (optional, uses env var if not provided)
        aws_secret_access_key: AWS secret access key (optional, uses env var if not provided)
        region_name: AWS region name (optional, uses env var if not provided)

    Returns:
        boto3.client: Configured S3 client

    Raises:
        NoCredentialsError: If AWS credentials are not found
    """
    try:
        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region_name or os.getenv("AWS_REGION", "us-east-1"),
        )
    except NoCredentialsError:
        logger.error(
            "AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
        )
        raise


def save_to_file(data: pd.DataFrame, file_path: str, format: str = "csv") -> None:
    """
    Save DataFrame to a file in the specified format.

    Args:
        data: DataFrame to save
        file_path: Path where to save the file
        format: File format ('csv' or 'json')

    Raises:
        ValueError: If format is not supported
        Exception: If file saving fails
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if format.lower() == "csv":
            data.to_csv(file_path, index=False)
            logger.info(f"Data saved to CSV file: {file_path}")
        elif format.lower() == "json":
            data.to_json(file_path, orient="records", lines=True)
            logger.info(f"Data saved to JSON file: {file_path}")
        else:
            raise ValueError(f"Unsupported file format: {format}. Supported formats: csv, json")

    except Exception as e:
        logger.error(f"Failed to save data to file '{file_path}': {str(e)}")
        raise


def upload_to_s3(
    file_path: str,
    bucket_name: str,
    key: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: Optional[str] = None,
) -> None:
    """
    Upload a file to S3 bucket.

    Args:
        file_path: Local file path to upload
        bucket_name: S3 bucket name
        key: S3 object key (path in bucket)
        aws_access_key_id: AWS access key ID (optional)
        aws_secret_access_key: AWS secret access key (optional)
        region_name: AWS region name (optional)

    Raises:
        FileNotFoundError: If local file doesn't exist
        ClientError: If S3 upload fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    s3_client = _get_s3_client(aws_access_key_id, aws_secret_access_key, region_name)

    try:
        s3_client.upload_file(file_path, bucket_name, key)
        logger.info(f"File '{file_path}' uploaded to S3 bucket '{bucket_name}' as '{key}'")
    except ClientError as e:
        logger.error(f"Failed to upload '{file_path}' to S3 bucket '{bucket_name}': {str(e)}")
        raise


def download_from_s3(
    bucket_name: str,
    key: str,
    file_path: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: Optional[str] = None,
) -> None:
    """
    Download a file from S3 bucket.

    Args:
        bucket_name: S3 bucket name
        key: S3 object key (path in bucket)
        file_path: Local file path to save downloaded file
        aws_access_key_id: AWS access key ID (optional)
        aws_secret_access_key: AWS secret access key (optional)
        region_name: AWS region name (optional)

    Raises:
        ClientError: If S3 download fails
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    s3_client = _get_s3_client(aws_access_key_id, aws_secret_access_key, region_name)

    try:
        s3_client.download_file(bucket_name, key, file_path)
        logger.info(f"File '{key}' downloaded from S3 bucket '{bucket_name}' to '{file_path}'")
    except ClientError as e:
        logger.error(f"Failed to download '{key}' from S3 bucket '{bucket_name}': {str(e)}")
        raise


def file_exists_in_s3(
    bucket_name: str,
    key: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: Optional[str] = None,
) -> bool:
    """
    Check if a file exists in S3 bucket.

    Args:
        bucket_name: S3 bucket name
        key: S3 object key (path in bucket)
        aws_access_key_id: AWS access key ID (optional)
        aws_secret_access_key: AWS secret access key (optional)
        region_name: AWS region name (optional)

    Returns:
        bool: True if file exists, False otherwise
    """
    s3_client = _get_s3_client(aws_access_key_id, aws_secret_access_key, region_name)

    try:
        s3_client.head_object(Bucket=bucket_name, Key=key)
        logger.info(f"File '{key}' exists in S3 bucket '{bucket_name}'")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.info(f"File '{key}' does not exist in S3 bucket '{bucket_name}'")
            return False
        else:
            logger.error(f"Error checking if file '{key}' exists in S3 bucket '{bucket_name}': {str(e)}")
            raise


def save_and_upload(
    data: pd.DataFrame,
    file_path: str,
    bucket_name: str,
    key: str,
    format: str = "csv",
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: Optional[str] = None,
    cleanup_local: bool = False,
) -> None:
    """
    Save data to a local file and upload it to S3 bucket.

    Args:
        data: DataFrame to save and upload
        file_path: Local file path to save data
        bucket_name: S3 bucket name
        key: S3 object key (path in bucket)
        format: File format ('csv' or 'json')
        aws_access_key_id: AWS access key ID (optional)
        aws_secret_access_key: AWS secret access key (optional)
        region_name: AWS region name (optional)
        cleanup_local: Whether to delete local file after upload

    Raises:
        ValueError: If format is not supported
        Exception: If save or upload fails
    """
    try:
        # Save to local file
        save_to_file(data, file_path, format)

        # Upload to S3
        upload_to_s3(file_path, bucket_name, key, aws_access_key_id, aws_secret_access_key, region_name)

        # Cleanup local file if requested
        if cleanup_local:
            os.remove(file_path)
            logger.info(f"Local file '{file_path}' deleted after successful upload")

    except Exception as e:
        logger.error(f"Failed to save and upload data: {str(e)}")
        raise
