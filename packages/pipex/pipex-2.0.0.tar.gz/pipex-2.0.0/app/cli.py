"""
Command Line Interface for PipeX ETL tool.

This module provides the main CLI commands for:
- Running complete ETL pipelines
- Individual extract, transform, load operations
- Interactive configuration
- Pipeline validation and testing
"""

import logging
import os
import sys
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import typer
import yaml

from app.extract import extract_data

# Import PipeX modules
from app.load import load_data
from app.transform import transform_data
from app.utils import apply_env_variables, get_dataframe_info, get_env_variable, load_config, setup_logging, validate_config

# Configure logging
setup_logging()
logger = logging.getLogger("PipeX.CLI")

# Create Typer app
app = typer.Typer(name="pipex", help="PipeX - A powerful ETL pipeline automation tool", add_completion=False)


def validate_file_exists(file_path: str, file_type: str = "file") -> Path:
    """Validate that a file exists and return Path object."""
    path = Path(file_path)
    if not path.exists():
        typer.echo(f"Error: {file_type} not found: {file_path}", err=True)
        raise typer.Exit(1)
    return path


def handle_pipeline_error(error: Exception, stage: str, context: Dict[str, Any] = None) -> None:
    """Handle pipeline errors with comprehensive user guidance."""
    from app.error_handler import handle_pipeline_error as handle_error

    try:
        handle_error(error, stage, context)
    except Exception as pipex_error:
        # If error handling fails, fall back to basic error display
        typer.echo(f"❌ Error in {stage} stage: {str(error)}", err=True)
        raise typer.Exit(1)


