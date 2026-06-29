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
:root{
  --bg:#070c18;--sidebar:#0a1020;--card:rgba(15,23,42,.65);
  --border:rgba(255,255,255,.07);--accent:#06b6d4;--accent2:#8b5cf6;
  --success:#10b981;--warn:#f59e0b;--danger:#f87171;--muted:#64748b;
  --text:#f1f5f9;--font:'Inter',sans-serif;--display:'Outfit',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--bg);color:var(--text);font-family:var(--font);
  display:flex;min-height:100vh;overflow-x:hidden;
}
body::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 70% 50% at 10% 0%,rgba(6,182,212,.07),transparent),
    radial-gradient(ellipse 60% 70% at 90% 100%,rgba(139,92,246,.07),transparent),
    radial-gradient(ellipse 40% 40% at 50% 50%,rgba(16,185,129,.03),transparent);
}

/* SIDEBAR */
aside{
  width:240px;min-height:100vh;background:var(--sidebar);
  border-right:1px solid var(--border);padding:1.75rem 1rem;
  position:fixed;top:0;left:0;bottom:0;overflow-y:auto;z-index:30;
  display:flex;flex-direction:column;
}
.logo{margin-bottom:2rem;padding:.75rem 1rem;
  background:linear-gradient(135deg,rgba(6,182,212,.1),rgba(139,92,246,.1));
  border:1px solid rgba(6,182,212,.15);border-radius:12px;}
