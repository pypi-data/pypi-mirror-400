"""
Data transformation module for PipeX ETL tool.

This module provides comprehensive data transformation capabilities including:
- Script-based transformations with custom Python functions
- Configuration-based transformations (drop, rename, filter, add columns)
- Multiple script support for complex transformation pipelines
- Default transformation functions for common use cases
- Progress tracking and error handling
"""

import logging
from typing import Any, Dict, List, Union

import pandas as pd
from tqdm import tqdm

logger = logging.getLogger("PipelineX.Transform")
logging.basicConfig(level=logging.INFO)


def load_transformation_script(script_path: str):
    """Safely load a transformation script as a Python module."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("transform_script", script_path)
    transform_script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transform_script)
    return transform_script


def apply_transformations(data: pd.DataFrame, config: Dict[str, Any], options: Dict[str, bool]) -> pd.DataFrame:
    """
    Apply transformations to the dataframe based on the config dictionary.

    Parameters:
        data: pd.DataFrame: Input dataframe to be transformed.
        config: Dict[str, Any]: Config dictionary containing transformation parameters.
        options: Dict[str, bool]: Options dictionary containing transformation options.

    Returns:
        pd.DataFrame: Transformed dataframe.
    """
    try:
        # Define steps for progress tracking
        steps = [
            {"action": "drop_columns", "desc": "Dropping Columns"},
            {"action": "rename_columns", "desc": "Renaming Columns"},
            {"action": "filter_rows", "desc": "Filtering Rows"},
            {"action": "add_columns", "desc": "Adding Columns"},
        ]

        # Initialize progress bar
        with tqdm(total=len(steps), desc="Applying Transformations", unit="step") as pbar:
            # Drop columns
            if options.get("drop_columns", True) and "drop_columns" in config:
                logger.info(f"Dropping columns: {config['drop_columns']}")
                data = data.drop(columns=config["drop_columns"], errors="ignore")
                pbar.set_description("Dropping Columns")
                pbar.update(1)

            # Rename columns
            if options.get("rename_columns", True) and "rename_columns" in config:
                logger.info(f"Renaming columns: {config['rename_columns']}")
                data = data.rename(columns=config["rename_columns"])
                pbar.set_description("Renaming Columns")
                pbar.update(1)

            # Filter rows using query
            if options.get("filter_rows", True) and "filter_rows" in config:
                logger.info(f"Filtering rows using query: {config['filter_rows']}")
                data = data.query(config["filter_rows"]).reset_index(drop=True)
                pbar.set_description("Filtering Rows")
                pbar.update(1)

            # Add columns
            if options.get("add_columns", True) and "add_columns" in config:
                logger.info(f"Adding columns: {config['add_columns']}")
                for col_name, col_formula in config["add_columns"].items():
                    # Make pandas available in the eval context
                    if "pd.Timestamp.now()" in col_formula:
                        data[col_name] = pd.Timestamp.now()
                    else:
                        data[col_name] = data.eval(col_formula)
                pbar.set_description("Adding Columns")
                pbar.update(1)

        return data

    except Exception as e:
        logger.error(f"Error in transformations: {str(e)}")
        raise


def transform_data(
    script_path: Union[str, List[str]], config: Dict[str, Any], data: pd.DataFrame, options: Dict[str, bool] = None
) -> pd.DataFrame:
    """
    Apply both script-based and config-based transformations to the dataframe.

    Parameters:
        script_path: Path to transformation script(s) or list of paths
        config: Config dictionary containing transformation parameters
        data: Input dataframe to be transformed
        options: Options dictionary containing transformation options

    Returns:
        pd.DataFrame: Transformed dataframe
    """
    if options is None:
        options = {
            "drop_columns": True,
            "rename_columns": True,
            "filter_rows": True,
            "add_columns": True,
        }

    try:
        # Handle multiple script paths
        script_paths = []
        if isinstance(script_path, str):
            if script_path and script_path.lower() not in ["none", "null", ""]:
                script_paths = [script_path]
        elif isinstance(script_path, list):
            script_paths = [path for path in script_path if path and path.lower() not in ["none", "null", ""]]

        # Apply external transformation scripts if provided
        for i, path in enumerate(script_paths):
            logger.info(f"Loading transformation script {i+1}/{len(script_paths)}: {path}")

            try:
                transform_script = load_transformation_script(path)
                if hasattr(transform_script, "transform"):
                    with tqdm(total=1, desc=f"Applying Script {i+1}", unit="step") as pbar:
                        data = transform_script.transform(data, config.get("script_config", {}))
                        pbar.update(1)
                else:
                    logger.warning(f"No transform function found in script {path}. Skipping.")
            except Exception as e:
                logger.error(f"Error in transformation script {path}: {str(e)}")
                if config.get("fail_on_script_error", True):
                    raise
                else:
                    logger.warning(f"Continuing with next script due to fail_on_script_error=False")

        # If no custom scripts provided, use default transformations
        if not script_paths and config.get("use_default_transforms", True):
            logger.info("No custom scripts provided, applying default transformations")
            from app.default_transforms import transform as default_transform

            with tqdm(total=1, desc="Applying Default Transformations", unit="step") as pbar:
                data = default_transform(data, config.get("default_config", {}))
                pbar.update(1)

        # Apply config-based transformations
        if any(options.values()):
            data = apply_transformations(data, config, options)

        logger.info("Data transformation completed successfully.")
        return data

    except Exception as e:
        logger.error(f"Error in data transformation: {str(e)}")
        raise
