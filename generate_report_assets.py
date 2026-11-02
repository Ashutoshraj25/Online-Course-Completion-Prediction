"""Generate all analytical figures, confusion matrices, and architectural diagrams for the academic project report."""

from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("report_figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load reports data
with open("reports/eda_summary.json", "r") as f:
    eda_data = json.load(f)

with open("reports/model_metrics.json", "r") as f:
    metrics_data = json.load(f)

df = pd.read_csv("dataset/online_course_engagement_data.csv").drop_duplicates()

# -------------------------------------------------------------
# 1. Figure 1: Outcome Class Distribution (Matching sample report style)
# -------------------------------------------------------------
plt.figure(figsize=(9, 5.5), dpi=300)
categories = ["Not Completed (0)", "Completed (1)"]
counts = [eda_data["kpis"]["not_completed_learners"], eda_data["kpis"]["completed_learners"]]
colors = ["#1E3A8A", "#2563EB"]
bars = plt.bar(categories, counts, color=colors, width=0.55, edgecolor="#0F172A", linewidth=1.2)
plt.title("Online Course Completion Distribution (N = 8,123)", fontsize=14, fontweight="bold", pad=15)
plt.ylabel("Number of Learners", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.gca().set_axisbelow(True)

for bar, val in zip(bars, counts):
    pct = (val / sum(counts)) * 100
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 80,
        f"{val:,}\n({pct:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

plt.ylim(0, max(counts) * 1.15)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig01_outcome_distribution.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 2. Figure 2: Category-wise Completion Ratio
# -------------------------------------------------------------
plt.figure(figsize=(10, 5.5), dpi=300)
cats = list(eda_data["category_analytics"].keys())
comp_pcts = [eda_data["category_analytics"][c]["completion_rate_pct"] for c in cats]
avg_scores = [eda_data["category_analytics"][c]["avg_quiz_score"] for c in cats]

x = np.arange(len(cats))
width = 0.35

fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)
rects1 = ax1.bar(x - width/2, comp_pcts, width, label="Completion Rate (%)", color="#2563EB", edgecolor="#1E3A8A")
rects2 = ax1.bar(x + width/2, avg_scores, width, label="Avg Quiz Score (%)", color="#93C5FD", edgecolor="#1E3A8A")

ax1.set_ylabel("Percentage (%)", fontsize=12)
ax1.set_title("Course Category Benchmark: Completion Rate vs Average Quiz Score", fontsize=13, fontweight="bold", pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(cats, fontsize=11)
ax1.legend(loc="upper right", framealpha=0.9)
ax1.grid(axis="y", linestyle="--", alpha=0.3)
ax1.set_ylim(0, 100)

for rect in rects1:
    h = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width()/2, h + 1.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

for rect in rects2:
    h = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width()/2, h + 1.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig02_category_analytics.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 3. Figure 3: Correlation Matrix Heatmap
# -------------------------------------------------------------
plt.figure(figsize=(8.5, 7), dpi=300)
corr_dict = eda_data["correlation_matrix"]
features = list(corr_dict.keys())
corr_matrix = np.array([[corr_dict[f1][f2] for f2 in features] for f1 in features])

im = plt.imshow(corr_matrix, cmap="Blues", vmin=-0.1, vmax=1.0)
cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
cbar.set_label("Pearson Correlation Coefficient (r)", fontsize=10)

plt.xticks(range(len(features)), features, rotation=40, ha="right", fontsize=9)
plt.yticks(range(len(features)), features, fontsize=9)
plt.title("Correlation Matrix Heatmap of Numerical Features", fontsize=13, fontweight="bold", pad=15)

for i in range(len(features)):
    for j in range(len(features)):
        val = corr_matrix[i, j]
        color = "white" if abs(val) > 0.4 else "black"
        plt.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=8.5, fontweight="bold")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig03_correlation_heatmap.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 4. Figure 4: Engagement Feature Boxplots
# -------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8), dpi=300)
box_features = [
    ("TimeSpentOnCourse", "Time Spent on Course (Hours)", axes[0, 0]),
    ("QuizScores", "Average Quiz Score (%)", axes[0, 1]),
    ("NumberOfVideosWatched", "Videos Watched", axes[1, 0]),
    ("NumberOfQuizzesTaken", "Quizzes Taken", axes[1, 1])
]

for col, title, ax in box_features:
    data_0 = df[df["CourseCompletion"] == 0][col]
    data_1 = df[df["CourseCompletion"] == 1][col]
    
    bp = ax.boxplot(
        [data_0, data_1],
        tick_labels=["Not Completed", "Completed"],
        patch_artist=True,
        widths=0.5,
        medianprops=dict(color="#DC2626", linewidth=1.5),
        boxprops=dict(facecolor="#EFF6FF", color="#1E3A8A", linewidth=1.2),
        whiskerprops=dict(color="#1E3A8A", linewidth=1.2),
        capprops=dict(color="#1E3A8A", linewidth=1.2),
        flierprops=dict(marker='o', markersize=3, alpha=0.3)
    )
    bp['boxes'][0].set_facecolor('#F1F5F9')
    bp['boxes'][1].set_facecolor('#DBEAFE')
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

plt.suptitle("Parametric Distribution of Engagement Features by Completion Outcome", fontsize=14, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig04_engagement_boxplots.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 5. Figure 5: Model Performance Comparison Bar Chart (Sample Report Fig 8 style)
# -------------------------------------------------------------
rf = metrics_data["models"]["random_forest"]
lr = metrics_data["models"]["logistic_regression"]

metrics_names = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
rf_scores = [rf["accuracy"]*100, rf["precision"]*100, rf["recall"]*100, rf["f1_score"]*100, rf["roc_auc"]*100]
lr_scores = [lr["accuracy"]*100, lr["precision"]*100, lr["recall"]*100, lr["f1_score"]*100, lr["roc_auc"]*100]

x = np.arange(len(metrics_names))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
bars_rf = ax.bar(x - width/2, rf_scores, width, label="Random Forest (Champion)", color="#1D4ED8", edgecolor="#0F172A")
bars_lr = ax.bar(x + width/2, lr_scores, width, label="Logistic Regression", color="#93C5FD", edgecolor="#0F172A")

ax.set_ylabel("Metric Score (%)", fontsize=12)
ax.set_title("Spark MLlib Model Evaluation Metrics Comparison (Held-out Test Set, N=1,551)", fontsize=13, fontweight="bold", pad=15)
ax.set_xticks(x)
ax.set_xticklabels(metrics_names, fontsize=11)
ax.set_ylim(0, 110)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.legend(loc="lower right", framealpha=0.95)

for b in bars_rf:
    h = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

for b in bars_lr:
    h = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig05_model_metrics_comparison.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 6. Figure 6: Confusion Matrix - Random Forest (Champion)
# -------------------------------------------------------------
cm_rf = np.array(rf["confusion_matrix"]["matrix"])
fig, ax = plt.subplots(figsize=(7, 5.5), dpi=300)
im = ax.imshow(cm_rf, cmap="Blues", vmin=0, vmax=900)
ax.set_title("Random Forest Confusion Matrix (Actual vs Predicted)", fontsize=13, fontweight="bold", pad=15)
ax.set_xlabel("Predicted Outcome", fontsize=11)
ax.set_ylabel("Actual Outcome", fontsize=11)
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(["Not Completed (0)", "Completed (1)"], fontsize=10)
ax.set_yticklabels(["Not Completed (0)", "Completed (1)"], fontsize=10)

thresh = cm_rf.max() / 2
for r in range(2):
    for c in range(2):
        val = cm_rf[r, c]
        color = "white" if val > thresh else "black"
        cell_type = "TN" if (r==0 and c==0) else "FP" if (r==0 and c==1) else "FN" if (r==1 and c==0) else "TP"
        ax.text(c, r, f"{val}\n({cell_type})", ha="center", va="center", color=color, fontsize=12, fontweight="bold")

cbar = fig.colorbar(im, ax=ax, label="Number of Test Learners")
ax.text(0.5, -0.15, "Accuracy: 95.10% | Precision: 98.01% | Recall: 91.05% | F1: 94.40%",
        ha="center", va="top", transform=ax.transAxes, fontsize=9.5, style="italic")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig06_rf_confusion_matrix.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 7. Figure 7: Confusion Matrix - Logistic Regression
# -------------------------------------------------------------
cm_lr = np.array(lr["confusion_matrix"]["matrix"])
fig, ax = plt.subplots(figsize=(7, 5.5), dpi=300)
im = ax.imshow(cm_lr, cmap="Blues", vmin=0, vmax=900)
ax.set_title("Logistic Regression Confusion Matrix (Actual vs Predicted)", fontsize=13, fontweight="bold", pad=15)
ax.set_xlabel("Predicted Outcome", fontsize=11)
ax.set_ylabel("Actual Outcome", fontsize=11)
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(["Not Completed (0)", "Completed (1)"], fontsize=10)
ax.set_yticklabels(["Not Completed (0)", "Completed (1)"], fontsize=10)

thresh = cm_lr.max() / 2
for r in range(2):
    for c in range(2):
        val = cm_lr[r, c]
        color = "white" if val > thresh else "black"
        cell_type = "TN" if (r==0 and c==0) else "FP" if (r==0 and c==1) else "FN" if (r==1 and c==0) else "TP"
        ax.text(c, r, f"{val}\n({cell_type})", ha="center", va="center", color=color, fontsize=12, fontweight="bold")

cbar = fig.colorbar(im, ax=ax, label="Number of Test Learners")
ax.text(0.5, -0.15, "Accuracy: 80.85% | Precision: 81.07% | Recall: 75.43% | F1: 78.15%",
        ha="center", va="top", transform=ax.transAxes, fontsize=9.5, style="italic")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig07_lr_confusion_matrix.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 8. Figure 8: Target Leakage Analysis (With vs Without CompletionRate)
# -------------------------------------------------------------
leak_data = metrics_data["leakage_investigation"]
fig, ax = plt.subplots(figsize=(9, 5), dpi=300)

labels = ["LR Accuracy", "LR F1-Score", "RF Accuracy", "RF F1-Score"]
with_vals = [
    leak_data["with_completion_rate"]["logistic_regression"]["accuracy"] * 100,
    leak_data["with_completion_rate"]["logistic_regression"]["f1_score"] * 100,
    leak_data["with_completion_rate"]["random_forest"]["accuracy"] * 100,
    leak_data["with_completion_rate"]["random_forest"]["f1_score"] * 100
]
without_vals = [
    leak_data["without_completion_rate"]["logistic_regression"]["accuracy"] * 100,
    leak_data["without_completion_rate"]["logistic_regression"]["f1_score"] * 100,
    leak_data["without_completion_rate"]["random_forest"]["accuracy"] * 100,
    leak_data["without_completion_rate"]["random_forest"]["f1_score"] * 100
]

x = np.arange(len(labels))
width = 0.35

rects1 = ax.bar(x - width/2, with_vals, width, label="With CompletionRate Feature", color="#2563EB", edgecolor="#0F172A")
rects2 = ax.bar(x + width/2, without_vals, width, label="Without CompletionRate (Leakage Test)", color="#F59E0B", edgecolor="#0F172A")

ax.set_ylabel("Score (%)", fontsize=11)
ax.set_title("Target Leakage Analysis: Model Performance With vs Without CompletionRate", fontsize=12, fontweight="bold", pad=15)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylim(0, 110)
ax.legend(loc="lower right")
ax.grid(axis="y", linestyle="--", alpha=0.3)

for r in rects1:
    h = r.get_height()
    ax.text(r.get_x() + r.get_width()/2, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
for r in rects2:
    h = r.get_height()
    ax.text(r.get_x() + r.get_width()/2, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig08_leakage_comparison.png", dpi=300)
plt.close()

import matplotlib.patches as mpatches

# Replace Rectangle calls with boxstyle with FancyBboxPatch
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.axis("off")

boxes = [
    ("Raw Dataset Ingestion\n• 9,000 CSV Records\n• Schema Validation\n• Duplicate Detection", 0.05, 0.55, 0.22, 0.35, "#DBEAFE", "#1E40AF"),
    ("PySpark Preprocessing Engine\n• Exact Deduplication (877 rows)\n• Null Imputation (Strategy=Mean)\n• StringIndexer (CourseCategory)\n• OneHotEncoder (5 Buckets)\n• VectorAssembler (12 features)", 0.32, 0.55, 0.28, 0.35, "#EFF6FF", "#1E3A8A"),
    ("Spark MLlib Model Engine\n• 80/20 Stratified Split\n• Random Forest (200 Trees)\n• Logistic Regression (Scaled)\n• PipelineModel Serialization", 0.65, 0.55, 0.28, 0.35, "#DBEAFE", "#1E40AF"),
    ("Model Evaluation & Artifacts\n• MulticlassClassificationEvaluator\n• BinaryClassificationEvaluator\n• Confusion Matrices & ROC-AUC\n• models/ & reports/ Storage", 0.32, 0.08, 0.28, 0.35, "#FEF3C7", "#92400E"),
    ("Streamlit Interactive UI\n• Executive Overview Dashboard\n• Category Performance Analytics\n• Live Inference Engine\n• Data Quality Explorer Table", 0.65, 0.08, 0.28, 0.35, "#DCFCE7", "#166534")
]

for title, x0, y0, w, h, bg, border in boxes:
    rect = mpatches.FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0.02", facecolor=bg, edgecolor=border, linewidth=2, transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(x0 + w/2, y0 + h/2, title, transform=ax.transAxes, ha="center", va="center", fontsize=9, fontweight="bold", color="#0F172A")

# Draw connecting arrows
ax.annotate("", xy=(0.32, 0.72), xytext=(0.27, 0.72), arrowprops=dict(arrowstyle="->", lw=2.5, color="#1E3A8A"))
ax.annotate("", xy=(0.65, 0.72), xytext=(0.60, 0.72), arrowprops=dict(arrowstyle="->", lw=2.5, color="#1E3A8A"))
ax.annotate("", xy=(0.46, 0.43), xytext=(0.46, 0.55), arrowprops=dict(arrowstyle="->", lw=2.5, color="#1E3A8A"))
ax.annotate("", xy=(0.79, 0.43), xytext=(0.79, 0.55), arrowprops=dict(arrowstyle="->", lw=2.5, color="#1E3A8A"))
ax.annotate("", xy=(0.65, 0.25), xytext=(0.60, 0.25), arrowprops=dict(arrowstyle="->", lw=2.5, color="#166534"))

plt.title("High-Level End-to-End System Architecture", fontsize=15, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig09_system_architecture.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 10. Figure 10: PySpark ML Pipeline Stages Flowchart
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 4), dpi=300)
ax.axis("off")

stages = [
    ("Stage 0:\nImputer\n(Mean replacement\nfor numeric inputs)", 0.02, "#F1F5F9"),
    ("Stage 1:\nStringIndexer\n(CourseCategory\n-> categoryIndex)", 0.18, "#EFF6FF"),
    ("Stage 2:\nOneHotEncoder\n(categoryIndex ->\ncategoryVec [5])", 0.34, "#DBEAFE"),
    ("Stage 3:\nVectorAssembler\n(Concatenates all 12\ninput features)", 0.50, "#BFDBFE"),
    ("Stage 4:\nStandardScaler\n(Used for Logistic\nRegression)", 0.66, "#93C5FD"),
    ("Stage 5:\nML Estimator\n(Random Forest or\nLogistic Regression)", 0.82, "#3B82F6")
]

for title, x_pos, bg in stages:
    rect = mpatches.FancyBboxPatch((x_pos, 0.2), 0.14, 0.6, boxstyle="round,pad=0.02", facecolor=bg, edgecolor="#1E3A8A", linewidth=1.8, transform=ax.transAxes)
    ax.add_patch(rect)
    text_color = "white" if x_pos >= 0.8 else "#0F172A"
    ax.text(x_pos + 0.07, 0.5, title, transform=ax.transAxes, ha="center", va="center", fontsize=8.5, fontweight="bold", color=text_color)
    if x_pos < 0.8:
        ax.annotate("", xy=(x_pos + 0.175, 0.5), xytext=(x_pos + 0.14, 0.5), arrowprops=dict(arrowstyle="->", lw=2, color="#1E3A8A"))

plt.title("PySpark MLlib Multi-Stage Pipeline Execution Flow", fontsize=14, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig10_pipeline_stages.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 11. Figure 11: Data Flow Diagram (DFD Level 0 & Level 1)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
ax1.axis("off")
ax2.axis("off")

# Level 0 DFD (Context Diagram)
ax1.set_title("Level 0 DFD (Context Level)", fontsize=12, fontweight="bold", pad=10)
rect_ext = mpatches.FancyBboxPatch((0.05, 0.35), 0.25, 0.3, boxstyle="round,pad=0.02", facecolor="#F8FAFC", edgecolor="#1E3A8A", lw=1.5)
circle_proc = plt.Circle((0.55, 0.5), 0.2, facecolor="#DBEAFE", edgecolor="#1E3A8A", lw=2)
rect_ui = mpatches.FancyBboxPatch((0.75, 0.35), 0.2, 0.3, boxstyle="round,pad=0.02", facecolor="#DCFCE7", edgecolor="#166534", lw=1.5)

ax1.add_patch(rect_ext)
ax1.add_patch(circle_proc)
ax1.add_patch(rect_ui)

ax1.text(0.175, 0.5, "Dataset Source\n(9,000 CSV Rows)", ha="center", va="center", fontsize=8.5, fontweight="bold")
ax1.text(0.55, 0.5, "0.0\nOnline Course\nCompletion\nPrediction System", ha="center", va="center", fontsize=8.5, fontweight="bold")
ax1.text(0.85, 0.5, "User / Learner\n(Streamlit Dashboard)", ha="center", va="center", fontsize=8.5, fontweight="bold")

ax1.annotate("", xy=(0.35, 0.53), xytext=(0.30, 0.53), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1E3A8A"))
ax1.text(0.325, 0.57, "Raw CSV", ha="center", fontsize=7.5)

ax1.annotate("", xy=(0.75, 0.53), xytext=(0.72, 0.53), arrowprops=dict(arrowstyle="->", lw=1.5, color="#166534"))
ax1.text(0.735, 0.57, "Analytics", ha="center", fontsize=7.5)

ax1.annotate("", xy=(0.72, 0.45), xytext=(0.75, 0.45), arrowprops=dict(arrowstyle="->", lw=1.5, color="#166534"))
ax1.text(0.735, 0.40, "Learner Inputs", ha="center", fontsize=7.5)

# Level 1 DFD
ax2.set_title("Level 1 DFD (Decomposed Functional Modules)", fontsize=12, fontweight="bold", pad=10)
p1 = plt.Circle((0.2, 0.75), 0.12, facecolor="#EFF6FF", edgecolor="#1E3A8A", lw=1.5)
p2 = plt.Circle((0.5, 0.75), 0.12, facecolor="#DBEAFE", edgecolor="#1E3A8A", lw=1.5)
p3 = plt.Circle((0.8, 0.75), 0.12, facecolor="#BFDBFE", edgecolor="#1E3A8A", lw=1.5)
p4 = plt.Circle((0.5, 0.25), 0.12, facecolor="#DCFCE7", edgecolor="#166534", lw=1.5)

ax2.add_patch(p1)
ax2.add_patch(p2)
ax2.add_patch(p3)
ax2.add_patch(p4)

ax2.text(0.2, 0.75, "1.0 Ingest &\nDeduplicate", ha="center", va="center", fontsize=8, fontweight="bold")
ax2.text(0.5, 0.75, "2.0 Spark MLlib\nPipeline", ha="center", va="center", fontsize=8, fontweight="bold")
ax2.text(0.8, 0.75, "3.0 Train &\nEvaluate", ha="center", va="center", fontsize=8, fontweight="bold")
ax2.text(0.5, 0.25, "4.0 Real-time\nStreamlit UI", ha="center", va="center", fontsize=8, fontweight="bold")

ax2.annotate("", xy=(0.38, 0.75), xytext=(0.32, 0.75), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1E3A8A"))
ax2.annotate("", xy=(0.68, 0.75), xytext=(0.62, 0.75), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1E3A8A"))
ax2.annotate("", xy=(0.58, 0.35), xytext=(0.75, 0.65), arrowprops=dict(arrowstyle="->", lw=1.5, color="#166534"))
ax2.text(0.70, 0.48, "Models / Metrics", fontsize=7.5)

plt.suptitle("System Data Flow Architecture", fontsize=14, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig11_dfd_level0_level1.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 12. Figure 12: Use Case Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.axis("off")

# System Boundary
boundary = mpatches.FancyBboxPatch((0.28, 0.05), 0.44, 0.88, boxstyle="round,pad=0.02", facecolor="#F8FAFC", edgecolor="#64748B", linestyle="--", lw=1.8)
ax.add_patch(boundary)
ax.text(0.5, 0.90, "Online Course Intelligence System", ha="center", fontsize=11, fontweight="bold", color="#1E293B")

# Actors
ax.text(0.12, 0.75, "👤\nLearner / Student", ha="center", va="center", fontsize=11, fontweight="bold")
ax.text(0.12, 0.25, "👤\nCourse Instructor", ha="center", va="center", fontsize=11, fontweight="bold")
ax.text(0.88, 0.50, "👤\nAcademic Admin", ha="center", va="center", fontsize=11, fontweight="bold")

use_cases = [
    ("Simulate Engagement\n& Predict Outcome", 0.78),
    ("View Category Benchmarks\n& Grade Trends", 0.62),
    ("Audit Learner Records\n& Filter Quality", 0.46),
    ("Inspect ML Metrics &\nConfusion Matrices", 0.30),
    ("Export Filtered Activity Data", 0.14)
]

for title, y_pos in use_cases:
    ellipse = plt.matplotlib.patches.Ellipse((0.5, y_pos), 0.38, 0.11, facecolor="#EFF6FF", edgecolor="#1E40AF", lw=1.5)
    ax.add_patch(ellipse)
    ax.text(0.5, y_pos, title, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0F172A")
    
    # Connect actors
    if y_pos in [0.78, 0.62]:
        ax.plot([0.18, 0.31], [0.75, y_pos], color="#64748B", lw=1.2)
    if y_pos in [0.62, 0.46, 0.78]:
        ax.plot([0.18, 0.31], [0.25, y_pos], color="#64748B", lw=1.2)
    ax.plot([0.82, 0.69], [0.50, y_pos], color="#64748B", lw=1.2)

plt.title("Use Case Diagram for Academic Learning Analytics Platform", fontsize=13, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig12_use_case_diagram.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 13. Figure 13: Activity Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4), dpi=300)
ax.axis("off")

steps = [
    ("Start:\nLearner Inputs\nParameters", 0.05, "#E2E8F0"),
    ("Validate &\nSanitize Inputs\n(Range Checks)", 0.22, "#FEF08A"),
    ("Create Spark DF &\nApply Pipeline\n(Assembler & Scaler)", 0.40, "#DBEAFE"),
    ("Score with MLlib\nChampion Model\n(Random Forest)", 0.60, "#BFDBFE"),
    ("Compute Class\nProbability &\nGenerate Rationale", 0.78, "#BBF7D0"),
    ("Render Gauge &\nPrediction Result\non Streamlit UI", 0.95, "#86EFAC")
]

for title, x_c, bg in steps:
    rect = mpatches.FancyBboxPatch((x_c - 0.07, 0.2), 0.14, 0.6, boxstyle="round,pad=0.02", facecolor=bg, edgecolor="#1E3A8A", lw=1.5)
    ax.add_patch(rect)
    ax.text(x_c, 0.5, title, ha="center", va="center", fontsize=8, fontweight="bold", color="#0F172A")
    if x_c < 0.9:
        ax.annotate("", xy=(x_c + 0.10, 0.5), xytext=(x_c + 0.07, 0.5), arrowprops=dict(arrowstyle="->", lw=2, color="#1E3A8A"))

plt.title("Activity Diagram: Real-Time Inference Execution Workflow", fontsize=13, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fig13_activity_diagram.png", dpi=300)
plt.close()

print("All technical figures and architecture diagrams generated successfully in 'report_figures/'!")
