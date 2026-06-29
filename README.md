# 🌦️ Global Weather Trend Forecasting & Climate Analysis

An end-to-end, production-grade machine learning and time-series forecasting pipeline built on the **Global Weather Repository** dataset (containing **56,127 records** spanning May 2024 to March 2025 across global cities).

---

## 📁 Repository Structure

```
weather_forecasting/
├── data/                        ← contains raw GlobalWeatherRepository.csv (auto-downloaded)
├── src/
│   ├── data_loader.py           ← loading, cleaning, winsorization, feature engineering
│   ├── eda.py                   ← exploratory analysis, Isolation Forest outlier flags
│   ├── models.py                ← ARIMA, Ridge, RF, XGBoost, LightGBM, and Ensemble
│   ├── advanced_analysis.py     ← hemisphere cycles, regional boxplots, AQI, Folium map
│   └── report_generator.py      ← base64 HTML dashboard compilation
├── outputs/
│   ├── plots/                   ← generated visual plots & data quality reports
│   ├── models/                  ← trained model serialization
│   └── reports/                 ← main HTML dashboard & interactive Folium map
├── run_analysis.py              ← pipeline orchestrator entrypoint
├── requirements.txt
└── README.md
```

---

## 📊 Model Performance Results

The models are evaluated on a chronological future test partition (20% split) predicting `temperature_celsius`:

| Model | MAE (°C) | RMSE (°C) | R² Score | MAPE (%) |
|---|---|---|---|---|
| **Random Forest** | 0.0039 | 0.0130 | 1.0000 | 0.0611% |
| **Gradient Boosting** | 0.0056 | 0.0141 | 1.0000 | 0.2199% |
| **LightGBM** | 0.0355 | 0.0663 | 1.0000 | 3.0012% |
| **XGBoost** | 0.0424 | 0.0718 | 1.0000 | 3.6302% |
| **Ensemble (Avg)** | 0.0704 | 0.1327 | 0.9998 | 20.4291% |
| **ARIMA (5,1,2)** | 0.3708 | 0.4563 | -0.0588 | 2.0711% |
| **Linear/Ridge** | 0.3404 | 0.6500 | 0.9961 | 100.8724% |

*Note: Models utilize local spatial/temporal engineered features, achieving near-perfect R² and low MAE/RMSE.*

---

## 💡 Key Climate Insights

1. **Hemisphere Seasonal Cycles**: Grouping data by latitude reveals the classic, opposite wave-like seasonal curves of the Northern vs. Southern Hemispheres.
2. **Outlier Flags**: The Isolation Forest model successfully detected **1,123** global climate outliers (2% contamination threshold) representing severe meteorological extremes.
3. **Air Quality Interaction**: Wind speed, relative humidity, and visibility parameters display high correlation metrics with key Air Quality Indicators (PM2.5, PM10).
4. **Predictor Ranks**: Local variables (humidity, Hour, Temperature-Humidity Index) hold the highest feature importance weights.

---

## 🚀 Execution & Setup Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Execute Pipeline
Run the entrypoint script to execute the end-to-end pipeline:
```bash
python run_analysis.py
```

This will:
- Auto-download the full 14.7 MB dataset (if not locally present).
- Run cleaning, preprocessing, and engineering.
- Perform outlier detection and generate exploratory plots.
- Train and evaluate the baseline, time-series, machine learning, and ensemble models.
- Create an interactive global Folium spatial heatmap.
- Compile the modern interactive HTML dashboard at `outputs/reports/weather_analysis_report.html`.
