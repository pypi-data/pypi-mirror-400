"""
Comprehensive error handling and user guidance system for PipeX.

This module provides detailed error messages with actionable solutions
to help users quickly resolve issues.
"""

import logging
import traceback
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors for better organization."""

    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    DATA_FORMAT = "data_format"
    FILE_SYSTEM = "file_system"
    DEPENDENCY = "dependency"
    TRANSFORMATION = "transformation"
    CLOUD_STORAGE = "cloud_storage"
    DATABASE = "database"
    VALIDATION = "validation"


class PipeXError(Exception):
    """Base exception class for PipeX with enhanced error information."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        solutions: List[str] = None,
        original_error: Exception = None,
        context: Dict[str, Any] = None,
    ):
        self.message = message
        self.category = category
        self.solutions = solutions or []
        self.original_error = original_error
        self.context = context or {}
        super().__init__(self.message)

    def get_user_friendly_message(self) -> str:
        """Generate a user-friendly error message with solutions."""
        msg = f"\n❌ {self.category.value.title()} Error: {self.message}\n"

        if self.context:
            msg += "\n📋 Context:\n"
            for key, value in self.context.items():
                msg += f"  • {key}: {value}\n"

        if self.solutions:
            msg += "\n💡 Suggested Solutions:\n"
            for i, solution in enumerate(self.solutions, 1):
                msg += f"  {i}. {solution}\n"

        if self.original_error:
            msg += f"\n🔍 Technical Details: {str(self.original_error)}\n"

        return msg


