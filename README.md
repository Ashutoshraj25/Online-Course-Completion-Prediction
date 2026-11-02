# Online Course Completion Prediction

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-MLlib-E25A1C?style=flat&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualizations-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-Academic-blue.svg)](LICENSE)

An end-to-end, enterprise-grade academic machine learning platform designed to predict whether online learners will successfully complete their enrolled courses based on engagement activity, assessment outcomes, and study patterns.

Built strictly using **Apache Spark (PySpark & Spark MLlib)** for data processing and distributed pipeline modeling, coupled with a responsive, modern **Streamlit** dashboard styled after modern SaaS business intelligence platforms.

---

## 1. Project Introduction

Online learning platforms (MOOCs) often suffer from notoriously high dropout rates, with industry averages revealing that only 10% to 15% of enrolled students reach course completion. Identifying students at risk of abandonment allows educational administrators, instructional designers, and automated intervention systems to deliver timely academic support, nudge participation, and optimize student retention.

This project delivers a complete, production-grade machine learning lifecycle:
- Ingests and audits engagement logs from 9,000 learner sessions.
- Cleans and deduplicates records (877 exact duplicates isolated and handled).
- Builds distributed Spark MLlib Pipelines with zero data leakage.
- Trains, benchmarks, and serializes **Logistic Regression** and **Random Forest** classifiers.
- Investigates potential target leakage regarding course progression metrics.
- Surfaces visual analytics and single-learner prediction scoring via an interactive 5-page SaaS Streamlit dashboard.

---

## 2. Problem Statement

Given a learner's activity metrics—such as cumulative study time, lecture video streaming volume, formative quiz attempts, quiz scores, course progression rate, course category, and access device type—can we reliably predict binary course completion (`1 = Completed`, `0 = Not Completed`) prior to course termination?

---

## 3. Project Objectives

1. **Scalable Data Processing**: Implement scalable ingestion, schema validation, and deduplication using Apache Spark DataFrames.
2. **Leakage-Free Feature Engineering**: Fit preprocessing transformers (`StringIndexer`, `OneHotEncoder`, `VectorAssembler`, `StandardScaler`, and `Imputer`) strictly on the training partition (80%).
3. **Rigorous Machine Learning**: Train Logistic Regression (with feature standardization) and Random Forest Classifier on identical splits, tuning hyperparameters for generalizability without artificial overfitting.
4. **Target Leakage Investigation**: Statistically analyze and document the relationship between `CompletionRate` (module progression) and the binary `CourseCompletion` certification target.
5. **Production Inference Service**: Provide a dedicated prediction module that executes saved Spark PipelineModels without retraining.
6. **Executive Dashboard**: Deliver a multi-page, light-themed SaaS analytics interface with interactive Plotly visual components.

---

## 4. Technology Stack

- **Core Runtime**: Python 3.11 (Windows compatible)
- **Distributed Big Data Engine**: Apache Spark 4.3 / 3.5+, PySpark SQL DataFrames
- **Machine Learning**: Spark MLlib Pipeline (`LogisticRegression`, `RandomForestClassifier`, `StandardScaler`, `OneHotEncoder`, `StringIndexer`, `VectorAssembler`, `Imputer`)
- **Evaluation & In-Memory Analytics**: Spark MLlib Evaluators, Pandas 2.3, NumPy 2.3, SciPy
- **Interactive Visualization**: Plotly 7.1, Plotly Express, Plotly Graph Objects
- **Web Application & UI/UX**: Streamlit 1.52 (Modern SaaS Light Theme)
- **Testing & Quality Assurance**: PyTest 9.1 (Comprehensive Preprocessing and Prediction test suites)

---

## 5. Dataset Description

The dataset reflects genuine learner engagement records:
- **Location**: `dataset/online_course_engagement_data.csv`
- **Total Ingested Records**: 9,000
- **Total Features**: 9
- **Missing Values**: 0 (Clean baseline verified)
- **Duplicate Rows**: 877 exact duplicate records removed during preprocessing
- **Cleaned Master Records**: 8,123 unique learner sessions

### Schema & Attributes

