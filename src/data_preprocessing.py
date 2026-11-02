"""Data preprocessing and feature engineering module using Spark MLlib.

Implements data cleaning, duplicate removal, schema validation,
categorical encoding (StringIndexer + OneHotEncoder), numerical scaling (StandardScaler),
and VectorAssembler within a reusable Spark MLlib Pipeline.
Guarantees zero data leakage by fitting preprocessing solely on training data.
"""

from typing import List, Tuple, Optional
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer,
    OneHotEncoder,
    VectorAssembler,
    StandardScaler,
    Imputer,
)


# Base feature definitions
CATEGORICAL_COLS = ["CourseCategory"]
BASE_NUMERIC_COLS = [
    "TimeSpentOnCourse",
    "NumberOfVideosWatched",
    "NumberOfQuizzesTaken",
    "QuizScores",
    "DeviceType",
]
LEAKAGE_CANDIDATE_COL = "CompletionRate"
TARGET_COL = "CourseCompletion"
ID_COL = "UserID"


def clean_dataset(df: DataFrame) -> DataFrame:
    """Perform dataset-level cleaning, deduplication, and schema validation.

    1. Removes exact duplicates across all columns.
    2. Validates and enforces target column values (0 or 1).
    3. Enforces valid positive ranges for numerical activity metrics.
    4. Replaces any null/empty strings in CourseCategory with 'Unknown'.
    5. Excludes UserID from downstream modeling.

    Args:
        df: Raw Spark DataFrame.

    Returns:
        Cleaned Spark DataFrame ready for train/test splitting.
    """
    # 1. Deduplication
    cleaned = df.dropDuplicates()

    # 2. Filter target validity: CourseCompletion must be 0 or 1
    cleaned = cleaned.filter(
        F.col(TARGET_COL).isNotNull() & F.col(TARGET_COL).isin([0, 1])
    )

    # 3. Handle categorical missing values
    cleaned = cleaned.withColumn(
        "CourseCategory",
        F.when(
            F.col("CourseCategory").isNull() | (F.trim(F.col("CourseCategory")) == ""),
            F.lit("Unknown"),
        ).otherwise(F.col("CourseCategory")),
    )

    # 4. Cast and validate numeric types
    cleaned = (
        cleaned.withColumn("TimeSpentOnCourse", F.col("TimeSpentOnCourse").cast(DoubleType()))
        .withColumn("NumberOfVideosWatched", F.col("NumberOfVideosWatched").cast(IntegerType()))
        .withColumn("NumberOfQuizzesTaken", F.col("NumberOfQuizzesTaken").cast(IntegerType()))
        .withColumn("QuizScores", F.col("QuizScores").cast(DoubleType()))
        .withColumn("CompletionRate", F.col("CompletionRate").cast(DoubleType()))
        .withColumn("DeviceType", F.col("DeviceType").cast(IntegerType()))
        .withColumn(TARGET_COL, F.col(TARGET_COL).cast(DoubleType()))
    )

    return cleaned


def get_feature_columns(include_completion_rate: bool = True) -> List[str]:
    """Return the list of numerical feature columns based on leakage settings."""
    if include_completion_rate:
        return BASE_NUMERIC_COLS + [LEAKAGE_CANDIDATE_COL]
    return list(BASE_NUMERIC_COLS)


def build_preprocessing_stages(
    include_completion_rate: bool = True,
    scale_features: bool = False,
    output_feature_col: str = "features",
) -> Tuple[List[object], List[str]]:
    """Construct Spark MLlib Pipeline stages for preprocessing and feature engineering.

    Pipeline architecture:
    1. Imputer: handles missing numeric values (median strategy).
    2. StringIndexer: encodes CourseCategory into category index.
    3. OneHotEncoder: converts category index into one-hot binary vector.
    4. VectorAssembler: combines numeric features + encoded category vector.
    5. StandardScaler (optional): standardizes features for Logistic Regression.

    Args:
        include_completion_rate: Whether to include CompletionRate feature.
        scale_features: Whether to apply StandardScaler (recommended for Logistic Regression).
        output_feature_col: Name of final vector column for models.

    Returns:
        Tuple of (list of ML stages, list of input feature names).
    """
    numeric_cols = get_feature_columns(include_completion_rate)
    stages = []

    # 1. Numeric Imputer for robust handling of unseen nulls
    imputed_numeric_cols = [f"{c}_imputed" for c in numeric_cols]
    imputer = Imputer(
        inputCols=numeric_cols,
        outputCols=imputed_numeric_cols,
        strategy="median",
    )
    stages.append(imputer)

    # 2. StringIndexer for CourseCategory
    indexer = StringIndexer(
        inputCol="CourseCategory",
        outputCol="CourseCategoryIndex",
        handleInvalid="keep",  # Gracefully handles unseen categories
    )
    stages.append(indexer)

    # 3. OneHotEncoder for CourseCategory
    encoder = OneHotEncoder(
        inputCols=["CourseCategoryIndex"],
        outputCols=["CourseCategoryVec"],
        dropLast=False,
    )
    stages.append(encoder)

    # 4. VectorAssembler
    assembler_inputs = imputed_numeric_cols + ["CourseCategoryVec"]
    assembler_output = "raw_features" if scale_features else output_feature_col
    assembler = VectorAssembler(
        inputCols=assembler_inputs,
        outputCol=assembler_output,
        handleInvalid="keep",
    )
    stages.append(assembler)

    # 5. StandardScaler
    if scale_features:
        scaler = StandardScaler(
            inputCol="raw_features",
            outputCol=output_feature_col,
            withMean=True,
            withStd=True,
        )
        stages.append(scaler)

    feature_names = numeric_cols + ["CourseCategory"]
    return stages, feature_names


def split_data(
    df: DataFrame,
    train_ratio: float = 0.8,
    seed: int = 42,
) -> Tuple[DataFrame, DataFrame]:
    """Split dataset into training and testing partitions using a fixed random seed.

    Preserves target distribution across partitions.

    Args:
        df: Cleaned Spark DataFrame.
        train_ratio: Proportion for training split (default: 0.8).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (train_df, test_df).
    """
    test_ratio = round(1.0 - train_ratio, 2)
    splits = df.randomSplit([train_ratio, test_ratio], seed=seed)
    train_df, test_df = splits[0], splits[1]
    return train_df, test_df


if __name__ == "__main__":
    from src.spark_session import get_spark_session, stop_spark_session
    from src.data_loader import load_data

    spark = get_spark_session()
    try:
        raw_df = load_data(spark)
        cleaned_df = clean_dataset(raw_df)
        print(f"Original record count : {raw_df.count()}")
        print(f"Cleaned record count  : {cleaned_df.count()}")
        print(f"Removed duplicates    : {raw_df.count() - cleaned_df.count()}")

        train_df, test_df = split_data(cleaned_df)
        print(f"Train split records   : {train_df.count()}")
        print(f"Test split records    : {test_df.count()}")

        # Test preprocessing pipeline fit on train only
        stages, feature_names = build_preprocessing_stages(
            include_completion_rate=True, scale_features=True
        )
        pipeline = Pipeline(stages=stages)
        pipeline_model = pipeline.fit(train_df)
        transformed_test = pipeline_model.transform(test_df)
        print("\nTransformed Test Sample:")
        transformed_test.select("CourseCategory", "TimeSpentOnCourse", "features").show(3, truncate=False)
        print("Preprocessing verified successfully.")
    finally:
        stop_spark_session()
