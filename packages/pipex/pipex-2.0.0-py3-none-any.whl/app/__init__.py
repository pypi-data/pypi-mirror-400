"""
PipeX - A powerful CLI-based ETL pipeline automation tool.

This package provides comprehensive ETL functionality including:
- Data extraction from APIs, databases, and files (CSV, JSON, Excel, Parquet, XML)
- Data transformation with custom scripts and configurations
- Data loading to various targets (Local files, AWS S3, GCP, Azure, DigitalOcean)
- Multi-cloud storage support
- Advanced error handling with user guidance
- Industry-specific transformation templates
- Robust error handling and logging
- Environment variable management
"""

import logging

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Import core modules that don't have optional dependencies
from .api import APIClient
from .default_transforms import add_metadata, clean_data, data_validation, feature_engineering
from .default_transforms import transform as default_transform
from .error_handler import ErrorHandler, PipeXError, handle_pipeline_error
from .utils import apply_env_variables, get_env_variable, load_config, setup_logging, validate_config, validate_data_schema

# Import main functions
from .extract import extract_data
from .transform import transform_data

# Conditional imports for modules with optional dependencies
try:
    from .load import load_data
    HAS_LOAD = True
except ImportError:
    HAS_LOAD = False
    load_data = None

try:
    from .storage import download_from_s3, file_exists_in_s3, save_and_upload, save_to_file, upload_to_s3
    HAS_STORAGE = True
except ImportError:
    HAS_STORAGE = False
    download_from_s3 = file_exists_in_s3 = save_and_upload = save_to_file = upload_to_s3 = None

try:
    from .cloud_storage import download_from_cloud, get_cloud_provider, upload_to_cloud
    HAS_CLOUD_STORAGE = True
except ImportError:
    HAS_CLOUD_STORAGE = False
    download_from_cloud = get_cloud_provider = upload_to_cloud = None

__version__ = "2.0.0"

# Build __all__ list dynamically based on available imports
__all__ = [
    # Core ETL functions (always available)
    "extract_data",
    "transform_data",
    # API client
    "APIClient",
    # Utility functions
    "setup_logging",
    "load_config",
    "validate_data_schema",
    "get_env_variable",
    "apply_env_variables",
    "validate_config",
    # Default transformations
    "clean_data",
    "add_metadata",
    "feature_engineering",
    "data_validation",
    "default_transform",
    # Error handling
    "PipeXError",
    "ErrorHandler",
    "handle_pipeline_error",
    # Version
    "__version__",
]

# Add conditional exports
if HAS_LOAD:
    __all__.append("load_data")

if HAS_STORAGE:
    __all__.extend([
        "save_to_file",
        "upload_to_s3",
        "download_from_s3",
        "file_exists_in_s3",
        "save_and_upload",
    ])

if HAS_CLOUD_STORAGE:
    __all__.extend([
        "get_cloud_provider",
        "upload_to_cloud",
        "download_from_cloud",
    ])