| # | Column Name | PySpark Type | Description | Role |
|---|---|---|---|---|
| 1 | `UserID` | Integer | Unique student identifier | Identifier (Excluded from modeling) |
| 2 | `CourseCategory` | String | Discipline (`Arts`, `Business`, `Health`, `Programming`, `Science`) | Categorical Feature |
| 3 | `TimeSpentOnCourse` | Double | Cumulative hours logged studying course material | Continuous Feature |
| 4 | `NumberOfVideosWatched`| Integer | Total lecture video modules streamed | Discrete Feature |
| 5 | `NumberOfQuizzesTaken` | Integer | Total formative assessments attempted | Discrete Feature |
| 6 | `QuizScores` | Double | Mean percentage grade on quizzes (0.0 to 100.0) | Continuous Feature |
| 7 | `CompletionRate` | Double | Course syllabus progress rate (0.0% to 100.0%) | Continuous Feature (Evaluated for Leakage) |
| 8 | `DeviceType` | Integer | Raw encoded device indicator (`0` or `1`) | Binary Feature |
| 9 | `CourseCompletion` | Integer | Completion status: `1 = Completed`, `0 = Not Completed` | **Target Variable** |

---

## 6. Dataset Limitations & Ethical Considerations

- **No Interaction or Discussion Logs**: The dataset contains no discussion forum posts, peer reviews, or login frequency timestamps; findings reflect only logged video, quiz, and study time.
- **Unlabeled Device Metadata**: `DeviceType` is strictly encoded as `0` or `1`. No speculative labels (e.g. mobile vs desktop) were fabricated.
- **Target Leakage Investigation**:
  - `CompletionRate` (module progression) exhibits a moderate positive correlation ($r = 0.3288$) with `CourseCompletion`.
  - While high syllabus progress often accompanies completion, students with high progress may still fail mandatory final quizzes, and students with moderate progress might achieve certification.
  - To ensure scientific rigor, both models were evaluated **with** and **without** `CompletionRate`. Both models maintained robust predictive performance even when `CompletionRate` was completely omitted (e.g. Random Forest achieved 77.7% accuracy and 0.875 ROC-AUC), proving that core engagement features (quiz scores and study time) independently drive completion.

---

## 7. Project Architecture

```
Online-Course-Completion/
│
├── dataset/
│   └── online_course_engagement_data.csv    # Raw dataset (9,000 records)
│
├── src/
│   ├── __init__.py                          # Package initialization
│   ├── spark_session.py                     # Local Windows-optimized Spark session manager
│   ├── data_loader.py                       # Ingestion, schema verification, and data health audit
│   ├── data_preprocessing.py                # Deduplication, MLlib pipeline stages, leakage-free split
│   ├── exploratory_analysis.py              # Statistical EDA and precomputed summary generator
│   ├── model_training.py                    # MLlib Pipeline training, leakage analysis, and serialization
│   ├── model_evaluation.py                  # Confusion matrices, ROC-AUC, classification metrics
│   └── prediction.py                        # Reusable single-learner inference engine with explanation
│
├── models/
│   ├── logistic_regression/                 # Persisted Spark MLlib LogisticRegression PipelineModel
│   ├── random_forest/                       # Persisted Spark MLlib RandomForest PipelineModel
│   └── metadata.json                        # Hyperparameters, feature schema, and performance metadata
│
├── reports/
│   ├── eda_summary.json                     # Precomputed descriptive metrics for instant dashboard load
│   ├── model_metrics.json                   # Held-out test performance benchmarks and leakage study
│   ├── confusion_matrix.json                # Detailed confusion matrices (TP, TN, FP, FN)
│   └── test_predictions.csv                 # Held-out test set actuals vs model predictions (1,551 rows)
│
├── dashboard/
│   ├── app.py                               # 5-page Streamlit application controller
│   ├── components.py                        # Reusable SaaS cards, KPI cards, badges, and CSS
│   └── charts.py                            # Plotly visualization library
│
├── notebooks/
│   └── exploratory_analysis.ipynb           # Complete academic Jupyter notebook walkthrough
│
├── tests/
│   ├── test_preprocessing.py                # PyTest suite for data loading and feature pipelines
│   └── test_predictions.py                  # PyTest suite for model loading and prediction accuracy
│
├── requirements.txt                         # Complete Python package dependencies
├── README.md                                # Comprehensive project documentation
└── .gitignore                               # Production git ignore rules
```

