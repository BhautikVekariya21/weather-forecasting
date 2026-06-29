"""
Generates a highly polished, interactive SaaS-style dark theme HTML dashboard containing all analysis plots, stats cards, and the PM Accelerator mission.
"""
from pathlib import Path
import base64
import json
import datetime

# Define categories and labels for tabbed presentation
SECTION_LABELS = {
    "01": ("Temperature Trend over Time", "Displays the long-term continuous readings across all sampled locations."),
    "02": ("Meteorological Correlation Matrix", "Heatmap of Pearson correlation coefficients between different climate indicators."),
    "03": ("Temperature vs Humidity", "Scatter distribution showing the combined envelope of relative humidity and temperatures."),
    "04": ("Wind Speed Boxplot", "Boxplot outlining the median, quartiles, and range of wind speeds."),
    "08": ("Isolation Forest Anomalies", "Identified climate outlier anomalies highlighted against standard conditions."),
    "09": ("ARIMA Daily Forecast", "Time-series projections using auto-regressive integrated moving averages."),
    "10": ("ML Regressor Comparison", "Comparative evaluation of Ridge, Ensemble, and true temperature values on the test set."),
    "11": ("Ensemble Model Residuals", "Frequency plot of residuals to check prediction distribution properties."),
    "14": ("Regional Temperature Extremes", "Temperature distribution across the top 10 hottest and coldest countries."),
    "17": ("AQI x Meteorological Matrix", "Air quality parameters correlated with temperature, wind, humidity, and visibility."),
    "20": ("Random Forest Importances", "Predictive feature rank weight computed via Random Forest Regressor."),
    "25": ("Hemisphere Seasonal Cycles", "Comparative seasonal temperature waves of the Northern and Southern Hemispheres.")
}

SECTIONS_ORDER = [
    ("📊 Overview", ["01", "10", "11"]),
    ("🔍 Exploratory Analysis", ["02", "03", "04"]),
    ("🚨 Anomaly Detection", ["08"]),
    ("🤖 Forecasting Models", ["09"]),
    ("🌍 Climate & Extremes", ["14", "25"]),
    ("💨 Environmental (AQI)", ["17"]),
    ("🧬 Feature Importance", ["20"])
]

def img_to_b64(path):
    """Encode an image file to a base64 string."""
    try:
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding image {path}: {e}")
        return ""

