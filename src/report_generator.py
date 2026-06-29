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
  --bg: #090d16;
  --sidebar: #06090f;
  --card: rgba(15, 22, 38, 0.6);
  --border: rgba(255, 255, 255, 0.05);
  --border-hover: rgba(99, 102, 241, 0.25);
  --accent: #60a5fa;
  --accent2: #a78bfa;
  --success: #34d399;
  --warn: #fbbf24;
  --danger: #f87171;
  --text: #f3f4f6;
  --muted: #6b7280;
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

/* Custom Thin Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Floating Ambient Orbs - Extremely soft, high end */
body::before {
  content: '';
  position: fixed;
  top: -10%;
  left: -5%;
  width: 45vw;
  height: 45vw;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.03) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

body::after {
  content: '';
  position: fixed;
  bottom: -10%;
  right: -5%;
  width: 50vw;
  height: 50vw;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.03) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

/* SIDEBAR - Solid Slate Dark */
aside {
  width: 260px;
  min-height: 100vh;
  background: var(--sidebar);
  border-right: 1px solid var(--border);
  padding: 2rem 1.2rem;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 30;
  display: flex;
  flex-direction: column;
}

.logo {
  margin-bottom: 2rem;
  padding: 0.85rem 1rem;
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
}

.logo-title {
  font-family: var(--display);
  font-weight: 800;
  font-size: 1.35rem;
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.logo-sub {
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 0.15rem;
}

.nav-section {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--muted);
  padding: 0.4rem 0.75rem;
  margin-top: 1.25rem;
  margin-bottom: 0.4rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.7rem 0.85rem;
  border-radius: 10px;
  cursor: pointer;
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 500;
  transition: all 0.2s ease;
  user-select: none;
  margin-bottom: 3px;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.02);
  color: var(--text);
}

.nav-item.active {
  background: rgba(99, 102, 241, 0.06);
  color: #60a5fa;
  border-left-color: #60a5fa;
  font-weight: 600;
}

.nav-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
}

.search-box-container {
  padding: 0.2rem 0.75rem;
  margin-bottom: 0.5rem;
}

.search-input {
  width: 100%;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
  color: #ffffff;
  font-family: var(--font);
  font-size: 0.78rem;
  outline: none;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.04);
}

/* MAIN CONTENT */
main {
  margin-left: 260px;
  flex: 1;
  padding: 2.5rem 3rem;
  position: relative;
  z-index: 10;
  max-width: 1400px;
  width: calc(100% - 260px);
}

/* PAGE HEADER */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.page-title {
  font-family: var(--display);
  font-weight: 800;
  font-size: 2rem;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #ffffff 40%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-sub {
  color: var(--muted);
  margin-top: 0.25rem;
  font-size: 0.85rem;
}

.date-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--accent);
  background: rgba(96, 165, 250, 0.05);
  border: 1px solid rgba(96, 165, 250, 0.15);
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
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
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.25rem;
  position: relative;
  transition: all 0.25s ease;
}

@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
  .kpi { grid-column: span 1; }
}

.kpi:hover {
  transform: translateY(-3px);
  border-color: var(--border-hover);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.kpi-icon {
  font-size: 1.4rem;
  margin-bottom: 0.5rem;
  color: var(--accent);
}

.kpi-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-value {
  font-family: var(--display);
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 0.25rem;
  color: #ffffff;
}

/* MISSION CARD */
.mission {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.03) 0%, rgba(167, 139, 250, 0.03) 100%);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.mission-badge {
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(96, 165, 250, 0.08);
  border: 1px solid rgba(96, 165, 250, 0.15);
  border-radius: 9999px;
  padding: 0.25rem 0.75rem;
  margin-bottom: 0.75rem;
}

.mission-title {
  font-family: var(--display);
  font-weight: 700;
  font-size: 1.15rem;
  margin-bottom: 0.5rem;
  color: #ffffff;
}

.mission-text {
  color: #9ca3af;
  font-size: 0.88rem;
  line-height: 1.6;
}

/* TABS */
.tab {
  display: none;
  animation: fadeIn 0.3s ease both;
}

.tab.active {
  display: block;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* METRICS TABLE */
.table-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.card-title {
  font-family: var(--display);
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 1.25rem;
  color: #ffffff;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  color: var(--muted);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
}

td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
  font-size: 0.85rem;
  color: #e5e7eb;
}

tr:last-child td {
  border-bottom: none;
}

.best-row {
  background: rgba(52, 211, 153, 0.03);
}

