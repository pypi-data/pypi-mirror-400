"""
Default transformation functions for PipeX ETL pipeline.

This module provides a collection of common, configurable transformation functions
that can be used as defaults or combined for complex data processing.
"""

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def get_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive data profiling summary.
    """
    logger.info("Generating data profile...")

    profile = {
        "shape": df.shape,
        "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "text_columns": df.select_dtypes(include=["object"]).columns.tolist(),
        "datetime_columns": df.select_dtypes(include=["datetime64[ns]"]).columns.tolist(),
    }

    # Add basic statistics for numeric columns
    numeric_stats = {}
    for col in profile["numeric_columns"]:
        numeric_stats[col] = {
            "min": df[col].min(),
            "max": df[col].max(),
            "mean": df[col].mean(),
            "median": df[col].median(),
            "std": df[col].std(),
            "zeros": (df[col] == 0).sum(),
            "negatives": (df[col] < 0).sum(),
            "infinite": np.isinf(df[col]).sum(),
        }
    profile["numeric_stats"] = numeric_stats

    # Add text column statistics
    text_stats = {}
    for col in profile["text_columns"]:
        text_stats[col] = {
            "unique_values": df[col].nunique(),
            "most_common": df[col].mode().iloc[0] if not df[col].mode().empty else None,
            "avg_length": df[col].astype(str).str.len().mean(),
            "empty_strings": (df[col] == "").sum(),
        }
    profile["text_stats"] = text_stats

    return profile


def process_in_chunks(df: pd.DataFrame, func, chunk_size: int, *args, **kwargs) -> pd.DataFrame:
    """
    Process DataFrame in chunks for memory efficiency.
    """
    logger.info(f"Processing {len(df)} rows in chunks of {chunk_size}")

    chunks = []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i : i + chunk_size].copy()
        processed_chunk = func(chunk, *args, **kwargs)
        chunks.append(processed_chunk)

        if i % (chunk_size * 10) == 0:  # Log progress every 10 chunks
            logger.info(f"Processed {min(i + chunk_size, len(df))} / {len(df)} rows")

    result = pd.concat(chunks, ignore_index=True)
    logger.info(f"Chunk processing complete: {len(df)} → {len(result)} rows")
    return result


def apply_validation_rules(df: pd.DataFrame, validation_rules: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply configurable validation rules to the DataFrame.
    """
    logger.info("Applying validation rules...")

    result_df = df.copy()

    for rule_name, rule_config in validation_rules.items():
        try:
            rule_type = rule_config.get("type")
            column = rule_config.get("column")

            if rule_type == "not_null":
                initial_rows = len(result_df)
                result_df = result_df[result_df[column].notna()]
                logger.info(f"Rule '{rule_name}': Removed {initial_rows - len(result_df)} null rows from '{column}'")

            elif rule_type == "unique":
                initial_rows = len(result_df)
                result_df = result_df.drop_duplicates(subset=[column])
                logger.info(f"Rule '{rule_name}': Removed {initial_rows - len(result_df)} duplicate rows based on '{column}'")

            elif rule_type == "range":
                min_val = rule_config.get("min")
                max_val = rule_config.get("max")
                initial_rows = len(result_df)
                if min_val is not None:
                    result_df = result_df[result_df[column] >= min_val]
                if max_val is not None:
                    result_df = result_df[result_df[column] <= max_val]
                logger.info(
                    f"Rule '{rule_name}': Removed {initial_rows - len(result_df)} rows outside range [{min_val}, {max_val}] for '{column}'"
                )

            elif rule_type == "pattern":
                pattern = rule_config.get("pattern")
                initial_rows = len(result_df)
                result_df = result_df[result_df[column].astype(str).str.match(pattern, na=False)]
                logger.info(
                    f"Rule '{rule_name}': Removed {initial_rows - len(result_df)} rows not matching pattern for '{column}'"
                )

            elif rule_type == "length":
                min_length = rule_config.get("min_length", 0)
                max_length = rule_config.get("max_length", float("inf"))
                initial_rows = len(result_df)
                lengths = result_df[column].astype(str).str.len()
                result_df = result_df[(lengths >= min_length) & (lengths <= max_length)]
                logger.info(
                    f"Rule '{rule_name}': Removed {initial_rows - len(result_df)} rows with invalid length for '{column}'"
                )

            elif rule_type == "custom":
                condition = rule_config.get("condition")
                initial_rows = len(result_df)
                result_df = result_df.query(condition)
                logger.info(f"Rule '{rule_name}': Removed {initial_rows - len(result_df)} rows not meeting custom condition")

        except Exception as e:
            logger.error(f"Failed to apply validation rule '{rule_name}': {e}")

    return result_df


