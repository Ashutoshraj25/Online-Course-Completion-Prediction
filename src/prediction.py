"""Inference and Prediction module for Online Course Completion.

Loads persisted Spark MLlib PipelineModels, accepts learner activity inputs,
applies the full saved preprocessing pipeline, and outputs prediction class,
probabilities, and interpretable engagement explanations.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType,
)
from pyspark.ml import PipelineModel

from src.spark_session import get_spark_session


MODELS_DIR = Path("models")
VALID_CATEGORIES = ["Arts", "Business", "Health", "Programming", "Science"]
VALID_DEVICE_TYPES = [0, 1]

# Schema matching the raw dataset input
INPUT_SCHEMA = StructType([
    StructField("CourseCategory", StringType(), False),
    StructField("TimeSpentOnCourse", DoubleType(), False),
    StructField("NumberOfVideosWatched", IntegerType(), False),
    StructField("NumberOfQuizzesTaken", IntegerType(), False),
    StructField("QuizScores", DoubleType(), False),
    StructField("CompletionRate", DoubleType(), False),
    StructField("DeviceType", IntegerType(), False),
])

# Global in-memory model cache to avoid reloading on every request
_MODEL_CACHE: Dict[str, PipelineModel] = {}


def validate_learner_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize learner input values.

    Args:
        data: Raw input dictionary.

    Returns:
        Sanitized input dictionary.

    Raises:
        ValueError: If any input field is invalid or out of permissible bounds.
    """
    category = str(data.get("CourseCategory", "")).strip()
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid CourseCategory '{category}'. Must be one of: {VALID_CATEGORIES}"
        )

    try:
        time_spent = float(data.get("TimeSpentOnCourse", 0.0))
        if time_spent < 0:
            raise ValueError("TimeSpentOnCourse cannot be negative.")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid TimeSpentOnCourse: {e}")

    try:
        videos_watched = int(data.get("NumberOfVideosWatched", 0))
        if videos_watched < 0:
            raise ValueError("NumberOfVideosWatched cannot be negative.")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid NumberOfVideosWatched: {e}")

    try:
        quizzes_taken = int(data.get("NumberOfQuizzesTaken", 0))
        if quizzes_taken < 0:
            raise ValueError("NumberOfQuizzesTaken cannot be negative.")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid NumberOfQuizzesTaken: {e}")

    try:
        quiz_scores = float(data.get("QuizScores", 0.0))
        if not (0.0 <= quiz_scores <= 100.0):
            raise ValueError("QuizScores must be between 0.0 and 100.0.")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid QuizScores: {e}")

    try:
        completion_rate = float(data.get("CompletionRate", 0.0))
        if not (0.0 <= completion_rate <= 100.0):
            raise ValueError("CompletionRate must be between 0.0 and 100.0.")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid CompletionRate: {e}")

    try:
        device_type = int(data.get("DeviceType", 0))
        if device_type not in VALID_DEVICE_TYPES:
            raise ValueError(f"DeviceType must be 0 or 1. Received: {device_type}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid DeviceType: {e}")

    return {
        "CourseCategory": category,
        "TimeSpentOnCourse": time_spent,
        "NumberOfVideosWatched": videos_watched,
        "NumberOfQuizzesTaken": quizzes_taken,
        "QuizScores": quiz_scores,
        "CompletionRate": completion_rate,
        "DeviceType": device_type,
    }


def get_cached_pipeline_model(
    model_name: str = "random_forest",
    models_dir: Optional[Path] = None,
) -> PipelineModel:
    """Retrieve or load a persisted Spark MLlib PipelineModel.

    Args:
        model_name: 'random_forest' or 'logistic_regression'.
        models_dir: Base directory containing models.

    Returns:
        Loaded Spark PipelineModel.
    """
    key = model_name.lower().replace(" ", "_")
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]

    base_dir = models_dir or MODELS_DIR
    model_path = base_dir / key
    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model artifact not found at '{model_path}'. "
            f"Please run 'python -m src.model_training' to train and persist models."
        )

    # Ensure Spark Session is active
    get_spark_session()
    # Normalize path for Spark
    norm_path = model_path.resolve().as_posix()
    loaded_model = PipelineModel.load(norm_path)
    _MODEL_CACHE[key] = loaded_model
    return loaded_model


