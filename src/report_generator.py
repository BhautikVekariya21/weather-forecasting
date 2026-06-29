"""
Premium SaaS-style interactive HTML dashboard generator.
Dark glassmorphism design with animated gradient background, tabbed navigation,
lightbox image zoom, KPI cards, and PM Accelerator mission statement.
"""
from pathlib import Path
import base64, datetime

# ── Plot metadata ─────────────────────────────────────────────────
PLOTS = {
    "01": ("🌡️", "Temperature Trend", "Global temperature over time across all sampled monitoring stations."),
    "02": ("🔗", "Correlation Matrix", "Pearson heatmap of core meteorological features — temp, humidity, wind, pressure, UV."),
    "03": ("💧", "Temp vs Humidity", "Scatter plot revealing the thermal-humidity envelope across global cities."),
    "04": ("🌬️", "Wind Speed Distribution", "Box-whisker of wind speeds summarising median, IQR and outlier range."),
    "05": ("🌧️", "Precipitation Distribution", "Non-zero rainfall histogram (log-scale) and intensity category breakdown."),
    "06": ("📅", "Monthly Precipitation", "Average precipitation by calendar month showing seasonal wet/dry cycles."),
    "07": ("🏙️", "Rainiest Cities", "Top 15 cities ranked by average daily precipitation volume."),
    "08": ("🚨", "Anomaly Detection", "Isolation Forest anomalies (2% contamination) — red × marks flagged outliers."),
    "09": ("📈", "ARIMA Forecast", "Classical ARIMA(5,1,2) daily temperature forecast vs actual future values."),
    "10": ("🤖", "Model Comparison", "Ridge, Ensemble and actual temperature on 150-record test window."),
    "11": ("📊", "Ensemble Residuals", "Prediction error distribution for the weighted ensemble model."),
    "14": ("🌍", "Country Extremes", "Temperature spread across the 8 hottest and 8 coldest countries."),
    "15": ("🗺️", "Continent Temperature", "Temperature boxplot by continent — reveals latitudinal climate zones."),
    "15b": ("🌦️", "Continent Precipitation", "Average daily precipitation per continent — tropical vs arid differences."),
    "16": ("☁️", "Weather Conditions", "Top 15 most frequent weather condition types worldwide."),
    "16b": ("🌤️", "Condition vs Temp", "Mean temperature for each of the top 10 weather condition types."),
    "17": ("💨", "AQI Correlation", "Air quality pollutants correlated with temp, wind, humidity and visibility."),
    "17b": ("📉", "EPA AQI Distribution", "US-EPA AQI category frequency from Good to Hazardous across all cities."),
    "20": ("🧬", "Feature Importance", "Random Forest predictor ranking — humidity and THI dominate."),
    "25": ("🌐", "Hemisphere Cycles", "Opposite seasonal temperature waves of Northern vs Southern Hemispheres."),
}

TABS = [
    ("📊", "Overview",            ["01","10","11"]),
    ("🌧️", "Precipitation",      ["05","06","07"]),
    ("🔍", "EDA",                 ["02","03","04"]),
    ("🚨", "Anomalies",          ["08"]),
    ("🤖", "Forecasting",        ["09"]),
    ("🌍", "Climate",            ["14","25"]),
    ("🗺️", "Geography",         ["15","15b","16","16b"]),
    ("💨", "Air Quality",        ["17","17b"]),
    ("🧬", "Features",           ["20"]),
    ("📍", "Spatial Map",        []),
]

PM_MISSION = (
    "PM Accelerator is on a mission to <strong>break down financial barriers and achieve "
    "educational fairness</strong>, empowering individuals for better life and career outcomes "
    "while fostering a more diverse and inclusive landscape in the tech industry. "
    "Driven by founder <strong>Dr. Nancy Li</strong>, the long-term vision is to establish "
    "<strong>200 schools worldwide over the next 20 years</strong>, providing world-class "
    "product management education to families who otherwise could not afford it."
)