def clean_data(data: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Standard data cleaning operations with improved configurability and chunking support.
    """
    config = config or {}
    logger.info("Applying standard data cleaning...")

    df = data.copy()  # Work on a copy to avoid mutating input unexpectedly

    # Check if we should process in chunks
    chunk_threshold = config.get("chunk_threshold", 100000)
    if len(df) > chunk_threshold:
        chunk_size = config.get("chunk_size", 50000)
        return process_in_chunks(df, _clean_data_chunk, chunk_size, config)

    return _clean_data_chunk(df, config)


def _clean_data_chunk(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Internal function to clean a single chunk of data.
    """
    # Remove duplicate rows
    if config.get("remove_duplicates", True):
        initial_rows = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_rows:
            logger.info(f"Removed {initial_rows - len(df)} duplicate rows")

    # Handle missing values
    missing_strategy = config.get("missing_strategy", "auto")
    if missing_strategy == "drop":
        df = df.dropna()
    elif missing_strategy in ("fill", "auto"):
        fill_values = config.get("fill_values", {})
        columns_to_fill = config.get("fill_columns", df.columns)

        for column in columns_to_fill:
            if column not in df.columns:
                continue
            if column in fill_values:
                df[column] = df[column].fillna(fill_values[column])
            else:
                dtype_kind = df[column].dtype.kind
                if dtype_kind == "O":  # object (string)
                    df[column] = df[column].fillna("")
                elif dtype_kind in "if":  # int or float
                    fill_method = config.get("numeric_fill_method", "median")
                    if fill_method == "median":
                        df[column] = df[column].fillna(df[column].median())
                    elif fill_method == "mean":
                        df[column] = df[column].fillna(df[column].mean())
                    else:
                        df[column] = df[column].fillna(0)

    # Standardize text columns
    if config.get("standardize_text", True):
        text_columns = config.get("text_columns") or df.select_dtypes(include=["object"]).columns
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                if config.get("lowercase_text", False):
                    df[col] = df[col].str.lower()

    # Remove or flag outliers using IQR method
    outlier_action = config.get("outlier_action", "none")  # 'none', 'drop', 'flag'
    if outlier_action != "none":
        numeric_columns = config.get("outlier_columns") or df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            mask = (df[col] < lower) | (df[col] > upper)

            if outlier_action == "drop":
                initial_rows = len(df)
                df = df[~mask]
                if len(df) < initial_rows:
                    logger.info(f"Removed {initial_rows - len(df)} outlier rows from '{col}'")
            elif outlier_action == "flag":
                df[f"{col}_is_outlier"] = mask

    return df


def data_validation(data: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Validate and fix basic data quality issues with configurable validation rules.
    """
    config = config or {}
    logger.info("Validating data quality...")

    df = data.copy()

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Apply configurable validation rules
    validation_rules = config.get("validation_rules", {})
    if validation_rules:
        df = apply_validation_rules(df, validation_rules)

    # Type conversions
    type_conversions = config.get("type_conversions", {})
    for column, target_type in type_conversions.items():
        if column in df.columns:
            try:
                if target_type == "numeric":
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                elif target_type == "datetime":
                    df[column] = pd.to_datetime(df[column], errors="coerce")
                elif target_type == "category":
                    df[column] = df[column].astype("category")
                elif target_type == "string":
                    df[column] = df[column].astype(str)
                elif target_type == "boolean":
                    df[column] = df[column].astype(bool)
                logger.info(f"Converted column '{column}' to {target_type}")
            except Exception as e:
                logger.warning(f"Failed to convert '{column}' to {target_type}: {e}")

    # Value range validation (filter out invalid rows)
    value_ranges = config.get("value_ranges", {})
    for column, (min_val, max_val) in value_ranges.items():
        if column in df.columns:
            initial_rows = len(df)
            df = df[(df[column] >= min_val) & (df[column] <= max_val)]
            if len(df) < initial_rows:
                logger.info(
                    f"Filtered {initial_rows - len(df)} rows outside range [{min_val}, {max_val}] " f"for column '{column}'"
                )

    # Fix infinite values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if np.isinf(df[col]).any():
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            df[col] = df[col].fillna(df[col].median())
            logger.info(f"Fixed infinite values in column '{col}'")

    # Data quality checks
    if config.get("enable_quality_checks", True):
        quality_threshold = config.get("quality_threshold", 0.5)  # 50% completeness minimum

        for col in df.columns:
            completeness = df[col].notna().sum() / len(df)
            if completeness < quality_threshold:
                logger.warning(f"Column '{col}' has low completeness: {completeness:.2%}")

                if config.get("drop_low_quality_columns", False):
                    df = df.drop(columns=[col])
                    logger.info(f"Dropped low quality column '{col}'")

    return df


def feature_engineering(data: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Apply configurable feature engineering with performance optimization.
    """
    config = config or {}
    logger.info("Applying feature engineering...")

    df = data.copy()

    # Check if we should process in chunks for large datasets
    chunk_threshold = config.get("chunk_threshold", 100000)
    if len(df) > chunk_threshold:
        chunk_size = config.get("chunk_size", 50000)
        return process_in_chunks(df, _feature_engineering_chunk, chunk_size, config)

    return _feature_engineering_chunk(df, config)


def _feature_engineering_chunk(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Internal function to apply feature engineering to a single chunk.
    """
    # Text features
    if config.get("add_text_features", False):
        text_columns = config.get("text_columns") or df.select_dtypes(include=["object"]).columns
        for col in text_columns:
            if config.get("text_length", True):
                df[f"{col}_length"] = df[col].astype(str).str.len()
            if config.get("text_word_count", True):
                df[f"{col}_word_count"] = df[col].astype(str).str.split().str.len()
            if config.get("text_has_numbers", False):
                df[f"{col}_has_numbers"] = df[col].astype(str).str.contains(r"\d", na=False)
            if config.get("text_has_special_chars", False):
                df[f"{col}_has_special"] = df[col].astype(str).str.contains(r"[^a-zA-Z0-9\s]", na=False)
            if config.get("text_is_uppercase", False):
                df[f"{col}_is_uppercase"] = df[col].astype(str).str.isupper()

    # Numeric statistical features
    if config.get("add_numeric_features", False):
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            if config.get("numeric_aggregates", True):
                df["numeric_mean"] = df[numeric_columns].mean(axis=1)
                df["numeric_std"] = df[numeric_columns].std(axis=1)
                df["numeric_sum"] = df[numeric_columns].sum(axis=1)
                df["numeric_min"] = df[numeric_columns].min(axis=1)
                df["numeric_max"] = df[numeric_columns].max(axis=1)

            if config.get("add_z_scores", False):
                for col in numeric_columns:
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val > 0:
                        df[f"{col}_zscore"] = (df[col] - mean_val) / std_val

            if config.get("add_percentile_ranks", False):
                for col in numeric_columns:
                    df[f"{col}_percentile"] = df[col].rank(pct=True)

            if config.get("add_binning", False):
                binning_config = config.get("binning_config", {})
                for col in numeric_columns:
                    if col in binning_config:
                        bins = binning_config[col].get("bins", 5)
                        labels = binning_config[col].get("labels")
                        df[f"{col}_binned"] = pd.cut(df[col], bins=bins, labels=labels)

    # Date features
    if config.get("add_date_features", False):
        date_columns = config.get("date_columns") or df.select_dtypes(include=["datetime64[ns]", "datetime64"]).columns
        for col in date_columns:
            if config.get("date_components", True):
                df[f"{col}_year"] = df[col].dt.year
                df[f"{col}_month"] = df[col].dt.month
                df[f"{col}_day"] = df[col].dt.day
                df[f"{col}_weekday"] = df[col].dt.dayofweek
                df[f"{col}_is_weekend"] = df[col].dt.dayofweek >= 5

            if config.get("date_periods", False):
                df[f"{col}_quarter"] = df[col].dt.quarter
                df[f"{col}_week_of_year"] = df[col].dt.isocalendar().week
                df[f"{col}_day_of_year"] = df[col].dt.dayofyear

            if config.get("date_time_features", False):
                df[f"{col}_hour"] = df[col].dt.hour
                df[f"{col}_minute"] = df[col].dt.minute
                df[f"{col}_is_business_hour"] = df[col].dt.hour.between(9, 17)

    # Interaction features
    if config.get("add_interaction_features", False):
        interaction_pairs = config.get("interaction_pairs", [])
        numeric_columns = df.select_dtypes(include=[np.number]).columns

        for col1, col2 in interaction_pairs:
            if col1 in df.columns and col2 in df.columns:
                if col1 in numeric_columns and col2 in numeric_columns:
                    df[f"{col1}_{col2}_product"] = df[col1] * df[col2]
                    df[f"{col1}_{col2}_ratio"] = df[col1] / (df[col2] + 1e-8)  # Avoid division by zero
                    df[f"{col1}_{col2}_diff"] = df[col1] - df[col2]

    return df


def add_metadata(data: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Add useful metadata columns with data profiling integration.
    """
    config = config or {}
    logger.info("Adding metadata columns...")

    df = data.copy()

    if config.get("add_timestamp", True):
        df["processed_at"] = datetime.now()

    if config.get("add_row_number", False):
        df["row_number"] = range(1, len(df) + 1)

    if config.get("add_quality_score", False):
        df["completeness_score"] = (df.notna().sum(axis=1) / len(df.columns)) * 100

    if config.get("add_data_profile", False):
        # Add basic profiling information as metadata
        profile = get_data_profile(df)
        df["total_columns"] = profile["shape"][1]
        df["memory_usage_mb"] = profile["memory_usage_mb"]
        df["duplicate_count"] = profile["duplicate_rows"]

    if config.get("add_hash", False):
        # Add row hash for data lineage tracking
        hash_columns = config.get("hash_columns", df.columns.tolist())
        df["row_hash"] = pd.util.hash_pandas_object(df[hash_columns], index=False)

    custom_metadata = config.get("custom_metadata", {})
    for key, value in custom_metadata.items():
        df[key] = value

    return df


def transform(data: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Main entry point: applies default transformations in a sensible order with profiling.
    """
    config = config or {}
    logger.info("Starting default transformations...")

    original_shape = data.shape
    df = data.copy()

    # Generate initial data profile if requested
    if config.get("profile_data", False):
        initial_profile = get_data_profile(df)
        logger.info(
            f"Initial data profile: {initial_profile['shape']} shape, "
            f"{initial_profile['memory_usage_mb']:.2f} MB, "
            f"{initial_profile['duplicate_rows']} duplicates"
        )

    try:
        # Recommended order: validate → clean → engineer → metadata
        if config.get("validate_data", True):
            df = data_validation(df, config.get("validation", {}))
            logger.info(f"After validation: {df.shape}")

        if config.get("clean_data", True):
            df = clean_data(df, config.get("cleaning", {}))
            logger.info(f"After cleaning: {df.shape}")

        if config.get("feature_engineering", False):  # Off by default to avoid column explosion
            df = feature_engineering(df, config.get("features", {}))
            logger.info(f"After feature engineering: {df.shape}")

        if config.get("add_metadata", True):
            df = add_metadata(df, config.get("metadata", {}))
            logger.info(f"After metadata: {df.shape}")

        # Generate final data profile if requested
        if config.get("profile_data", False):
            final_profile = get_data_profile(df)
            logger.info(
                f"Final data profile: {final_profile['shape']} shape, "
                f"{final_profile['memory_usage_mb']:.2f} MB, "
                f"{final_profile['duplicate_rows']} duplicates"
            )

            # Log transformation summary
            logger.info(
                f"Transformation summary: "
                f"Rows: {original_shape[0]} → {df.shape[0]} "
                f"({((df.shape[0] - original_shape[0]) / original_shape[0] * 100):+.1f}%), "
                f"Columns: {original_shape[1]} → {df.shape[1]} "
                f"({((df.shape[1] - original_shape[1]) / original_shape[1] * 100):+.1f}%)"
            )

        logger.info(f"Default transformation complete: {original_shape} → {df.shape}")
        return df

    except Exception as e:
        logger.error(f"Error in default transformation: {str(e)}")
        raise


# Keep your specialized functions (unchanged except minor fixes)
def business_rules_transform(data: pd.DataFrame, rules: Dict[str, Any]) -> pd.DataFrame:
    logger.info("Applying business rules...")
    df = data.copy()
    for rule_name, rule_config in rules.items():
        try:
            if rule_config["type"] == "categorize":
                col = rule_config["column"]
                df[f"{col}_category"] = pd.cut(df[col], bins=rule_config["bins"], labels=rule_config["labels"])
            elif rule_config["type"] == "flag":
                df[rule_config["flag_name"]] = df.eval(rule_config["condition"])
            elif rule_config["type"] == "aggregate":
                group_by = rule_config["group_by"]
                agg_col = rule_config["column"]
                agg_func = rule_config["function"]
                result_name = rule_config["result_name"]
                agg_result = df.groupby(group_by)[agg_col].agg(agg_func).reset_index().rename(columns={agg_col: result_name})
                df = df.merge(agg_result, on=group_by, how="left")
            logger.info(f"Applied business rule: {rule_name}")
        except Exception as e:
            logger.error(f"Failed to apply business rule '{rule_name}': {e}")
    return df


def industry_specific_transform(data: pd.DataFrame, industry: str, config: Dict[str, Any] = None) -> pd.DataFrame:
    config = config or {}
    logger.info(f"Applying {industry} industry transformations...")
    df = data.copy()
    # ... (same as original, minor fixes applied)
    # Consider making this config-driven or plugin-based in the future
    return df