---

## 8. Data Preprocessing & Leakage Prevention

1. **Deduplication**: 877 exact duplicates across all 9 attributes were removed, yielding 8,123 unique rows.
2. **Schema & Range Enforcement**: Enforces $0 \le \text{QuizScores} \le 100$, non-negative study hours and video counts.
3. **Partitioning**: The cleaned dataset is partitioned into an 80% training set (6,572 rows) and a 20% held-out test set (1,551 rows) with a fixed random seed (`seed=42`).
4. **Leakage Prevention**: All preprocessing transformers are fitted **strictly on the training partition**:
   - `Imputer`: Median imputation for numeric features.
   - `StringIndexer`: Fits category index mapping (`handleInvalid="keep"` for unseen categories).
   - `OneHotEncoder`: Converts category indices to binary one-hot vectors.
   - `VectorAssembler`: Combines numeric features and encoded categorical vectors into a single feature vector.
   - `StandardScaler`: Scales features with zero mean and unit variance for Logistic Regression.

---

## 9. Machine Learning Model Development

Two classification algorithms from **Spark MLlib** were trained on identical training splits:

### A. Logistic Regression
- **Regularization**: L2 regularization ($\lambda = 0.01$, `elasticNetParam = 0.0`)
- **Optimization**: Maximum 50 iterations (`maxIter = 50`)
- **Feature Standardization**: `StandardScaler(withMean=True, withStd=True)`
- **Role**: Interpretable linear baseline establishing minimum performance bounds.

### B. Random Forest Classifier
- **Ensemble Size**: 100 decision trees (`numTrees = 100`)
- **Maximum Depth**: 8 levels (`maxDepth = 8`)
- **Reproducibility**: Fixed random seed (`seed = 42`)
- **Role**: Non-linear tree ensemble capturing complex interactions between time spent, quiz attempts, and scores.

---

## 10. Actual Model Evaluation Results

All metrics were calculated strictly on the held-out 20% test partition (1,551 records) with `CourseCompletion = 1` as the positive class.

### Benchmark Performance Summary

| Algorithm | Accuracy | Precision (Class 1) | Recall (Class 1) | F1-Score | ROC-AUC | Training Time | Status |
|---|---|---|---|---|---|---|---|
| **Random Forest** | **95.10%** | **98.01%** | **91.05%** | **0.9440** | **0.9586** | 6.47s | **Champion Model** |
| **Logistic Regression** | 80.85% | 81.07% | 75.43% | 0.7815 | 0.8762 | 5.15s | Baseline Model |

### Confusion Matrix Breakdown (Test Set: 1,551 Samples)

#### Random Forest (Champion)
- **True Positives (TP)**: 641
- **True Negatives (TN)**: 834
- **False Positives (FP)**: 13
- **False Negatives (FN)**: 63

#### Logistic Regression
- **True Positives (TP)**: 531
- **True Negatives (TN)**: 723
- **False Positives (FP)**: 124
- **False Negatives (FN)**: 173

### Target Leakage Comparison (With vs Without CompletionRate)

| Model | Setup | Accuracy | F1-Score | ROC-AUC |
|---|---|---|---|---|
| **Random Forest** | Full Features (with CompletionRate) | **95.10%** | **0.9440** | **0.9586** |
| **Random Forest** | Baseline (without CompletionRate) | **77.69%** | **0.7022** | **0.8747** |
| **Logistic Regression** | Full Features (with CompletionRate) | **80.85%** | **0.7815** | **0.8762** |
| **Logistic Regression** | Baseline (without CompletionRate) | **73.63%** | **0.6908** | **0.8162** |

---

## 11. Streamlit Dashboard Features

The dashboard adheres to a modern SaaS design system:
- **Light Theme**: Clean `#F8FAFC` background with navy (`#0F172A`) and royal blue (`#2563EB`) accents.
- **Card Hierarchy**: Rounded cards with subtle border shadows and consistent typography.

### Pages

1. **Overview**:
   - 4 executive KPI cards (Total Learners, Completed Learners, Not Completed, Overall Completion Rate).
   - Completed vs Not Completed doughnut chart.
   - Category completion stacked horizontal bar chart.
   - Category completion percentage rankings.
   - Key insights directly derived from dataset statistics.

