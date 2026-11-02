"""Model evaluation and metrics generation module using Spark MLlib.

Computes Accuracy, Precision, Recall, F1-Score, and ROC-AUC for binary classification
with CourseCompletion = 1 as the positive class.
Generates confusion matrices, saves comparison metrics, and outputs test predictions CSV.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator


def evaluate_predictions(
    predictions_df: DataFrame,
    model_name: str,
    label_col: str = "CourseCompletion",
    prediction_col: str = "prediction",
    probability_col: str = "probability",
) -> Dict[str, Any]:
    """Calculate comprehensive classification metrics on held-out test predictions.

    Args:
        predictions_df: Spark DataFrame containing ground truth and model predictions.
        model_name: Descriptive name of the model.
        label_col: Ground truth label column name (default: CourseCompletion).
        prediction_col: Predicted binary class column name.
        probability_col: Probability vector column name.

    Returns:
        Dictionary containing all metrics and confusion matrix values.
    """
    # Compute confusion matrix elements using exact Spark aggregations
    cm_row = (
        predictions_df.select(
            F.count(
                F.when((F.col(prediction_col) == 1.0) & (F.col(label_col) == 1.0), True)
            ).alias("TP"),
            F.count(
                F.when((F.col(prediction_col) == 0.0) & (F.col(label_col) == 0.0), True)
            ).alias("TN"),
            F.count(
                F.when((F.col(prediction_col) == 1.0) & (F.col(label_col) == 0.0), True)
            ).alias("FP"),
            F.count(
                F.when((F.col(prediction_col) == 0.0) & (F.col(label_col) == 1.0), True)
            ).alias("FN"),
        )
        .collect()[0]
        .asDict()
    )

    tp = int(cm_row["TP"])
    tn = int(cm_row["TN"])
    fp = int(cm_row["FP"])
    fn = int(cm_row["FN"])
    total = tp + tn + fp + fn

    accuracy = round((tp + tn) / total, 4) if total > 0 else 0.0
    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    f1_score = (
        round(2 * (precision * recall) / (precision + recall), 4)
        if (precision + recall) > 0
        else 0.0
    )

    # ROC-AUC evaluation via Spark BinaryClassificationEvaluator
    roc_evaluator = BinaryClassificationEvaluator(
        labelCol=label_col,
        rawPredictionCol=probability_col,
        metricName="areaUnderROC",
    )
    roc_auc = round(float(roc_evaluator.evaluate(predictions_df)), 4)

    metrics = {
        "model_name": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "roc_auc": roc_auc,
        "total_test_samples": total,
        "confusion_matrix": {
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "matrix": [[tn, fp], [fn, tp]],
        },
    }
    return metrics


def select_best_model(models_metrics: Dict[str, Dict[str, Any]]) -> str:
    """Select the best-performing model based on balanced F1-score and ROC-AUC.

    Args:
        models_metrics: Dictionary mapping model key to its metrics.

    Returns:
        Key of the best performing model.
    """
    # Score composite metric: 0.6 * ROC-AUC + 0.4 * F1-score
    best_key = ""
    highest_score = -1.0
    for key, m in models_metrics.items():
        composite_score = (0.6 * m["roc_auc"]) + (0.4 * m["f1_score"])
        if composite_score > highest_score:
            highest_score = composite_score
            best_key = key
    return best_key


def save_reports(
    models_metrics: Dict[str, Dict[str, Any]],
    test_predictions_pandas: pd.DataFrame,
    leakage_comparison: Dict[str, Any],
    output_dir: Path = Path("reports"),
) -> None:
    """Save all evaluation outputs to required files in reports/ directory.

    Args:
        models_metrics: Metrics for each evaluated model.
        test_predictions_pandas: DataFrame of test set actuals and predictions.
        leakage_comparison: Results comparing models with vs without CompletionRate.
        output_dir: Target reports directory.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    best_model_key = select_best_model(models_metrics)

    # 1. reports/model_metrics.json
    metrics_payload = {
        "best_model": best_model_key,
        "selection_criteria": "Composite ranking prioritized by ROC-AUC and F1-Score on positive class (CourseCompletion=1)",
        "models": models_metrics,
        "leakage_investigation": leakage_comparison,
    }
    metrics_file = output_dir / "model_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    # 2. reports/confusion_matrix.json
    cm_payload = {
        model_name: info["confusion_matrix"]
        for model_name, info in models_metrics.items()
    }
    cm_file = output_dir / "confusion_matrix.json"
    with open(cm_file, "w", encoding="utf-8") as f:
        json.dump(cm_payload, f, indent=2)

    # 3. reports/test_predictions.csv
    pred_file = output_dir / "test_predictions.csv"
    test_predictions_pandas.to_csv(pred_file, index=False)


def print_comparison_table(models_metrics: Dict[str, Dict[str, Any]], best_key: str) -> None:
    """Print formatted comparison table to terminal."""
    print("\n" + "=" * 78)
    print("MODEL EVALUATION BENCHMARK ON HELD-OUT TEST DATA (20%)")
    print("=" * 78)
    header = f"{'Model':25s} {'Accuracy':10s} {'Precision':11s} {'Recall':10s} {'F1-Score':10s} {'ROC-AUC':10s}"
    print(header)
    print("-" * 78)
    for key, m in models_metrics.items():
        mark = " (BEST)" if key == best_key else ""
        name = f"{m['model_name']}{mark}"
        row = (
            f"{name:25s} "
            f"{m['accuracy']:<10.4f} "
            f"{m['precision']:<11.4f} "
            f"{m['recall']:<10.4f} "
            f"{m['f1_score']:<10.4f} "
            f"{m['roc_auc']:<10.4f}"
        )
        print(row)
    print("=" * 78)
    print(f"Selected Champion Model: {models_metrics[best_key]['model_name']}")
    print("=" * 78)
