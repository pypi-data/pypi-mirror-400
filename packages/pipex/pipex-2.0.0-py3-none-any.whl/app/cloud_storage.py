"""
Multi-cloud storage module for PipeX ETL tool.

This module provides unified interface for multiple cloud storage providers:
- AWS S3
- Google Cloud Storage (GCS)
- Azure Blob Storage
- DigitalOcean Spaces
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class CloudStorageProvider(ABC):
    """Abstract base class for cloud storage providers."""

    @abstractmethod
    def upload_dataframe(self, data: pd.DataFrame, bucket: str, key: str, **kwargs) -> None:
        """Upload DataFrame to cloud storage."""
        pass

    @abstractmethod
    def download_dataframe(self, bucket: str, key: str, **kwargs) -> pd.DataFrame:
        """Download DataFrame from cloud storage."""
        pass

    @abstractmethod
    def file_exists(self, bucket: str, key: str) -> bool:
        """Check if file exists in cloud storage."""
        pass

    @abstractmethod
    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in cloud storage bucket."""
        pass


class AWSProvider(CloudStorageProvider):
    """AWS S3 storage provider."""

    def __init__(self, config: Dict[str, Any]):
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError

            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=config.get("aws_access_key_id") or os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=config.get("aws_secret_access_key") or os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=config.get("region_name") or os.getenv("AWS_REGION", "us-east-1"),
            )
            logger.info("AWS S3 client initialized successfully")
        except ImportError:
            raise ImportError("boto3 is required for AWS S3 support. Install with: pip install boto3")
        except NoCredentialsError:
            raise ValueError("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")

    def upload_dataframe(self, data: pd.DataFrame, bucket: str, key: str, **kwargs) -> None:
        """Upload DataFrame to S3 bucket."""
        try:
            file_format = kwargs.get("format", "csv")

            if file_format.lower() == "csv":
                csv_buffer = data.to_csv(index=False)
                self.s3_client.put_object(Bucket=bucket, Key=key, Body=csv_buffer)
            elif file_format.lower() == "json":
                json_buffer = data.to_json(orient="records", lines=True)
                self.s3_client.put_object(Bucket=bucket, Key=key, Body=json_buffer)
            elif file_format.lower() == "parquet":
                import io

                parquet_buffer = io.BytesIO()
                data.to_parquet(parquet_buffer, index=False)
                parquet_buffer.seek(0)
                self.s3_client.put_object(Bucket=bucket, Key=key, Body=parquet_buffer.getvalue())
            else:
                raise ValueError(f"Unsupported format: {file_format}")

            logger.info(f"Successfully uploaded {len(data)} records to S3: s3://{bucket}/{key}")
        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise

    def download_dataframe(self, bucket: str, key: str, **kwargs) -> pd.DataFrame:
        """Download DataFrame from S3 bucket."""
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read()

            file_format = kwargs.get("format", "csv")
            if file_format.lower() == "csv":
                import io

                return pd.read_csv(io.StringIO(content.decode("utf-8")))
            elif file_format.lower() == "json":
                import io

                return pd.read_json(io.StringIO(content.decode("utf-8")), lines=True)
            elif file_format.lower() == "parquet":
                import io

                return pd.read_parquet(io.BytesIO(content))
            else:
                raise ValueError(f"Unsupported format: {file_format}")
        except Exception as e:
            logger.error(f"Failed to download from S3: {str(e)}")
            raise

    def file_exists(self, bucket: str, key: str) -> bool:
        """Check if file exists in S3 bucket."""
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except:
            return False

    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in S3 bucket."""
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            logger.error(f"Failed to list S3 files: {str(e)}")
            raise


class GCPProvider(CloudStorageProvider):
    """Google Cloud Storage provider."""

    def __init__(self, config: Dict[str, Any]):
        try:
            from google.cloud import storage

            credentials_path = config.get("credentials_path") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            project_id = config.get("project_id") or os.getenv("GOOGLE_CLOUD_PROJECT")

            if credentials_path:
                self.client = storage.Client.from_service_account_json(credentials_path, project=project_id)
            else:
                self.client = storage.Client(project=project_id)

            logger.info("Google Cloud Storage client initialized successfully")
        except ImportError:
            raise ImportError(
                "google-cloud-storage is required for GCS support. Install with: pip install google-cloud-storage"
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize GCS client: {str(e)}")

    def upload_dataframe(self, data: pd.DataFrame, bucket: str, key: str, **kwargs) -> None:
        """Upload DataFrame to GCS bucket."""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(key)

            file_format = kwargs.get("format", "csv")

            if file_format.lower() == "csv":
                csv_data = data.to_csv(index=False)
                blob.upload_from_string(csv_data, content_type="text/csv")
            elif file_format.lower() == "json":
                json_data = data.to_json(orient="records", lines=True)
                blob.upload_from_string(json_data, content_type="application/json")
            elif file_format.lower() == "parquet":
                import io

                parquet_buffer = io.BytesIO()
                data.to_parquet(parquet_buffer, index=False)
                parquet_buffer.seek(0)
                blob.upload_from_file(parquet_buffer, content_type="application/octet-stream")
            else:
                raise ValueError(f"Unsupported format: {file_format}")

            logger.info(f"Successfully uploaded {len(data)} records to GCS: gs://{bucket}/{key}")
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {str(e)}")
            raise

    def download_dataframe(self, bucket: str, key: str, **kwargs) -> pd.DataFrame:
        """Download DataFrame from GCS bucket."""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(key)
            content = blob.download_as_text()

            file_format = kwargs.get("format", "csv")
            if file_format.lower() == "csv":
                import io

                return pd.read_csv(io.StringIO(content))
            elif file_format.lower() == "json":
                import io

                return pd.read_json(io.StringIO(content), lines=True)
            elif file_format.lower() == "parquet":
                content_bytes = blob.download_as_bytes()
                import io

                return pd.read_parquet(io.BytesIO(content_bytes))
            else:
                raise ValueError(f"Unsupported format: {file_format}")
        except Exception as e:
            logger.error(f"Failed to download from GCS: {str(e)}")
            raise

    def file_exists(self, bucket: str, key: str) -> bool:
        """Check if file exists in GCS bucket."""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(key)
            return blob.exists()
        except:
            return False

    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in GCS bucket."""
        try:
            bucket_obj = self.client.bucket(bucket)
            blobs = bucket_obj.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Failed to list GCS files: {str(e)}")
            raise


