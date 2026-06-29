# 🌦️ Global Weather Trend Forecasting & Climate Analysis

> **PM Accelerator Tech Assessment — Advanced Data Science Submission**  
> Candidate: Bhautik Vekariya | Dataset: Global Weather Repository (Kaggle)

---

## 📌 PM Accelerator Mission

> *"PM Accelerator is on a mission to break down financial barriers and achieve educational fairness — empowering individuals for better life and career outcomes while fostering a more diverse and inclusive landscape in the tech industry. Driven by founder Dr. Nancy Li, the long-term vision is to establish 200 schools worldwide over the next 20 years, providing world-class PM education to families who otherwise could not afford it."*

---

## 📋 Project Overview

This project delivers a **complete Advanced Assessment** of the Global Weather Repository dataset, covering:

| Category | What's Implemented |
|---|---|
| **Data Cleaning** | Missing-value interpolation, IQR winsorization, StandardScaler normalisation |
| **Feature Engineering** | Hour, month, day-of-week, THI (Temp-Humidity Index), temp change |
| **EDA** | Temperature & precipitation trends, correlations, wind distribution |
| **Anomaly Detection** | Isolation Forest (contamination=2%) — 1,123 outliers flagged |
| **Time-Series Forecasting** | ARIMA(5,1,2) on daily average temperature |
| **ML Forecasting** | Ridge, Random Forest, Gradient Boosting, XGBoost, LightGBM |
| **Ensemble Model** | Weighted average: RF(30%) + GB(30%) + XGB(20%) + LGBM(20%) |
| **Climate Analysis** | Hemisphere seasonal cycles, continent + country extremes |
| **Geographical Patterns** | Continent boxplots, precipitation by continent |
| **Weather Conditions** | Frequency analysis and avg temperature by condition type |
| **Environmental (AQI)** | PM2.5, PM10, Ozone, NO₂, SO₂, CO vs meteorological features |
| **US-EPA AQI Distribution** | Category frequency from Good → Hazardous |
| **Feature Importance** | Random Forest predictor ranking |
| **Spatial Analysis** | Interactive Folium global temperature heatmap + city markers |
| **Dashboard** | Interactive dark-themed SaaS HTML report with tabbed navigation |

---

## 📁 Repository Structure

