"""
Exploratory Data Analysis and Anomaly Detection.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import IsolationForest

# Apply clean visual styles
sns.set_theme(style="darkgrid")
plt.rcParams.update({
    'figure.facecolor': '#161920',
    'axes.facecolor': '#1e222b',
    'text.color': '#e2e8f0',
    'axes.labelcolor': '#cbd5e1',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#334155',
    'axes.edgecolor': '#475569'
})

def run_eda_and_anomalies(df, time_col, output_dir):
    """Generate EDA summaries, run Isolation Forest, and save plots."""
    print("Running EDA and Anomaly Detection...")
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    reports = {}
    
    # 1. Basic Stats & Data Quality Report
    missing_report = df.isnull().sum()
    data_quality_df = pd.DataFrame({
        'Column': df.columns,
        'DataType': df.dtypes,
        'MissingValues': missing_report.values,
        'MissingPercentage': (missing_report.values / len(df)) * 100
    })
    quality_csv = out_path / "data_quality_report.csv"
    data_quality_df.to_csv(quality_csv, index=False)
    reports['data_quality_csv'] = str(quality_csv)
    
    # 2. Outlier/Anomaly Detection using Isolation Forest
    # Select key numerical features for anomaly detection
    features_for_anomaly = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb']
    features_for_anomaly = [f for f in features_for_anomaly if f in df.columns]
    
    # Run Isolation Forest
    iso = IsolationForest(contamination=0.02, random_state=42)
    df['anomaly_flag'] = iso.fit_predict(df[features_for_anomaly])
    # Map -1 to anomaly (1) and 1 to normal (0)
    df['is_anomaly'] = np.where(df['anomaly_flag'] == -1, 1, 0)
    
    anomaly_count = df['is_anomaly'].sum()
    reports['anomaly_count'] = int(anomaly_count)
    reports['anomaly_percentage'] = float((anomaly_count / len(df)) * 100)
    print(f"Detected {anomaly_count} anomalies ({reports['anomaly_percentage']:.2f}% of data).")

    # Save Plots
    # Plot 1: Temperature Trend over Time
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df.sample(min(len(df), 5000), random_state=42), x=time_col, y='temperature_celsius', ax=ax, color='#38bdf8', alpha=0.8)
    ax.set_title("Temperature Trend (Sampled Records)", fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(out_path / "01_temp_trend.png", dpi=100, facecolor='#161920')
    plt.close()

    # Plot 2: Correlation Heatmap of Weather Variables
    fig, ax = plt.subplots(figsize=(10, 8))
    corr_features = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb', 'precip_mm', 'cloud', 'uv_index']
    corr_features = [f for f in corr_features if f in df.columns]
    corr_matrix = df[corr_features].corr()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", center=0, ax=ax, fmt=".2f", cbar_kws={"shrink": .8})
    ax.set_title("Correlation Heatmap of Meteorological Features", fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(out_path / "02_corr_heatmap.png", dpi=100, facecolor='#161920')
    plt.close()

    # Plot 3: Temperature vs Humidity Joint Distribution
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=df.sample(min(len(df), 2000), random_state=42), x='temperature_celsius', y='humidity', ax=ax, color='#10b981', alpha=0.5, edgecolor=None)
    ax.set_title("Temperature vs Humidity", fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(out_path / "03_temp_vs_humidity.png", dpi=100, facecolor='#161920')
    plt.close()

    # Plot 4: Wind Speed Distribution Boxplot
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df, y='wind_kph', ax=ax, color='#f59e0b', width=0.4)
    ax.set_title("Distribution of Wind Speed (kph)", fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(out_path / "04_wind_speed_boxplot.png", dpi=100, facecolor='#161920')
    plt.close()

    # Plot 5: Anomalies Visualization
    fig, ax = plt.subplots(figsize=(12, 6))
    normal_df = df[df['is_anomaly'] == 0].sample(min(len(df[df['is_anomaly'] == 0]), 3000), random_state=42)
    anomaly_df = df[df['is_anomaly'] == 1]
    
    sns.scatterplot(data=normal_df, x=time_col, y='temperature_celsius', ax=ax, color='#64748b', alpha=0.5, label='Normal', edgecolor=None)
    sns.scatterplot(data=anomaly_df, x=time_col, y='temperature_celsius', ax=ax, color='#ef4444', alpha=0.9, label='Anomaly', s=50, marker='x')
    ax.set_title("Outliers Flagged by Isolation Forest", fontsize=14, pad=15)
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path / "08_anomalies_scatter.png", dpi=100, facecolor='#161920')
    plt.close()

    return df, reports