class AzureProvider(CloudStorageProvider):
    """Azure Blob Storage provider."""

    def __init__(self, config: Dict[str, Any]):
        try:
            from azure.storage.blob import BlobServiceClient

            connection_string = config.get("connection_string") or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            account_name = config.get("account_name") or os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
            account_key = config.get("account_key") or os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

            if connection_string:
                self.client = BlobServiceClient.from_connection_string(connection_string)
            elif account_name and account_key:
                self.client = BlobServiceClient(
                    account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key
                )
            else:
                raise ValueError("Azure credentials not found")

            logger.info("Azure Blob Storage client initialized successfully")
        except ImportError:
            raise ImportError("azure-storage-blob is required for Azure support. Install with: pip install azure-storage-blob")
        except Exception as e:
            raise ValueError(f"Failed to initialize Azure client: {str(e)}")

    def upload_dataframe(self, data: pd.DataFrame, bucket: str, key: str, **kwargs) -> None:
        """Upload DataFrame to Azure Blob Storage."""
        try:
            blob_client = self.client.get_blob_client(container=bucket, blob=key)

            file_format = kwargs.get("format", "csv")

            if file_format.lower() == "csv":
                csv_data = data.to_csv(index=False)
                blob_client.upload_blob(csv_data, overwrite=True, content_type="text/csv")
            elif file_format.lower() == "json":
                json_data = data.to_json(orient="records", lines=True)
                blob_client.upload_blob(json_data, overwrite=True, content_type="application/json")
            elif file_format.lower() == "parquet":
                import io

                parquet_buffer = io.BytesIO()
                data.to_parquet(parquet_buffer, index=False)
                parquet_buffer.seek(0)
                blob_client.upload_blob(parquet_buffer.getvalue(), overwrite=True, content_type="application/octet-stream")
            else:
                raise ValueError(f"Unsupported format: {file_format}")

            logger.info(f"Successfully uploaded {len(data)} records to Azure: {bucket}/{key}")
        except Exception as e:
            logger.error(f"Failed to upload to Azure: {str(e)}")
            raise

    def download_dataframe(self, bucket: str, key: str, **kwargs) -> pd.DataFrame:
        """Download DataFrame from Azure Blob Storage."""
        try:
            blob_client = self.client.get_blob_client(container=bucket, blob=key)
            content = blob_client.download_blob().readall()

            file_format = kwargs.get("format", "csv")
            if file_format.lower() == "csv":
                import io

                return pd.read_csv(io.StringIO(content.decode("utf-8")))
            elif file_format.lower() == "json":
                import io

                return pd.read_json(io.StringIO(content.decode("utf-8")), lines=True)
            elif file_format.lower() == "parquet":
                import io

                return pd.read_parquet(io.BytesIO(content))
            else:
                raise ValueError(f"Unsupported format: {file_format}")
        except Exception as e:
            logger.error(f"Failed to download from Azure: {str(e)}")
            raise

    def file_exists(self, bucket: str, key: str) -> bool:
        """Check if file exists in Azure Blob Storage."""
        try:
            blob_client = self.client.get_blob_client(container=bucket, blob=key)
            return blob_client.exists()
        except:
            return False

    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in Azure Blob Storage container."""
        try:
            container_client = self.client.get_container_client(bucket)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Failed to list Azure files: {str(e)}")
            raise


class DigitalOceanProvider(CloudStorageProvider):
    """DigitalOcean Spaces provider (S3-compatible)."""

    def __init__(self, config: Dict[str, Any]):
        try:
            import boto3

            self.s3_client = boto3.client(
                "s3",
                endpoint_url=config.get("endpoint_url") or f"https://{config.get('region', 'nyc3')}.digitaloceanspaces.com",
                aws_access_key_id=config.get("access_key_id") or os.getenv("DO_SPACES_ACCESS_KEY_ID"),
                aws_secret_access_key=config.get("secret_access_key") or os.getenv("DO_SPACES_SECRET_ACCESS_KEY"),
                region_name=config.get("region", "nyc3"),
            )
            logger.info("DigitalOcean Spaces client initialized successfully")
        except ImportError:
            raise ImportError("boto3 is required for DigitalOcean Spaces support. Install with: pip install boto3")
        except Exception as e:
            raise ValueError(f"Failed to initialize DigitalOcean Spaces client: {str(e)}")

    def upload_dataframe(self, data: pd.DataFrame, bucket: str, key: str, **kwargs) -> None:
        """Upload DataFrame to DigitalOcean Spaces."""
        # Use same implementation as AWS S3
        aws_provider = AWSProvider({})
        aws_provider.s3_client = self.s3_client
        return aws_provider.upload_dataframe(data, bucket, key, **kwargs)

    def download_dataframe(self, bucket: str, key: str, **kwargs) -> pd.DataFrame:
        """Download DataFrame from DigitalOcean Spaces."""
        # Use same implementation as AWS S3
        aws_provider = AWSProvider({})
        aws_provider.s3_client = self.s3_client
        return aws_provider.download_dataframe(bucket, key, **kwargs)

    def file_exists(self, bucket: str, key: str) -> bool:
        """Check if file exists in DigitalOcean Spaces."""
        # Use same implementation as AWS S3
        aws_provider = AWSProvider({})
        aws_provider.s3_client = self.s3_client
        return aws_provider.file_exists(bucket, key)

    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in DigitalOcean Spaces."""
        # Use same implementation as AWS S3
        aws_provider = AWSProvider({})
        aws_provider.s3_client = self.s3_client
        return aws_provider.list_files(bucket, prefix)