CSS = """
:root {
  --bg: #030712;
  --sidebar: rgba(10, 15, 30, 0.75);
  --card: rgba(17, 24, 39, 0.55);
  --border: rgba(255, 255, 255, 0.06);
  --border-hover: rgba(6, 182, 212, 0.35);
  --accent: #22d3ee;
  --accent-glow: rgba(34, 211, 238, 0.15);
  --accent2: #a78bfa;
  --success: #34d399;
  --warn: #fbbf24;
  --danger: #f87171;
  --text: #f3f4f6;
  --muted: #9ca3af;
  --font: 'Inter', sans-serif;
  --display: 'Outfit', sans-serif;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg);
  color: var(--text);
  font-family: var(--font);
  display: flex;
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

/* Floating Neon Background Orbs */
body::before {
  content: '';
  position: fixed;
  top: -10%;
  left: -10%;
  width: 50vw;
  height: 50vw;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.08) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
  animation: floatOrb 25s infinite alternate ease-in-out;
}

body::after {
  content: '';
  position: fixed;
  bottom: -10%;
  right: -10%;
  width: 60vw;
  height: 60vw;
  background: radial-gradient(circle, rgba(167, 139, 250, 0.08) 0%, transparent 70%);
  filter: blur(100px);
  pointer-events: none;
  z-index: 0;
  animation: floatOrb2 30s infinite alternate ease-in-out;
}

@keyframes floatOrb {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(8%, 12%) scale(1.1); }
}

@keyframes floatOrb2 {
  0% { transform: translate(0, 0) scale(1.1); }
  100% { transform: translate(-8%, -12%) scale(0.9); }
}

/* SIDEBAR - Ultra Modern Glassmorphism */
aside {
  width: 250px;
  min-height: 100vh;
  background: var(--sidebar);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid var(--border);
  padding: 2.25rem 1.25rem;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 30;
  display: flex;
  flex-direction: column;
}

.logo {
  margin-bottom: 2.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  box-shadow: inset 0 0 12px rgba(255, 255, 255, 0.01);
  position: relative;
  overflow: hidden;
}

.logo::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent 45%, rgba(34, 211, 238, 0.1) 50%, transparent 55%);
  transform: rotate(45deg);
  animation: logoShine 4s infinite linear;
}

@keyframes logoShine {
  0% { transform: translate(-100%, -100%) rotate(45deg); }
  100% { transform: translate(100%, 100%) rotate(45deg); }
}

.logo-title {
  font-family: var(--display);
  font-weight: 800;
  font-size: 1.45rem;
  background: linear-gradient(135deg, #22d3ee 0%, #a78bfa 50%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.75px;
}

.logo-sub {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.25rem;
  letter-spacing: 0.5px;
}

.nav-section {
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--muted);
  padding: 0.5rem 0.85rem;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  cursor: pointer;
  color: var(--muted);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  margin-bottom: 4px;
  border: 1px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.03);
  color: var(--text);
  border-color: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(34, 211, 238, 0.12) 0%, rgba(167, 139, 250, 0.04) 100%);
  color: var(--accent);
  border-color: rgba(34, 211, 238, 0.25);
  font-weight: 600;
  box-shadow: 0 4px 20px rgba(34, 211, 238, 0.05);
}

.nav-icon {
  font-size: 1.1rem;
  width: 24px;
  text-align: center;
}

/* MAIN CONTENT */
main {
  margin-left: 250px;
  flex: 1;
  padding: 2.5rem 3.5rem;
  position: relative;
  z-index: 10;
  max-width: 1500px;
  width: calc(100% - 250px);
}

/* PAGE HEADER */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.75rem;
  border-bottom: 1px solid var(--border);
}

.page-title {
  font-family: var(--display);
  font-weight: 800;
  font-size: 2.2rem;
  letter-spacing: -1.25px;
  background: linear-gradient(135deg, #ffffff 40%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-sub {
  color: var(--muted);
  margin-top: 0.4rem;
  font-size: 0.9rem;
}

.date-badge {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--accent);
  background: rgba(34, 211, 238, 0.06);
  border: 1px solid rgba(34, 211, 238, 0.18);
  padding: 0.45rem 1rem;
  border-radius: 9999px;
  box-shadow: 0 4px 15px rgba(34, 211, 238, 0.04);
}

/* BENTO KPI GRID */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.kpi {
  grid-column: span 1;
  background: var(--card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
}

@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
  .kpi { grid-column: span 1; }
}

.kpi:hover {
  transform: translateY(-5px);
  border-color: var(--border-hover);
  box-shadow: 0 15px 35px -5px var(--accent-glow);
}

.kpi::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--c1, #22d3ee), var(--c2, #a78bfa));
}

.kpi-icon {
  font-size: 1.6rem;
  margin-bottom: 0.75rem;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.75px;
}

.kpi-value {
  font-family: var(--display);
  font-size: 1.75rem;
  font-weight: 700;
  margin-top: 0.4rem;
  color: #ffffff;
}

/* PM ACCELERATOR MISSION */
.mission {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.08) 0%, rgba(167, 139, 250, 0.08) 50%, rgba(236, 72, 153, 0.04) 100%);
  border: 1px solid rgba(34, 211, 238, 0.2);
  border-radius: 24px;
  padding: 2rem 2.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.mission::after {
  content: '“';
  position: absolute;
  right: 2rem;
  bottom: -2rem;
  font-size: 12rem;
  font-family: Georgia, serif;
  color: rgba(34, 211, 238, 0.05);
  line-height: 1;
  pointer-events: none;
}

.mission-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--accent);
  background: rgba(34, 211, 238, 0.12);
  border: 1px solid rgba(34, 211, 238, 0.25);
  border-radius: 9999px;
  padding: 0.3rem 1rem;
  margin-bottom: 1rem;
}

.mission-title {
  font-family: var(--display);
  font-weight: 800;
  font-size: 1.35rem;
  margin-bottom: 0.75rem;
  background: linear-gradient(to right, #ffffff, #e2e8f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.mission-text {
  color: #e2e8f0;
  font-size: 0.95rem;
  line-height: 1.8;
}

/* TAB VISIBILITY SYSTEM */
.tab {
  display: none;
  animation: scaleUpTab 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.tab.active {
  display: block;
}

@keyframes scaleUpTab {
  from { opacity: 0; transform: scale(0.98) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

/* METRICS TABLE */
.table-card {
  background: var(--card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 1.75rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
}

.card-title {
  font-family: var(--display);
  font-weight: 700;
  font-size: 1.2rem;
  border-left: 4px solid var(--accent);
  padding-left: 0.85rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  color: var(--muted);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
  font-weight: 700;
}

td {
  padding: 1.1rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  font-size: 0.9rem;
  color: #e5e7eb;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background: rgba(255, 255, 255, 0.015);
}

.best-row {
  background: linear-gradient(90deg, rgba(52, 211, 153, 0.08) 0%, rgba(52, 211, 153, 0.01) 100%);
}

.best-row td {
  border-bottom-color: rgba(52, 211, 153, 0.15);
}

.best-badge {
  background: var(--success);
  color: #030712;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  margin-left: 0.6rem;
  vertical-align: middle;
  box-shadow: 0 2px 10px rgba(52, 211, 153, 0.3);
}

/* PLOT GRID & NEON CARDS */
.plot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.plot-card {
  background: var(--card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
}

.plot-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -10px var(--accent-glow);
}

.plot-title {
  font-family: var(--display);
  font-weight: 700;
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #ffffff;
}

.plot-title-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 1.1rem;
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.15) 0%, rgba(167, 139, 250, 0.15) 100%);
  border: 1px solid rgba(34, 211, 238, 0.25);
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(34, 211, 238, 0.05);
}

.plot-desc {
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.6;
}

.img-wrap {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--border);
  cursor: zoom-in;
  position: relative;
  background: #020617;
  transition: border-color 0.3s;
}

.img-wrap:hover {
  border-color: var(--accent);
}

.img-wrap img {
  width: 100%;
  display: block;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.img-wrap:hover img {
  transform: scale(1.025);
}

.zoom-label {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--accent);
  background: rgba(3, 7, 18, 0.85);
  border: 1px solid rgba(34, 211, 238, 0.25);
  padding: 0.25rem 0.65rem;
  border-radius: 8px;
  opacity: 0;
  transform: translateY(5px);
  transition: all 0.25s ease;
}

.img-wrap:hover .zoom-label {
  opacity: 1;
  transform: translateY(0);
}

/* SPATIAL MAP CARD */
.map-card {
  background: var(--card);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 2rem;
  margin-top: 1.5rem;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
}

.map-frame {
  width: 100%;
  height: 580px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border);
  margin-top: 1.25rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.map-frame iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* OVERLAY LIGHTBOX */
.overlay {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(3, 7, 18, 0.96);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.overlay.open {
  display: flex;
}

.overlay img {
  max-width: 92vw;
  max-height: 90vh;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 40px 100px -10px rgba(0, 0, 0, 0.8), 0 0 40px rgba(34, 211, 238, 0.1);
  animation: zoomIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes zoomIn {
  from { transform: scale(0.92); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.close-btn {
  position: absolute;
  top: 1.5rem;
  right: 2rem;
  font-size: 2.5rem;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
  background: none;
  border: none;
  line-height: 1;
}

.close-btn:hover {
  color: #ffffff;
  transform: rotate(90deg);
}
"""

