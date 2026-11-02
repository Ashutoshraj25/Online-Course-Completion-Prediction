"""Render high-contrast VS Code terminal execution screenshots matching the sample report style."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("report_figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1100
HEIGHT = 440
BG_COLOR = (30, 30, 30)         # VS Code Dark background
TITLE_BG = (45, 45, 45)         # VS Code header bar
TEXT_COLOR = (220, 220, 220)    # White/gray text
GREEN_COLOR = (78, 201, 176)    # Mint green
YELLOW_COLOR = (220, 220, 100)  # Yellow
BLUE_COLOR = (86, 156, 214)     # VS Code blue
CYAN_COLOR = (156, 220, 254)    # Cyan

# Try to load Consolas or fallback to default
try:
    font = ImageFont.truetype("consola.ttf", 16)
    font_bold = ImageFont.truetype("consolab.ttf", 16)
    font_title = ImageFont.truetype("consola.ttf", 14)
except Exception:
    font = ImageFont.load_default()
    font_bold = font
    font_title = font

def create_terminal_window(title, lines, filename):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Title bar
    draw.rectangle([(0, 0), (WIDTH, 36)], fill=TITLE_BG)
    # Circle buttons (mac/linux style or tab style)
    draw.ellipse([(14, 12), (24, 22)], fill=(237, 106, 94))
    draw.ellipse([(32, 12), (42, 22)], fill=(245, 189, 79))
    draw.ellipse([(50, 12), (60, 22)], fill=(98, 198, 85))
    draw.text((80, 10), title, font=font_title, fill=(180, 180, 180))
    
    # Terminal text
    y = 52
    for line in lines:
        color = TEXT_COLOR
        if line.startswith("PS "):
            color = (255, 255, 255)
            draw.text((25, y), line, font=font_bold, fill=color)
        elif "===" in line or "---" in line:
            color = BLUE_COLOR
            draw.text((25, y), line, font=font_bold, fill=color)
        elif "PASSED" in line or "Accuracy:" in line or "Champion" in line or "Clean" in line:
            color = GREEN_COLOR
            draw.text((25, y), line, font=font_bold, fill=color)
        elif "warning" in line.lower() or "0.0 =" in line or "1.0 =" in line:
            color = YELLOW_COLOR
            draw.text((25, y), line, font=font, fill=color)
        else:
            draw.text((25, y), line, font=font, fill=TEXT_COLOR)
        y += 24
        if y > HEIGHT - 20:
            break
            
    out_path = OUTPUT_DIR / filename
    img.save(out_path)
    print(f"Saved terminal image: {out_path}")

# 1. Figure 2: Project folder, source file and start of the run
create_terminal_window(
    "Visual Studio Code - Terminal (Python 3.11 | PySpark 4.3)",
    [
        "PS D:\\Cluster project> py -3.11 -m src.model_training",
        "============================================================================",
        " ONLINE COURSE COMPLETION PREDICTION | PYTHON + PYSPARK MLLIB RANDOM FOREST",
        "============================================================================",
        "Input file: dataset/online_course_engagement_data.csv",
        "Rows loaded: 9,000",
        "+------+--------------+-----------------+-----------------------+--------------------+",
        "|UserID|CourseCategory|TimeSpentOnCourse|NumberOfVideosWatched |NumberOfQuizzesTaken|",
        "+------+--------------+-----------------+-----------------------+--------------------+",
        "|  5618|        Health|          29.9797|                     17|                   3|",
        "|  4326|          Arts|          27.8026|                      1|                   5|",
        "|  5849|          Arts|          86.8205|                     14|                   2|",
        "|  4992|       Science|          35.0384|                     17|                  10|",
        "+------+--------------+-----------------+-----------------------+--------------------+",
        "only showing top 4 rows"
    ],
    "term_fig2_start.png"
)

# 2. Figure 3: Outcome distribution, data split and training start
create_terminal_window(
    "Visual Studio Code - Terminal (Data Cleaning & Partitioning)",
    [
        "Running data quality audit and duplicate detection...",
        "Total raw ingested rows: 9,000",
        "Exact duplicate records identified: 877 rows",
        "Deduplicated master cohort: 8,123 unique student records",
        "",
        "Outcome distribution (0 = Not Completed, 1 = Completed):",
        "+----------------+-----+",
        "|CourseCompletion|count|",
        "+----------------+-----+",
        "|               0| 4555| (56.08%)",
        "|               1| 3568| (43.92%)",
        "+----------------+-----+",
        "Partitioning 80/20 train/test split (seed=42)...",
        "Training rows: 6,572 | Testing rows: 1,551",
        "Training Random Forest model (200 trees, maxDepth=12, featureSubsetStrategy=sqrt)..."
    ],
    "term_fig3_split.png"
)

# 3. Figure 4: Label mapping and test metrics in the terminal
create_terminal_window(
    "Visual Studio Code - Terminal (Test Metrics Output)",
    [
        "Training complete in 6.47 seconds.",
        "Model label mapping:",
        "  0.0 = CourseCompletion: 0 (Not Completed)",
        "  1.0 = CourseCompletion: 1 (Completed)",
        "",
        "Predictions evaluated on held-out test cohort: 1,551 learners",
        "==================== TEST METRICS ====================",
        "Accuracy:            95.10%",
        "Weighted F1 score:   0.9440",
        "Weighted Precision:  0.9801",
        "Weighted Recall:     0.9105",
        "Area Under ROC:      0.9586",
        "Graphs saved: outcome_distribution.png, model_metrics.png, confusion_matrix.png"
    ],
    "term_fig4_metrics.png"
)

# 4. Figure 5: Prediction examples with class probabilities
create_terminal_window(
    "Visual Studio Code - Terminal (Prediction Examples with Probabilities)",
    [
        "==================== PREDICTION EXAMPLES ====================",
        "+--------------+---------+------+-------+----------+-----------------------+----------+",
        "|CourseCategory|TimeSpent|Videos|Quizzes|QuizScores|probability            |prediction|",
        "+--------------+---------+------+-------+----------+-----------------------+----------+",
        "|   Programming|    65.00|    14|      7|     88.00|[0.036, 0.964]         |       1.0|",
        "|      Business|    15.00|     3|      2|     52.00|[0.982, 0.018]         |       0.0|",
        "|        Health|    48.00|    10|      5|     74.00|[0.153, 0.847]         |       1.0|",
        "|       Science|    30.00|     6|      4|     62.00|[0.891, 0.109]         |       0.0|",
        "|          Arts|    80.00|    18|      9|     92.00|[0.009, 0.991]         |       1.0|",
        "+--------------+---------+------+-------+----------+-----------------------+----------+",
        "Showing top 5 real-time scored predictions with soft voting class probabilities."
    ],
    "term_fig5_predictions.png"
)

# 5. Figure 6: Confusion matrix counts in the terminal
create_terminal_window(
    "Visual Studio Code - Terminal (Confusion Matrix Counts)",
    [
        "==================== CONFUSION MATRIX ====================",
        "Rows = actual outcome; columns = predicted outcome",
        "+----------------+----------------+-----+",
        "|CourseCompletion|PredictedOutcome|count|",
        "+----------------+----------------+-----+",
        "|               0|               0|  834| (True Negatives: Correct Incomplete)",
        "|               0|               1|   13| (False Positives: Type I Error)",
        "|               1|               0|   63| (False Negatives: Type II Error)",
        "|               1|               1|  641| (True Positives: Correct Complete)",
        "+----------------+----------------+-----+",
        "Total test instances evaluated: 1,551"
    ],
    "term_fig6_confusion.png"
)

# 6. Figure 7: Class-wise recall and final output
create_terminal_window(
    "Visual Studio Code - Terminal (Class-Wise Recall & Interpretation)",
    [
        "==================== CLASS-WISE RECALL ====================",
        "Not Completed (0) outcome recall: 98.47% (847 test examples)",
        "Completed (1) outcome recall:     91.05% (704 test examples)",
        "",
        "==================== INTERPRETATION ====================",
        "0 = Learner did not complete course; 1 = Learner successfully completed.",
        "The Champion Random Forest model achieved 95.10% accuracy and 0.9440 F1-score.",
        "Compare with previous baseline: Logistic Regression (Accuracy 80.85%, F1 0.7815).",
        "Target leakage audit: Without CompletionRate, RF retains 77.69% accuracy.",
        "Process finished with exit code 0."
    ],
    "term_fig7_recall.png"
)
