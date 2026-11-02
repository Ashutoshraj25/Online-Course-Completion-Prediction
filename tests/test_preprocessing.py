"""Unit and integration tests for data loading and preprocessing modules."""

import pytest
from src.spark_session import get_spark_session, stop_spark_session
from src.data_loader import load_data, get_dataset_summary
from src.data_preprocessing import (
    clean_dataset,
    split_data,
    build_preprocessing_stages,
    TARGET_COL,
)
from pyspark.ml import Pipeline


@pytest.fixture(scope="session")
def spark():
    """Session-scoped SparkSession fixture."""
    session = get_spark_session("TestPreprocessing")
    yield session
    stop_spark_session()


def test_dataset_loading(spark):
    """Test that the CSV dataset loads correctly into a Spark DataFrame."""
    df = load_data(spark)
    assert df is not None
    assert df.count() == 9000
    assert len(df.columns) == 9
    assert "UserID" in df.columns
    assert "CourseCompletion" in df.columns


def test_duplicate_removal_and_cleaning(spark):
    """Test that deduplication removes all 877 exact duplicates."""
    df = load_data(spark)
    cleaned = clean_dataset(df)
    assert cleaned.count() == 8123  # 9000 - 877 = 8123
    assert cleaned.filter("CourseCompletion NOT IN (0, 1)").count() == 0


def test_null_handling_and_summary(spark):
    """Test that missing values are correctly computed and none exist in raw data."""
    df = load_data(spark)
    summary = get_dataset_summary(df)
    for col_name, null_cnt in summary["missing_values"].items():
        assert null_cnt == 0, f"Unexpected nulls in column {col_name}"
    assert summary["duplicate_records"] == 877


def test_train_test_split(spark):
    """Test 80/20 reproducible partition split."""
    df = clean_dataset(load_data(spark))
    train_df, test_df = split_data(df, train_ratio=0.8, seed=42)
    assert train_df.count() > 0
    assert test_df.count() > 0
    assert train_df.count() + test_df.count() == 8123


def test_preprocessing_pipeline_stages(spark):
    """Test that the MLlib preprocessing pipeline fits and transforms feature vectors."""
    df = clean_dataset(load_data(spark))
    train_df, test_df = split_data(df, train_ratio=0.8, seed=42)

    stages, feature_names = build_preprocessing_stages(
        include_completion_rate=True, scale_features=True
    )
    pipeline = Pipeline(stages=stages)
    model = pipeline.fit(train_df)
    transformed = model.transform(test_df)

    assert "features" in transformed.columns
    row = transformed.select("features").first()
    # 6 numeric + 6 one-hot encoded categories (5 known + 1 unseen handleInvalid index) = 12 dimensions
    assert len(row["features"]) == 12
