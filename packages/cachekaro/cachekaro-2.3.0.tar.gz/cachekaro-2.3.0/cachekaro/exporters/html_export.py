"""
HTML exporter for CacheKaro.

Produces interactive HTML reports with charts and tables.
"""

from __future__ import annotations

import base64
import html
import json
from datetime import datetime

from cachekaro.exporters.base import Exporter, ExportFormat
from cachekaro.models.scan_result import ScanResult


# Build metadata - do not modify
def _d(x: str) -> str:
    return base64.b64decode(x).decode()


_attr = {
    "n": "TU9ISVQgQkFHUkk=",  # Name
    "u": "aHR0cHM6Ly9naXRodWIuY29tL01vaGl0LUJhZ3Jp",  # Profile URL
    "r": "aHR0cHM6Ly9naXRodWIuY29tL01vaGl0LUJhZ3JpL2NhY2hla2Fybw==",  # Repo URL
    "c": "SW5kaWE=",  # Country
}


class HtmlExporter(Exporter):
    """
    Exports scan results to HTML format.

    Produces a standalone HTML page with:
    - Interactive charts (using Chart.js)
    - Sortable/filterable tables
    - Responsive design
    - Clean minimalist purple theme
    """

    def __init__(self, title: str = "CacheKaro Report", dark_mode: bool = True):
        """
        Initialize the HTML exporter.

        Args:
            title: Page title
            dark_mode: Use dark color scheme (default True)
        """
        self.title = title
        self.dark_mode = dark_mode

    @property
    def format(self) -> ExportFormat:
        return ExportFormat.HTML

    @property
    def file_extension(self) -> str:
        return "html"

    def export(self, result: ScanResult) -> str:
        """Export scan result to HTML format."""
        # Prepare data for charts
        category_data = self._prepare_category_data(result)
        top_items_data = self._prepare_top_items_data(result)

        # Build HTML with pixelated Minecraft-style theme
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(self.title)}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');

        :root {{
            --bg-primary: #1a0a2e;
            --bg-secondary: #2d1b4e;
            --bg-card: #251442;
            --bg-card-hover: #3d2266;
            --purple-primary: #9d4edd;
            --purple-light: #c77dff;
            --purple-dark: #7b2cbf;
            --purple-glow: #e0aaff;
            --text-primary: #f0e6ff;
            --text-secondary: #b8a9c9;
            --text-muted: #7c6f8a;
            --border-light: #5a3d7a;
            --border-dark: #0d0515;
            --success: #39ff14;
            --warning: #ffff00;
            --danger: #ff3131;
            --pixel-size: 4px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            image-rendering: pixelated;
        }}

        body {{
            font-family: 'VT323', monospace;
            background-color: var(--bg-primary);
            background-image:
                linear-gradient(rgba(157, 78, 221, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(157, 78, 221, 0.03) 1px, transparent 1px);
            background-size: 20px 20px;
            color: var(--text-primary);
            line-height: 1.4;
            min-height: 100vh;
            font-size: 18px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 24px;
        }}

        /* Pixel Block Effect */
        .pixel-block {{
            background: var(--bg-card);
            border: var(--pixel-size) solid;
            border-color: var(--border-light) var(--border-dark) var(--border-dark) var(--border-light);
            box-shadow:
                inset calc(var(--pixel-size) * -1) calc(var(--pixel-size) * -1) 0 rgba(0, 0, 0, 0.3),
                inset var(--pixel-size) var(--pixel-size) 0 rgba(255, 255, 255, 0.1),
                0 var(--pixel-size) 0 var(--border-dark),
                var(--pixel-size) 0 0 var(--border-dark),
                var(--pixel-size) var(--pixel-size) 0 var(--border-dark);
        }}

        .pixel-block:hover {{
            background: var(--bg-card-hover);
            box-shadow:
                inset calc(var(--pixel-size) * -1) calc(var(--pixel-size) * -1) 0 rgba(0, 0, 0, 0.3),
                inset var(--pixel-size) var(--pixel-size) 0 rgba(255, 255, 255, 0.15),
                0 var(--pixel-size) 0 var(--border-dark),
                var(--pixel-size) 0 0 var(--border-dark),
                var(--pixel-size) var(--pixel-size) 0 var(--border-dark),
                0 0 20px rgba(199, 125, 255, 0.3);
        }}

        /* Header */
        header {{
            text-align: center;
            margin-bottom: 32px;
            padding: 32px 24px;
        }}

        .logo {{
            font-family: 'Press Start 2P', cursive;
            font-size: 2rem;
            color: var(--purple-light);
            text-shadow:
                4px 4px 0 var(--purple-dark),
                8px 8px 0 var(--border-dark),
                0 0 20px var(--purple-glow);
            margin-bottom: 16px;
            letter-spacing: 2px;
            animation: pixel-glow 2s ease-in-out infinite alternate;
        }}

        @keyframes pixel-glow {{
            0% {{ text-shadow: 4px 4px 0 var(--purple-dark), 8px 8px 0 var(--border-dark), 0 0 10px var(--purple-glow); }}
            100% {{ text-shadow: 4px 4px 0 var(--purple-dark), 8px 8px 0 var(--border-dark), 0 0 30px var(--purple-glow), 0 0 60px var(--purple-primary); }}
        }}

        .tagline {{
            font-family: 'Press Start 2P', cursive;
            font-size: 0.6rem;
            color: var(--text-secondary);
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        .timestamp {{
            margin-top: 16px;
            font-size: 1rem;
            color: var(--text-muted);
        }}

        /* Decorative pixels */
        .pixel-decoration {{
            display: flex;
            justify-content: center;
            gap: 8px;
            margin: 16px 0;
        }}

        .pixel-dot {{
            width: 8px;
            height: 8px;
            background: var(--purple-primary);
            animation: pixel-blink 1s ease-in-out infinite;
        }}

        .pixel-dot:nth-child(2) {{ animation-delay: 0.2s; background: var(--purple-light); }}
        .pixel-dot:nth-child(3) {{ animation-delay: 0.4s; }}
        .pixel-dot:nth-child(4) {{ animation-delay: 0.6s; background: var(--purple-light); }}
        .pixel-dot:nth-child(5) {{ animation-delay: 0.8s; }}

        @keyframes pixel-blink {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.5; transform: scale(0.8); }}
        }}

        /* Grid Layout */
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
            margin-bottom: 24px;
        }}

        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
            .logo {{ font-size: 1.2rem; }}
            .tagline {{ font-size: 0.5rem; }}
        }}

        /* Cards */
        .card {{
            padding: 20px;
        }}

        .card-title {{
            font-family: 'Press Start 2P', cursive;
            font-size: 0.55rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--purple-light);
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 2px dashed var(--border-light);
        }}

        /* Stats */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }}

        .stat {{
            text-align: center;
            padding: 16px 8px;
            background: var(--bg-secondary);
            border: 2px solid var(--border-light);
            border-color: var(--border-dark) var(--border-light) var(--border-light) var(--border-dark);
        }}

        .stat:hover {{
            background: var(--bg-card-hover);
            box-shadow: 0 0 15px rgba(199, 125, 255, 0.4);
        }}

        .stat-value {{
            font-family: 'Press Start 2P', cursive;
            font-size: 0.9rem;
            color: var(--purple-light);
            margin-bottom: 8px;
            text-shadow: 2px 2px 0 var(--border-dark);
        }}

        .stat-value.highlight {{
            color: var(--success);
            text-shadow: 0 0 10px var(--success), 2px 2px 0 #0a3d00;
        }}

        .stat-value.warning {{
            color: var(--warning);
            text-shadow: 0 0 10px var(--warning), 2px 2px 0 #4a4a00;
        }}

        .stat-label {{
            font-family: 'Press Start 2P', cursive;
            font-size: 0.4rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Chart Container */
        .chart-container {{
            position: relative;
            height: 280px;
            padding: 8px;
        }}

        /* Full width card */
        .card-full {{
            grid-column: 1 / -1;
        }}

        /* Table */
        .table-wrapper {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }}

        th, td {{
            padding: 12px 12px;
            text-align: left;
            border-bottom: 2px solid var(--border-dark);
        }}

        th {{
            font-family: 'Press Start 2P', cursive;
            font-size: 0.45rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--purple-light);
            background: var(--bg-secondary);
            cursor: pointer;
            user-select: none;
            border-bottom: 3px solid var(--purple-primary);
        }}

        th:hover {{
            color: var(--purple-glow);
            text-shadow: 0 0 10px var(--purple-glow);
        }}

        tr {{
            transition: all 0.1s ease;
        }}

        tr:hover {{
            background: var(--bg-secondary);
            box-shadow: inset 4px 0 0 var(--purple-primary);
        }}

        td {{
            font-size: 1rem;
        }}

        /* Size colors */
        .size-large {{
            color: var(--purple-light);
            font-weight: bold;
            text-shadow: 0 0 8px var(--purple-glow);
        }}

        .size-medium {{
            color: var(--warning);
        }}

        .size-small {{
            color: var(--text-secondary);
        }}

        /* Risk badges - Pixel style */
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            font-family: 'Press Start 2P', cursive;
            font-size: 0.4rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 2px solid;
            border-color: rgba(255,255,255,0.3) rgba(0,0,0,0.5) rgba(0,0,0,0.5) rgba(255,255,255,0.3);
        }}

        .badge-safe {{
            background: #0a3d00;
            color: var(--success);
            box-shadow: 0 0 8px rgba(57, 255, 20, 0.3);
        }}

        .badge-moderate {{
            background: #4a4a00;
            color: var(--warning);
            box-shadow: 0 0 8px rgba(255, 255, 0, 0.3);
        }}

        .badge-caution {{
            background: #4a0000;
            color: var(--danger);
            box-shadow: 0 0 8px rgba(255, 49, 49, 0.3);
        }}

        /* Search box */
        .search-box {{
            width: 100%;
            padding: 12px 16px;
            margin-bottom: 20px;
            border: 3px solid;
            border-color: var(--border-dark) var(--border-light) var(--border-light) var(--border-dark);
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-family: 'VT323', monospace;
            font-size: 1.1rem;
        }}

        .search-box:focus {{
            outline: none;
            border-color: var(--purple-primary);
            box-shadow: 0 0 15px rgba(157, 78, 221, 0.5);
        }}

        .search-box::placeholder {{
            color: var(--text-muted);
        }}

        /* Footer */
        footer {{
            text-align: center;
            margin-top: 48px;
            padding: 24px;
        }}

        footer p {{
            font-size: 1rem;
            color: var(--text-muted);
            margin: 8px 0;
        }}

        footer a {{
            color: var(--purple-light);
            text-decoration: none;
        }}

        footer a:hover {{
            color: var(--purple-glow);
            text-shadow: 0 0 10px var(--purple-glow);
        }}

        .footer-pixel {{
            font-family: 'Press Start 2P', cursive;
            font-size: 0.5rem;
            color: var(--purple-primary);
        }}

        /* Pixel Scrollbar */
        ::-webkit-scrollbar {{
            width: 12px;
            height: 12px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--bg-primary);
            border: 2px solid var(--border-dark);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--purple-dark);
            border: 2px solid;
            border-color: var(--purple-light) var(--border-dark) var(--border-dark) var(--purple-light);
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--purple-primary);
        }}

        /* Corner decorations */
        .corner-decoration {{
            position: fixed;
            width: 40px;
            height: 40px;
            opacity: 0.3;
        }}

        .corner-tl {{ top: 20px; left: 20px; border-top: 4px solid var(--purple-primary); border-left: 4px solid var(--purple-primary); }}
        .corner-tr {{ top: 20px; right: 20px; border-top: 4px solid var(--purple-primary); border-right: 4px solid var(--purple-primary); }}
        .corner-bl {{ bottom: 20px; left: 20px; border-bottom: 4px solid var(--purple-primary); border-left: 4px solid var(--purple-primary); }}
        .corner-br {{ bottom: 20px; right: 20px; border-bottom: 4px solid var(--purple-primary); border-right: 4px solid var(--purple-primary); }}

        /* Pixel Heart */
        .pixel-heart {{
            color: #ff3131;
            font-size: 1rem;
            margin: 0 4px;
            animation: heart-beat 1s ease-in-out infinite;
        }}

        @keyframes heart-beat {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.15); }}
        }}
    </style>
