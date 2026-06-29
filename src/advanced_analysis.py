"""
Advanced Climate Analysis, Environmental (AQI) Correlations, Feature Importance,
Continent-level Geographical Patterns, Weather Conditions, and Interactive Folium Mapping.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

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

# ─────────────────────────────────────────────────────────────────
# Country → Continent mapping (210 countries covered)
# ─────────────────────────────────────────────────────────────────
COUNTRY_CONTINENT = {
    # Africa
    "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa", "Botswana": "Africa",
    "Burkina Faso": "Africa", "Burundi": "Africa", "Cameroon": "Africa", "Cape Verde": "Africa",
    "Central African Republic": "Africa", "Chad": "Africa", "Comoros": "Africa",
    "Congo": "Africa", "DR Congo": "Africa", "Djibouti": "Africa", "Egypt": "Africa",
    "Equatorial Guinea": "Africa", "Eritrea": "Africa", "Eswatini": "Africa",
    "Ethiopia": "Africa", "Gabon": "Africa", "Gambia": "Africa", "Ghana": "Africa",
    "Guinea": "Africa", "Guinea-Bissau": "Africa", "Ivory Coast": "Africa",
    "Kenya": "Africa", "Lesotho": "Africa", "Liberia": "Africa", "Libya": "Africa",
    "Madagascar": "Africa", "Malawi": "Africa", "Mali": "Africa", "Mauritania": "Africa",
    "Mauritius": "Africa", "Morocco": "Africa", "Mozambique": "Africa", "Namibia": "Africa",
    "Niger": "Africa", "Nigeria": "Africa", "Rwanda": "Africa", "Sao Tome and Principe": "Africa",
    "Senegal": "Africa", "Seychelles": "Africa", "Sierra Leone": "Africa", "Somalia": "Africa",
    "South Africa": "Africa", "South Sudan": "Africa", "Sudan": "Africa", "Tanzania": "Africa",
    "Togo": "Africa", "Tunisia": "Africa", "Uganda": "Africa", "Zambia": "Africa",
    "Zimbabwe": "Africa",
    # Asia
    "Afghanistan": "Asia", "Armenia": "Asia", "Azerbaijan": "Asia", "Bahrain": "Asia",
    "Bangladesh": "Asia", "Bhutan": "Asia", "Brunei": "Asia", "Cambodia": "Asia",
    "China": "Asia", "Cyprus": "Asia", "Georgia": "Asia", "India": "Asia",
    "Indonesia": "Asia", "Iran": "Asia", "Iraq": "Asia", "Israel": "Asia",
    "Japan": "Asia", "Jordan": "Asia", "Kazakhstan": "Asia", "Kuwait": "Asia",
    "Kyrgyzstan": "Asia", "Laos": "Asia", "Lebanon": "Asia", "Malaysia": "Asia",
    "Maldives": "Asia", "Mongolia": "Asia", "Myanmar": "Asia", "Nepal": "Asia",
    "North Korea": "Asia", "Oman": "Asia", "Pakistan": "Asia", "Palestine": "Asia",
    "Philippines": "Asia", "Qatar": "Asia", "Saudi Arabia": "Asia", "Singapore": "Asia",
    "South Korea": "Asia", "Sri Lanka": "Asia", "Syria": "Asia", "Taiwan": "Asia",
    "Tajikistan": "Asia", "Thailand": "Asia", "Timor-Leste": "Asia", "Turkey": "Asia",
    "Turkmenistan": "Asia", "UAE": "Asia", "United Arab Emirates": "Asia",
    "Uzbekistan": "Asia", "Vietnam": "Asia", "Yemen": "Asia",
    # Europe
    "Albania": "Europe", "Andorra": "Europe", "Austria": "Europe", "Belarus": "Europe",
    "Belgium": "Europe", "Bosnia and Herzegovina": "Europe", "Bulgaria": "Europe",
    "Croatia": "Europe", "Czech Republic": "Europe", "Czechia": "Europe",
    "Denmark": "Europe", "Estonia": "Europe", "Finland": "Europe", "France": "Europe",
    "Germany": "Europe", "Greece": "Europe", "Hungary": "Europe", "Iceland": "Europe",
    "Ireland": "Europe", "Italy": "Europe", "Kosovo": "Europe", "Latvia": "Europe",
    "Liechtenstein": "Europe", "Lithuania": "Europe", "Luxembourg": "Europe",
    "Malta": "Europe", "Moldova": "Europe", "Monaco": "Europe", "Montenegro": "Europe",
    "Netherlands": "Europe", "North Macedonia": "Europe", "Norway": "Europe",
    "Poland": "Europe", "Portugal": "Europe", "Romania": "Europe", "Russia": "Europe",
    "San Marino": "Europe", "Serbia": "Europe", "Slovakia": "Europe", "Slovenia": "Europe",
    "Spain": "Europe", "Sweden": "Europe", "Switzerland": "Europe", "Ukraine": "Europe",
    "United Kingdom": "Europe", "UK": "Europe", "Vatican": "Europe",
    # North America
    "Antigua and Barbuda": "North America", "Bahamas": "North America",
    "Barbados": "North America", "Belize": "North America", "Canada": "North America",
    "Costa Rica": "North America", "Cuba": "North America", "Dominica": "North America",
    "Dominican Republic": "North America", "El Salvador": "North America",
    "Grenada": "North America", "Guatemala": "North America", "Haiti": "North America",
    "Honduras": "North America", "Jamaica": "North America", "Mexico": "North America",
    "Nicaragua": "North America", "Panama": "North America",
    "Saint Kitts and Nevis": "North America", "Saint Lucia": "North America",
    "Saint Vincent and the Grenadines": "North America", "Trinidad and Tobago": "North America",
    "USA": "North America", "United States": "North America", "United States of America": "North America",
    # South America
    "Argentina": "South America", "Bolivia": "South America", "Brazil": "South America",
    "Chile": "South America", "Colombia": "South America", "Ecuador": "South America",
    "Guyana": "South America", "Paraguay": "South America", "Peru": "South America",
    "Suriname": "South America", "Uruguay": "South America", "Venezuela": "South America",
    # Oceania
    "Australia": "Oceania", "Fiji": "Oceania", "Kiribati": "Oceania",
    "Marshall Islands": "Oceania", "Micronesia": "Oceania", "Nauru": "Oceania",
    "New Zealand": "Oceania", "Palau": "Oceania", "Papua New Guinea": "Oceania",
    "Samoa": "Oceania", "Solomon Islands": "Oceania", "Tonga": "Oceania",
    "Tuvalu": "Oceania", "Vanuatu": "Oceania",
}


def _assign_continent(country):
    """Map country name to continent; fallback to 'Other'."""
    return COUNTRY_CONTINENT.get(str(country).strip(), "Other")


def run_advanced_analysis(df, models_dict, output_dir, reports_dir):
    """
    Run all advanced analyses:
      1. Hemisphere seasonal cycles
      2. Regional country-level temperature extremes
      3. Continent-level geographical patterns  ← NEW
      4. Weather condition frequency analysis   ← NEW
      5. Environmental AQI correlations (fixed column names)
      6. Feature importance
      7. Interactive Folium spatial heatmap
    """
    print("Running advanced climate and geographic analysis...")
    out_path = Path(output_dir)
    rep_path = Path(reports_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rep_path.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────
    # 1. Hemisphere Seasonal Cycles
    # ─────────────────────────────────────────────
    if 'latitude' in df.columns and 'temperature_celsius' in df.columns:
        df_hemi = df.copy()
        df_hemi['hemisphere'] = np.where(df_hemi['latitude'] >= 0,
                                          'Northern Hemisphere', 'Southern Hemisphere')
        hemi_monthly = (df_hemi.groupby(['month', 'hemisphere'])['temperature_celsius']
                                .mean().unstack())
        month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        hemi_monthly.index = [month_names[int(m) - 1] for m in hemi_monthly.index]

        fig, ax = plt.subplots(figsize=(12, 6))
        for col, color in zip(hemi_monthly.columns, ['#38bdf8', '#ef4444']):
            ax.plot(hemi_monthly.index, hemi_monthly[col],
                    marker='o', linewidth=2.5, markersize=6, label=col, color=color)
        ax.set_title("Northern vs Southern Hemisphere — Seasonal Temperature Cycles",
                     fontsize=14, pad=12, fontweight='bold')
        ax.set_ylabel("Avg Temperature (°C)"); ax.set_xlabel("Month")
        ax.legend()
        plt.tight_layout()
        plt.savefig(out_path / "25_hemisphere_seasonal_cycle.png", dpi=100, facecolor='#161920')
        plt.close()

    # ─────────────────────────────────────────────
    # 2. Country-Level Extremes Boxplot
    # ─────────────────────────────────────────────
    if 'country' in df.columns:
        ctry_temp = df.groupby('country')['temperature_celsius'].mean().dropna().sort_values()
        extreme_countries = ctry_temp.head(8).index.tolist() + ctry_temp.tail(8).index.tolist()
        df_ext = df[df['country'].isin(extreme_countries)]

        fig, ax = plt.subplots(figsize=(15, 7))
        palette = ['#38bdf8' if df.groupby('country')['temperature_celsius'].mean().get(c, 0) > 20
                   else '#818cf8' for c in sorted(extreme_countries)]
        sns.boxplot(data=df_ext, x='country', y='temperature_celsius',
                    ax=ax, palette='coolwarm', order=sorted(extreme_countries,
                    key=lambda c: df.groupby('country')['temperature_celsius'].mean().get(c, 0)))
        plt.xticks(rotation=45, ha='right', fontsize=9)
        ax.set_title("Temperature Distribution — Top 8 Hottest & Coldest Countries",
                     fontsize=14, pad=12, fontweight='bold')
        ax.set_xlabel("Country"); ax.set_ylabel("Temperature (°C)")
        plt.tight_layout()
        plt.savefig(out_path / "14_regional_extremes_boxplot.png", dpi=100, facecolor='#161920')
        plt.close()

    # ─────────────────────────────────────────────
    # 3. Continent-Level Geographical Patterns ← NEW
    # ─────────────────────────────────────────────
    if 'country' in df.columns:
        df_cont = df.copy()
        df_cont['continent'] = df_cont['country'].apply(_assign_continent)

        # 3a: Continent temperature boxplot
        continent_order = (df_cont.groupby('continent')['temperature_celsius']
                           .median().sort_values(ascending=False).index.tolist())
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=df_cont, x='continent', y='temperature_celsius',
                    ax=ax, order=continent_order, palette='Set2',
                    flierprops=dict(marker='o', markersize=2, alpha=0.3))
        ax.set_title("Temperature Distribution by Continent",
                     fontsize=14, pad=12, fontweight='bold')
        ax.set_xlabel("Continent"); ax.set_ylabel("Temperature (°C)")
        plt.tight_layout()
        plt.savefig(out_path / "15_continent_temp_boxplot.png", dpi=100, facecolor='#161920')
        plt.close()

        # 3b: Continent avg precipitation bar
        fig, ax = plt.subplots(figsize=(11, 5))
        cont_precip = (df_cont.groupby('continent')['precip_mm'].mean()
                               .sort_values(ascending=False))
        colors = ['#38bdf8', '#10b981', '#f59e0b', '#ef4444', '#818cf8', '#fb7185', '#34d399']
        ax.barh(cont_precip.index, cont_precip.values,
                color=colors[:len(cont_precip)], alpha=0.85, edgecolor='none')
        for i, (idx, val) in enumerate(cont_precip.items()):
            ax.text(val + 0.001, i, f'{val:.3f} mm', va='center', fontsize=9, color='#94a3b8')
        ax.set_title("Average Precipitation by Continent",
                     fontsize=14, pad=12, fontweight='bold')
        ax.set_xlabel("Avg Precipitation (mm)")
        plt.tight_layout()
        plt.savefig(out_path / "15b_continent_precip_bar.png", dpi=100, facecolor='#161920')
        plt.close()

    # ─────────────────────────────────────────────
    # 4. Weather Condition Text Analysis ← NEW
    # ─────────────────────────────────────────────
    if 'condition_text' in df.columns:
        top_conditions = df['condition_text'].value_counts().head(15)

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(top_conditions.index[::-1], top_conditions.values[::-1],
                       color='#38bdf8', alpha=0.85, edgecolor='none')
        for bar, val in zip(bars, top_conditions.values[::-1]):
            ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=8, color='#94a3b8')
        ax.set_title("Top 15 Most Frequent Weather Conditions Worldwide",
                     fontsize=14, pad=12, fontweight='bold')
        ax.set_xlabel("Number of Records")
        plt.tight_layout()
        plt.savefig(out_path / "16_weather_conditions_freq.png", dpi=100, facecolor='#161920')
        plt.close()

        # Avg temperature per condition (top 10)
        top10_conditions = top_conditions.head(10).index.tolist()
        cond_temp = (df[df['condition_text'].isin(top10_conditions)]
                     .groupby('condition_text')['temperature_celsius'].mean()
                     .sort_values(ascending=False))
        fig, ax = plt.subplots(figsize=(11, 5))
        cmap_vals = plt.cm.RdYlBu_r(np.linspace(0, 1, len(cond_temp)))
        ax.barh(cond_temp.index[::-1], cond_temp.values[::-1],
                color=cmap_vals[::-1], alpha=0.9, edgecolor='none')
        ax.set_title("Average Temperature by Weather Condition (Top 10)",
                     fontsize=14, pad=12, fontweight='bold')
        ax.set_xlabel("Avg Temperature (°C)")
        plt.tight_layout()
        plt.savefig(out_path / "16b_condition_temp_avg.png", dpi=100, facecolor='#161920')
        plt.close()

    # ─────────────────────────────────────────────
    # 5. Environmental AQI Correlations (fixed col names)
    # ─────────────────────────────────────────────
    # Actual column names from the dataset:
    aqi_candidates = [
        'air_quality_PM2.5', 'air_quality_PM10',
        'air_quality_Ozone', 'air_quality_Nitrogen_dioxide',
        'air_quality_Sulphur_dioxide', 'air_quality_Carbon_Monoxide',
        'air_quality_us-epa-index', 'air_quality_gb-defra-index'
    ]
    aqi_cols = [c for c in aqi_candidates if c in df.columns]

    if aqi_cols:
        met_cols = ['temperature_celsius', 'humidity', 'wind_kph', 'visibility_km', 'pressure_mb']
        met_cols = [c for c in met_cols if c in df.columns]
        all_cols = aqi_cols + met_cols

        fig, ax = plt.subplots(figsize=(11, 8))
        corr_matrix = df[all_cols].corr()
        mask = np.zeros_like(corr_matrix, dtype=bool)
        mask[np.triu_indices_from(mask, k=1)] = True  # upper triangle only
        sns.heatmap(corr_matrix, annot=True, cmap="mako", fmt=".2f",
                    ax=ax, linewidths=0.5, mask=mask, annot_kws={'size': 8})
        ax.set_title("Air Quality Indicators × Meteorological Features — Correlation Matrix",
                     fontsize=13, pad=12, fontweight='bold')
        plt.tight_layout()
        plt.savefig(out_path / "17_aqi_weather_correlations.png", dpi=100, facecolor='#161920')
        plt.close()

        # AQI Index distribution by EPA category
        if 'air_quality_us-epa-index' in df.columns:
            epa_labels = {1:'Good', 2:'Moderate', 3:'Unhealthy (Sensitive)', 4:'Unhealthy', 5:'Very Unhealthy', 6:'Hazardous'}
            epa_counts = df['air_quality_us-epa-index'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(9, 5))
            colors_epa = ['#10b981','#f59e0b','#f97316','#ef4444','#7c3aed','#1e1b4b']
            ax.bar([epa_labels.get(int(k), str(k)) for k in epa_counts.index],
                   epa_counts.values, color=colors_epa[:len(epa_counts)], alpha=0.85, edgecolor='none')
            ax.set_title("Air Quality Index Distribution (US-EPA Standard)",
                         fontsize=14, pad=12, fontweight='bold')
            ax.set_xlabel("AQI Category"); ax.set_ylabel("Number of Records")
            plt.xticks(rotation=20, ha='right')
            plt.tight_layout()
            plt.savefig(out_path / "17b_aqi_epa_distribution.png", dpi=100, facecolor='#161920')
            plt.close()

    # ─────────────────────────────────────────────
    # 6. Feature Importance (Random Forest)
    # ─────────────────────────────────────────────
    if 'Random Forest' in models_dict:
        rf_model = models_dict['Random Forest']
        feature_names = [
            'humidity', 'wind_kph', 'pressure_mb', 'precip_mm', 'cloud',
            'uv_index', 'hour', 'day_of_week', 'month', 'temp_humidity_index'
        ]
        feature_names = [f for f in feature_names if f in df.columns]

        importances = rf_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        sorted_features = [feature_names[i] for i in indices]
        sorted_importances = importances[indices]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(sorted_features[::-1], sorted_importances[::-1],
                       color='#10b981', alpha=0.85, edgecolor='none')
        for bar, val in zip(bars, sorted_importances[::-1]):
            ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}', va='center', fontsize=9, color='#94a3b8')
        ax.set_title("Feature Importance Ranking — Random Forest Regressor",
                     fontsize=14, pad=12, fontweight='bold')
        ax.set_xlabel("Importance Score")
        plt.tight_layout()
        plt.savefig(out_path / "20_feature_importance_rf.png", dpi=100, facecolor='#161920')
        plt.close()

    # ─────────────────────────────────────────────
    # 7. Interactive Folium Spatial Heatmap
    # ─────────────────────────────────────────────
    if 'latitude' in df.columns and 'longitude' in df.columns:
        print("  → Generating interactive Folium spatial heatmap...")
        try:
            import folium
            from folium.plugins import HeatMap

            group_cols = [c for c in ['location_name', 'country', 'latitude', 'longitude'] if c in df.columns]
            map_data = (df.groupby(group_cols)[['temperature_celsius', 'precip_mm']]
                          .mean().reset_index())

            m = folium.Map(location=[20.0, 0.0], zoom_start=2, tiles="cartodbdark_matter")

            # Temperature heatmap layer
            heat_data = [[row['latitude'], row['longitude'], row['temperature_celsius']]
                         for _, row in map_data.iterrows()]
            HeatMap(heat_data, name="Temperature Heatmap",
                    min_opacity=0.3, radius=14, blur=12, max_zoom=1).add_to(m)

            # City markers (top 200 cities)
            for _, row in map_data.head(200).iterrows():
                city = row.get('location_name', row.get('country', 'City'))
                country = row.get('country', '')
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=4,
                    popup=folium.Popup(
                        f"<b>{city}</b><br>{country}<br>"
                        f"Avg Temp: <b>{row['temperature_celsius']:.1f}°C</b><br>"
                        f"Avg Precip: <b>{row['precip_mm']:.2f} mm</b>",
                        max_width=200
                    ),
                    color="#38bdf8", fill=True, fill_color="#38bdf8", fill_opacity=0.75
                ).add_to(m)

            folium.LayerControl().add_to(m)
            map_html = rep_path / "interactive_map.html"
            m.save(str(map_html))
            print(f"  → Folium map saved to {map_html}")

        except Exception as e:
            print(f"  → Folium map failed: {e}")
            map_html = rep_path / "interactive_map.html"
            map_html.write_text("<html><body><p>Folium map unavailable.</p></body></html>")
    else:
        print("  → Latitude/longitude not found. Skipping Folium map.")