.logo-title{font-family:var(--display);font-weight:800;font-size:1.25rem;
  background:linear-gradient(135deg,#06b6d4,#8b5cf6);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-.5px;}
.logo-sub{font-size:.7rem;color:var(--muted);margin-top:.2rem;letter-spacing:.3px;}
.nav-section{font-size:.65rem;font-weight:700;text-transform:uppercase;
  letter-spacing:1.2px;color:var(--muted);padding:.5rem .75rem;margin-top:.5rem;}
.nav-item{
  display:flex;align-items:center;gap:.6rem;padding:.65rem .85rem;
  border-radius:10px;cursor:pointer;color:var(--muted);font-size:.83rem;
  font-weight:500;transition:all .2s;user-select:none;margin-bottom:2px;
}
.nav-item:hover{background:rgba(6,182,212,.08);color:var(--text);}
.nav-item.active{
  background:linear-gradient(135deg,rgba(6,182,212,.15),rgba(139,92,246,.1));
  color:var(--accent);border-left:3px solid var(--accent);font-weight:600;
}
.nav-icon{font-size:1rem;width:20px;text-align:center;}

/* MAIN */
main{margin-left:240px;flex:1;padding:2rem 2.5rem;position:relative;z-index:1;max-width:1400px;}

/* HEADER */
.page-header{
  display:flex;justify-content:space-between;align-items:flex-start;
  margin-bottom:1.75rem;padding-bottom:1.5rem;
  border-bottom:1px solid var(--border);
}
.page-title{font-family:var(--display);font-weight:800;font-size:1.9rem;
  letter-spacing:-1px;
  background:linear-gradient(to right,#f8fafc 40%,#94a3b8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.page-sub{color:var(--muted);margin-top:.3rem;font-size:.85rem;}
.date-badge{
  font-size:.75rem;color:var(--muted);white-space:nowrap;
  background:rgba(15,23,42,.8);border:1px solid var(--border);
  padding:.35rem .85rem;border-radius:20px;margin-top:.25rem;
}

/* KPI GRID */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:1rem;margin-bottom:1.75rem;}
.kpi{
  background:var(--card);backdrop-filter:blur(20px);
  border:1px solid var(--border);border-radius:14px;
  padding:1.25rem 1.35rem;position:relative;overflow:hidden;
  transition:transform .25s,box-shadow .25s;
}
.kpi:hover{transform:translateY(-3px);box-shadow:0 12px 32px -8px rgba(6,182,212,.15);border-color:rgba(6,182,212,.2);}
.kpi::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--c1,#06b6d4),var(--c2,#8b5cf6));
}
.kpi-icon{font-size:1.4rem;margin-bottom:.5rem;}
.kpi-label{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;}
.kpi-value{font-family:var(--display);font-size:1.6rem;font-weight:700;margin-top:.25rem;color:var(--text);}

/* MISSION */
.mission{
  background:linear-gradient(135deg,rgba(6,182,212,.07),rgba(139,92,246,.07));
  border:1px solid rgba(6,182,212,.18);border-radius:16px;
  padding:1.75rem 2rem;margin-bottom:1.75rem;position:relative;overflow:hidden;
}
.mission::after{
  content:'"';position:absolute;right:1.5rem;top:-.5rem;font-size:8rem;
  font-family:Georgia,serif;color:rgba(6,182,212,.06);line-height:1;pointer-events:none;
}
.mission-badge{
  display:inline-flex;align-items:center;gap:.4rem;
  font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;
  color:var(--accent);background:rgba(6,182,212,.1);
  border:1px solid rgba(6,182,212,.2);border-radius:20px;
  padding:.25rem .75rem;margin-bottom:.85rem;
}
.mission-title{font-family:var(--display);font-weight:700;font-size:1.1rem;margin-bottom:.6rem;}
.mission-text{color:#cbd5e1;font-size:.88rem;line-height:1.75;}

/* TABS */
.tab{display:none;animation:fadeUp .3s ease both;}
.tab.active{display:block;}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

/* METRICS TABLE */
.table-card{
  background:var(--card);backdrop-filter:blur(20px);
  border:1px solid var(--border);border-radius:16px;
  padding:1.5rem;margin-bottom:1.5rem;overflow-x:auto;
}
.card-title{
  font-family:var(--display);font-weight:700;font-size:1.05rem;
  border-left:3px solid var(--accent);padding-left:.75rem;margin-bottom:1.25rem;
}
table{width:100%;border-collapse:collapse;}
th{color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.6px;
  padding:.7rem 1rem;border-bottom:1px solid var(--border);text-align:left;font-weight:600;}
td{padding:.85rem 1rem;border-bottom:1px solid rgba(255,255,255,.03);font-size:.87rem;}
tr:last-child td{border-bottom:none;}
tr:hover td{background:rgba(255,255,255,.02);}
.best-row{background:linear-gradient(90deg,rgba(16,185,129,.07),rgba(16,185,129,.02));}
.best-badge{
  background:var(--success);color:#000;font-size:.62rem;font-weight:700;
  padding:.12rem .4rem;border-radius:4px;margin-left:.4rem;vertical-align:middle;
}

/* PLOT GRID */
.plot-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(460px,1fr));gap:1.5rem;margin-top:1.25rem;}
.plot-card{
  background:var(--card);backdrop-filter:blur(20px);
  border:1px solid var(--border);border-radius:16px;
  padding:1.35rem;display:flex;flex-direction:column;gap:.75rem;
  transition:border-color .25s,transform .25s;
}
.plot-card:hover{border-color:rgba(6,182,212,.25);transform:translateY(-2px);}
.plot-title{
  font-family:var(--display);font-weight:600;font-size:.95rem;
  display:flex;align-items:center;gap:.5rem;
}
.plot-title-icon{
  width:28px;height:28px;border-radius:8px;display:grid;place-items:center;font-size:.85rem;
  background:linear-gradient(135deg,rgba(6,182,212,.15),rgba(139,92,246,.15));
  border:1px solid rgba(6,182,212,.1);flex-shrink:0;
}
.plot-desc{color:var(--muted);font-size:.78rem;line-height:1.5;}
.img-wrap{
  border-radius:10px;overflow:hidden;border:1px solid var(--border);
  cursor:zoom-in;position:relative;background:#060c18;
  transition:border-color .25s;
}
.img-wrap:hover{border-color:var(--accent);}
.img-wrap img{width:100%;display:block;transition:transform .35s;}
.img-wrap:hover img{transform:scale(1.02);}
.zoom-label{
  position:absolute;bottom:8px;right:10px;font-size:.68rem;color:var(--muted);
  background:rgba(7,12,24,.8);padding:.15rem .45rem;border-radius:5px;
  opacity:0;transition:opacity .2s;
}
.img-wrap:hover .zoom-label{opacity:1;}

/* MAP */
.map-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.5rem;margin-top:1.25rem;}
.map-frame{width:100%;height:540px;border-radius:10px;overflow:hidden;border:1px solid var(--border);margin-top:1rem;}
.map-frame iframe{width:100%;height:100%;border:none;}

/* MODAL */
.overlay{
  display:none;position:fixed;inset:0;z-index:999;
  background:rgba(7,12,24,.95);backdrop-filter:blur(8px);
  align-items:center;justify-content:center;padding:2rem;
}
.overlay.open{display:flex;}
.overlay img{
  max-width:90vw;max-height:88vh;border-radius:12px;
  border:1px solid var(--border);box-shadow:0 30px 80px -10px rgba(0,0,0,.7);
  animation:zoomIn .25s ease;
}
@keyframes zoomIn{from{transform:scale(.9);opacity:0}to{transform:scale(1);opacity:1}}
.close-btn{
  position:absolute;top:1.25rem;right:1.5rem;font-size:2rem;
  color:var(--muted);cursor:pointer;transition:color .2s;line-height:1;
  background:none;border:none;
}
.close-btn:hover{color:var(--text);}
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