JS = """
function switchTab(id,el){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  var t=document.getElementById(id);if(t)t.classList.add('active');
  if(el)el.classList.add('active');
}
function openModal(src){
  document.getElementById('mi').src=src;
  document.getElementById('ov').classList.add('open');
}
function closeModal(){document.getElementById('ov').classList.remove('open');}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeModal();});
"""

def _b64(path):
    try: return "data:image/png;base64,"+base64.b64encode(Path(path).read_bytes()).decode()
    except: return ""

def _find_plot(plots_path, key):
    for p in sorted(plots_path.glob(f"{key}_*.png")):
        return p
    for p in sorted(plots_path.glob(f"{key}.png")):
        return p
    return None

def generate_html_report(df, metrics_report, plots_dir, reports_dir):
    print("Compiling interactive HTML dashboard...")
    pp = Path(plots_dir); rp = Path(reports_dir)
    rp.mkdir(parents=True, exist_ok=True)

    total   = len(df)
    cities  = df['location_name'].nunique() if 'location_name' in df.columns else 0
    ctries  = df['country'].nunique() if 'country' in df.columns else 0
    anom    = int(df['is_anomaly'].sum()) if 'is_anomaly' in df.columns else 0
    apct    = round(anom/total*100,2)
    avg_t   = round(df['temperature_celsius'].mean(),1) if 'temperature_celsius' in df.columns else 0
    best    = min({k:v for k,v in metrics_report.items() if k!='ARIMA'},
                  key=lambda k:metrics_report[k].get('MAE',9999))
    today   = datetime.date.today().strftime('%b %d, %Y')

    kpi_data = [
        ("🌡️","Global Avg Temp",f"{avg_t}°C","--c1:#06b6d4;--c2:#0ea5e9"),
        ("📍","Cities Monitored",f"{cities:,}","--c1:#8b5cf6;--c2:#a78bfa"),
        ("🌍","Countries",f"{ctries}","--c1:#10b981;--c2:#34d399"),
        ("🚨","Anomalies",f"{anom:,} ({apct}%)","--c1:#f59e0b;--c2:#fbbf24"),
        ("🏆","Best Model",best,"--c1:#10b981;--c2:#06b6d4"),
        ("📊","Total Records",f"{total:,}","--c1:#8b5cf6;--c2:#ec4899"),
    ]

    kpis_html = "".join(
        f'<div class="kpi" style="{st}"><div class="kpi-icon">{ic}</div>'
        f'<div class="kpi-label">{lb}</div><div class="kpi-value">{vl}</div></div>'
        for ic,lb,vl,st in kpi_data
    )

    # Metrics table
    rows = ""
    for mn,m in sorted(metrics_report.items(),key=lambda x:x[1].get('MAE',9999)):
        ib = mn==best
        badge = '<span class="best-badge">★ BEST</span>' if ib else ""
        rc = 'class="best-row"' if ib else ""
        rows += (f'<tr {rc}><td><strong>{mn}</strong>{badge}</td>'
                 f'<td>{m.get("MAE",0):.4f}</td><td>{m.get("RMSE",0):.4f}</td>'
                 f'<td>{m.get("R2",0):.4f}</td><td>{m.get("MAPE",0):.2f}%</td></tr>')

    metrics_html = f"""
<div class="table-card">
  <div class="card-title">Model Evaluation Metrics</div>
  <table>
    <thead><tr><th>Model</th><th>MAE (°C)</th><th>RMSE (°C)</th><th>R² Score</th><th>MAPE</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""

    # Build tabs
    nav_items = ""
    tab_divs  = ""
    for i,(icon,label,keys) in enumerate(TABS):
        tid = f"t{i}"
        nav_items += (f'<div class="nav-item{" active" if i==0 else ""}" '
                      f'onclick="switchTab(\'{tid}\',this)">'
                      f'<span class="nav-icon">{icon}</span>{label}</div>\n')

        if label=="Spatial Map":
            tab_divs += f"""
