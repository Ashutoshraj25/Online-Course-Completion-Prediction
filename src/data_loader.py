"""Data loading and inspection module using PySpark.

Provides utilities to ingest the online course engagement dataset,
verify schema, compute data health metrics (missing values, exact duplicates),
and summarize category & target distributions.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from src.spark_session import get_spark_session, stop_spark_session

DEFAULT_DATASET_PATHS = [
    Path("dataset") / "online_course_engagement_data.csv",
    Path("online_course_engagement_data.csv"),
    Path(__file__).resolve().parent.parent / "dataset" / "online_course_engagement_data.csv",
]


def resolve_dataset_path(custom_path: Optional[str] = None) -> Path:
    """Find the valid dataset CSV file path."""
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p.resolve()
        raise FileNotFoundError(f"Dataset not found at specified path: {custom_path}")

    for candidate in DEFAULT_DATASET_PATHS:
        if candidate.exists():
            return candidate.resolve()

    raise FileNotFoundError(
        "Could not locate 'online_course_engagement_data.csv' in dataset/ or root directory."
    )


def load_data(
    spark: SparkSession, file_path: Optional[str] = None
) -> DataFrame:
    """Read online course engagement dataset into a Spark DataFrame.

    Enables header detection and automatic schema inference.

    Args:
        spark: Active SparkSession.
        file_path: Optional path to the CSV file.

    Returns:
        Spark DataFrame with typed columns.
    """
    resolved_path = resolve_dataset_path(file_path)
    # Use normalized posix path string for Spark
    path_str = resolved_path.as_posix()

    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load(path_str)
    )
    return df


def get_dataset_summary(df: DataFrame) -> Dict[str, Any]:
    """Compute comprehensive data quality and distribution metrics.

    Args:
        df: Input PySpark DataFrame.

    Returns:
        Dictionary containing record counts, missing values, duplicates,
        course categories, and target distributions.
    """
    total_records = df.count()
    total_columns = len(df.columns)

    # Calculate missing/null values per column
    null_exprs = []
    for c, dtype in df.dtypes:
        if dtype in ("double", "float"):
            cond = F.col(c).isNull() | F.isnan(F.col(c))
        elif dtype == "string":
            cond = F.col(c).isNull() | (F.trim(F.col(c)) == "")
        else:
            cond = F.col(c).isNull()
        null_exprs.append(F.count(F.when(cond, c)).alias(c))
    null_counts_row = df.select(null_exprs).collect()[0].asDict()

    # Exact duplicates count (across all 9 columns)
    distinct_count = df.dropDuplicates().count()
    duplicate_records = total_records - distinct_count

    # Distinct course categories
    categories = [
        row["CourseCategory"]
        for row in df.select("CourseCategory").distinct().orderBy("CourseCategory").collect()
        if row["CourseCategory"] is not None
    ]

    # Distinct device types
    device_types = [
        row["DeviceType"]
        for row in df.select("DeviceType").distinct().orderBy("DeviceType").collect()
        if row["DeviceType"] is not None
    ]

    # Target class distribution
    target_rows = (
        df.groupBy("CourseCompletion")
        .count()
        .orderBy("CourseCompletion")
        .collect()
    )
    target_distribution: Dict[int, Dict[str, Any]] = {}
    for r in target_rows:
        val = int(r["CourseCompletion"])
        cnt = int(r["count"])
        pct = round((cnt / total_records) * 100, 2) if total_records > 0 else 0.0
        target_distribution[val] = {"count": cnt, "percentage": pct}

    return {
        "total_records": total_records,
        "total_columns": total_columns,
        "columns": df.dtypes,
        "missing_values": null_counts_row,
        "duplicate_records": duplicate_records,
        "distinct_categories": categories,
        "distinct_device_types": device_types,
        "target_distribution": target_distribution,
    }


def display_dataset_info(df: DataFrame, summary: Dict[str, Any]) -> None:
    """Print formatted dataset statistics to console."""
    print("=" * 60)
    print("ONLINE COURSE ENGAGEMENT DATASET SUMMARY")
    print("=" * 60)
    print(f"Total Records  : {summary['total_records']}")
    print(f"Total Columns  : {summary['total_columns']}")
    print(f"Exact Duplicates: {summary['duplicate_records']}")
    print("\n--- Schema ---")
    df.printSchema()

    print("\n--- First 5 Records ---")
    df.show(5, truncate=False)

    print("--- Missing Values Per Column ---")
    for col_name, null_cnt in summary["missing_values"].items():
        print(f"  {col_name:25s}: {null_cnt}")

    print("\n--- Distinct Course Categories ---")
    print(f"  {summary['distinct_categories']}")

    print("\n--- Distinct Device Types ---")
    print(f"  {summary['distinct_device_types']}")

    print("\n--- Target Class Distribution (CourseCompletion) ---")
    for label, info in summary["target_distribution"].items():
        name = "Completed (1)" if label == 1 else "Not Completed (0)"
        print(f"  Class {name:18s}: {info['count']:5d} ({info['percentage']}%)")
    print("=" * 60)


if __name__ == "__main__":
    spark = get_spark_session()
    try:
        raw_df = load_data(spark)
        summary = get_dataset_summary(raw_df)
        display_dataset_info(raw_df, summary)
    finally:
        stop_spark_session()
