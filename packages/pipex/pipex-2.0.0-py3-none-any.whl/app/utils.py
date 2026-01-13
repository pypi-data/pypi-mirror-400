"""
Utility functions for PipeX ETL tool.

This module provides common utility functions for:
- Logging configuration
- Configuration file loading and validation
- Environment variable management
- Data validation
- File operations
- Error handling helpers
"""

import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import yaml
from dotenv import load_dotenv
from jsonschema import ValidationError, validate

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def setup_logging(
    log_level: Union[int, str] = logging.INFO, log_format: Optional[str] = None, log_file: Optional[str] = None
) -> None:
    """
    Setup logging configuration with customizable options.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
        log_file: Optional log file path
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure logging
    logging_config = {"level": log_level, "format": log_format, "datefmt": "%Y-%m-%d %H:%M:%S"}

    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logging_config["filename"] = log_file
        logging_config["filemode"] = "a"

    logging.basicConfig(**logging_config)

    # Set specific loggers to appropriate levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)

    logger.info(f"Logging configured with level: {logging.getLevelName(log_level)}")


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load and parse a YAML configuration file with environment variable substitution.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dict[str, Any]: Parsed configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    try:
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        # Apply environment variable substitution
        config = apply_env_variables(config)

        logger.info(f"Configuration loaded from {config_path}")
        return config

    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in configuration file {config_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        raise


def apply_env_variables(config: Any) -> Any:
    """
    Recursively replace environment variable placeholders in configuration.

    Args:
        config: Configuration object (dict, list, or string)

    Returns:
        Any: Configuration with environment variables substituted
    """
    if isinstance(config, dict):
        return {key: apply_env_variables(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [apply_env_variables(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        env_var = config[2:-1]
        default_value = None

        # Support default values: ${VAR_NAME:default_value}
        if ":" in env_var:
            env_var, default_value = env_var.split(":", 1)

        value = os.getenv(env_var, default_value)
        if value is None:
            logger.warning(f"Environment variable {env_var} is not set and no default provided")
            return config  # Return original placeholder

        return value
    else:
        return config


def validate_config(config: Dict[str, Any], required_keys: List[str]) -> None:
    """
    Validate that all required keys are present in the configuration.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys

    Raises:
        KeyError: If required keys are missing
        ValueError: If unresolved placeholders are found
    """
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise KeyError(f"Missing required configuration keys: {missing_keys}")

    # Check for unresolved placeholders
    unresolved = find_unresolved_placeholders(config)
    if unresolved:
        raise ValueError(f"Unresolved environment variable placeholders: {unresolved}")

    logger.info("Configuration validation successful")


def find_unresolved_placeholders(config: Any, path: str = "") -> List[str]:
    """
    Find unresolved environment variable placeholders in configuration.

    Args:
        config: Configuration object
        path: Current path in the configuration (for error reporting)

    Returns:
        List[str]: List of unresolved placeholder paths
    """
    unresolved = []

    if isinstance(config, dict):
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            unresolved.extend(find_unresolved_placeholders(value, current_path))
    elif isinstance(config, list):
        for i, item in enumerate(config):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            unresolved.extend(find_unresolved_placeholders(item, current_path))
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        unresolved.append(f"{path}: {config}")

    return unresolved


def validate_data_schema(data: Union[Dict, List], schema: Dict[str, Any]) -> None:
    """
    Validate data against a JSON schema.

    Args:
        data: Data to validate
        schema: JSON schema dictionary

    Raises:
        ValidationError: If data doesn't match schema
    """
    try:
        validate(instance=data, schema=schema)
        logger.info("Data schema validation successful")
    except ValidationError as e:
        logger.error(f"Data schema validation failed: {e.message}")
        raise


def get_env_variable(var_name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get an environment variable with optional default and required validation.

    Args:
        var_name: Environment variable name
        default: Default value if variable is not set
        required: Whether the variable is required

    Returns:
        Optional[str]: Environment variable value or default

    Raises:
        ValueError: If required variable is not set
    """
    value = os.getenv(var_name, default)

    if required and value is None:
        raise ValueError(f"Required environment variable {var_name} is not set")

    if value is None:
        logger.warning(f"Environment variable {var_name} is not set")

    return value


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path: Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """
    Generate hash for a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')

    Returns:
        str: File hash

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If algorithm is not supported
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if algorithm not in ["md5", "sha1", "sha256"]:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hash_func = getattr(hashlib, algorithm)()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback to default value.

    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Any: Parsed JSON data or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        str: Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def get_dataframe_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get comprehensive information about a DataFrame.

    Args:
        df: Pandas DataFrame

    Returns:
        Dict[str, Any]: DataFrame information
    """
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "memory_usage": df.memory_usage(deep=True).sum(),
        "memory_usage_formatted": format_bytes(df.memory_usage(deep=True).sum()),
        "null_counts": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "numeric_columns": list(df.select_dtypes(include=["number"]).columns),
        "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
        "datetime_columns": list(df.select_dtypes(include=["datetime"]).columns),
    }


def create_backup_filename(original_path: Union[str, Path], timestamp: bool = True) -> str:
    """
    Create a backup filename for a given file path.

    Args:
        original_path: Original file path
        timestamp: Whether to include timestamp in backup name

    Returns:
        str: Backup filename
    """
    path = Path(original_path)
    stem = path.stem
    suffix = path.suffix

    if timestamp:
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{stem}_backup_{timestamp_str}{suffix}"
    else:
        backup_name = f"{stem}_backup{suffix}"

    return str(path.parent / backup_name)


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""

    pass


class DataValidationError(Exception):
    """Custom exception for data validation errors."""

    pass