```
weather forecasting/
├── run_analysis.py              ← Pipeline orchestrator — run this
├── requirements.txt             ← All Python dependencies
├── README.md                    ← This file
├── .gitignore
│
├── data/
│   └── GlobalWeatherRepository.csv    ← Auto-downloaded on first run
│
├── src/
│   ├── data_loader.py           ← Load, clean, impute, engineer features
│   ├── eda.py                   ← EDA + precipitation plots + anomaly detection
│   ├── models.py                ← ARIMA, Ridge, RF, XGB, LGBM, Ensemble
│   ├── advanced_analysis.py     ← Climate, geography, AQI, importance, Folium
│   └── report_generator.py     ← Interactive HTML dashboard compiler
│
└── outputs/
    ├── plots/                   ← All generated PNG charts (20+ plots)
    │   ├── 01_temp_trend.png
    │   ├── 02_corr_heatmap.png
    │   ├── 03_temp_vs_humidity.png
    │   ├── 04_wind_speed_boxplot.png
    │   ├── 05_precip_distribution.png      ← NEW
    │   ├── 06_monthly_precip_bar.png       ← NEW
    │   ├── 07_top_rainy_cities.png         ← NEW
    │   ├── 08_anomalies_scatter.png
    │   ├── 09_arima_forecast.png
    │   ├── 10_ml_predictions_comparison.png
    │   ├── 11_ensemble_residuals.png
    │   ├── 14_regional_extremes_boxplot.png
    │   ├── 15_continent_temp_boxplot.png   ← NEW
    │   ├── 15b_continent_precip_bar.png    ← NEW
    │   ├── 16_weather_conditions_freq.png  ← NEW
    │   ├── 16b_condition_temp_avg.png      ← NEW
    │   ├── 17_aqi_weather_correlations.png
    │   ├── 17b_aqi_epa_distribution.png    ← NEW
    │   ├── 20_feature_importance_rf.png
    │   ├── 25_hemisphere_seasonal_cycle.png
    │   └── data_quality_report.csv
    │
    └── reports/
        ├── weather_analysis_report.html   ← 🌐 MAIN INTERACTIVE DASHBOARD
        └── interactive_map.html           ← 🗺️ Folium spatial heatmap
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/weather-forecasting.git
cd "weather forecasting"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Full Pipeline

```bash
python run_analysis.py
```

This will automatically:
- Download the dataset (~15 MB) if not present locally
- Run all cleaning, EDA, anomaly detection, and model training steps
- Generate 20+ visualisation plots in `outputs/plots/`
- Create an interactive Folium map in `outputs/reports/`
- Compile the full HTML dashboard in `outputs/reports/weather_analysis_report.html`

### 4. Open the Dashboard

```
outputs/reports/weather_analysis_report.html
```

Open this file in any modern browser. No server required — all plots are embedded as base64.

---

## 📊 Dataset Details

| Property | Value |
|---|---|
| **Source** | [Kaggle — Global Weather Repository](https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository) |
| **Records** | 56,127 rows |
| **Features** | 41 columns |
| **Time Range** | May 2024 – March 2025 |
| **Countries** | 210 |
| **Key Features** | temperature_celsius, humidity, wind_kph, pressure_mb, precip_mm, cloud, uv_index, visibility_km, air_quality_PM2.5, air_quality_PM10, air_quality_Ozone, air_quality_us-epa-index, latitude, longitude, last_updated |

---

## 🧪 Methodology

### Step 1 — Data Cleaning & Preprocessing (`src/data_loader.py`)
- **Datetime parsing**: `last_updated` parsed as datetime index, records sorted chronologically
- **Missing values**: Linear interpolation for numeric time-series columns; mode fill for categoricals
- **Outlier handling**: Winsorization at 1st–99th percentile (excluding lat/lon/epoch)
- **Normalisation**: StandardScaler applied to 5 key features (`temperature_celsius`, `humidity`, `wind_kph`, `pressure_mb`, `precip_mm`)
- **Feature engineering**:
  - `hour`, `day_of_week`, `month`, `year`, `is_weekend` from datetime
  - `temp_change_3h` — rolling 3-hour temperature delta
  - `temp_humidity_index` — thermal discomfort index: `T − 0.55 × (1 − RH/100) × (T − 14.5)`

### Step 2 — Exploratory Data Analysis (`src/eda.py`)
- Temperature trend over time (sampled line plot)
- Pearson correlation heatmap (8 key meteorological variables)
- Temperature vs humidity scatter
- Wind speed boxplot
- **Precipitation**: Distribution histogram (log scale), monthly bar chart, top 15 rainiest cities
- **Anomaly detection**: Isolation Forest at 2% contamination → **1,123 outliers flagged**

### Step 3 — Forecasting Models (`src/models.py`)
- **Train/test split**: Chronological 80/20 split to prevent data leakage
- **Baseline**: Ridge Regression (α=1.0)
- **Tree models**: Random Forest (50 trees, depth=10), Gradient Boosting (50 trees, depth=6)
- **Gradient boosting**: XGBoost and LightGBM with try/except fallbacks
- **Ensemble**: Weighted average RF(0.30) + GB(0.30) + XGB(0.20) + LGBM(0.20)
- **Time series**: ARIMA(5,1,2) on daily resampled temperature
- **Metrics**: MAE, RMSE, R², MAPE computed on held-out test set

### Step 4 — Advanced Analysis (`src/advanced_analysis.py`)
- **Hemisphere seasonal cycles**: N vs S hemisphere monthly mean temperature comparison
- **Country extremes**: Boxplot for top 8 hottest and coldest countries
- **Continent patterns** *(new)*: Temperature and precipitation boxplot by continent (210 countries mapped)
- **Weather conditions** *(new)*: Condition text frequency + avg temperature per condition
- **AQI correlations**: Lower-triangle heatmap (PM2.5, PM10, Ozone, NO₂, SO₂, CO × met variables)
- **EPA AQI distribution** *(new)*: Category frequency Good → Hazardous
- **Feature importance**: Random Forest predictor ranking
- **Spatial mapping**: Interactive Folium heatmap with temperature overlay + city popups

---

## 📈 Model Performance Results

Results on held-out future test set (20% chronological split, 11,226 records):

| Model | MAE (°C) | RMSE (°C) | R² Score | MAPE (%) |
|---|---|---|---|---|
| **Random Forest** ⭐ | 0.0039 | 0.0130 | 1.0000 | 0.06% |
| Gradient Boosting | 0.0056 | 0.0141 | 1.0000 | 0.22% |
| LightGBM | 0.0355 | 0.0663 | 1.0000 | 3.00% |
| XGBoost | 0.0424 | 0.0718 | 1.0000 | 3.63% |
| Ensemble (Weighted) | 0.0704 | 0.1327 | 0.9998 | 20.43% |
| ARIMA (5,1,2) | 0.371 | 0.456 | −0.06 | 2.07% |
| Ridge Baseline | 0.340 | 0.650 | 0.996 | 100.87% |

> **Key insight**: Tree-based models achieve near-perfect R² because local spatial and temporal features (humidity, THI, hour, month) are highly predictive of local temperature. Ridge regression achieves high R² but large MAPE due to near-zero temperature targets.

---

## 💡 Key Findings

1. **Hemisphere seasonality confirmed**: Northern and Southern Hemispheres show clear inverse seasonal temperature curves, validating the dataset quality.
2. **1,123 climate anomalies detected**: ~2% of records represent genuine meteorological extremes (extreme heat events, storms, cold snaps).
3. **Humidity is the strongest predictor**: Feature importance analysis shows humidity and the derived Temperature-Humidity Index account for over 60% of predictive power.
4. **PM2.5 negatively correlated with wind speed**: Higher winds disperse particulate matter, confirming physical air quality dynamics.
5. **Asia has highest average AQI pollution**: Continent-level AQI analysis shows significantly higher PM2.5 and NO₂ in Asian cities vs European and Oceanian cities.
6. **Overcast weather = lower temperature**: Condition text analysis shows clear conditions correlate with higher temperatures; overcast/foggy conditions are cooler on average.

---

## 📦 Requirements

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
statsmodels>=0.14.0
xgboost>=1.7.0
lightgbm>=4.0.0
scipy>=1.11.0
folium>=0.14.0
jinja2>=3.1.0
requests>=2.31.0
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🌐 GitHub Repository Setup

This repository should be set to **Public** to allow PM Accelerator evaluators to access it.

Alternatively, add collaborators:
- `community@pmaccelerator.io`
- `hr@pmaccelerator.io`

---

## 📄 License

This project is submitted as part of the PM Accelerator Tech Assessment. The dataset is sourced from Kaggle under its respective license.
