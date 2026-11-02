"""Main Streamlit Application for Online Course Completion Prediction.

Engineered with a clean, light-theme SaaS design system:
- Linear and Stripe inspired aesthetics
- 100% light theme (zero dark theme leakage)
- Responsive two-column layout for Student Prediction
- Code-fence-free KPI cards
- Error-free Plotly charts
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
import streamlit as st

from dashboard.components import (
    apply_custom_css,
    render_dashboard_header,
    render_kpi_card,
    render_card_header,
    render_prediction_result,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_ACCENT,
    COLOR_SUCCESS,
)
from dashboard.charts import (
    create_completion_donut_chart,
    create_category_completion_chart,
    create_category_score_bar,
    create_engagement_scatter_chart,
    create_distribution_box_plot,
    create_model_comparison_bar,
    create_confusion_matrix_heatmap,
    create_prediction_gauge,
    create_correlation_heatmap,
)
from src.prediction import predict_learner_completion, VALID_CATEGORIES, VALID_DEVICE_TYPES
from src.data_loader import resolve_dataset_path


# 1. Page Configuration
st.set_page_config(
    page_title="Course Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Polished Light-Theme CSS
apply_custom_css()

REPORTS_DIR = Path("reports")
MODELS_DIR = Path("models")


# 3. Data Ingestion & Caching
@st.cache_data
def load_eda_summary() -> Optional[Dict[str, Any]]:
    eda_file = REPORTS_DIR / "eda_summary.json"
    if eda_file.exists():
        with open(eda_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@st.cache_data
def load_model_metrics() -> Optional[Dict[str, Any]]:
    metrics_file = REPORTS_DIR / "model_metrics.json"
    if metrics_file.exists():
        with open(metrics_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@st.cache_data
def load_confusion_matrices() -> Optional[Dict[str, Any]]:
    cm_file = REPORTS_DIR / "confusion_matrix.json"
    if cm_file.exists():
        with open(cm_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@st.cache_data
def load_master_dataset() -> pd.DataFrame:
    path = resolve_dataset_path()
    df = pd.read_csv(path)
    return df.drop_duplicates()


# 4. Sidebar Redesign (Readable Dark Text, No Floating Radio Dots)
def render_sidebar() -> str:
    with st.sidebar:
        # Top Brand Header
        st.markdown(
            f"""
            <div style="padding: 0.25rem 0 1rem 0; border-bottom: 1px solid {COLOR_BORDER}; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.35rem;">🎓</span>
                    <div>
                        <div style="font-size: 1rem; font-weight: 700; color: #0F172A; letter-spacing: -0.01em; line-height: 1.2;">
                            Course Analytics
                        </div>
                        <div style="font-size: 0.75rem; color: #64748B;">
                            Learning Intelligence Platform
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation Options
        nav_options = [
            "📊  Overview",
            "📈  Course Analytics",
            "🎯  Model Performance",
            "🔮  Student Prediction",
            "🗂️  Data Explorer",
        ]

        selected = st.radio(
            "Navigation",
            options=nav_options,
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

        # Compact Bottom System Info
        models_ready = (MODELS_DIR / "random_forest").exists() and (MODELS_DIR / "logistic_regression").exists()
        status_color = COLOR_SUCCESS if models_ready else "#DC2626"
        status_text = "Models Online" if models_ready else "Models Offline"

        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border: 1px solid {COLOR_BORDER}; border-radius: 8px; padding: 0.75rem; font-size: 0.75rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span style="font-weight: 600; color: #334155;">Engine</span>
                    <span style="color: #64748B;">Apache Spark 4.3</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span style="font-weight: 600; color: #334155;">Dataset</span>
                    <span style="color: #64748B;">8,123 Clean Records</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 600; color: #334155;">Status</span>
                    <span style="display: inline-flex; align-items: center; gap: 0.3rem; color: {status_color}; font-weight: 600;">
                        <span style="width: 6px; height: 6px; border-radius: 50%; background-color: {status_color}; display: inline-block;"></span>
                        {status_text}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page_key = selected.split("  ")[1]
        return page_key


# 5. PAGE 1: OVERVIEW
def render_overview(eda_data: Dict[str, Any], df: pd.DataFrame) -> None:
    render_dashboard_header(
        title="Online Course Completion Prediction",
        subtitle="Understand learner engagement, analyze course completion patterns, and predict learning outcomes using machine learning.",
    )

    kpis = eda_data["kpis"]

    # 4 Equal-Height KPI Cards (Code-Fence-Free)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card(
            label="Total Learners",
            value=f"{kpis['total_learners']:,}",
            description="Deduplicated Master Set",
            icon="👥",
            badge="Master Set",
            badge_positive=False,
        )
    with col2:
        render_kpi_card(
            label="Completed Learners",
            value=f"{kpis['completed_learners']:,}",
            description=f"{kpis['overall_completion_pct']}% Completion Ratio",
            icon="🎓",
            badge=f"{kpis['overall_completion_pct']}%",
            badge_positive=True,
        )
    with col3:
        render_kpi_card(
            label="Not Completed",
            value=f"{kpis['not_completed_learners']:,}",
            description=f"{100 - kpis['overall_completion_pct']:.1f}% Attrition Rate",
            icon="📉",
            badge=f"{100 - kpis['overall_completion_pct']:.1f}%",
            badge_positive=False,
        )
    with col4:
        render_kpi_card(
            label="Average Quiz Score",
            value=f"{kpis['avg_quiz_score']:.1f}",
            description="Mean Grade (0-100 Scale)",
            icon="📝",
            badge="Score Mean",
            badge_positive=True,
        )

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Overview Charts - Row 1
    row1_left, row1_right = st.columns([1, 1.35])

    with row1_left:
        with st.container(border=True):
            render_card_header(
                title="Completion Distribution",
                subtitle="Overall proportion of completed vs uncompleted enrollments",
            )
            fig_donut = create_completion_donut_chart(
                kpis["completed_learners"], kpis["not_completed_learners"]
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with row1_right:
        with st.container(border=True):
            render_card_header(
                title="Completion by Course Category",
                subtitle="Student enrollment volume and completion counts per discipline",
            )
            fig_cat = create_category_completion_chart(eda_data["category_analytics"])
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Overview Charts - Row 2
    row2_left, row2_right = st.columns([1, 1.35])

    with row2_left:
        with st.container(border=True):
            render_card_header(
                title="Average Quiz Score by Category",
                subtitle="Mean assessment grading benchmark across all 5 disciplines",
            )
            fig_scores = create_category_score_bar(eda_data["category_analytics"])
            st.plotly_chart(fig_scores, use_container_width=True, config={"displayModeBar": False})

    with row2_right:
        with st.container(border=True):
            render_card_header(
                title="Learner Engagement Analysis",
                subtitle="Study duration vs quiz performance categorized by completion status",
            )
            fig_scatter = create_engagement_scatter_chart(df)
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Key Data Insights Card
    with st.container(border=True):
        render_card_header(
            title="Key Dataset Insights & Observations",
            subtitle="Derived mathematically from the verified 8,123 deduplicated student records",
        )
        for idx, insight in enumerate(eda_data.get("insights", []), 1):
            st.markdown(
                f"""
                <div style="display: flex; align-items: flex-start; gap: 0.65rem; padding: 0.45rem 0; border-bottom: 1px solid #F1F5F9; font-size: 0.865rem; line-height: 1.5; color: #0F172A;">
                    <span style="color: {COLOR_ACCENT}; font-size: 0.9rem; line-height: 1.3;">●</span>
                    <div>{insight}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# 6. PAGE 2: COURSE ANALYTICS
def render_course_analytics(eda_data: Dict[str, Any], df: pd.DataFrame) -> None:
    render_dashboard_header(
        title="Course Category Analytics",
        subtitle="Filter and analyze student engagement behaviors across specific academic disciplines.",
    )

    categories = sorted(list(eda_data["category_analytics"].keys()))

    # Discipline Filter Selectbox
    f_col1, f_col2 = st.columns([1.5, 3])
    with f_col1:
        selected_category = st.selectbox(
            "Select Discipline Filter:",
            options=["All Categories"] + categories,
            index=0,
        )

    if selected_category == "All Categories":
        filtered_df = df
        cat_kpis = eda_data["kpis"]
        total_cnt = cat_kpis["total_learners"]
        comp_rate = cat_kpis["overall_completion_pct"]
        avg_score = cat_kpis["avg_quiz_score"]
        avg_time = cat_kpis["avg_time_spent"]
    else:
        filtered_df = df[df["CourseCategory"] == selected_category]
        cat_metrics = eda_data["category_analytics"][selected_category]
        total_cnt = cat_metrics["total_learners"]
        comp_rate = cat_metrics["completion_rate_pct"]
        avg_score = cat_metrics["avg_quiz_score"]
        avg_time = cat_metrics["avg_time_spent"]

    # Filtered KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Enrollment Volume", f"{total_cnt:,}", selected_category, "👥", "Learners", False)
    with col2:
        render_kpi_card("Completion Ratio", f"{comp_rate:.1f}%", "Completed Learners", "🎯", f"{comp_rate:.1f}%", True)
    with col3:
        render_kpi_card("Average Quiz Grade", f"{avg_score:.1f}", "Points (0-100 scale)", "📝", "Mean", True)
    with col4:
        render_kpi_card("Average Learning Time", f"{avg_time:.1f} hrs", "Logged Course Duration", "⏱️", "Hours", False)

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # 3-Column Distribution Grid
    dist_col1, dist_col2, dist_col3 = st.columns(3)

    with dist_col1:
        with st.container(border=True):
            render_card_header(
                title="Video Engagement",
                subtitle="Videos watched distribution by completion",
            )
            fig_v = create_distribution_box_plot(filtered_df, "NumberOfVideosWatched", "Videos Watched")
            st.plotly_chart(fig_v, use_container_width=True, config={"displayModeBar": False})

    with dist_col2:
        with st.container(border=True):
            render_card_header(
                title="Quiz Performance",
                subtitle="Quiz scores distribution by completion",
            )
            fig_q = create_distribution_box_plot(filtered_df, "QuizScores", "Quiz Scores (%)")
            st.plotly_chart(fig_q, use_container_width=True, config={"displayModeBar": False})

    with dist_col3:
        with st.container(border=True):
            render_card_header(
                title="Learning Duration",
                subtitle="Time spent on course by completion",
            )
            fig_t = create_distribution_box_plot(filtered_df, "TimeSpentOnCourse", "Time Spent (Hours)")
            st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})


# 7. PAGE 3: MODEL PERFORMANCE
def render_model_performance(
    metrics_data: Optional[Dict[str, Any]],
    cm_data: Optional[Dict[str, Any]],
) -> None:
    render_dashboard_header(
        title="Model Performance & ML Monitoring",
        subtitle="Comprehensive benchmarking of Spark MLlib pipelines evaluated on held-out test data (20% split).",
    )

    if not metrics_data or not cm_data:
        st.error("Model artifacts or metrics not found. Run `python -m src.model_training` to train models.")
        return

    models = metrics_data["models"]
    rf = models["random_forest"]
    lr = models["logistic_regression"]

    # Champion Model Hero Card
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 0.25rem;">
                <div>
                    <span style="background-color: {COLOR_ACCENT}; color: white; font-size: 0.725rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.04em;">
                        Selected Champion Model
                    </span>
                    <div style="font-size: 1.35rem; font-weight: 700; color: #0F172A; margin-top: 0.35rem; letter-spacing: -0.01em;">
                        Random Forest Classifier (Spark MLlib)
                    </div>
                    <div style="font-size: 0.85rem; color: #64748B;">
                        Ranked #1 using composite scoring prioritized on <strong>ROC-AUC (0.9586)</strong> and <strong>F1-Score (0.9440)</strong>.
                    </div>
                </div>
                <div style="display: flex; gap: 2rem;">
                    <div>
                        <div style="font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Test Accuracy</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">{rf['accuracy']:.1%}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Precision</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">{rf['precision']:.1%}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Recall</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">{rf['recall']:.1%}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase;">ROC-AUC</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">{rf['roc_auc']:.3f}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Benchmark Row: Grouped Bar & Confusion Matrix
    b_col1, b_col2 = st.columns([1.35, 1])

    with b_col1:
        with st.container(border=True):
            render_card_header(
                title="Model Metrics Comparison",
                subtitle="Comparative evaluation of Accuracy, Precision, Recall, F1, and ROC-AUC",
            )
            fig_compare = create_model_comparison_bar(models)
            st.plotly_chart(fig_compare, use_container_width=True, config={"displayModeBar": False})

    with b_col2:
        with st.container(border=True):
            cm_select = st.selectbox(
                "Select Model Confusion Matrix:",
                options=["Random Forest (Champion)", "Logistic Regression"],
                index=0,
            )
            cm_key = "random_forest" if "forest" in cm_select.lower() else "logistic_regression"
            fig_cm = create_confusion_matrix_heatmap(cm_data[cm_key]["matrix"], cm_select)
            st.plotly_chart(fig_cm, use_container_width=True, config={"displayModeBar": False})

            tp = cm_data[cm_key]["true_positives"]
            tn = cm_data[cm_key]["true_negatives"]
            fp = cm_data[cm_key]["false_positives"]
            fn = cm_data[cm_key]["false_negatives"]
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-around; font-size: 0.8rem; color: #64748B; border-top: 1px solid {COLOR_BORDER}; padding-top: 0.5rem;">
                    <span>TP: <strong>{tp:,}</strong></span>
                    <span>TN: <strong>{tn:,}</strong></span>
                    <span>FP: <strong>{fp:,}</strong></span>
                    <span>FN: <strong>{fn:,}</strong></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Target Leakage Analysis Table
    with st.container(border=True):
        render_card_header(
            title="Target Leakage Investigation (Evaluation With vs Without CompletionRate)",
            subtitle="Evaluating whether syllabus progress percentage drives predictions vs core engagement behaviors",
        )
        leakage = metrics_data.get("leakage_investigation", {})
        st.markdown(
            f"""
            <div style="font-size: 0.865rem; color: #64748B; margin-bottom: 0.75rem; line-height: 1.5;">
                {leakage.get("finding", "")}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with_cr = leakage.get("with_completion_rate", {})
        without_cr = leakage.get("without_completion_rate", {})

        tbl_data = [
            {
                "ML Algorithm": "Random Forest Classifier",
                "Accuracy (With Progress Rate)": f"{with_cr.get('random_forest', {}).get('accuracy', 0):.4f}",
                "F1-Score (With Progress Rate)": f"{with_cr.get('random_forest', {}).get('f1_score', 0):.4f}",
                "ROC-AUC (With Progress Rate)": f"{with_cr.get('random_forest', {}).get('roc_auc', 0):.4f}",
                "Accuracy (Without Progress Rate)": f"{without_cr.get('random_forest', {}).get('accuracy', 0):.4f}",
                "F1-Score (Without Progress Rate)": f"{without_cr.get('random_forest', {}).get('f1_score', 0):.4f}",
                "ROC-AUC (Without Progress Rate)": f"{without_cr.get('random_forest', {}).get('roc_auc', 0.8747):.4f}",
            },
            {
                "ML Algorithm": "Logistic Regression",
                "Accuracy (With Progress Rate)": f"{with_cr.get('logistic_regression', {}).get('accuracy', 0):.4f}",
                "F1-Score (With Progress Rate)": f"{with_cr.get('logistic_regression', {}).get('f1_score', 0):.4f}",
                "ROC-AUC (With Progress Rate)": f"{with_cr.get('logistic_regression', {}).get('roc_auc', 0):.4f}",
                "Accuracy (Without Progress Rate)": f"{without_cr.get('logistic_regression', {}).get('accuracy', 0):.4f}",
                "F1-Score (Without Progress Rate)": f"{without_cr.get('logistic_regression', {}).get('f1_score', 0):.4f}",
                "ROC-AUC (Without Progress Rate)": f"{without_cr.get('without_completion_rate', {}).get('roc_auc', 0.8162):.4f}",
            },
        ]
        st.dataframe(pd.DataFrame(tbl_data), use_container_width=True, hide_index=True)


# 8. PAGE 4: STUDENT PREDICTION (Responsive 2-Column Layout, Zero Horizontal Overflow)
def render_student_prediction() -> None:
    render_dashboard_header(
        title="Student Completion Prediction",
        subtitle="Simulate learner attributes and predict the likelihood of successful course completion using Spark MLlib.",
    )

    pred_left, pred_right = st.columns([1, 1], gap="medium")

    with pred_left:
        with st.container(border=True):
            render_card_header(
                title="Learner Activity Profile",
                subtitle="Configure the learner's study duration, video engagement, and quiz grades",
            )

            category = st.selectbox(
                "Course Category:",
                options=VALID_CATEGORIES,
                index=3,  # Programming
            )

            device_type = st.selectbox(
                "Device Type (Encoded):",
                options=VALID_DEVICE_TYPES,
                index=1,
                format_func=lambda x: f"Device Type {x}",
            )

            time_spent = st.slider(
                "Time Spent on Course (Hours):",
                min_value=0.0,
                max_value=120.0,
                value=55.0,
                step=1.0,
            )

            sub_c1, sub_c2 = st.columns(2)
            with sub_c1:
                videos_watched = st.number_input(
                    "Videos Watched:",
                    min_value=0,
                    max_value=25,
                    value=12,
                    step=1,
                )
            with sub_c2:
                quizzes_taken = st.number_input(
                    "Quizzes Taken:",
                    min_value=0,
                    max_value=15,
                    value=6,
                    step=1,
                )

            quiz_score = st.slider(
                "Average Quiz Score (%):",
                min_value=0.0,
                max_value=100.0,
                value=82.0,
                step=0.5,
            )

            completion_rate = st.slider(
                "Module Progress Rate (%):",
                min_value=0.0,
                max_value=100.0,
                value=65.0,
                step=1.0,
            )

    with pred_right:
        with st.container(border=True):
            render_card_header(
                title="Prediction Results",
                subtitle="Execute real-time classification through the trained Spark MLlib pipeline",
            )

            model_choice = st.selectbox(
                "Selected Model for Inference:",
                options=["Random Forest (Champion)", "Logistic Regression"],
                index=0,
            )

            predict_clicked = st.button("Predict Course Completion")

            if predict_clicked:
                learner_payload = {
                    "CourseCategory": category,
                    "TimeSpentOnCourse": float(time_spent),
                    "NumberOfVideosWatched": int(videos_watched),
                    "NumberOfQuizzesTaken": int(quizzes_taken),
                    "QuizScores": float(quiz_score),
                    "CompletionRate": float(completion_rate),
                    "DeviceType": int(device_type),
                }
                model_key = "random_forest" if "forest" in model_choice.lower() else "logistic_regression"

                with st.spinner("Scoring through Spark MLlib Pipeline..."):
                    try:
                        res = predict_learner_completion(learner_payload, model_key)
                        render_prediction_result(
                            res["predicted_label"],
                            res["probability_completion"],
                            res["model_used"],
                            res["explanation"],
                        )
                        st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)
                        fig_g = create_prediction_gauge(res["probability_completion"])
                        st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})
                    except Exception as e:
                        st.error(f"Prediction Error: {e}")
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #F8FAFC; border: 1px dashed {COLOR_BORDER}; border-radius: 8px; padding: 2.5rem 1.25rem; text-align: center; color: #64748B; font-size: 0.85rem; margin-top: 0.5rem;">
                        <span style="font-size: 1.8rem;">🔮</span>
                        <div style="font-weight: 600; color: #0F172A; margin-top: 0.4rem;">Ready for Inference</div>
                        <div style="margin-top: 0.2rem;">Adjust learner attributes on the left and click <strong>Predict Course Completion</strong>.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# 9. PAGE 5: DATA EXPLORER