@app.command()
def extract(
    source_type: str = typer.Argument(..., help="Source type: api, database, non_relational_database, file"),
    config_file: str = typer.Argument(..., help="Path to configuration file"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (optional)"),
) -> None:
    """Extract data from specified source."""
    try:
        typer.echo(f"🔄 Starting data extraction from {source_type}")

        # Load and validate configuration
        config_path = validate_file_exists(config_file, "Configuration file")
        config = load_config(str(config_path))

        # Validate extract configuration
        if "extract" not in config:
            raise ValueError("Missing 'extract' section in configuration")

        extract_config = config["extract"]
        required_keys = ["connection_details", "query_or_endpoint"]
        validate_config(extract_config, required_keys)

        # Extract data
        data = extract_data(
            source_type=source_type,
            connection_details=extract_config["connection_details"],
            query_or_endpoint=extract_config["query_or_endpoint"],
        )

        # Display data info
        info = get_dataframe_info(data)
        typer.echo(f"✅ Extracted {info['shape'][0]} rows, {info['shape'][1]} columns")
        typer.echo(f"📊 Memory usage: {info['memory_usage_formatted']}")

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.suffix.lower() == ".csv":
                data.to_csv(output_path, index=False)
            elif output_path.suffix.lower() == ".json":
                data.to_json(output_path, orient="records", lines=True)
            else:
                # Default to CSV
                data.to_csv(output_path.with_suffix(".csv"), index=False)

            typer.echo(f"💾 Data saved to: {output_path}")

        typer.echo("✅ Data extraction completed successfully")

    except Exception as e:
        handle_pipeline_error(e, "extraction")


@app.command()
def transform(
    script_path: str = typer.Argument(..., help="Path to transformation script"),
    config_file: str = typer.Argument(..., help="Path to configuration file"),
    input_data: str = typer.Argument(..., help="Input data (JSON string or file path)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (optional)"),
) -> None:
    """Transform data using specified script and configuration."""
    try:
        typer.echo("🔄 Starting data transformation")

        # Load configuration
        config_path = validate_file_exists(config_file, "Configuration file")
        config = load_config(str(config_path))

        # Validate transform configuration
        if "transform" not in config:
            raise ValueError("Missing 'transform' section in configuration")

        transform_config = config["transform"]

        # Load input data
        if Path(input_data).exists():
            # Input is a file path
            input_path = Path(input_data)
            if input_path.suffix.lower() == ".csv":
                data = pd.read_csv(input_path)
            elif input_path.suffix.lower() == ".json":
                data = pd.read_json(input_path, orient="records", lines=True)
            else:
                raise ValueError(f"Unsupported input file format: {input_path.suffix}")
        else:
            # Input is JSON string
            try:
                data = pd.read_json(StringIO(input_data), orient="split")
            except:
                raise ValueError("Invalid input data format. Expected JSON string or file path.")

        typer.echo(f"📊 Input data: {data.shape[0]} rows, {data.shape[1]} columns")

        # Validate script exists
        if script_path and script_path != "none":
            validate_file_exists(script_path, "Transformation script")

        # Transform data
        transformed_data = transform_data(
            script_path=script_path if script_path != "none" else None,
            config=transform_config.get("config", {}),
            data=data,
            options=transform_config.get("options", {}),
        )

        # Display transformation results
        info = get_dataframe_info(transformed_data)
        typer.echo(f"✅ Transformed to {info['shape'][0]} rows, {info['shape'][1]} columns")
        typer.echo(f"📊 Memory usage: {info['memory_usage_formatted']}")

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.suffix.lower() == ".csv":
                transformed_data.to_csv(output_path, index=False)
            elif output_path.suffix.lower() == ".json":
                transformed_data.to_json(output_path, orient="records", lines=True)
            else:
                # Default to CSV
                transformed_data.to_csv(output_path.with_suffix(".csv"), index=False)

            typer.echo(f"💾 Data saved to: {output_path}")

        typer.echo("✅ Data transformation completed successfully")

    except Exception as e:
        handle_pipeline_error(e, "transformation")


@app.command()
def load(
    target_type: str = typer.Argument(..., help="Target type: S3 Bucket, database, non_relational_database, Local File"),
    config_file: str = typer.Argument(..., help="Path to configuration file"),
    input_data: str = typer.Argument(..., help="Input data (JSON string or file path)"),
) -> None:
    """Load data to specified target."""
    try:
        typer.echo(f"🔄 Starting data loading to {target_type}")

        # Load configuration
        config_path = validate_file_exists(config_file, "Configuration file")
        config = load_config(str(config_path))

        # Validate load configuration
        if "load" not in config:
            raise ValueError("Missing 'load' section in configuration")

        load_config_data = config["load"]

        # Load input data
        if Path(input_data).exists():
            # Input is a file path
            input_path = Path(input_data)
            if input_path.suffix.lower() == ".csv":
                data = pd.read_csv(input_path)
            elif input_path.suffix.lower() == ".json":
                data = pd.read_json(input_path, orient="records", lines=True)
            else:
                raise ValueError(f"Unsupported input file format: {input_path.suffix}")
        else:
            # Input is JSON string
            try:
                data = pd.read_json(StringIO(input_data), orient="split")
            except:
                raise ValueError("Invalid input data format. Expected JSON string or file path.")

        typer.echo(f"📊 Loading {data.shape[0]} rows, {data.shape[1]} columns")

        # Load data
        load_data(target=target_type, config=load_config_data.get("config", {}), data=data)

        typer.echo("✅ Data loading completed successfully")

    except Exception as e:
        handle_pipeline_error(e, "loading")


@app.command()
def run(
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Path to configuration file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate configuration without executing pipeline"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Run the complete ETL pipeline."""
    try:
        if verbose:
            setup_logging(logging.DEBUG)

        typer.echo("🚀 Starting PipeX ETL Pipeline")
        typer.echo(f"📋 Configuration: {config_file}")

        # Load and validate configuration
        config_path = validate_file_exists(config_file, "Configuration file")
        config = load_config(str(config_path))

        # Validate required sections
        required_sections = ["extract", "transform", "load"]
        missing_sections = [section for section in required_sections if section not in config]
        if missing_sections:
            raise ValueError(f"Missing required configuration sections: {missing_sections}")

        # Validate each section
        extract_config = config["extract"]
        transform_config = config["transform"]
        load_config_data = config["load"]

        validate_config(extract_config, ["source", "connection_details", "query_or_endpoint"])
        validate_config(load_config_data, ["target", "config"])

        if dry_run:
            typer.echo("✅ Configuration validation completed successfully")
            typer.echo("🔍 Dry run mode - pipeline not executed")
            return

        # Step 1: Extract data
        typer.echo("\n📥 Step 1: Extracting data...")
        extracted_data = extract_data(
            source_type=extract_config["source"],
            connection_details=extract_config["connection_details"],
            query_or_endpoint=extract_config["query_or_endpoint"],
        )

        extract_info = get_dataframe_info(extracted_data)
        typer.echo(f"✅ Extracted {extract_info['shape'][0]} rows, {extract_info['shape'][1]} columns")

        # Step 2: Transform data
        typer.echo("\n🔄 Step 2: Transforming data...")
        script_path = transform_config.get("script")
        if script_path and script_path != "none":
            validate_file_exists(script_path, "Transformation script")

        transformed_data = transform_data(
            script_path=script_path if script_path and script_path != "none" else None,
            config=transform_config.get("config", {}),
            data=extracted_data,
            options=transform_config.get("options", {}),
        )

        transform_info = get_dataframe_info(transformed_data)
        typer.echo(f"✅ Transformed to {transform_info['shape'][0]} rows, {transform_info['shape'][1]} columns")

        # Step 3: Load data
        typer.echo("\n📤 Step 3: Loading data...")
        load_data(target=load_config_data["target"], config=load_config_data["config"], data=transformed_data)

        typer.echo("\n🎉 ETL Pipeline completed successfully!")
        typer.echo(f"📊 Final dataset: {transform_info['shape'][0]} rows, {transform_info['shape'][1]} columns")
        typer.echo(f"💾 Memory usage: {transform_info['memory_usage_formatted']}")

    except Exception as e:
        handle_pipeline_error(e, "pipeline execution")


@app.command()
def validate(config_file: str = typer.Argument(..., help="Path to configuration file")) -> None:
    """Validate configuration file."""
    try:
        typer.echo("🔍 Validating configuration...")

        # Load configuration
        config_path = validate_file_exists(config_file, "Configuration file")
        config = load_config(str(config_path))

        # Validate structure
        required_sections = ["extract", "transform", "load"]
        missing_sections = [section for section in required_sections if section not in config]
        if missing_sections:
            raise ValueError(f"Missing required sections: {missing_sections}")

        # Validate extract section
        extract_config = config["extract"]
        validate_config(extract_config, ["source", "connection_details", "query_or_endpoint"])

        # Validate load section
        load_config_data = config["load"]
        validate_config(load_config_data, ["target", "config"])

        # Check transformation script if specified
        transform_config = config.get("transform", {})
        script_path = transform_config.get("script")
        if script_path and script_path != "none":
            validate_file_exists(script_path, "Transformation script")

        typer.echo("✅ Configuration validation completed successfully")
        typer.echo(f"📋 Extract source: {extract_config['source']}")
        typer.echo(f"🔄 Transform script: {script_path or 'Config-based only'}")
        typer.echo(f"📤 Load target: {load_config_data['target']}")

    except Exception as e:
        handle_pipeline_error(e, "configuration validation")


@app.command()
def info() -> None:
    """Display PipeX information and system status."""
    typer.echo("🔧 PipeX ETL Pipeline Tool")
    typer.echo("=" * 40)
    typer.echo(f"Version: 0.2.0")
    typer.echo(f"Python: {sys.version.split()[0]}")

    # Check environment variables
    typer.echo("\n🌍 Environment Variables:")
    env_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]
    for var in env_vars:
        value = get_env_variable(var)
        status = "✅ Set" if value else "❌ Not set"
        typer.echo(f"  {var}: {status}")

    # Check current directory
    typer.echo(f"\n📁 Current directory: {Path.cwd()}")

    # Check for config files
    config_files = list(Path.cwd().glob("*.yaml")) + list(Path.cwd().glob("*.yml"))
    if config_files:
        typer.echo("\n📋 Configuration files found:")
        for config_file in config_files:
            typer.echo(f"  - {config_file.name}")
    else:
        typer.echo("\n📋 No configuration files found in current directory")


if __name__ == "__main__":
    app()
