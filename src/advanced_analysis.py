"""
Advanced Climate analysis, Environmental (AQI) correlations, Feature Importance, and Interactive Folium Spatial Mapping.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

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

def run_advanced_analysis(df, models_dict, output_dir, reports_dir):
    """Run advanced climate seasonal, geographical, air quality, feature importance, and spatial mapping analyses."""
    print("Running advanced climate and geographic analysis...")
    out_path = Path(output_dir)
    rep_path = Path(reports_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rep_path.mkdir(parents=True, exist_ok=True)

    # 1. Hemisphere Seasonal Cycles Analysis
    if 'latitude' in df.columns and 'temperature_celsius' in df.columns:
        df_hemi = df.copy()
        df_hemi['hemisphere'] = np.where(df_hemi['latitude'] >= 0, 'Northern Hemisphere', 'Southern Hemisphere')
        
        # Monthly average temperature for each hemisphere
        hemi_monthly = df_hemi.groupby(['month', 'hemisphere'])['temperature_celsius'].mean().unstack()
        
        # Re-index to ensure correct month order
        month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        # Map actual present months
        hemi_monthly.index = [month_names[int(m) - 1] for m in hemi_monthly.index]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        hemi_monthly.plot(kind='line', marker='o', ax=ax, linewidth=2.5, markersize=6)
        ax.set_title("Northern vs. Southern Hemisphere Seasonal Cycles", fontsize=14, pad=15)
        ax.set_ylabel("Average Temperature (°C)")
        ax.set_xlabel("Month")
        plt.tight_layout()
        plt.savefig(out_path / "25_hemisphere_seasonal_cycle.png", dpi=100, facecolor='#161920')
        plt.close()

    # 2. Regional / Country level temperature extremes boxplot
    if 'country' in df.columns:
        # Filter top 10 hottest and coldest countries
        ctry_temp = df.groupby('country')['temperature_celsius'].mean().dropna().sort_values()
        coldest = ctry_temp.head(10).index.tolist()
        hottest = ctry_temp.tail(10).index.tolist()
        extreme_countries = coldest + hottest
        
        df_ext = df[df['country'].isin(extreme_countries)]
        
        fig, ax = plt.subplots(figsize=(14, 7))
        sns.boxplot(data=df_ext, x='country', y='temperature_celsius', ax=ax, palette='coolwarm')
        plt.xticks(rotation=45, ha='right')
        ax.set_title("Temperature Extremes Distribution Across Top Hottest & Coldest Countries", fontsize=14, pad=15)
        plt.tight_layout()
        plt.savefig(out_path / "14_regional_extremes_boxplot.png", dpi=100, facecolor='#161920')
        plt.close()

    # 3. Environmental Impact: Air Quality Index Correlations
    aqi_cols = ['air_quality_PM2_5', 'air_quality_PM10', 'air_quality_O3', 'air_quality_NO2', 'air_quality_SO2']
    aqi_cols = [c for c in aqi_cols if c in df.columns]
    
    if aqi_cols and 'temperature_celsius' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        env_corr = df[aqi_cols + ['temperature_celsius', 'humidity', 'wind_kph', 'visibility_km']].corr()
        sns.heatmap(env_corr, annot=True, cmap="mako", fmt=".2f", ax=ax)
        ax.set_title("Air Quality Indicators x Meteorological Features Correlation Matrix", fontsize=14, pad=15)
        plt.tight_layout()
        plt.savefig(out_path / "17_aqi_weather_correlations.png", dpi=100, facecolor='#161920')
        plt.close()

    # 4. Feature Importance using Random Forest Tree model
    if 'Random Forest' in models_dict:
        rf_model = models_dict['Random Forest']
        features = [
            'humidity', 'wind_kph', 'pressure_mb', 'precip_mm', 'cloud', 
            'uv_index', 'hour', 'day_of_week', 'month', 'temp_humidity_index'
        ]
        # Align with models.py features list
        features = [f for f in features if f in df.columns]
        
        importances = rf_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=importances[indices], y=[features[i] for i in indices], ax=ax, palette='viridis')
        ax.set_title("Feature Importance Ranking (Random Forest)", fontsize=14, pad=15)
        plt.tight_layout()
        plt.savefig(out_path / "20_feature_importance_rf.png", dpi=100, facecolor='#161920')
        plt.close()

    # 5. Spatial Folium Map (Global Temperature Heatmap)
    # Check if we have latitude, longitude, and temperature
    if 'latitude' in df.columns and 'longitude' in df.columns and 'temperature_celsius' in df.columns:
        print("Generating interactive Folium spatial heatmap...")
        try:
            import folium
            from folium.plugins import HeatMap
            
            # Group by unique city/location to get average temperature for mapping
            group_cols = ['location_name', 'latitude', 'longitude']
            group_cols = [c for c in group_cols if c in df.columns]
            
            map_data = df.groupby(group_cols)['temperature_celsius'].mean().reset_index()
            
            # Start map centered globally
            m = folium.Map(location=[20.0, 0.0], zoom_start=2, tiles="cartodbpositron")
            
            # Add HeatMap layer
            heat_data = [[row['latitude'], row['longitude'], row['temperature_celsius']] for idx, row in map_data.iterrows()]
            HeatMap(heat_data, min_opacity=0.3, radius=15, blur=10, max_zoom=1).add_to(m)
            
            # Add marker popups for top 100 cities
            for idx, row in map_data.head(100).iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=4,
                    popup=f"<b>{row.get('location_name', 'City')}</b><br>Avg Temp: {row['temperature_celsius']:.1f}°C",
                    color="#38bdf8",
                    fill=True,
                    fill_color="#38bdf8",
                    fill_opacity=0.8
                ).add_to(m)
                
            map_html = rep_path / "interactive_map.html"
            m.save(str(map_html))
            print(f"Interactive Folium map saved to {map_html}")
        except Exception as e:
            print(f"Folium map generation failed: {e}. Writing placeholder interactive map.")
            # Write a basic HTML fallback
            map_html = rep_path / "interactive_map.html"
            with open(map_html, 'w') as fh:
                fh.write("<html><body><h3>Folium map generation not available. See static plots in report.</h3></body></html>")
    else:
        print("Latitude/longitude columns not found. Skipping Folium map.")
