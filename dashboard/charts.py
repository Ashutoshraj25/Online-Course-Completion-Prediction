"""Plotly visualization suite for Course Analytics Dashboard.

Fully compliant with modern Plotly specifications:
- Zero deprecated 'titlefont' properties
- Inter typography and crisp light-theme styling
- Sized cleanly to fit inside card containers without overflow
"""

from typing import Any, Dict, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Strict SaaS Color Palette
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_MUTED = "#64748B"
COLOR_ACCENT = "#2563EB"
COLOR_ACCENT_LIGHT = "#93C5FD"
COLOR_SUCCESS = "#16A34A"
COLOR_DANGER = "#DC2626"
COLOR_GRID = "#F1F5F9"
COLOR_BORDER = "#E2E8F0"

PLOTLY_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color=COLOR_TEXT_PRIMARY, size=12),
)


def create_completion_donut_chart(completed: int, not_completed: int) -> go.Figure:
    """Generate minimal doughnut chart for overall completion ratio."""
    total = completed + not_completed
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Completed", "Not Completed"],
                values=[completed, not_completed],
                hole=0.68,
                marker=dict(colors=[COLOR_SUCCESS, COLOR_DANGER]),
                textinfo="percent",
                hoverinfo="label+value+percent",
                textposition="inside",
                insidetextfont=dict(size=12, color="#FFFFFF", weight=600),
                direction="clockwise",
                sort=False,
            )
        ]
    )
    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color=COLOR_TEXT_MUTED),
        ),
        annotations=[
            dict(
                text=f"<b style='font-size:22px;color:{COLOR_TEXT_PRIMARY};'>{total:,}</b><br><span style='font-size:11px;color:{COLOR_TEXT_MUTED};font-weight:500;'>TOTAL LEARNERS</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ],
    )
    return fig


def create_category_completion_chart(cat_analytics: Dict[str, Dict[str, Any]]) -> go.Figure:
    """Generate horizontal stacked bar chart of completion by course category."""
    categories = sorted(list(cat_analytics.keys()))
    completed_vals = [cat_analytics[c]["completed_learners"] for c in categories]
    not_completed_vals = [cat_analytics[c]["not_completed_learners"] for c in categories]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Completed",
                y=categories,
                x=completed_vals,
                orientation="h",
                marker=dict(color=COLOR_SUCCESS, line=dict(width=0)),
                text=completed_vals,
                textposition="auto",
                insidetextfont=dict(color="#FFFFFF", size=11, weight=600),
            ),
            go.Bar(
                name="Not Completed",
                y=categories,
                x=not_completed_vals,
                orientation="h",
                marker=dict(color=COLOR_DANGER, line=dict(width=0)),
                text=not_completed_vals,
                textposition="auto",
                insidetextfont=dict(color="#FFFFFF", size=11, weight=600),
            ),
        ]
    )
    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=280,
        margin=dict(l=20, r=20, t=10, b=20),
        barmode="stack",
        xaxis=dict(
            title=dict(text="Number of Learners", font=dict(size=11, color=COLOR_TEXT_MUTED)),
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_BORDER,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
        ),
        yaxis=dict(
            title=None,
            autorange="reversed",
            tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY, weight=600),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=COLOR_TEXT_MUTED),
        ),
    )
    return fig


def create_category_score_bar(cat_analytics: Dict[str, Dict[str, Any]]) -> go.Figure:
    """Generate clean vertical bar chart of average quiz score by category."""
    categories = sorted(list(cat_analytics.keys()))
    scores = [cat_analytics[c]["avg_quiz_score"] for c in categories]

    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=scores,
                marker=dict(color=COLOR_ACCENT, line=dict(width=0), opacity=0.9),
                text=[f"{s:.1f}" for s in scores],
                textposition="outside",
                textfont=dict(size=11, color=COLOR_TEXT_PRIMARY, weight=600),
            )
        ]
    )
    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=280,
        margin=dict(l=20, r=20, t=25, b=20),
        yaxis=dict(
            title=dict(text="Average Quiz Score (%)", font=dict(size=11, color=COLOR_TEXT_MUTED)),
            range=[0, 105],
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_BORDER,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY, weight=500),
        ),
    )
    return fig


def create_engagement_scatter_chart(df: pd.DataFrame) -> go.Figure:
    """Generate high-clarity scatter plot showing Time Spent vs Quiz Score by completion."""
    sample_df = df.sample(min(800, len(df)), random_state=42).copy()
    sample_df["Outcome"] = sample_df["CourseCompletion"].map({1: "Completed", 0: "Not Completed"})

    fig = px.scatter(
        sample_df,
        x="TimeSpentOnCourse",
        y="QuizScores",
        color="Outcome",
        color_discrete_map={"Completed": COLOR_SUCCESS, "Not Completed": COLOR_DANGER},
        opacity=0.65,
        hover_data={"TimeSpentOnCourse": ":.1f", "QuizScores": ":.1f", "Outcome": True},
    )
    fig.update_traces(marker=dict(size=6, line=dict(width=0)))
    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=280,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis=dict(
            title=dict(text="Time Spent on Course (Hours)", font=dict(size=11, color=COLOR_TEXT_MUTED)),
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_BORDER,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
        ),
        yaxis=dict(
            title=dict(text="Quiz Scores (%)", font=dict(size=11, color=COLOR_TEXT_MUTED)),
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_BORDER,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title="",
            font=dict(size=11, color=COLOR_TEXT_MUTED),
        ),
    )
    return fig