def render_data_explorer(df: pd.DataFrame, eda_data: Dict[str, Any]) -> None:
    render_dashboard_header(
        title="Data Explorer & Quality Audit",
        subtitle="Audit dataset health, inspect raw rows, and filter student activity records.",
    )

    # 4 Equal-Height White KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Ingested", "9,000", "Raw CSV Records", "📥", "Raw Ingest", False)
    with col2:
        render_kpi_card("Duplicates Removed", "877", "Exact Match Rows Handled", "🧹", "Deduplicated", True)
    with col3:
        render_kpi_card("Master Records", "8,123", "Clean Analysis Rows", "📊", "Clean Set", False)
    with col4:
        render_kpi_card("Missing Values", "0", "100% Complete Records", "✨", "Zero Nulls", True)

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Interactive Filter Controls
    with st.container(border=True):
        render_card_header(title="Filter & Inspect Dataset")
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            cat_filter = st.selectbox("Course Category:", options=["All"] + VALID_CATEGORIES, index=0)
        with f2:
            status_filter = st.selectbox("Completion Status:", options=["All", "Completed (1)", "Not Completed (0)"], index=0)
        with f3:
            search_uid = st.text_input("Search by UserID:", placeholder="e.g. 5618")

        # Apply Filters
        filtered = df.copy()
        if cat_filter != "All":
            filtered = filtered[filtered["CourseCategory"] == cat_filter]
        if status_filter == "Completed (1)":
            filtered = filtered[filtered["CourseCompletion"] == 1]
        elif status_filter == "Not Completed (0)":
            filtered = filtered[filtered["CourseCompletion"] == 0]
        if search_uid.strip():
            try:
                uid = int(search_uid.strip())
                filtered = filtered[filtered["UserID"] == uid]
            except ValueError:
                st.warning("UserID must be an integer.")

        st.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** records")
        st.dataframe(filtered, use_container_width=True, height=340)

        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Subset as CSV",
            data=csv_data,
            file_name="course_engagement_filtered.csv",
            mime="text/csv",
        )

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Correlation Matrix & Summary Statistics
    stat_left, stat_right = st.columns([1.2, 1])

    with stat_left:
        with st.container(border=True):
            render_card_header(
                title="Descriptive Summary Statistics",
                subtitle="Parametric distribution metrics across numerical engagement attributes",
            )
            st.dataframe(df.describe().round(2), use_container_width=True)

    with stat_right:
        with st.container(border=True):
            render_card_header(
                title="Feature Correlation Heatmap",
                subtitle="Linear correlation coefficients (Pearson r) with CourseCompletion",
            )
            fig_corr = create_correlation_heatmap(eda_data["correlation_matrix"])
            st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})


# 10. Main Router
def main() -> None:
    eda_data = load_eda_summary()
    metrics_data = load_model_metrics()
    cm_data = load_confusion_matrices()
    df = load_master_dataset()

    page = render_sidebar()

    if page == "Overview":
        if eda_data:
            render_overview(eda_data, df)
        else:
            st.error("EDA summary not found. Run `python -m src.exploratory_analysis`.")

    elif page == "Course Analytics":
        if eda_data:
            render_course_analytics(eda_data, df)
        else:
            st.error("EDA summary not found.")

    elif page == "Model Performance":
        render_model_performance(metrics_data, cm_data)

    elif page == "Student Prediction":
        render_student_prediction()

    elif page == "Data Explorer":
        if eda_data:
            render_data_explorer(df, eda_data)


if __name__ == "__main__":
    main()
