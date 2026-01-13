"""
Data loading module for PipeX ETL tool.

This module provides functions to load data to various targets:
- AWS S3 buckets
- Relational databases (MySQL, PostgreSQL)
- NoSQL databases (MongoDB)
- Local files (CSV, JSON)
"""

import logging
import os
from typing import Any, Dict, Optional

import pandas as pd
from dotenv import load_dotenv

# Optional imports for cloud storage
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    HAS_AWS = True
except ImportError:
    HAS_AWS = False
    boto3 = None
    ClientError = Exception
    NoCredentialsError = Exception

# Optional imports for databases
try:
    from pymongo import MongoClient
    HAS_MONGODB = True
except ImportError:
    HAS_MONGODB = False
    MongoClient = None

try:
    from sqlalchemy import create_engine
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    create_engine = None

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def load_data(target: str, config: Dict[str, Any], data: pd.DataFrame) -> None:
    """
    Load data to specified target based on target type.

    Args:
        target: Target type ('S3 Bucket', 'database', 'non_relational_database', 'Local File')
        config: Configuration dictionary for the target
        data: DataFrame to load

    Raises:
        ValueError: If target type is not supported
        Exception: If loading fails
    """
    try:
        target = target.strip()

        if target in ["S3 Bucket", "Cloud Storage"]:
            _load_to_cloud_storage(config, data)
        elif target == "database":
            _load_to_database(config, data)
        elif target == "non_relational_database":
            _load_to_nosql_database(config, data)
        elif target == "Local File":
            _load_to_file(config, data)
        else:
            raise ValueError(f"Unsupported target type: {target}")

    except Exception as e:
        logger.error(f"Failed to load data to {target}: {str(e)}")
        raise


def _load_to_cloud_storage(config: Dict[str, Any], data: pd.DataFrame) -> None:
    """Load data to cloud storage (AWS S3, GCP, Azure, etc.)."""
    try:
        from app.cloud_storage import upload_to_cloud

        # Validate required config keys
        required_keys = ["provider", "bucket_name", "file_name"]
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise KeyError(f"Missing required config keys: {missing_keys}")

        provider = config["provider"].lower()

        logger.info(f"Uploading data to {provider} cloud storage")
        upload_to_cloud(data, provider, config)
        logger.info(f"Successfully loaded {len(data)} records to {provider} cloud storage")

    except Exception as e:
        logger.error(f"Cloud storage loading failed: {str(e)}")
        raise


def _load_to_database(config: Dict[str, Any], data: pd.DataFrame) -> None:
    """Load data to relational database."""
    db_type = config.get("db_type", "").lower()
    engine = None

    try:
        # Validate required config keys
        required_keys = ["host", "username", "password", "database", "table_name"]
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise KeyError(f"Missing required config keys: {missing_keys}")

        logger.info(f"Connecting to {db_type} database")

        if db_type == "mysql":
            connection_string = (
                f"mysql+mysqlconnector://{config['username']}:{config['password']}"
                f"@{config['host']}:{config.get('port', 3306)}/{config['database']}"
            )
        elif db_type == "postgres":
            connection_string = (
                f"postgresql+psycopg2://{config['username']}:{config['password']}"
                f"@{config['host']}:{config.get('port', 5432)}/{config['database']}"
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        engine = create_engine(connection_string)

        # Load data with configurable options
        if_exists = config.get("if_exists", "replace")  # 'fail', 'replace', 'append'
        table_name = config["table_name"]

        logger.info(f"Loading data to table '{table_name}' with mode '{if_exists}'")
        data.to_sql(table_name, engine, if_exists=if_exists, index=False)
        logger.info(f"Successfully loaded {len(data)} records to {db_type} database: {config['database']}")

    except Exception as e:
        logger.error(f"Database loading failed: {str(e)}")
        raise
    finally:
        if engine:
            engine.dispose()
            logger.info("Database connection closed")


def _load_to_nosql_database(config: Dict[str, Any], data: pd.DataFrame) -> None:
    """Load data to NoSQL database."""
    db_type = config.get("db_type", "").lower()
    client = None

    try:
        if db_type == "mongodb":
            # Validate required config keys
            required_keys = ["host", "database", "collection"]
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                raise KeyError(f"Missing required config keys: {missing_keys}")

            logger.info("Connecting to MongoDB")

            client = MongoClient(
                host=config["host"],
                port=config.get("port", 27017),
                username=config.get("username"),
                password=config.get("password"),
            )

            db = client[config["database"]]
            collection = db[config["collection"]]

            # Convert DataFrame to records and handle NaN values
            records = data.where(pd.notnull(data), None).to_dict("records")

            # Insert data with configurable behavior
            if config.get("replace_collection", False):
                collection.drop()
                logger.info(f"Dropped existing collection: {config['collection']}")

            logger.info(f"Inserting data to MongoDB collection '{config['collection']}'")
            if records:
                collection.insert_many(records)

            logger.info(f"Successfully loaded {len(data)} records to MongoDB collection: {config['collection']}")
        else:
            raise ValueError(f"Unsupported NoSQL database type: {db_type}")

    except Exception as e:
        logger.error(f"NoSQL database loading failed: {str(e)}")
        raise
    finally:
        if client:
            client.close()
            logger.info("MongoDB connection closed")


def _load_to_file(config: Dict[str, Any], data: pd.DataFrame) -> None:
    """Load data to local file."""
    file_type = config.get("file_type", "").lower()

    try:
        # Validate required config keys
        if "file_path" not in config:
            raise KeyError("Missing required config key: file_path")

        file_path = config["file_path"]

        # Create directory structure if it doesn't exist
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")

        # Add timestamp to filename if requested
        if config.get("add_timestamp", False):
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path_parts = os.path.splitext(file_path)
            file_path = f"{path_parts[0]}_{timestamp}{path_parts[1]}"

        logger.info(f"Saving data to {file_type} file: {file_path}")

        if file_type == "csv":
            # Support additional CSV parameters
            csv_params = {
                "index": False,
                "sep": config.get("separator", ","),
                "encoding": config.get("encoding", "utf-8"),
                "quoting": config.get("quoting", 1),  # QUOTE_ALL by default
            }
            data.to_csv(file_path, **csv_params)
        elif file_type == "json":
            # Support different JSON orientations
            orient = config.get("orient", "records")
            lines = config.get("lines", True)
            indent = config.get("indent", 2)
            data.to_json(file_path, orient=orient, lines=lines, indent=indent)
        elif file_type == "excel":
            # Excel support with multiple sheets
            excel_params = {
                "index": False,
                "sheet_name": config.get("sheet_name", "Sheet1"),
                "engine": config.get("engine", "openpyxl"),
            }
            data.to_excel(file_path, **excel_params)
        elif file_type == "parquet":
            # Parquet support for efficient storage
            parquet_params = {"index": False, "compression": config.get("compression", "snappy")}
            data.to_parquet(file_path, **parquet_params)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Supported formats: csv, json, excel, parquet")

        logger.info(f"Successfully loaded {len(data)} records to {file_type} file: {file_path}")

    except Exception as e:
        logger.error(f"File loading failed: {str(e)}")
        raise
