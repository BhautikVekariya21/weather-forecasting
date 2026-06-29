"""
Orchestrator script to run the Global Weather Trend Forecasting & Climate Analysis pipeline end-to-end.
"""
import urllib.request
import ssl
from pathlib import Path
import pandas as pd
import time

# Import pipeline steps
from src.data_loader import load_data, preprocess
from src.eda import run_eda_and_anomalies
from src.models import train_and_evaluate
from src.advanced_analysis import run_advanced_analysis
from src.report_generator import generate_html_report

# Constants
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
PLOTS_DIR = OUTPUT_DIR / "plots"
REPORTS_DIR = OUTPUT_DIR / "reports"
MODELS_DIR = OUTPUT_DIR / "models"

CSV_FILE = DATA_DIR / "GlobalWeatherRepository.csv"

# Dataset raw download URLs from git repository
DATASET_URLS = [
    "https://raw.githubusercontent.com/shuailishasls/PoisonCatcher_Code/main/File/GlobalWeatherRepository.csv",
    "https://raw.githubusercontent.com/shuailishasls/PoisonCatcher_Code/master/File/GlobalWeatherRepository.csv"
]

def download_dataset():
    """Download the actual Kaggle dataset from public raw git branch repositories."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if CSV_FILE.exists():
        print(f"Dataset already exists at {CSV_FILE}. Skipping download.")
        return

    print("Downloading dataset from public repositories...")
    
    # Bypassing SSL cert validation issues if present
    ssl_context = ssl._create_unverified_context()
    
    download_success = False
    for url in DATASET_URLS:
        try:
            print(f"Trying download from: {url}")
            urllib.request.urlretrieve(url, CSV_FILE)
            if CSV_FILE.exists() and CSV_FILE.stat().st_size > 1024 * 1024: # Must be >1MB
                print("Download completed successfully!")
                download_success = True
                break
        except Exception as e:
            print(f"Failed to download from {url}: {e}")
            if CSV_FILE.exists():
                CSV_FILE.unlink()

    if not download_success:
        raise RuntimeError("Unable to download the dataset from any of the provided URLs.")


def main():
    start_time = time.time()
    print("======================================================================")
    print("      🌦️  Global Weather Trend Forecasting & Climate Analysis         ")
    print("======================================================================")
    
    # 1. Download dataset
    download_dataset()
    
    # Create required directories
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Load and Clean/Impute/Normalize Data
    df_raw = load_data(CSV_FILE)
    print(f"Dataset Dimensions: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns.")
    
    df, time_col = preprocess(df_raw)
    
    # 3. Exploratory Data Analysis & Outlier Detection
    df, eda_reports = run_eda_and_anomalies(df, time_col, PLOTS_DIR)
    
    # 4. Train Forecasting Regressors and ARIMA Model
    metrics_report, trained_models = train_and_evaluate(df, time_col, PLOTS_DIR)
    
    # 5. Advanced Geographical Patterns and Spatial Mapping
    run_advanced_analysis(df, trained_models, PLOTS_DIR, REPORTS_DIR)
    
    # 6. Generate compiled interactive HTML report
    generate_html_report(df, metrics_report, PLOTS_DIR, REPORTS_DIR)
    
    elapsed_time = time.time() - start_time
    print("======================================================================")
    print(f"🎉 Pipeline completed successfully in {elapsed_time:.1f} seconds!")
    print("======================================================================")
    print(f"📂 Project Root: {BASE_DIR}")
    print(f"📈 Evaluation Data quality report: {PLOTS_DIR / 'data_quality_report.csv'}")
    print(f"🖼️ Plots and Charts folder: {PLOTS_DIR}")
    print(f"🌍 Interactive Spatial Heatmap: {REPORTS_DIR / 'interactive_map.html'}")
    print(f"💻 Main HTML Dashboard: {REPORTS_DIR / 'weather_analysis_report.html'}")
    print("======================================================================")


if __name__ == "__main__":
    main()