def generate_explanation(
    sanitized: Dict[str, Any],
    pred_class: int,
    prob_completion: float,
) -> str:
    """Generate human-interpretable rationale for the prediction result."""
    reasons = []

    if sanitized["QuizScores"] >= 75.0:
        reasons.append("strong quiz performance (>= 75.0)")
    else:
        reasons.append("lower quiz performance (< 75.0)")

    if sanitized["TimeSpentOnCourse"] >= 50.0:
        reasons.append("above-average time invested in course material")
    else:
        reasons.append("limited study duration")

    if sanitized["NumberOfQuizzesTaken"] >= 5:
        reasons.append("consistent quiz participation")
    else:
        reasons.append("low quiz engagement")

    if sanitized["CompletionRate"] >= 60.0:
        reasons.append("high course module progression")

    if pred_class == 1:
        summary = (
            f"The learner is predicted to COMPLETE the course with a estimated probability of "
            f"{prob_completion:.1%}, driven by {', '.join(reasons)}."
        )
    else:
        summary = (
            f"The learner is at risk of NOT COMPLETING the course (completion probability: "
            f"{prob_completion:.1%}). Primary risk factors include {', '.join(reasons)}."
        )
    return summary


def predict_learner_completion(
    learner_data: Dict[str, Any],
    model_name: str = "random_forest",
    spark: Optional[SparkSession] = None,
) -> Dict[str, Any]:
    """Generate course completion prediction for a single learner activity record.

    Applies the exact saved Spark MLlib Pipeline stages (imputation, string indexing,
    one-hot encoding, vector assembly, optional scaling, and estimator inference).

    Args:
        learner_data: Dictionary containing learner feature inputs.
        model_name: Selected model ('random_forest' or 'logistic_regression').
        spark: Optional active SparkSession.

    Returns:
        Dictionary with prediction class (0/1), label, probabilities, and explanation.
    """
    sanitized = validate_learner_input(learner_data)
    pipeline_model = get_cached_pipeline_model(model_name)

    spark_sess = spark or get_spark_session()

    # Create single-row Spark DataFrame
    input_df = spark_sess.createDataFrame([sanitized], schema=INPUT_SCHEMA)

    # Transform through full Spark MLlib Pipeline
    pred_df = pipeline_model.transform(input_df)
    row = pred_df.select("prediction", "probability").collect()[0]

    pred_class = int(row["prediction"])
    prob_vector = row["probability"]
    prob_non_completion = round(float(prob_vector[0]), 4)
    prob_completion = round(float(prob_vector[1]), 4)

    label_str = "Completed" if pred_class == 1 else "Not Completed"
    model_display = (
        "Random Forest Classifier"
        if "forest" in model_name.lower()
        else "Logistic Regression"
    )

    explanation = generate_explanation(sanitized, pred_class, prob_completion)

    return {
        "status": "success",
        "model_used": model_display,
        "prediction": pred_class,
        "predicted_label": label_str,
        "probability_completion": prob_completion,
        "probability_non_completion": prob_non_completion,
        "confidence": max(prob_completion, prob_non_completion),
        "explanation": explanation,
        "inputs": sanitized,
    }


if __name__ == "__main__":
    from src.spark_session import stop_spark_session

    sample_student_1 = {
        "CourseCategory": "Programming",
        "TimeSpentOnCourse": 85.5,
        "NumberOfVideosWatched": 18,
        "NumberOfQuizzesTaken": 8,
        "QuizScores": 88.0,
        "CompletionRate": 92.0,
        "DeviceType": 1,
    }

    sample_student_2 = {
        "CourseCategory": "Arts",
        "TimeSpentOnCourse": 15.0,
        "NumberOfVideosWatched": 2,
        "NumberOfQuizzesTaken": 1,
        "QuizScores": 45.0,
        "CompletionRate": 20.0,
        "DeviceType": 0,
    }

    print("Testing Student 1 (High Engagement) with Random Forest:")
    res1 = predict_learner_completion(sample_student_1, "random_forest")
    print(f"  Prediction: {res1['predicted_label']} (Class {res1['prediction']})")
    print(f"  Probability of Completion: {res1['probability_completion']:.1%}")
    print(f"  Explanation: {res1['explanation']}")

    print("\nTesting Student 2 (Low Engagement) with Logistic Regression:")
    res2 = predict_learner_completion(sample_student_2, "logistic_regression")
    print(f"  Prediction: {res2['predicted_label']} (Class {res2['prediction']})")
    print(f"  Probability of Completion: {res2['probability_completion']:.1%}")
    print(f"  Explanation: {res2['explanation']}")

    stop_spark_session()