<div id="{tid}" class="tab">
  <div class="map-card">
    <div class="card-title">📍 Global Temperature Spatial Heatmap</div>
    <p style="color:var(--muted);font-size:.83rem;margin-top:.3rem">
      Interactive Folium heatmap. Click any city marker for temperature and precipitation details.
    </p>
    <div class="map-frame"><iframe src="interactive_map.html" title="Global Heatmap"></iframe></div>
  </div>
</div>"""
            continue

        cards = ""
        for key in keys:
            path = _find_plot(pp, key)
            if path:
                b64  = _b64(path)
                ico,ttl,desc = PLOTS.get(key,("📊",path.stem,""))
                cards += f"""
<div class="plot-card">
  <div class="plot-title">
    <div class="plot-title-icon">{ico}</div>{ttl}
  </div>
  <p class="plot-desc">{desc}</p>
  <div class="img-wrap" onclick="openModal('{b64}')">
    <img src="{b64}" alt="{ttl}" loading="lazy">
    <div class="zoom-label">🔍 Click to zoom</div>
  </div>
</div>"""

        tab_divs += f"""
<div id="{tid}" class="tab{' active' if i==0 else ''}">
  {metrics_html if i==0 else ""}
  <div class="plot-grid">{cards}</div>
</div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Global Weather Trend Forecasting | PM Accelerator</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<aside>
  <div class="logo">
    <div class="logo-title">🌦️ WeatherDS</div>
    <div class="logo-sub">PM Accelerator · Advanced Assessment</div>
  </div>
  <div class="nav-section">Navigation</div>
  {nav_items}
</aside>

<main>
  <div class="page-header">
    <div>
      <div class="page-title">Global Weather Trend Forecasting</div>
      <div class="page-sub">Advanced Climate Modelling · Anomaly Detection · Multi-Model Forecasting · Spatial Analysis</div>
    </div>
    <div class="date-badge">📅 {today}</div>
  </div>

  <div class="kpi-grid">{kpis_html}</div>

  <div class="mission">
    <div class="mission-badge">🎯 PM Accelerator Mission</div>
    <div class="mission-title">Empowering the Next Generation of Product Leaders</div>
    <p class="mission-text">{PM_MISSION}</p>
  </div>

  {tab_divs}
</main>

<div class="overlay" id="ov" onclick="closeModal()">
  <button class="close-btn" onclick="closeModal()">×</button>
  <img id="mi" src="" alt="Zoom">
</div>
<script>{JS}</script>
</body>
</html>"""

    out = rp / "weather_analysis_report.html"
    out.write_text(html, encoding='utf-8')
    print(f"  → Dashboard saved: {out}")
