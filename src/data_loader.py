"""
Data Loading, Cleaning, Preprocessing, and Feature Engineering.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def load_data(file_path):
    """Load dataset from CSV file."""
    print(f"Loading data from {file_path}...")
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    return pd.read_csv(file_path)

def preprocess(df):
    """Clean, impute missing values, cap outliers, normalize data, and engineer features."""
    print("Running preprocessing and feature engineering...")
    df = df.copy()
    
    # 1. Identify and parse datetime column
    time_col = next((c for c in df.columns if c.lower().replace(' ', '_') in 
                     ['last_updated', 'lastupdated', 'date', 'datetime']), None)
    if time_col:
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(by=time_col).reset_index(drop=True)
    else:
        # If no explicit datetime, create an artificial one to allow time-series modeling
        df['last_updated'] = pd.date_range(start='2024-01-01', periods=len(df), freq='H')
        time_col = 'last_updated'
        df[time_col] = pd.to_datetime(df[time_col])

    # 2. Handle missing values
    # For numeric columns, fill using interpolation/forward-fill to maintain time-series properties
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col] = df[col].interpolate(method='linear').ffill().bfill()
            
    # For categorical columns, fill with mode
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in categorical_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')

    # 3. Handle outliers using winsorization (capping at 1st and 99th percentiles)
    # Exclude latitude/longitude and epoch from capping to maintain spatial/temporal integrity
    exclude_cols = ['latitude', 'longitude', 'last_updated_epoch', 'elevation']
    for col in numeric_cols:
        if col not in exclude_cols:
            lower_limit = df[col].quantile(0.01)
            upper_limit = df[col].quantile(0.99)
            df[col] = np.clip(df[col], lower_limit, upper_limit)

    # 4. Feature Engineering
    # Extract temporal features
    df['hour'] = df[time_col].dt.hour
    df['day_of_week'] = df[time_col].dt.dayofweek
    df['month'] = df[time_col].dt.month
    df['year'] = df[time_col].dt.year
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Temperature Change (hourly difference if sorted)
    if 'temperature_celsius' in df.columns:
        df['temp_change_3h'] = df['temperature_celsius'].diff().fillna(0)
    
    # Heat Index / Temp-Humidity Index (THI) approximation
    if 'temperature_celsius' in df.columns and 'humidity' in df.columns:
        # THI = T - 0.55 * (1 - RH/100) * (T - 14.5)
        T = df['temperature_celsius']
        RH = df['humidity']
        df['temp_humidity_index'] = T - 0.55 * (1 - RH / 100.0) * (T - 14.5)
    else:
        df['temp_humidity_index'] = 0.0

    # 5. Normalize/Scale selected key features for ML
    scale_features = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb', 'precip_mm']
    scale_features = [f for f in scale_features if f in df.columns]
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[scale_features])
    for i, col in enumerate(scale_features):
        df[f'{col}_scaled'] = scaled_data[:, i]

    return df, time_col
