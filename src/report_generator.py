"""
Compiles a premium, interactive SaaS-style dark-themed HTML dashboard
with tabbed navigation, KPI cards, PM Accelerator mission, image lightbox,
and all generated analysis plots embedded as base64.
"""
from pathlib import Path
import base64
import datetime

# ─────────────────────────────────────────────────────────────────
# Plot catalog: prefix → (title, description)
# ─────────────────────────────────────────────────────────────────
PLOT_META = {
    "01": ("Global Temperature Trend",
           "Continuous temperature readings sampled across all global monitoring stations over time."),
    "02": ("Meteorological Correlation Matrix",
           "Pearson correlation heatmap between core weather variables — temperature, humidity, wind, pressure, UV, visibility."),
    "03": ("Temperature vs Humidity",
           "Scatter distribution revealing the combined thermal-humidity envelope across all global cities."),
    "04": ("Wind Speed Distribution",
           "Box-and-whisker plot summarising median, IQR, and outlier wind speeds across the full dataset."),
    "05": ("Precipitation Distribution & Categories",
           "Histogram of non-zero rainfall (log scale) and intensity category breakdown: None / Light / Moderate / Heavy."),
    "06": ("Monthly Average Precipitation",
           "Global average precipitation (mm) aggregated by calendar month to identify seasonal wet/dry cycles."),
    "07": ("Top 15 Rainiest Cities",
           "Horizontal bar chart of the 15 cities with the highest average daily precipitation across the observation period."),
    "08": ("Isolation Forest Anomaly Detection",
           "Anomalous climate events (red ×) flagged at 2% contamination threshold against normal readings (grey dots)."),
    "09": ("ARIMA(5,1,2) Daily Forecast",
           "Classical time-series ARIMA forecast of daily average temperature vs actual future values."),
    "10": ("ML Regressor Predictions vs Actual",
           "First 150 test-set predictions compared for Ridge baseline, Ensemble model, and true temperature values."),
    "11": ("Ensemble Model Residuals",
           "Distribution of prediction errors for the weighted ensemble model — should be centred on zero for an unbiased model."),
    "14": ("Country-Level Temperature Extremes",
           "Boxplot of temperature distributions across the 8 hottest and 8 coldest countries by average temperature."),
    "15": ("Continent-Level Temperature Distribution",
           "Boxplot comparing temperature spread across all 6 continents — reveals clear latitudinal climate zones."),
    "15b": ("Continent-Level Precipitation",
            "Average daily precipitation (mm) per continent — highlights tropical vs arid regional differences."),
    "16": ("Top 15 Weather Conditions (Global Frequency)",
           "Bar chart of the 15 most frequently recorded weather condition descriptions worldwide."),
    "16b": ("Average Temperature by Weather Condition",
            "Mean temperature for each of the top 10 weather conditions, showing thermal differences between condition types."),
    "17": ("AQI × Meteorological Correlation Matrix",
           "Lower-triangle heatmap of Air Quality Index pollutants correlated with temperature, wind, humidity, and visibility."),
    "17b": ("US-EPA Air Quality Index Distribution",
            "Frequency of each EPA AQI category from Good to Hazardous across all global cities."),
    "20": ("Random Forest Feature Importance",
           "Ranked predictive importance scores for each input feature computed by the Random Forest regressor."),
    "25": ("N vs S Hemisphere Seasonal Cycles",
           "Opposite seasonal temperature waves of the Northern and Southern Hemispheres confirming inverse climate cycles."),
}

# Tab structure: (label, [plot_prefix_list])
TABS = [
    ("📊 Overview",              ["01", "10", "11"]),
    ("🌧️ Precipitation",         ["05", "06", "07"]),
    ("🔍 EDA & Correlations",    ["02", "03", "04"]),
    ("🚨 Anomaly Detection",     ["08"]),
    ("🤖 Forecasting Models",    ["09"]),
    ("🌍 Climate & Extremes",    ["14", "25"]),
    ("🗺️ Geographical Patterns", ["15", "15b", "16", "16b"]),
    ("💨 Air Quality (AQI)",     ["17", "17b"]),
    ("🧬 Feature Importance",    ["20"]),
    ("📍 Spatial Map",           []),   # Folium iframe, handled separately
]