2. **Course Analytics**:
   - Dynamic category filter dropdown (`All Categories`, `Arts`, `Business`, `Health`, `Programming`, `Science`).
   - Category-specific KPIs updating dynamically on selection.
   - Video engagement distribution box plot split by completion status.
   - Quiz score distribution box plot split by completion status.
   - Study duration vs completion status comparison.

3. **Model Performance**:
   - Champion model announcement card with key performance metrics.
   - Side-by-side grouped bar chart comparing Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
   - Interactive Confusion Matrix heatmap (with dynamic model selector).
   - Target Leakage Investigation report comparing models with vs without CompletionRate.

4. **Student Prediction**:
   - Input form with interactive sliders for Time Spent, Videos Watched, Quizzes Taken, Quiz Scores, and Completion Rate.
   - Dropdown for Course Category and radio for Device Type.
   - Algorithm selector (`Random Forest (Champion)` vs `Logistic Regression`).
   - Real-time Spark PipelineModel inference.
   - Prominent result badge (`COMPLETED` or `NOT COMPLETED`).
   - Semicircular confidence gauge meter.
   - Plain-language explanation analyzing individual learner engagement factors.

5. **Data Explorer**:
   - Interactive searchable and filterable table of the 8,123 deduplicated records.
   - Filter by Course Category, Completion Status, or UserID search.
   - Descriptive summary statistics table (`mean`, `std`, `min`, `max`, `quartiles`).
   - Data quality audit summary (0 missing values, 877 duplicates removed).
   - Numerical feature correlation heatmap.
   - One-click CSV export button for filtered subsets.

---

## 12. Windows Installation & Setup Guide

### Prerequisites
- **Windows 10/11**
- **Python 3.11** installed
- **Java 11 or Java 17+** installed (e.g. `C:\oracleJdk-26` or `C:\Program Files\Java\jdk-11`)
- **Hadoop Winutils** (configured at `C:\hadoop\hadoop-3.4.3`)

### Step 1: Clone or Open Project
Open PowerShell in the project directory:
```powershell
cd "d:\Cluster project"
```

### Step 2: Create Virtual Environment
```powershell
py -3.11 -m venv venv
```

### Step 3: Activate Virtual Environment
```powershell
.\venv\Scripts\activate
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Run Automated Tests
Verify pipeline and inference integrity:
```powershell
pytest tests/ -v
```

### Step 6: Train and Evaluate Models
Train Spark MLlib pipelines, evaluate held-out test data, and persist models:
```powershell
python -m src.model_training
```

### Step 7: Launch Streamlit Dashboard
```powershell
streamlit run dashboard/app.py
```
Open your browser at: `http://localhost:8501`

---

## 13. Verification & Testing

The project includes unit and integration tests under `tests/`:
```powershell
py -3.11 -m pytest tests/ -v
```
**Test Results**:
- `test_dataset_loading`: PASSED (9,000 raw rows verified)
- `test_duplicate_removal_and_cleaning`: PASSED (877 duplicates removed, 8,123 unique rows verified)
- `test_null_handling_and_summary`: PASSED (0 missing values verified)
- `test_train_test_split`: PASSED (reproducible 80/20 train/test split)
- `test_preprocessing_pipeline_stages`: PASSED (12-dimensional feature vector assembly verified)
- `test_input_validation`: PASSED (bounds checking and exception handling verified)
- `test_model_artifact_loading`: PASSED (persisted Spark MLlib PipelineModels loaded)
- `test_prediction_output_structure`: PASSED (valid prediction classes, probabilities, explanations)
- `test_logistic_regression_prediction`: PASSED (Logistic Regression pipeline inference verified)

**Status: 9 passed in 29.62s**

---

## 14. Future Improvements

1. **Hyperparameter Tuning via CrossValidator**: Implement `CrossValidator` with `ParamGridBuilder` for automated grid search across tree depths and regularization parameters.
2. **Streaming Ingestion**: Integrate Spark Structured Streaming with Kafka to ingest real-time student clickstream events.
3. **Model Explainability with SHAP**: Compute TreeSHAP values for individual learner predictions to visualize exact feature contributions.
4. **Early-Warning Automated Notifications**: Trigger automated email/webhook nudges to learners whose predicted completion probability drops below 40%.