def get_cloud_provider(provider_name: str, config: Dict[str, Any]) -> CloudStorageProvider:
    """
    Factory function to get cloud storage provider.

    Args:
        provider_name: Name of the cloud provider ('aws', 'gcp', 'azure', 'digitalocean')
        config: Configuration dictionary for the provider

    Returns:
        CloudStorageProvider: Initialized cloud storage provider
    """
    providers = {
        "aws": AWSProvider,
        "s3": AWSProvider,
        "gcp": GCPProvider,
        "gcs": GCPProvider,
        "google": GCPProvider,
        "azure": AzureProvider,
        "digitalocean": DigitalOceanProvider,
        "do": DigitalOceanProvider,
        "spaces": DigitalOceanProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unsupported cloud provider: {provider_name}. Supported providers: {list(providers.keys())}")

    return provider_class(config)


def upload_to_cloud(data: pd.DataFrame, provider_name: str, config: Dict[str, Any]) -> None:
    """
    Upload DataFrame to cloud storage.

    Args:
        data: DataFrame to upload
        provider_name: Name of the cloud provider
        config: Configuration dictionary including bucket, key, and provider config
    """
    try:
        provider = get_cloud_provider(provider_name, config)

        bucket = config["bucket_name"]
        key = config["file_name"]
        file_format = config.get("format", "csv")

        provider.upload_dataframe(data, bucket, key, format=file_format)
        logger.info(f"Successfully uploaded data to {provider_name} cloud storage")

    except Exception as e:
        logger.error(f"Failed to upload to {provider_name}: {str(e)}")
        raise


def download_from_cloud(provider_name: str, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Download DataFrame from cloud storage.

    Args:
        provider_name: Name of the cloud provider
        config: Configuration dictionary including bucket, key, and provider config

    Returns:
        pd.DataFrame: Downloaded data
    """
    try:
        provider = get_cloud_provider(provider_name, config)

        bucket = config["bucket_name"]
        key = config["file_name"]
        file_format = config.get("format", "csv")

        data = provider.download_dataframe(bucket, key, format=file_format)
        logger.info(f"Successfully downloaded data from {provider_name} cloud storage")
        return data

    except Exception as e:
        logger.error(f"Failed to download from {provider_name}: {str(e)}")
        raise