def generate_html_report(df, metrics_report, plots_dir, reports_dir):
    """Compile the interactive HTML report using base64-embedded plots and a modern dashboard design."""
    print("Compiling interactive HTML dashboard...")
    plots_path = Path(plots_dir)
    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # Calculate values for KPI cards
    total_records = len(df)
    unique_cities = df['location_name'].nunique() if 'location_name' in df.columns else df['country'].nunique() if 'country' in df.columns else 1
    anomalies = df['is_anomaly'].sum() if 'is_anomaly' in df.columns else 0
    anomaly_pct = (anomalies / total_records) * 100 if total_records > 0 else 0
    
    # Identify the best model based on MAE
    best_model_name = "Ensemble"
    best_mae = 9999.0
    for model_name, metrics in metrics_report.items():
        if model_name != 'ARIMA' and metrics.get('MAE', 9999.0) < best_mae:
            best_mae = metrics['MAE']
            best_model_name = model_name

    # Build the HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Weather Trend Forecasting & Climate Analysis Dashboard</title>
    
    <!-- Premium Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-main: #0b0f17;
            --bg-sidebar: #0f172a;
            --bg-card: rgba(30, 41, 59, 0.4);
            --border-card: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-primary: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --font-family: 'Plus Jakarta Sans', sans-serif;
            --font-display: 'Outfit', sans-serif;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: var(--font-family);
            display: flex;
            min-height: 100vh;
            overflow-x: hidden;
        }}

        /* Sidebar Styling */
        aside {{
            width: 280px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-card);
            padding: 2rem 1.5rem;
            display: flex;
            flex-direction: column;
            position: fixed;
            height: 100vh;
            z-index: 10;
        }}

        .logo-area {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 3rem;
        }}

        .logo-text {{
            font-family: var(--font-display);
            font-weight: 800;
            font-size: 1.5rem;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }}

        .nav-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .nav-item {{
            padding: 0.85rem 1.25rem;
            border-radius: 12px;
            cursor: pointer;
            color: var(--text-secondary);
            font-weight: 500;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .nav-item:hover, .nav-item.active {{
            color: var(--text-primary);
            background-color: rgba(56, 189, 248, 0.1);
            box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.2);
        }}

        .nav-item.active {{
            border-left: 3px solid var(--accent-primary);
        }}

        /* Main Content Panel */
        main {{
            flex: 1;
            margin-left: 280px;
            padding: 2.5rem 3rem;
            max-width: 1400px;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--border-card);
            padding-bottom: 1.5rem;
        }}

        h1 {{
            font-family: var(--font-display);
            font-weight: 800;
            font-size: 2.2rem;
            letter-spacing: -1px;
            background: linear-gradient(to right, #f8fafc, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .subtitle {{
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}

        .timestamp {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            background: rgba(30, 41, 59, 0.6);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            border: 1px solid var(--border-card);
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }}

        .kpi-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 1.5rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px -10px var(--accent-glow);
            border-color: rgba(56, 189, 248, 0.3);
        }}

        .kpi-title {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}

        .kpi-value {{
            font-family: var(--font-display);
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .kpi-value.accent {{
            color: var(--accent-primary);
        }}

        .kpi-value.success {{
            color: var(--success);
        }}

        .kpi-value.warning {{
            color: var(--warning);
        }}

        /* Dashboard Tabs Content */
        .tab-content {{
            display: none;
            animation: fadeIn 0.4s ease forwards;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Grid for Plots and Metrics */
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            margin-bottom: 2.5rem;
        }}

        .plot-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-card);
            border-radius: 20px;
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .plot-title {{
            font-family: var(--font-display);
            font-weight: 600;
            font-size: 1.25rem;
            border-left: 3px solid var(--accent-primary);
            padding-left: 0.75rem;
        }}

        .plot-desc {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.4;
        }}

        .plot-img-container {{
            width: 100%;
            background: #161920;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-card);
            cursor: zoom-in;
            transition: border-color 0.3s ease;
        }}

        .plot-img-container:hover {{
            border-color: var(--accent-primary);
        }}

        .plot-img-container img {{
            width: 100%;
            display: block;
            transition: transform 0.3s ease;
        }}

        .plot-img-container img:hover {{
            transform: scale(1.02);
        }}

        /* Model Metrics Table Style */
        .metrics-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2.5rem;
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th {{
            color: var(--text-secondary);
            font-weight: 600;
            padding: 1rem;
            border-bottom: 1px solid var(--border-card);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 1.25rem 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            font-size: 0.95rem;
        }}

        tr:hover td {{
            background: rgba(255,255,255,0.02);
        }}

        .best-row {{
            background: rgba(16, 185, 129, 0.05);
        }}

        .best-badge {{
            background: var(--success);
            color: var(--bg-main);
            font-weight: bold;
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            margin-left: 0.5rem;
        }}

        /* Mission Card styling */
        .mission-card {{
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(129, 140, 248, 0.1) 100%);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 20px;
            padding: 2.5rem;
            margin-bottom: 2.5rem;
            position: relative;
            overflow: hidden;
        }}

        .mission-card::after {{
            content: "PM Accelerator";
            position: absolute;
            right: -20px;
            bottom: -20px;
            font-family: var(--font-display);
            font-size: 6rem;
            font-weight: 800;
            opacity: 0.03;
            pointer-events: none;
        }}

        .mission-title {{
            font-family: var(--font-display);
            font-weight: 700;
            font-size: 1.4rem;
            color: var(--accent-primary);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .mission-quote {{
            font-size: 1.05rem;
            line-height: 1.6;
            color: var(--text-primary);
            font-style: italic;
        }}

        /* Lightbox modal overlay */
        .modal {{
            display: none;
            position: fixed;
            z-index: 100;
            padding-top: 50px;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(11, 15, 23, 0.95);
        }}

        .modal-content {{
            margin: auto;
            display: block;
            max-width: 80%;
            max-height: 80vh;
            border-radius: 12px;
            border: 1px solid var(--border-card);
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
            animation: modalZoom 0.3s ease;
        }}

        @keyframes modalZoom {{
            from {{ transform: scale(0.9); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}

        .close-modal {{
            position: absolute;
            top: 25px;
            right: 35px;
            color: var(--text-secondary);
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
            cursor: pointer;
        }}

        .close-modal:hover {{
            color: var(--text-primary);
        }}

        /* Interactive Folium Section Container */
        .map-section-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2.5rem;
        }}

        .map-frame-wrapper {{
            width: 100%;
            height: 550px;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-card);
        }}

        .map-frame-wrapper iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
    </style>
</head>
<body>

    <!-- Sidebar navigation -->
    <aside>
        <div class="logo-area">
            <span style="font-size: 1.75rem;">🌦️</span>
            <span class="logo-text">WeatherDS</span>
        </div>
        <ul class="nav-list">
            <li class="nav-item active" onclick="switchTab('overview')">📊 Overview</li>
            <li class="nav-item" onclick="switchTab('exploratory')">🔍 Exploratory Analysis</li>
            <li class="nav-item" onclick="switchTab('anomaly')">🚨 Anomaly Detection</li>
            <li class="nav-item" onclick="switchTab('forecasting')">🤖 Forecasting Models</li>
            <li class="nav-item" onclick="switchTab('climate')">🌍 Climate & Extremes</li>
            <li class="nav-item" onclick="switchTab('environmental')">💨 Environmental (AQI)</li>
            <li class="nav-item" onclick="switchTab('feature')">🧬 Feature Importance</li>
            <li class="nav-item" onclick="switchTab('spatial')">📍 Spatial Map</li>
        </ul>
    </aside>

    <!-- Main Workspace -->
    <main>
        <header>
            <div>
                <h1>Global Weather Trend Forecasting</h1>
                <div class="subtitle">Advanced Climate Modeling, Anomaly Flags, and Interactive Prediction Engines</div>
            </div>
            <div class="timestamp">Generated: {datetime.date.today().strftime('%B %d, %Y')}</div>
        </header>

        <!-- KPI Metrics Ribbon -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Samples Processed</div>
                <div class="kpi-value accent">{total_records:,}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Active Monitoring Cities</div>
                <div class="kpi-value">{unique_cities}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Outliers Flagged (Isolation Forest)</div>
                <div class="kpi-value warning">{anomalies:,} ({anomaly_pct:.2f}%)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Best Forecasting Model</div>
                <div class="kpi-value success">{best_model_name}</div>
            </div>
        </section>

        <!-- PM Accelerator Mission Segment -->
        <section class="mission-card">
            <div class="mission-title">
                <span>🎯</span> PM Accelerator Mission Statement
            </div>
            <p class="mission-quote">
                "PM Accelerator is on a mission to unlock the world's PM talent by providing the most accessible, community-driven, and outcome-focused product management education. We help aspiring and experienced PMs gain the skills, network, and confidence to land their dream PM roles and excel in their careers."
            </p>
        </section>

        <!-- Tab contents compiling sections dynamically -->
"""
    
    # Render all tabs individually
    for tab_label, plot_keys in SECTIONS_ORDER:
        tab_id = tab_label.split(" ")[1].lower().replace("(", "").replace(")", "")
        active_class = "active" if tab_id == "overview" else ""
        
        html_content += f"""
        <div id="tab-{tab_id}" class="tab-content {active_class}">
        """
        
        # If it is Overview, render the Metrics evaluation table first
        if tab_id == "overview":
            html_content += f"""
            <div class="metrics-card">
                <div class="plot-title" style="margin-bottom: 1.5rem;">Forecasting Model Evaluation Performance</div>
                <table>
                    <thead>
                        <tr>
                            <th>Model Description</th>
                            <th>MAE (°C)</th>
                            <th>RMSE (°C)</th>
                            <th>R² Score</th>
                            <th>MAPE (%)</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for model_name, metrics in sorted(metrics_report.items(), key=lambda x: x[1].get('MAE', 999.0)):
                is_best = (model_name == best_model_name)
                row_class = 'class="best-row"' if is_best else ""
                badge = '<span class="best-badge">BEST ML</span>' if is_best else ""
                
                html_content += f"""
                        <tr {row_class}>
                            <td style="font-weight: 600;">{model_name}{badge}</td>
                            <td>{metrics.get('MAE', 0.0):.4f}</td>
                            <td>{metrics.get('RMSE', 0.0):.4f}</td>
                            <td>{metrics.get('R2', 0.0):.4f}</td>
                            <td>{metrics.get('MAPE', 0.0):.4f}%</td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            </div>
            """

        # Render all images of the section
        html_content += """
            <div class="grid-2">
        """
        
        for k in plot_keys:
            # Find the filename prefix matching the key
            matching_files = list(plots_path.glob(f"{k}_*.png"))
            if matching_files:
                img_path = matching_files[0]
                b64_data = img_to_b64(img_path)
                title, desc = SECTION_LABELS.get(k, (img_path.stem, ""))
                
                html_content += f"""
                <div class="plot-card">
                    <div class="plot-title">{title}</div>
                    <p class="plot-desc">{desc}</p>
                    <div class="plot-img-container" onclick="openLightbox('{b64_data}')">
                        <img src="{b64_data}" alt="{title}">
                    </div>
                </div>
                """
        
        html_content += """
            </div>
        </div>
        """

    # Add the spatial map tab separately containing Folium iframe
    spatial_active_class = ""
    html_content += f"""
        <div id="tab-spatial" class="tab-content {spatial_active_class}">
            <div class="map-section-card">
                <div class="plot-title" style="margin-bottom: 1rem;">📍 Global Average Temperature Spatial Heatmap</div>
                <p class="plot-desc" style="margin-bottom: 1.5rem;">
                    This interactive spatial projection leverages Folium to map unique meteorological stations globally.
                    Warm concentrations identify intense thermal areas, and point markers indicate individual cities with localized metrics.
                </p>
                <div class="map-frame-wrapper">
                    <iframe src="interactive_map.html"></iframe>
                </div>
            </div>
        </div>
    """

    # Add Javascript for Tab Switching and Lightbox
    html_content += """
    </main>

    <!-- Image Lightbox Modal Zoom -->
    <div id="imageModal" class="modal" onclick="closeLightbox()">
        <span class="close-modal" onclick="closeLightbox()">&times;</span>
        <img class="modal-content" id="modalImg">
    </div>

    <script>
        function switchTab(tabId) {
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(c => c.classList.remove('active'));

            // Remove active nav styling
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(n => n.classList.remove('active'));

            // Show selected tab content
            const targetContent = document.getElementById('tab-' + tabId);
            if (targetContent) {
                targetContent.classList.add('active');
            }

            // Find clicked nav item and add active styling
            event.currentTarget.classList.add('active');
        }

        function openLightbox(imgSrc) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImg');
            modal.style.display = "block";
            modalImg.src = imgSrc;
        }

        function closeLightbox() {
            const modal = document.getElementById('imageModal');
            modal.style.display = "none";
        }
    </script>
</body>
</html>
"""
    
    report_file = reports_path / "weather_analysis_report.html"
    with open(report_file, 'w', encoding='utf-8') as fh:
        fh.write(html_content)
        
    print(f"Interactive HTML dashboard compiled successfully at {report_file}!")
