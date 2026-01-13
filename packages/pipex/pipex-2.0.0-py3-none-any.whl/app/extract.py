"""
Data extraction module for PipeX ETL tool.

This module provides functions to extract data from various sources:
- APIs with authentication support
- Relational databases (MySQL, PostgreSQL)
- NoSQL databases (MongoDB)
- Files (CSV, JSON)
"""

import logging
from typing import Any, Dict, Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Optional database imports
try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False
    mysql = None

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    psycopg2 = None

try:
    from pymongo import MongoClient
    HAS_MONGODB = True
except ImportError:
    HAS_MONGODB = False
    MongoClient = None

logger = logging.getLogger(__name__)


def _create_session_with_retries(retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    """
    Create a requests session with retry strategy.

    Args:
        retries: Number of retry attempts
        backoff_factor: Backoff factor for retries

    Returns:
        requests.Session: Configured session with retry strategy
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],  # Updated parameter name
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def extract_data(source_type: str, connection_details: Dict[str, Any], query_or_endpoint: str) -> pd.DataFrame:
    """
    Extract data from various sources based on source type.

    Args:
        source_type: Type of data source ('api', 'database', 'non_relational_database', 'file')
        connection_details: Connection configuration dictionary
        query_or_endpoint: Query string or endpoint URL

    Returns:
        pd.DataFrame: Extracted data as DataFrame

    Raises:
        ValueError: If source type is not supported
        Exception: If extraction fails
    """
    try:
        source_type = source_type.lower()

        if source_type == "api":
            return _extract_from_api(connection_details, query_or_endpoint)
        elif source_type == "database":
            return _extract_from_database(connection_details, query_or_endpoint)
        elif source_type == "non_relational_database":
            return _extract_from_nosql_database(connection_details, query_or_endpoint)
        elif source_type == "file":
            return _extract_from_file(connection_details, query_or_endpoint)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    except Exception as e:
        logger.error(f"Failed to extract data from {source_type}: {str(e)}")
        raise


def _extract_from_api(connection_details: Dict[str, Any], endpoint: str) -> pd.DataFrame:
    """Extract data from API endpoint."""
    try:
        session = _create_session_with_retries()
        headers = connection_details.get("headers", {})
        timeout = connection_details.get("timeout", 30)

        logger.info(f"Extracting data from API: {endpoint}")
        response = session.get(endpoint, headers=headers, timeout=timeout)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Successfully extracted {len(data) if isinstance(data, list) else 1} records from API")

        return pd.DataFrame(data)

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        raise


def _extract_from_database(connection_details: Dict[str, Any], query: str) -> pd.DataFrame:
    """Extract data from relational database."""
    db_type = connection_details.get("db_type", "").lower()
    connection = None

    try:
        logger.info(f"Connecting to {db_type} database")

        if db_type == "mysql":
            connection = mysql.connector.connect(
                host=connection_details["host"],
                user=connection_details["user"],
                password=connection_details["password"],
                database=connection_details["database"],
                port=connection_details.get("port", 3306),
            )
        elif db_type == "postgres":
            connection = psycopg2.connect(
                host=connection_details["host"],
                user=connection_details["user"],
                password=connection_details["password"],
                database=connection_details["database"],
                port=connection_details.get("port", 5432),
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        logger.info(f"Executing query: {query[:100]}...")
        df = pd.read_sql(query, connection)
        logger.info(f"Successfully extracted {len(df)} records from {db_type} database")

        return df

    except Exception as e:
        logger.error(f"Database extraction failed: {str(e)}")
        raise
    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed")


def _extract_from_nosql_database(connection_details: Dict[str, Any], query: Dict[str, Any]) -> pd.DataFrame:
    """Extract data from NoSQL database."""
    db_type = connection_details.get("db_type", "").lower()
    client = None

    try:
        if db_type == "mongodb":
            logger.info("Connecting to MongoDB")

            client = MongoClient(
                host=connection_details["host"],
                port=connection_details.get("port", 27017),
                username=connection_details.get("username"),
                password=connection_details.get("password"),
            )

            db = client[connection_details["database"]]
            collection = db[connection_details["collection"]]

            # Convert string query to dict if needed
            if isinstance(query, str):
                import json

                query = json.loads(query)

            logger.info(f"Executing MongoDB query: {query}")
            data = list(collection.find(query))
            logger.info(f"Successfully extracted {len(data)} records from MongoDB")

            return pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported NoSQL database type: {db_type}")

    except Exception as e:
        logger.error(f"NoSQL database extraction failed: {str(e)}")
        raise
    finally:
        if client:
            client.close()
            logger.info("MongoDB connection closed")


def _extract_from_file(connection_details: Dict[str, Any], file_path: str) -> pd.DataFrame:
    """Extract data from file."""
    file_type = connection_details.get("file_type", "").lower()

    try:
        logger.info(f"Extracting data from {file_type} file: {file_path}")

        if file_type == "csv":
            # Support additional CSV parameters
            csv_params = {
                "sep": connection_details.get("separator", ","),
                "encoding": connection_details.get("encoding", "utf-8"),
                "header": connection_details.get("header", 0),
                "skiprows": connection_details.get("skiprows", None),
                "nrows": connection_details.get("nrows", None),
            }
            df = pd.read_csv(file_path, **csv_params)
        elif file_type == "json":
            # Support different JSON orientations
            orient = connection_details.get("orient", "records")
            lines = connection_details.get("lines", None)
            df = pd.read_json(file_path, orient=orient, lines=lines)
        elif file_type == "excel":
            # Excel support with sheet selection
            excel_params = {
                "sheet_name": connection_details.get("sheet_name", 0),
                "header": connection_details.get("header", 0),
                "skiprows": connection_details.get("skiprows", None),
                "nrows": connection_details.get("nrows", None),
                "engine": connection_details.get("engine", "openpyxl"),
            }
            df = pd.read_excel(file_path, **excel_params)
        elif file_type == "parquet":
            # Parquet support
            parquet_params = {
                "columns": connection_details.get("columns", None),
                "engine": connection_details.get("engine", "pyarrow"),
            }
            df = pd.read_parquet(file_path, **parquet_params)
        elif file_type == "xml":
            # XML support (requires lxml)
            xml_params = {
                "xpath": connection_details.get("xpath", ".//row"),
                "encoding": connection_details.get("encoding", "utf-8"),
            }
            df = pd.read_xml(file_path, **xml_params)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Supported formats: csv, json, excel, parquet, xml")

        logger.info(f"Successfully extracted {len(df)} records from {file_type} file")
        return df

    except Exception as e:
        logger.error(f"File extraction failed: {str(e)}")
        raise