.best-badge {
  background: var(--success);
  color: #000000;
  font-size: 0.6rem;
  font-weight: 800;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  margin-left: 0.5rem;
}

/* PLOT GRID */
.plot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(460px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.plot-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  transition: all 0.25s ease;
}

.plot-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.plot-title {
  font-family: var(--display);
  font-weight: 700;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ffffff;
}

.plot-title-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
}

.plot-desc {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.5;
}

.img-wrap {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border);
  cursor: zoom-in;
  position: relative;
  background: #000000;
}

.img-wrap img {
  width: 100%;
  display: block;
  transition: transform 0.3s ease;
}

.img-wrap:hover img {
  transform: scale(1.015);
}

.zoom-label {
  position: absolute;
  bottom: 10px;
  right: 10px;
  font-size: 0.65rem;
  color: var(--text);
  background: rgba(0, 0, 0, 0.8);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

/* SPATIAL MAP */
.map-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.map-frame {
  width: 100%;
  height: 560px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
  margin-top: 1rem;
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
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(5px);
  align-items: center;
  justify-content: center;
}

.overlay.open {
  display: flex;
}

.overlay img {
  max-width: 90vw;
  max-height: 88vh;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  animation: zoomIn 0.2s ease;
}

@keyframes zoomIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.close-btn {
  position: absolute;
  top: 1.5rem;
  right: 2rem;
  font-size: 2.5rem;
  color: var(--muted);
  cursor: pointer;
  background: none;
  border: none;
}

.close-btn:hover {
  color: #ffffff;
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

function setTheme(themeName, el) {
  document.body.className = 'theme-' + themeName;
  document.querySelectorAll('.theme-dot').forEach(d => d.classList.remove('active'));
  if (el) el.classList.add('active');
  localStorage.setItem('selected-theme', themeName);
}

function filterPlots(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('.plot-card').forEach(card => {
    const title = card.querySelector('.plot-title').innerText.toLowerCase();
    const desc = card.querySelector('.plot-desc').innerText.toLowerCase();
    if (title.includes(q) || desc.includes(q)) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });
}

function animateCountUp() {
  document.querySelectorAll('.kpi-value').forEach(el => {
    const raw = el.getAttribute('data-value');
    if (!raw) return;
    const target = parseFloat(raw.replace(/[^\d\.-]/g, ''));
    if (isNaN(target)) return;
    let start = 0;
    const duration = 1200;
    const startTime = performance.now();
    
    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = progress * (2 - progress);
      const current = start + ease * (target - start);
      
      if (raw.includes('%')) {
        el.innerText = current.toFixed(2) + '%';
      } else if (raw.includes('°C')) {
        el.innerText = current.toFixed(1) + '°C';
      } else {
        el.innerText = Math.floor(current).toLocaleString();
      }
      
      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.innerText = raw;
      }
    }
    requestAnimationFrame(update);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  animateCountUp();
  const saved = localStorage.getItem('selected-theme') || 'cyber';
  const dot = document.querySelector('.dot-' + saved);
  setTheme(saved, dot);

  // 3D tilt effect on interactive cards
  document.querySelectorAll('.plot-card, .kpi, .mission').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const xc = rect.width / 2;
      const yc = rect.height / 2;
      card.style.transform = `translateY(-6px) rotateY(${(x - xc) / 25}deg) rotateX(${-(y - yc) / 12}deg)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
});
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
        ("🌡️","Global Avg Temp",f"{avg_t}°C","--c1:#22d3ee;--c2:#0ea5e9"),
        ("📍","Cities Monitored",f"{cities:,}","--c1:#a78bfa;--c2:#c084fc"),
        ("🌍","Countries",f"{ctries}","--c1:#34d399;--c2:#059669"),
        ("🚨","Anomalies",f"{anom:,} ({apct}%)","--c1:#f59e0b;--c2:#d97706"),
        ("🏆","Best Model",best,"--c1:#34d399;--c2:#22d3ee"),
        ("📊","Total Records",f"{total:,}","--c1:#ec4899;--c2:#f472b6"),
    ]

    kpis_html = "".join(
        f'<div class="kpi" style="{st}"><div class="kpi-icon">{ic}</div>'
        f'<div class="kpi-label">{lb}</div>'
        f'<div class="kpi-value" data-value="{vl}">0</div></div>'
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
  <div class="nav-section">Search Charts</div>
  <div class="search-box-container">
    <input type="text" class="search-input" placeholder="🔍 Search charts..." oninput="filterPlots(this.value)">
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