class ErrorHandler:
    """Centralized error handling with user-friendly messages and solutions."""

    @staticmethod
    def handle_configuration_error(error: Exception, config_file: str = None) -> PipeXError:
        """Handle configuration-related errors."""
        error_msg = str(error).lower()

        if "missing required" in error_msg:
            return PipeXError(
                message="Required configuration keys are missing",
                category=ErrorCategory.CONFIGURATION,
                solutions=[
                    f"Check your configuration file: {config_file or 'config.yaml'}",
                    "Ensure all required sections (extract, transform, load) are present",
                    "Validate your configuration with: pipex validate <config_file>",
                    "Refer to the documentation for configuration examples",
                ],
                original_error=error,
                context={"config_file": config_file},
            )

        elif "unresolved" in error_msg and "placeholder" in error_msg:
            return PipeXError(
                message="Environment variable placeholders are not resolved",
                category=ErrorCategory.CONFIGURATION,
                solutions=[
                    "Create a .env file in your project root",
                    "Set the required environment variables (check .env.example)",
                    "Ensure environment variable names match the placeholders in config",
                    "Use format ${VARIABLE_NAME} for placeholders in config file",
                ],
                original_error=error,
                context={"config_file": config_file},
            )

        elif "yaml" in error_msg or "parsing" in error_msg:
            return PipeXError(
                message="Configuration file has invalid YAML syntax",
                category=ErrorCategory.CONFIGURATION,
                solutions=[
                    "Check YAML syntax - ensure proper indentation (use spaces, not tabs)",
                    "Validate YAML online at yamllint.com",
                    "Ensure all strings with special characters are quoted",
                    "Check for missing colons after keys",
                ],
                original_error=error,
                context={"config_file": config_file},
            )

        else:
            return PipeXError(
                message="Configuration error occurred",
                category=ErrorCategory.CONFIGURATION,
                solutions=[
                    "Validate your configuration file syntax",
                    "Check the documentation for correct configuration format",
                    "Use pipex validate <config_file> to check for issues",
                ],
                original_error=error,
                context={"config_file": config_file},
            )

    @staticmethod
    def handle_authentication_error(error: Exception, provider: str = None) -> PipeXError:
        """Handle authentication-related errors."""
        error_msg = str(error).lower()

        if "credentials not found" in error_msg or "no credentials" in error_msg:
            solutions = [
                "Set up your credentials in environment variables",
                "Check .env.example for required credential names",
            ]

            if provider and provider.lower() in ["aws", "s3"]:
                solutions.extend(
                    [
                        "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY",
                        "Optionally set AWS_REGION (defaults to us-east-1)",
                        "Or configure AWS CLI: aws configure",
                    ]
                )
            elif provider and provider.lower() in ["gcp", "gcs", "google"]:
                solutions.extend(
                    [
                        "Set GOOGLE_APPLICATION_CREDENTIALS to your service account key file",
                        "Or set GOOGLE_CLOUD_PROJECT for your project ID",
                        "Download service account key from Google Cloud Console",
                    ]
                )
            elif provider and provider.lower() == "azure":
                solutions.extend(
                    [
                        "Set AZURE_STORAGE_CONNECTION_STRING",
                        "Or set AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY",
                        "Get connection string from Azure Portal",
                    ]
                )

            return PipeXError(
                message=f"Authentication credentials not found for {provider or 'service'}",
                category=ErrorCategory.AUTHENTICATION,
                solutions=solutions,
                original_error=error,
                context={"provider": provider},
            )

        elif "access denied" in error_msg or "forbidden" in error_msg:
            return PipeXError(
                message="Access denied - insufficient permissions",
                category=ErrorCategory.AUTHENTICATION,
                solutions=[
                    "Check if your credentials have the required permissions",
                    "Verify bucket/container names are correct",
                    "Ensure your account has read/write access to the resource",
                    "Contact your administrator for permission updates",
                ],
                original_error=error,
                context={"provider": provider},
            )

        else:
            return PipeXError(
                message="Authentication error occurred",
                category=ErrorCategory.AUTHENTICATION,
                solutions=[
                    "Verify your credentials are correct and not expired",
                    "Check network connectivity to the service",
                    "Ensure the service endpoint is accessible",
                ],
                original_error=error,
                context={"provider": provider},
            )

    @staticmethod
    def handle_network_error(error: Exception, endpoint: str = None) -> PipeXError:
        """Handle network-related errors."""
        error_msg = str(error).lower()

        if "timeout" in error_msg:
            return PipeXError(
                message="Network request timed out",
                category=ErrorCategory.NETWORK,
                solutions=[
                    "Check your internet connection",
                    "Increase timeout value in configuration",
                    "Verify the endpoint URL is correct and accessible",
                    "Try again later - the service might be temporarily unavailable",
                ],
                original_error=error,
                context={"endpoint": endpoint},
            )

        elif "connection" in error_msg and ("refused" in error_msg or "failed" in error_msg):
            return PipeXError(
                message="Connection to service failed",
                category=ErrorCategory.NETWORK,
                solutions=[
                    "Verify the endpoint URL is correct",
                    "Check if the service is running and accessible",
                    "Ensure no firewall is blocking the connection",
                    "Check if you're behind a proxy that needs configuration",
                ],
                original_error=error,
                context={"endpoint": endpoint},
            )

        elif "ssl" in error_msg or "certificate" in error_msg:
            return PipeXError(
                message="SSL/TLS certificate error",
                category=ErrorCategory.NETWORK,
                solutions=[
                    "Check if the SSL certificate is valid and not expired",
                    "Verify system date and time are correct",
                    "Update your system's certificate store",
                    "Contact the service provider if certificate issues persist",
                ],
                original_error=error,
                context={"endpoint": endpoint},
            )

        else:
            return PipeXError(
                message="Network error occurred",
                category=ErrorCategory.NETWORK,
                solutions=["Check your internet connection", "Verify the service endpoint is accessible", "Try again later"],
                original_error=error,
                context={"endpoint": endpoint},
            )

    @staticmethod
    def handle_file_error(error: Exception, file_path: str = None) -> PipeXError:
        """Handle file system errors."""
        error_msg = str(error).lower()

        if "no such file" in error_msg or "not found" in error_msg:
            return PipeXError(
                message=f"File not found: {file_path}",
                category=ErrorCategory.FILE_SYSTEM,
                solutions=[
                    "Check if the file path is correct",
                    "Ensure the file exists in the specified location",
                    "Use absolute path or verify relative path is correct",
                    "Check file permissions and accessibility",
                ],
                original_error=error,
                context={"file_path": file_path},
            )

        elif "permission denied" in error_msg:
            return PipeXError(
                message="Permission denied accessing file",
                category=ErrorCategory.FILE_SYSTEM,
                solutions=[
                    "Check file permissions - ensure read/write access",
                    "Run with appropriate user permissions",
                    "Ensure the directory is writable for output files",
                    "Check if file is locked by another process",
                ],
                original_error=error,
                context={"file_path": file_path},
            )

        elif "directory" in error_msg and "not found" in error_msg:
            return PipeXError(
                message="Directory not found",
                category=ErrorCategory.FILE_SYSTEM,
                solutions=[
                    "Create the directory structure manually",
                    "Enable automatic directory creation in configuration",
                    "Check if parent directories exist",
                    "Verify the path is correct",
                ],
                original_error=error,
                context={"file_path": file_path},
            )

        else:
            return PipeXError(
                message="File system error occurred",
                category=ErrorCategory.FILE_SYSTEM,
                solutions=[
                    "Check file path and permissions",
                    "Ensure sufficient disk space",
                    "Verify file is not locked by another process",
                ],
                original_error=error,
                context={"file_path": file_path},
            )

    @staticmethod
    def handle_data_format_error(error: Exception, file_type: str = None, data_source: str = None) -> PipeXError:
        """Handle data format and parsing errors."""
        error_msg = str(error).lower()

        if "json" in error_msg and ("decode" in error_msg or "parse" in error_msg):
            return PipeXError(
                message="Invalid JSON format",
                category=ErrorCategory.DATA_FORMAT,
                solutions=[
                    "Validate JSON syntax using online JSON validator",
                    "Check for missing quotes, commas, or brackets",
                    "Ensure proper encoding (UTF-8 recommended)",
                    "Verify the API returns valid JSON response",
                ],
                original_error=error,
                context={"file_type": file_type, "data_source": data_source},
            )

        elif "csv" in error_msg or "delimiter" in error_msg:
            return PipeXError(
                message="CSV parsing error",
                category=ErrorCategory.DATA_FORMAT,
                solutions=[
                    "Check CSV delimiter/separator in configuration",
                    "Verify file encoding (try UTF-8, UTF-16, or latin-1)",
                    "Ensure consistent number of columns across rows",
                    "Check for special characters that need escaping",
                ],
                original_error=error,
                context={"file_type": file_type, "data_source": data_source},
            )

        elif "excel" in error_msg or "xlsx" in error_msg:
            return PipeXError(
                message="Excel file parsing error",
                category=ErrorCategory.DATA_FORMAT,
                solutions=[
                    "Ensure the Excel file is not corrupted",
                    "Check if the specified sheet name exists",
                    "Verify the file is not password protected",
                    "Install openpyxl: pip install openpyxl",
                ],
                original_error=error,
                context={"file_type": file_type, "data_source": data_source},
            )

        elif "encoding" in error_msg:
            return PipeXError(
                message="File encoding error",
                category=ErrorCategory.DATA_FORMAT,
                solutions=[
                    "Try different encodings: utf-8, utf-16, latin-1, cp1252",
                    "Specify encoding in configuration file",
                    "Use a text editor to check file encoding",
                    "Convert file to UTF-8 encoding",
                ],
                original_error=error,
                context={"file_type": file_type, "data_source": data_source},
            )

        else:
            return PipeXError(
                message="Data format error",
                category=ErrorCategory.DATA_FORMAT,
                solutions=[
                    "Verify the data format matches the specified type",
                    "Check for data corruption or incomplete files",
                    "Ensure proper file encoding",
                ],
                original_error=error,
                context={"file_type": file_type, "data_source": data_source},
            )

    @staticmethod
    def handle_dependency_error(error: Exception, package: str = None) -> PipeXError:
        """Handle missing dependency errors."""
        error_msg = str(error).lower()

        if "no module named" in error_msg or "import" in error_msg:
            missing_package = package or error_msg.split("'")[1] if "'" in error_msg else "unknown"

            install_commands = {
                "boto3": "pip install boto3",
                "google-cloud-storage": "pip install google-cloud-storage",
                "azure-storage-blob": "pip install azure-storage-blob",
                "openpyxl": "pip install openpyxl",
                "xlrd": "pip install xlrd",
                "lxml": "pip install lxml",
                "pyarrow": "pip install pyarrow",
                "fastparquet": "pip install fastparquet",
            }

            install_cmd = install_commands.get(missing_package, f"pip install {missing_package}")

            return PipeXError(
                message=f"Required package '{missing_package}' is not installed",
                category=ErrorCategory.DEPENDENCY,
                solutions=[
                    f"Install the package: {install_cmd}",
                    "Or install all optional dependencies: pip install pipex[all]",
                    "Check if you're in the correct virtual environment",
                    "Update pip if installation fails: pip install --upgrade pip",
                ],
                original_error=error,
                context={"missing_package": missing_package},
            )

        else:
            return PipeXError(
                message="Dependency error occurred",
                category=ErrorCategory.DEPENDENCY,
                solutions=[
                    "Check if all required packages are installed",
                    "Update packages: pip install --upgrade -r requirements.txt",
                    "Recreate virtual environment if issues persist",
                ],
                original_error=error,
            )

    @staticmethod
    def handle_transformation_error(error: Exception, script_path: str = None, column: str = None) -> PipeXError:
        """Handle data transformation errors."""
        error_msg = str(error).lower()

        if "not defined" in error_msg:
            undefined_item = error_msg.split("'")[1] if "'" in error_msg else "unknown"
            return PipeXError(
                message=f"Variable or column '{undefined_item}' is not defined",
                category=ErrorCategory.TRANSFORMATION,
                solutions=[
                    "Check if the column exists in your data",
                    "Verify column names match exactly (case-sensitive)",
                    "Ensure transformations are applied in correct order",
                    "Check transformation script for typos",
                ],
                original_error=error,
                context={"script_path": script_path, "undefined_item": undefined_item},
            )

        elif "keyerror" in error_msg or "column" in error_msg:
            return PipeXError(
                message="Column not found in data",
                category=ErrorCategory.TRANSFORMATION,
                solutions=[
                    "Check available columns in your data",
                    "Verify column names in configuration match data",
                    "Ensure previous transformations didn't remove required columns",
                    "Use data.columns to see available column names",
                ],
                original_error=error,
                context={"script_path": script_path, "column": column},
            )

        elif "syntax" in error_msg:
            return PipeXError(
                message="Syntax error in transformation script",
                category=ErrorCategory.TRANSFORMATION,
                solutions=[
                    "Check Python syntax in transformation script",
                    "Ensure proper indentation (use spaces, not tabs)",
                    "Verify all brackets and quotes are properly closed",
                    "Test script independently before using in pipeline",
                ],
                original_error=error,
                context={"script_path": script_path},
            )

        else:
            return PipeXError(
                message="Data transformation error",
                category=ErrorCategory.TRANSFORMATION,
                solutions=[
                    "Check transformation script for errors",
                    "Verify data types are compatible with operations",
                    "Ensure required columns exist in data",
                    "Test transformations on sample data first",
                ],
                original_error=error,
                context={"script_path": script_path},
            )

    @staticmethod
    def wrap_error(error: Exception, context: Dict[str, Any] = None) -> PipeXError:
        """
        Wrap any exception into a PipeXError with appropriate handling.

        Args:
            error: Original exception
            context: Additional context information

        Returns:
            PipeXError: Wrapped error with user-friendly message
        """
        context = context or {}
        error_msg = str(error).lower()

        # Try to categorize the error based on content
        if any(keyword in error_msg for keyword in ["config", "yaml", "missing required", "placeholder"]):
            return ErrorHandler.handle_configuration_error(error, context.get("config_file"))

        elif any(keyword in error_msg for keyword in ["credentials", "access denied", "forbidden", "unauthorized"]):
            return ErrorHandler.handle_authentication_error(error, context.get("provider"))

        elif any(keyword in error_msg for keyword in ["timeout", "connection", "network", "ssl", "certificate"]):
            return ErrorHandler.handle_network_error(error, context.get("endpoint"))

        elif any(keyword in error_msg for keyword in ["file not found", "no such file", "permission denied", "directory"]):
            return ErrorHandler.handle_file_error(error, context.get("file_path"))

        elif any(keyword in error_msg for keyword in ["json", "csv", "excel", "encoding", "parse", "decode"]):
            return ErrorHandler.handle_data_format_error(error, context.get("file_type"), context.get("data_source"))

        elif any(keyword in error_msg for keyword in ["no module", "import", "package"]):
            return ErrorHandler.handle_dependency_error(error, context.get("package"))

        elif any(keyword in error_msg for keyword in ["not defined", "keyerror", "column", "syntax"]):
            return ErrorHandler.handle_transformation_error(error, context.get("script_path"), context.get("column"))

        else:
            # Generic error handling
            return PipeXError(
                message=f"An unexpected error occurred: {str(error)}",
                category=ErrorCategory.VALIDATION,
                solutions=[
                    "Check the error details below for more information",
                    "Verify your configuration and data are correct",
                    "Try running with --verbose flag for more details",
                    "Check the documentation for similar issues",
                ],
                original_error=error,
                context=context,
            )


def log_error_with_context(error: Exception, context: Dict[str, Any] = None, logger_instance: logging.Logger = None) -> None:
    """
    Log error with full context and traceback.

    Args:
        error: Exception to log
        context: Additional context information
        logger_instance: Logger instance to use
    """
    log = logger_instance or logger
    context = context or {}

    log.error(f"Error occurred: {str(error)}")
    if context:
        log.error(f"Context: {context}")
    log.error(f"Traceback: {traceback.format_exc()}")


def handle_pipeline_error(error: Exception, stage: str, context: Dict[str, Any] = None) -> None:
    """
    Handle pipeline errors with user-friendly messages.

    Args:
        error: Exception that occurred
        stage: Pipeline stage where error occurred
        context: Additional context information
    """
    context = context or {}
    context["stage"] = stage

    # Wrap the error with appropriate handling
    pipex_error = ErrorHandler.wrap_error(error, context)

    # Log the error with full context
    log_error_with_context(error, context)

    # Print user-friendly message
    print(pipex_error.get_user_friendly_message())

    # Re-raise as PipeXError
    raise pipex_error
