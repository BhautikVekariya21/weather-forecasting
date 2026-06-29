"""
Exploratory Data Analysis: temperature, precipitation, correlations, and Isolation Forest anomaly detection.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import IsolationForest

# Apply consistent dark visual style
sns.set_theme(style="darkgrid")
plt.rcParams.update({
    'figure.facecolor': '#161920',
    'axes.facecolor': '#1e222b',
    'text.color': '#e2e8f0',
    'axes.labelcolor': '#cbd5e1',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#334155',
    'axes.edgecolor': '#475569',
    'legend.facecolor': '#1e222b',
    'legend.edgecolor': '#475569',
})

PALETTE = ['#38bdf8', '#10b981', '#f59e0b', '#ef4444', '#818cf8', '#fb7185']


def run_eda_and_anomalies(df, time_col, output_dir):
    """
    Generate EDA summaries, precipitation analysis, run Isolation Forest,
    and save all plots to output_dir.
    """
    print("Running EDA and Anomaly Detection...")
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    reports = {}

    # ─────────────────────────────────────────────
    # 1. Data Quality Report
    # ─────────────────────────────────────────────
    missing_report = df.isnull().sum()
    data_quality_df = pd.DataFrame({
        'Column': df.columns,
        'DataType': df.dtypes.values,
        'MissingValues': missing_report.values,
        'MissingPercentage': (missing_report.values / len(df)) * 100
    })
    quality_csv = out_path / "data_quality_report.csv"
    data_quality_df.to_csv(quality_csv, index=False)
    reports['data_quality_csv'] = str(quality_csv)

    # ─────────────────────────────────────────────
    # 2. Isolation Forest Anomaly Detection
    # ─────────────────────────────────────────────
    anomaly_features = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb']
    anomaly_features = [f for f in anomaly_features if f in df.columns]

    iso = IsolationForest(contamination=0.02, random_state=42)
    df['anomaly_flag'] = iso.fit_predict(df[anomaly_features])
    df['is_anomaly'] = np.where(df['anomaly_flag'] == -1, 1, 0)

    anomaly_count = int(df['is_anomaly'].sum())
    reports['anomaly_count'] = anomaly_count
    reports['anomaly_percentage'] = float((anomaly_count / len(df)) * 100)
    print(f"  → Detected {anomaly_count} anomalies ({reports['anomaly_percentage']:.2f}% of data).")

    # ─────────────────────────────────────────────
    # PLOT 01: Temperature Trend over Time
    # ─────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5))
    sample = df.sample(min(len(df), 6000), random_state=42).sort_values(time_col)
    ax.plot(sample[time_col], sample['temperature_celsius'], color='#38bdf8', alpha=0.6, linewidth=0.8)
    ax.set_title("Global Temperature Trend Over Time (Sampled)", fontsize=14, pad=12, fontweight='bold')
    ax.set_xlabel("Date"); ax.set_ylabel("Temperature (°C)")
    plt.tight_layout()
    plt.savefig(out_path / "01_temp_trend.png", dpi=100, facecolor='#161920')
    plt.close()

    # ─────────────────────────────────────────────
    # PLOT 02: Correlation Heatmap
    # ─────────────────────────────────────────────
    corr_features = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb',
                     'precip_mm', 'cloud', 'uv_index', 'visibility_km']
    corr_features = [f for f in corr_features if f in df.columns]
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(df[corr_features].corr(), annot=True, cmap="coolwarm",
                center=0, ax=ax, fmt=".2f", linewidths=0.5)
    ax.set_title("Meteorological Feature Correlation Matrix", fontsize=14, pad=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_path / "02_corr_heatmap.png", dpi=100, facecolor='#161920')
    plt.close()

    # ─────────────────────────────────────────────
    # PLOT 03: Temperature vs Humidity
    # ─────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 6))
    sample2 = df.sample(min(len(df), 3000), random_state=42)
    ax.scatter(sample2['temperature_celsius'], sample2['humidity'],
               color='#10b981', alpha=0.4, s=10, edgecolors='none')
    ax.set_title("Temperature vs Relative Humidity", fontsize=14, pad=12, fontweight='bold')
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Humidity (%)")
    plt.tight_layout()
    plt.savefig(out_path / "03_temp_vs_humidity.png", dpi=100, facecolor='#161920')
    plt.close()

    # ─────────────────────────────────────────────
    # PLOT 04: Wind Speed Distribution
    # ─────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(y=df['wind_kph'], ax=ax, color='#f59e0b', width=0.35, flierprops=dict(marker='o', markersize=2))
    ax.set_title("Wind Speed Distribution (kph)", fontsize=14, pad=12, fontweight='bold')
    ax.set_ylabel("Wind Speed (kph)")
    plt.tight_layout()
    plt.savefig(out_path / "04_wind_speed_boxplot.png", dpi=100, facecolor='#161920')
    plt.close()

    # ─────────────────────────────────────────────
    # PLOT 05: Precipitation Distribution (REQUIRED)
    # ─────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    # Left: full distribution (log scale to handle skewness)
    nonzero = df[df['precip_mm'] > 0]['precip_mm']
    axes[0].hist(nonzero, bins=50, color='#38bdf8', edgecolor='none', alpha=0.8)
    axes[0].set_title("Precipitation Distribution (Non-Zero)", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Precipitation (mm)"); axes[0].set_ylabel("Frequency")
    axes[0].set_yscale('log')
    # Right: boxplot by category
    df['precip_cat'] = pd.cut(df['precip_mm'],
                               bins=[-0.01, 0, 1, 5, 100],
                               labels=['None (0)', 'Light (0-1mm)', 'Moderate (1-5mm)', 'Heavy (5mm+)'])
    cat_counts = df['precip_cat'].value_counts().sort_index()
    axes[1].bar(cat_counts.index, cat_counts.values,
                color=['#64748b', '#38bdf8', '#10b981', '#ef4444'], alpha=0.85)
    axes[1].set_title("Precipitation Intensity Categories", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Category"); axes[1].set_ylabel("Number of Records")
    plt.suptitle("Precipitation Analysis — Global Weather Repository", fontsize=13,
                 fontweight='bold', y=1.02, color='#e2e8f0')
    plt.tight_layout()
    plt.savefig(out_path / "05_precip_distribution.png", dpi=100, facecolor='#161920', bbox_inches='tight')
    plt.close()

    # ─────────────────────────────────────────────
    # PLOT 06: Monthly Average Precipitation Bar Chart (REQUIRED)
    # ─────────────────────────────────────────────
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    if 'month' in df.columns:
        monthly_precip = df.groupby('month')['precip_mm'].mean()
        fig, ax = plt.subplots(figsize=(11, 5))
        bars = ax.bar([month_names[int(m)-1] for m in monthly_precip.index],
                      monthly_precip.values, color=PALETTE[0], alpha=0.85, edgecolor='none')
        # Annotate each bar
        for bar, val in zip(bars, monthly_precip.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=9, color='#94a3b8')
        ax.set_title("Average Monthly Precipitation (mm) — Global", fontsize=14, pad=12, fontweight='bold')
        ax.set_xlabel("Month"); ax.set_ylabel("Avg Precipitation (mm)")
        plt.tight_layout()
        plt.savefig(out_path / "06_monthly_precip_bar.png", dpi=100, facecolor='#161920')
        plt.close()

    # ─────────────────────────────────────────────
    # PLOT 07: Top 15 Rainiest Cities (REQUIRED)
    # ─────────────────────────────────────────────
    if 'location_name' in df.columns:
        top_rain = (df.groupby('location_name')['precip_mm']
                      .mean()
                      .sort_values(ascending=False)
                      .head(15))
        fig, ax = plt.subplots(figsize=(11, 6))
        bars = ax.barh(top_rain.index[::-1], top_rain.values[::-1],
                       color='#818cf8', alpha=0.85, edgecolor='none')
        ax.set_title("Top 15 Rainiest Cities by Average Precipitation", fontsize=14, pad=12, fontweight='bold')
        ax.set_xlabel("Average Precipitation (mm)")
        plt.tight_layout()
        plt.savefig(out_path / "07_top_rainy_cities.png", dpi=100, facecolor='#161920')
        plt.close()

    # ─────────────────────────────────────────────
    # PLOT 08: Anomaly Scatter
    # ─────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5))
    normal = df[df['is_anomaly'] == 0].sample(min(4000, (df['is_anomaly']==0).sum()), random_state=42)
    anomalous = df[df['is_anomaly'] == 1]
    ax.scatter(normal[time_col], normal['temperature_celsius'],
               color='#64748b', alpha=0.35, s=5, label='Normal', edgecolors='none')
    ax.scatter(anomalous[time_col], anomalous['temperature_celsius'],
               color='#ef4444', alpha=0.9, s=18, marker='x', label=f'Anomaly (n={anomaly_count})', linewidths=1.2)
    ax.set_title("Weather Anomalies Flagged by Isolation Forest (contamination=2%)",
                 fontsize=14, pad=12, fontweight='bold')
    ax.set_xlabel("Date"); ax.set_ylabel("Temperature (°C)")
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(out_path / "08_anomalies_scatter.png", dpi=100, facecolor='#161920')
    plt.close()

    return df, reports