# PM Accelerator Real Mission Statement (from pmaccelerator.io)
PM_ACCELERATOR_MISSION = """
PM Accelerator is on a mission to <strong>break down financial barriers and achieve
educational fairness</strong> — empowering individuals for better life and career outcomes
while fostering a more diverse and inclusive landscape in the tech industry.
Driven by founder <strong>Dr. Nancy Li</strong>, PM Accelerator's long-term vision is to
establish <strong>200 schools worldwide over the next 20 years</strong>, providing
world-class product management and entrepreneurship education to families who
otherwise could not afford it. The program offers the most accessible, community-driven,
and outcome-focused product management education available today — helping aspiring and
experienced PMs gain the skills, network, and confidence to land their dream PM roles
and excel throughout their careers.
"""


def _img_b64(path: Path) -> str:
    """Return base64-encoded data URI for a PNG file."""
    try:
        data = path.read_bytes()
        return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    except Exception:
        return ""


def generate_html_report(df, metrics_report, plots_dir, reports_dir):
    """Compile the full interactive HTML dashboard."""
    print("Compiling interactive HTML dashboard...")
    plots_path = Path(plots_dir)
    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)

    # ── KPI values ──────────────────────────────
    total_records  = len(df)
    unique_cities  = df['location_name'].nunique() if 'location_name' in df.columns else 0
    unique_countries = df['country'].nunique() if 'country' in df.columns else 0
    anomaly_count  = int(df['is_anomaly'].sum()) if 'is_anomaly' in df.columns else 0
    anomaly_pct    = round(anomaly_count / total_records * 100, 2) if total_records else 0

    best_model = min(
        {k: v for k, v in metrics_report.items() if k != 'ARIMA'},
        key=lambda k: metrics_report[k].get('MAE', 9999)
    )
    best_mae = metrics_report[best_model]['MAE']

    avg_temp = round(df['temperature_celsius'].mean(), 1) if 'temperature_celsius' in df.columns else 0

    today = datetime.date.today().strftime('%B %d, %Y')

    # ── Pre-render tab buttons & content ────────
    tab_buttons = ""
    tab_contents = ""

    for tab_idx, (label, plot_keys) in enumerate(TABS):
        tab_id = f"tab{tab_idx}"
        active_btn = "active" if tab_idx == 0 else ""
        active_div = "active" if tab_idx == 0 else ""

        tab_buttons += f'<li class="nav-item {active_btn}" onclick="switchTab(\'{tab_id}\', this)">{label}</li>\n'

        # Spatial Map tab — iframe only
        if label == "📍 Spatial Map":
            tab_contents += f"""
<div id="{tab_id}" class="tab-content {active_div}">
  <div class="section-card">
    <div class="section-title">📍 Global Temperature Spatial Heatmap</div>
    <p class="section-desc">
      Interactive Folium map showing global temperature intensity and city-level markers.
      Click any marker for city name, average temperature, and average precipitation.
    </p>
    <div class="map-wrapper">
      <iframe src="interactive_map.html" title="Global Temperature Heatmap"></iframe>
    </div>
  </div>
</div>"""
            continue

        # Overview tab — metrics table first
        metrics_table = ""
        if tab_idx == 0:
            rows = ""
            for model_name, m in sorted(metrics_report.items(), key=lambda x: x[1].get('MAE', 9999)):
                is_best = (model_name == best_model)
                badge = '<span class="best-badge">★ BEST</span>' if is_best else ""
                row_cls = 'class="best-row"' if is_best else ""
                rows += f"""<tr {row_cls}>
  <td><strong>{model_name}</strong>{badge}</td>
  <td>{m.get('MAE',0):.4f}</td>
  <td>{m.get('RMSE',0):.4f}</td>
  <td>{m.get('R2',0):.4f}</td>
  <td>{m.get('MAPE',0):.2f}%</td>
</tr>"""
            metrics_table = f"""
<div class="metrics-card">
  <div class="section-title" style="margin-bottom:1.25rem;">📈 Forecasting Model Evaluation</div>
  <div class="table-wrapper">
    <table>
      <thead><tr>
        <th>Model</th><th>MAE (°C)</th><th>RMSE (°C)</th><th>R² Score</th><th>MAPE (%)</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</div>"""

        # Plot grid
        plot_cards = ""
        for key in plot_keys:
            matching = sorted(plots_path.glob(f"{key}_*.png")) + sorted(plots_path.glob(f"{key}.png"))
            # Also try prefix match
            if not matching:
                matching = [p for p in plots_path.glob("*.png") if p.stem.startswith(key + "_") or p.stem == key]
            if matching:
                img_path = matching[0]
                b64 = _img_b64(img_path)
                title, desc = PLOT_META.get(key, (img_path.stem.replace("_", " ").title(), ""))
                plot_cards += f"""
<div class="plot-card">
  <div class="plot-title">{title}</div>
  <p class="plot-desc">{desc}</p>
  <div class="img-box" onclick="openModal('{b64}')">
    <img src="{b64}" alt="{title}" loading="lazy">
    <div class="zoom-hint">🔍 Click to zoom</div>
  </div>
</div>"""

        tab_contents += f"""
<div id="{tab_id}" class="tab-content {active_div}">
  {metrics_table}
  <div class="plot-grid">{plot_cards}</div>
</div>"""

    # ── Full HTML ────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Weather Trend Forecasting | PM Accelerator Assessment</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:        #0b0f17;
  --sidebar:   #0f172a;
  --card:      rgba(30,41,59,0.45);
  --border:    rgba(255,255,255,0.07);
  --accent:    #38bdf8;
  --accent2:   #818cf8;
  --success:   #10b981;
  --warn:      #f59e0b;
  --danger:    #ef4444;
  --text:      #f1f5f9;
  --muted:     #94a3b8;
  --glow:      rgba(56,189,248,0.12);
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
  display: flex;
  min-height: 100vh;
  overflow-x: hidden;
}}