</head>
<body>
    <div class="corner-decoration corner-tl"></div>
    <div class="corner-decoration corner-tr"></div>
    <div class="corner-decoration corner-bl"></div>
    <div class="corner-decoration corner-br"></div>

    <div class="container">
        <header class="pixel-block">
            <div class="logo">CACHEKARO</div>
            <p class="tagline">STORAGE & CACHE ANALYSIS</p>
            <div class="pixel-decoration">
                <div class="pixel-dot"></div>
                <div class="pixel-dot"></div>
                <div class="pixel-dot"></div>
                <div class="pixel-dot"></div>
                <div class="pixel-dot"></div>
            </div>
            <p class="timestamp">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        </header>

        <div class="grid">
            <div class="card pixel-block">
                <h2 class="card-title">[ DISK OVERVIEW ]</h2>
                <div class="stats-grid">
                    <div class="stat">
                        <div class="stat-value">{result.formatted_disk_total}</div>
                        <div class="stat-label">Total</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value warning">{result.formatted_disk_used}</div>
                        <div class="stat-label">Used</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value highlight">{result.formatted_disk_free}</div>
                        <div class="stat-label">Free</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{result.disk_usage_percent:.1f}%</div>
                        <div class="stat-label">Usage</div>
                    </div>
                </div>
            </div>

            <div class="card pixel-block">
                <h2 class="card-title">[ CACHE SUMMARY ]</h2>
                <div class="stats-grid">
                    <div class="stat">
                        <div class="stat-value">{result.formatted_total_size}</div>
                        <div class="stat-label">Total</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value highlight">{result.formatted_cleanable_size}</div>
                        <div class="stat-label">Clean</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{result.total_files:,}</div>
                        <div class="stat-label">Files</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{len(result.items)}</div>
                        <div class="stat-label">Paths</div>
                    </div>
                </div>
            </div>

            <div class="card pixel-block">
                <h2 class="card-title">[ SPACE BY CATEGORY ]</h2>
                <div class="chart-container">
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>

            <div class="card pixel-block">
                <h2 class="card-title">[ TOP CONSUMERS ]</h2>
                <div class="chart-container">
                    <canvas id="topItemsChart"></canvas>
                </div>
            </div>

            <div class="card card-full pixel-block">
                <h2 class="card-title">[ ALL CACHE LOCATIONS ]</h2>
                <input type="text" class="search-box" id="searchBox" placeholder="> Search cache locations...">
                <div class="table-wrapper">
                    <table id="cacheTable">
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)">Name</th>
                                <th onclick="sortTable(1)">Category</th>
                                <th onclick="sortTable(2)">Size</th>
                                <th onclick="sortTable(3)">Files</th>
                                <th onclick="sortTable(4)">Age</th>
                                <th onclick="sortTable(5)">Risk</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._generate_table_rows(result)}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <footer class="pixel-block">
            <p class="footer-pixel">- GENERATED BY -</p>
            <p><a href="{_d(_attr['r'])}"><strong>CACHEKARO</strong></a> - Clean It Up!</p>
            <p style="margin-top: 16px;">Made in India with <span class="pixel-heart">❤</span> by <a href="{_d(_attr['u'])}">{_d(_attr['n'])}</a></p>
            <p style="margin-top: 12px;">Star on <a href="{_d(_attr['r'])}">GitHub</a> if you found this useful!</p>
        </footer>
    </div>

    <script>
        // Pixel color palette (purple theme)
        const colors = [
            '#9d4edd', '#c77dff', '#e0aaff', '#7b2cbf',
            '#5a189a', '#3c096c', '#240046', '#10002b',
            '#39ff14', '#ffff00'
        ];

        // Category Doughnut Chart - Pixel style
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(category_data['labels'])},
                datasets: [{{
                    data: {json.dumps(category_data['values'])},
                    backgroundColor: colors,
                    borderColor: '#1a0a2e',
                    borderWidth: 3,
                    hoverBorderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            color: '#b8a9c9',
                            font: {{
                                family: "'VT323', monospace",
                                size: 14
                            }},
                            padding: 10,
                            usePointStyle: true,
                            pointStyle: 'rect'
                        }}
                    }}
                }}
            }}
        }});

        // Top Items Bar Chart - Pixel style
        const topCtx = document.getElementById('topItemsChart').getContext('2d');
        new Chart(topCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(top_items_data['labels'])},
                datasets: [{{
                    data: {json.dumps(top_items_data['values'])},
                    backgroundColor: '#9d4edd',
                    borderColor: '#c77dff',
                    borderWidth: 2,
                    borderRadius: 0,
                    borderSkipped: false
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        grid: {{
                            color: '#3d2266',
                            lineWidth: 1
                        }},
                        ticks: {{
                            color: '#7c6f8a',
                            font: {{
                                family: "'VT323', monospace",
                                size: 14
                            }}
                        }}
                    }},
                    y: {{
                        grid: {{
                            display: false
                        }},
                        ticks: {{
                            color: '#b8a9c9',
                            font: {{
                                family: "'VT323', monospace",
                                size: 14
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Table sorting
        let sortDirection = {{}};
        function sortTable(columnIndex) {{
            const table = document.getElementById('cacheTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));

            sortDirection[columnIndex] = !sortDirection[columnIndex];
            const direction = sortDirection[columnIndex] ? 1 : -1;

            rows.sort((a, b) => {{
                let aValue = a.cells[columnIndex].textContent;
                let bValue = b.cells[columnIndex].textContent;

                if (columnIndex === 2 || columnIndex === 3 || columnIndex === 4) {{
                    aValue = parseFloat(aValue.replace(/[^0-9.-]/g, '')) || 0;
                    bValue = parseFloat(bValue.replace(/[^0-9.-]/g, '')) || 0;
                    return (aValue - bValue) * direction;
                }}

                return aValue.localeCompare(bValue) * direction;
            }});

            rows.forEach(row => tbody.appendChild(row));
        }}

        // Search filtering
        document.getElementById('searchBox').addEventListener('input', function() {{
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#cacheTable tbody tr');

            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            }});
        }});
    </script>
</body>
</html>"""

        return html_content

    def _prepare_category_data(self, result: ScanResult) -> dict:
        """Prepare data for category pie chart."""
        summaries = result.get_category_summaries()
        sorted_summaries = sorted(
            summaries.values(),
            key=lambda x: x.total_size,
            reverse=True
        )

        labels = []
        values = []
        for summary in sorted_summaries[:10]:  # Top 10 categories
            name = summary.category.value.replace("_", " ").title()
            labels.append(name)
            values.append(round(summary.total_size / (1024 * 1024), 2))  # MB

        return {"labels": labels, "values": values}

    def _prepare_top_items_data(self, result: ScanResult) -> dict:
        """Prepare data for top items bar chart."""
        top_items = result.get_top_items(8)

        labels = []
        values = []
        for item in top_items:
            labels.append(item.name[:25])  # Truncate long names
            values.append(round(item.size_bytes / (1024 * 1024), 2))  # MB

        return {"labels": labels, "values": values}

    def _generate_table_rows(self, result: ScanResult) -> str:
        """Generate HTML table rows for all items."""
        rows = []
        for item in sorted(result.items, key=lambda x: x.size_bytes, reverse=True):
            size_class = "size-large" if item.size_bytes > 100 * 1024 * 1024 else (
                "size-medium" if item.size_bytes > 10 * 1024 * 1024 else "size-small"
            )
            risk_class = f"badge-{item.risk_level.value}"

            rows.append(f"""
                <tr>
                    <td>{html.escape(item.name)}</td>
                    <td>{item.category.value.replace('_', ' ').title()}</td>
                    <td class="{size_class}">{item.formatted_size}</td>
                    <td>{item.file_count:,}</td>
                    <td>{item.age_days}d</td>
                    <td><span class="badge {risk_class}">{item.risk_level.value}</span></td>
                </tr>
            """)

        return "\n".join(rows)