def create_distribution_box_plot(
    df: pd.DataFrame,
    col_name: str,
    y_title: str,
) -> go.Figure:
    """Generate minimalist box plot comparing metric by completion status."""
    plot_df = df.copy()
    plot_df["Status"] = plot_df["CourseCompletion"].map({1: "Completed", 0: "Not Completed"})

    fig = px.box(
        plot_df,
        x="Status",
        y=col_name,
        color="Status",
        color_discrete_map={"Completed": COLOR_SUCCESS, "Not Completed": COLOR_DANGER},
        points=False,
    )
    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=270,
        margin=dict(l=20, r=20, t=10, b=20),
        showlegend=False,
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=11, color=COLOR_TEXT_MUTED)),
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_BORDER,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY, weight=600),
        ),
    )
    return fig


def create_model_comparison_bar(models_metrics: Dict[str, Dict[str, Any]]) -> go.Figure:
    """Generate side-by-side grouped benchmark bar chart."""
    metrics_keys = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]

    lr_vals = [models_metrics["logistic_regression"][m] for m in metrics_keys]
    rf_vals = [models_metrics["random_forest"][m] for m in metrics_keys]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Logistic Regression",
                x=metric_labels,
                y=lr_vals,
                marker=dict(color=COLOR_ACCENT_LIGHT, line=dict(width=0)),
                text=[f"{v:.3f}" for v in lr_vals],
                textposition="outside",
                textfont=dict(size=10, color=COLOR_TEXT_MUTED, weight=600),
            ),
            go.Bar(
                name="Random Forest (Champion)",
                x=metric_labels,
                y=rf_vals,
                marker=dict(color=COLOR_ACCENT, line=dict(width=0)),
                text=[f"{v:.3f}" for v in rf_vals],
                textposition="outside",
                textfont=dict(size=10, color=COLOR_TEXT_PRIMARY, weight=600),
            ),
        ]
    )
    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=320,
        margin=dict(l=20, r=20, t=25, b=20),
        barmode="group",
        yaxis=dict(
            title=dict(text="Performance Metric Score", font=dict(size=11, color=COLOR_TEXT_MUTED)),
            range=[0, 1.15],
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_BORDER,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY, weight=600),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(size=11, color=COLOR_TEXT_MUTED),
        ),
    )
    return fig


def create_confusion_matrix_heatmap(matrix_data: List[List[int]], model_name: str) -> go.Figure:
    """Generate styled 2x2 confusion matrix heatmap."""
    z = matrix_data
    x = ["Pred: Not Completed", "Pred: Completed"]
    y = ["Actual: Not Completed", "Actual: Completed"]

    tn, fp = z[0]
    fn, tp = z[1]
    annotations = [
        [f"TN<br><b style='font-size:16px;'>{tn:,}</b>", f"FP<br><b style='font-size:16px;'>{fp:,}</b>"],
        [f"FN<br><b style='font-size:16px;'>{fn:,}</b>", f"TP<br><b style='font-size:16px;'>{tp:,}</b>"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale=[[0, "#EFF6FF"], [0.4, "#93C5FD"], [1, "#1D4ED8"]],
            showscale=False,
            hoverinfo="none",
        )
    )

    for i in range(len(y)):
        for j in range(len(x)):
            fig.add_annotation(
                text=annotations[i][j],
                x=x[j],
                y=y[i],
                font=dict(size=13, color=COLOR_TEXT_PRIMARY if z[i][j] < 400 else "#FFFFFF", weight=600),
                showarrow=False,
            )

    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(side="bottom", tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY, weight=600)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY, weight=600)),
    )
    return fig


def create_prediction_gauge(probability: float) -> go.Figure:
    """Generate minimal semicircular probability gauge."""
    pct = round(probability * 100, 1)
    bar_color = COLOR_SUCCESS if probability >= 0.5 else COLOR_DANGER

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 36, "color": COLOR_TEXT_PRIMARY, "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": COLOR_TEXT_MUTED},
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": COLOR_BORDER,
                "steps": [
                    {"range": [0, 50], "color": "#FEE2E2"},
                    {"range": [50, 100], "color": "#DCFCE7"},
                ],
                "threshold": {
                    "line": {"color": COLOR_TEXT_PRIMARY, "width": 3},
                    "thickness": 0.75,
                    "value": pct,
                },
            },
        )
    )
    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=200,
        margin=dict(l=20, r=20, t=10, b=10),
    )
    return fig


def create_correlation_heatmap(corr_dict: Dict[str, Dict[str, float]]) -> go.Figure:
    """Generate correlation heatmap for numeric features."""
    corr_df = pd.DataFrame(corr_dict)
    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        color_continuous_scale="Blues",
        aspect="auto",
    )
    fig.update_layout(
        **PLOTLY_DEFAULTS,
        height=380,
        margin=dict(l=30, r=30, t=20, b=30),
        coloraxis_showscale=False,
        xaxis=dict(tickangle=-25, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
    )
    return fig