/* ── Sidebar ─────────────────────────────── */
aside {{
  width: 270px;
  min-height: 100vh;
  background: var(--sidebar);
  border-right: 1px solid var(--border);
  padding: 2rem 1.25rem;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  overflow-y: auto;
  z-index: 20;
}}
.logo {{ margin-bottom: 2.5rem; }}
.logo-title {{
  font-family: 'Outfit', sans-serif;
  font-weight: 800;
  font-size: 1.4rem;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
  line-height: 1.2;
}}
.logo-sub {{ font-size: 0.75rem; color: var(--muted); margin-top: 0.25rem; }}
.nav-list {{ list-style: none; display: flex; flex-direction: column; gap: 0.35rem; }}
.nav-item {{
  padding: 0.75rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  color: var(--muted);
  font-size: 0.88rem;
  font-weight: 500;
  transition: all 0.2s;
  user-select: none;
}}
.nav-item:hover {{ background: rgba(56,189,248,0.07); color: var(--text); }}
.nav-item.active {{
  background: rgba(56,189,248,0.12);
  color: var(--accent);
  border-left: 3px solid var(--accent);
  font-weight: 600;
}}

/* ── Main ────────────────────────────────── */
main {{
  margin-left: 270px;
  flex: 1;
  padding: 2.5rem 2.75rem;
  max-width: calc(100vw - 270px);
}}
header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}}
.header-title {{
  font-family: 'Outfit', sans-serif;
  font-weight: 800;
  font-size: 2rem;
  letter-spacing: -1px;
  background: linear-gradient(to right, #f8fafc, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.header-sub {{ color: var(--muted); margin-top: 0.3rem; font-size: 0.9rem; }}
.timestamp {{
  font-size: 0.8rem;
  color: var(--muted);
  background: rgba(30,41,59,0.6);
  padding: 0.4rem 0.9rem;
  border-radius: 20px;
  border: 1px solid var(--border);
  white-space: nowrap;
}}

/* ── KPI Cards ───────────────────────────── */
.kpi-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}}
.kpi-card {{
  background: var(--card);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.4rem 1.5rem;
  transition: transform 0.25s, box-shadow 0.25s;
}}
.kpi-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 30px -10px var(--glow);
  border-color: rgba(56,189,248,0.25);
}}
.kpi-label {{ font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; }}
.kpi-value {{
  font-family: 'Outfit', sans-serif;
  font-size: 1.8rem;
  font-weight: 700;
  margin-top: 0.3rem;
}}
.kpi-value.blue   {{ color: var(--accent); }}
.kpi-value.green  {{ color: var(--success); }}
.kpi-value.yellow {{ color: var(--warn); }}
.kpi-value.purple {{ color: var(--accent2); }}

