"""Unit and integration tests for model persistence, loading, and inference."""

import pytest
from pathlib import Path
from src.spark_session import get_spark_session, stop_spark_session
from src.prediction import (
    predict_learner_completion,
    validate_learner_input,
    get_cached_pipeline_model,
)


@pytest.fixture(scope="session")
def spark():
    """Session-scoped SparkSession fixture."""
    session = get_spark_session("TestPredictions")
    yield session
    stop_spark_session()


def test_input_validation():
    """Test input schema validation and bounds checking."""
    valid_input = {
        "CourseCategory": "Science",
        "TimeSpentOnCourse": 65.0,
        "NumberOfVideosWatched": 14,
        "NumberOfQuizzesTaken": 7,
        "QuizScores": 85.0,
        "CompletionRate": 70.0,
        "DeviceType": 1,
    }
    sanitized = validate_learner_input(valid_input)
    assert sanitized["CourseCategory"] == "Science"
    assert sanitized["TimeSpentOnCourse"] == 65.0

    # Invalid category
    with pytest.raises(ValueError, match="Invalid CourseCategory"):
        validate_learner_input({**valid_input, "CourseCategory": "Astronomy"})

    # Negative hours
    with pytest.raises(ValueError, match="cannot be negative"):
        validate_learner_input({**valid_input, "TimeSpentOnCourse": -5.0})

    # Out of range quiz score
    with pytest.raises(ValueError, match="must be between 0.0 and 100.0"):
        validate_learner_input({**valid_input, "QuizScores": 150.0})


def test_model_artifact_loading(spark):
    """Test loading trained Spark MLlib PipelineModels from disk."""
    rf_model = get_cached_pipeline_model("random_forest")
    assert rf_model is not None
    lr_model = get_cached_pipeline_model("logistic_regression")
    assert lr_model is not None


def test_prediction_output_structure(spark):
    """Test single learner prediction output format, classes, and probabilities."""
    high_engagement_student = {
        "CourseCategory": "Programming",
        "TimeSpentOnCourse": 90.0,
        "NumberOfVideosWatched": 18,
        "NumberOfQuizzesTaken": 9,
        "QuizScores": 92.0,
        "CompletionRate": 95.0,
        "DeviceType": 0,
    }
    result = predict_learner_completion(high_engagement_student, "random_forest", spark=spark)

    assert result["status"] == "success"
    assert result["prediction"] in (0, 1)
    assert result["predicted_label"] in ("Completed", "Not Completed")
    assert 0.0 <= result["probability_completion"] <= 1.0
    assert 0.0 <= result["probability_non_completion"] <= 1.0
    assert abs((result["probability_completion"] + result["probability_non_completion"]) - 1.0) < 0.01
    assert "explanation" in result
    assert len(result["explanation"]) > 10


def test_logistic_regression_prediction(spark):
    """Test prediction using the Logistic Regression pipeline."""
    low_engagement_student = {
        "CourseCategory": "Arts",
        "TimeSpentOnCourse": 10.0,
        "NumberOfVideosWatched": 2,
        "NumberOfQuizzesTaken": 1,
        "QuizScores": 40.0,
        "CompletionRate": 15.0,
        "DeviceType": 1,
    }
    result = predict_learner_completion(low_engagement_student, "logistic_regression", spark=spark)
    assert result["prediction"] == 0
    assert result["predicted_label"] == "Not Completed"
    assert result["probability_completion"] < 0.5
