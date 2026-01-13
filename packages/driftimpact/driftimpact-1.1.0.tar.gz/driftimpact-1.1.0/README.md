# DriftImpact Library

![DriftImpact Banner](banner.png)

A comprehensive Python library for detecting **Data Drift** and **Concept Drift**, and analyzing their impact on **Model Performance**.

## 🧠 Methodology

The library analyzes changes in datasets across three main layers:

### 1. Data Drift
Compares feature distributions between training data (Train) and scoring data (Score).
- **Numerical Variables**: Uses `KS Test` for distribution differences, `Mann-Whitney U` for central tendency shifts, and `Levene Test` for variance changes.
- **Categorical Variables**: Frequency distribution changes are measured using the `Chi-Square` test.
- **P-Value Standardization**: All test results are standardized according to the selected threshold. Metrics with detected drift are reported in **red**, and those without in **green**.

### 2. Concept Drift
Analyzes how the relationship between features and the target variable changes over time.
- **Fisher Z-Test**: Detects significant changes in the correlation of numerical features with the target variable.
- **Cramer's V**: Measures changes in the strength of association between categorical features and the target variable.
- **Temporal Analysis**: Finds the point where the relationship begins to deteriorate (**First Drift Point**) by dividing data into time windows.

### 3. Performance Impact Analysis
Analyzes whether drift is just a statistical deviation or if it actually degrades model performance.
- Calculates a **"Weighted Drift Score"** using model feature importances.
- Compares the drift score with model performance metrics (Accuracy, F1, RMSE, etc.) across time periods.
- Visualizes whether performance drops as drift increases, helping you determine the right time for intervention.

---

## ✨ Key Features

- **Interactive HTML Report**: A modern dashboard with drag-and-drop support and modal zooming.
- **P-Value Color Coding**: Immediate visual feedback based on drift status.
- **Automated Dashboards**: Detailed visual analyses and summary tables with a single command.
- **AI Advisor (LLM)**: Actionable recommendations to fix drift, supporting local (Ollama, vLLM) and cloud (OpenAI) models.
- **Flexible Integration**: Works directly with scikit-learn compatible models.

---

## 🚀 Installation

To install the library locally:

```bash
pip install .
```

---

## 🛠 Usage

### 1. Full Drift Analysis and Reporting

```python
from driftimpact import DriftAnalyzer
import pandas as pd

# Initialize Analyzer
analyzer = DriftAnalyzer(target_col='churn', threshold=0.05)

# Load data
train_df = pd.read_csv('train.csv')
score_df = pd.read_csv('score.csv')

# Run all analyses (Data Drift + Concept Drift + Temporal)
results = analyzer.full_analysis(train_df, score_df, time_col='date')

# Create Interactive HTML Report
analyzer.generate_html_report(results, save_dir='./reports')
```

### 2. Model Performance Impact Analysis

To measure your model's resilience against drift:

```python
# Run analysis by providing the model, score data, and actual labels
impact_df = analyzer.analyze_performance_impact(
    model=my_trained_model,
    score_df=score_df,        # Features + Time column
    y_true=score_df['label'], # Realized labels
    time_col='date',
    drift_results=results.get('temporal_drift')
)

# Visualize the relationship between Drift and Performance
analyzer.visualize_performance_impact(impact_df, metric_name='accuracy', save_dir='./reports')
```

### 3. AI Advisor (Actionable Insights)

Get technical roadmap to fix detected drift using LLMs. Supports OpenAI-compatible APIs (Ollama, vLLM, OpenAI, etc.):

#### Option A: Local LLM (e.g., Ollama)
```python
# Default is configured for local Ollama with qwen2.5
advice = analyzer.get_ai_advice(results, language='tr')
```

#### Option B: Cloud API (e.g., OpenAI, Azure)
```python
# Pass your API key and base URL
advice = analyzer.get_ai_advice(
    results, 
    base_url="https://api.openai.com/v1",
    api_key="your-api-key-here",
    model="gpt-4",
    language='en'
)
```

# Generate report with AI insights included
analyzer.generate_html_report(results, ai_advice=advice)
```

---

## 📁 Project Structure

- `driftimpact/`: Core library code.
- `reports/`: Generated HTML reports and PNG charts.
- `test.py`: Testing the entire flow using an example Churn model.

## 📄 License

MIT License