/* ── Mission Card ────────────────────────── */
.mission-card {{
  background: linear-gradient(135deg, rgba(56,189,248,0.07), rgba(129,140,248,0.07));
  border: 1px solid rgba(56,189,248,0.2);
  border-radius: 18px;
  padding: 2rem 2.25rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}}
.mission-card::before {{
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 200px; height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(56,189,248,0.08), transparent 70%);
  pointer-events: none;
}}
.mission-badge {{
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--accent);
  background: rgba(56,189,248,0.1);
  border: 1px solid rgba(56,189,248,0.25);
  border-radius: 20px;
  padding: 0.3rem 0.85rem;
  margin-bottom: 1rem;
}}
.mission-heading {{
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  font-size: 1.2rem;
  margin-bottom: 0.75rem;
  color: var(--text);
}}
.mission-text {{
  color: #cbd5e1;
  font-size: 0.93rem;
  line-height: 1.7;
}}

/* ── Tab Content ─────────────────────────── */
.tab-content {{ display: none; animation: fadeUp 0.35s ease both; }}
.tab-content.active {{ display: block; }}
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ── Plot Grid ───────────────────────────── */
.plot-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
  gap: 1.75rem;
  margin-top: 1.5rem;
}}
.plot-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: border-color 0.25s;
}}
.plot-card:hover {{ border-color: rgba(56,189,248,0.25); }}
.plot-title {{
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  font-size: 1.1rem;
  border-left: 3px solid var(--accent);
  padding-left: 0.75rem;
}}
.plot-desc {{ color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}
.img-box {{
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border);
  cursor: zoom-in;
  position: relative;
  background: #0f172a;
  transition: border-color 0.25s;
}}
.img-box:hover {{ border-color: var(--accent); }}
.img-box img {{ width: 100%; display: block; transition: transform 0.3s; }}
.img-box:hover img {{ transform: scale(1.015); }}
.zoom-hint {{
  position: absolute;
  bottom: 8px; right: 10px;
  font-size: 0.72rem;
  color: var(--muted);
  background: rgba(15,23,42,0.75);
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  opacity: 0;
  transition: opacity 0.2s;
}}
.img-box:hover .zoom-hint {{ opacity: 1; }}

/* ── Metrics Table ───────────────────────── */
.metrics-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.75rem;
  margin-bottom: 1.75rem;
  overflow-x: auto;
}}
.section-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.75rem;
  margin-bottom: 1.5rem;
}}
.section-title {{
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  font-size: 1.2rem;
  border-left: 3px solid var(--accent);
  padding-left: 0.75rem;
}}
.section-desc {{ color: var(--muted); font-size: 0.88rem; line-height: 1.6; margin-top: 0.5rem; }}
.table-wrapper {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{
  color: var(--muted);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
}}
td {{
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.035);
  font-size: 0.9rem;
}}
tr:hover td {{ background: rgba(255,255,255,0.018); }}
.best-row {{ background: rgba(16,185,129,0.06); }}
.best-badge {{
  background: var(--success);
  color: #0b0f17;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  margin-left: 0.5rem;
  vertical-align: middle;
}}

/* ── Map ─────────────────────────────────── */
.map-wrapper {{
  width: 100%;
  height: 560px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
  margin-top: 1rem;
}}
.map-wrapper iframe {{ width: 100%; height: 100%; border: none; }}

/* ── Lightbox Modal ──────────────────────── */
.modal-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(11,15,23,0.94);
  z-index: 999;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}}
.modal-overlay.open {{ display: flex; }}
.modal-img {{
  max-width: 90vw;
  max-height: 88vh;
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 25px 60px -15px rgba(0,0,0,0.6);
  animation: zoomIn 0.25s ease;
}}
@keyframes zoomIn {{
  from {{ transform: scale(0.88); opacity: 0; }}
  to   {{ transform: scale(1);    opacity: 1; }}
}}
.modal-close {{
  position: absolute;
  top: 1.25rem; right: 1.5rem;
  font-size: 2.5rem;
  color: var(--muted);
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s;
}}
.modal-close:hover {{ color: var(--text); }}
</style>
</head>
<body>

<!-- Sidebar -->
<aside>
  <div class="logo">
    <div class="logo-title">🌦️ WeatherDS</div>
    <div class="logo-sub">PM Accelerator Assessment</div>
  </div>
  <ul class="nav-list">
    {tab_buttons}
  </ul>
</aside>

<!-- Main workspace -->
<main>
  <!-- Header -->
  <header>
    <div>
      <div class="header-title">Global Weather Trend Forecasting</div>
      <div class="header-sub">Advanced Climate Modelling · Anomaly Detection · Multi-Model Forecasting · Spatial Analysis</div>
    </div>
    <div class="timestamp">📅 Generated: {today}</div>
  </header>

  <!-- KPI Cards -->
  <section class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Total Records Processed</div>
      <div class="kpi-value blue">{total_records:,}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Global Cities Monitored</div>
      <div class="kpi-value">{unique_cities:,}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Countries Represented</div>
      <div class="kpi-value purple">{unique_countries}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Anomalies Detected</div>
      <div class="kpi-value yellow">{anomaly_count:,} ({anomaly_pct}%)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Best Forecast Model</div>
      <div class="kpi-value green">{best_model}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Global Avg Temperature</div>
      <div class="kpi-value blue">{avg_temp}°C</div>
    </div>
  </section>

  <!-- PM Accelerator Mission -->
  <section class="mission-card">
    <div class="mission-badge">🎯 PM Accelerator Mission</div>
    <div class="mission-heading">Empowering the Next Generation of Product Leaders</div>
    <p class="mission-text">{PM_ACCELERATOR_MISSION}</p>
  </section>

  <!-- Tab Contents -->
  {tab_contents}
</main>

<!-- Lightbox Modal -->
<div class="modal-overlay" id="lightbox" onclick="closeModal()">
  <span class="modal-close" onclick="closeModal()">×</span>
  <img class="modal-img" id="modalImg" src="" alt="Plot Zoom">
</div>

<script>
  function switchTab(tabId, el) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');
    if (el) el.classList.add('active');
  }}
  function openModal(src) {{
    document.getElementById('modalImg').src = src;
    document.getElementById('lightbox').classList.add('open');
  }}
  function closeModal() {{
    document.getElementById('lightbox').classList.remove('open');
  }}
  document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});
</script>
</body>
</html>
"""
    out_file = reports_path / "weather_analysis_report.html"
    out_file.write_text(html, encoding='utf-8')
    print(f"  → Dashboard saved: {out_file}")
