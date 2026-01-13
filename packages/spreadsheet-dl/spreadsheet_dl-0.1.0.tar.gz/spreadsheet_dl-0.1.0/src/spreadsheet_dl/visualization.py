"""Interactive Visualization Module.

Provides interactive charts and dashboards for budget visualization:
- Pie charts for category breakdown
- Bar charts for spending trends
- Line charts for budget tracking over time
- Drill-down by category
- HTML dashboard with embedded charts
- Static image export

"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


class ChartType(Enum):
    """Types of charts available."""

    PIE = "pie"
    BAR = "bar"
    LINE = "line"
    DOUGHNUT = "doughnut"
    STACKED_BAR = "stacked_bar"
    AREA = "area"
    HORIZONTAL_BAR = "horizontal_bar"


@dataclass
class ChartDataPoint:
    """Single data point for charts."""

    label: str
    value: float
    color: str | None = None
    category: str | None = None


@dataclass
class ChartSeries:
    """Series of data for multi-series charts."""

    name: str
    data: list[float]
    color: str | None = None


@dataclass
class ChartConfig:
    """Configuration for chart generation."""

    title: str
    chart_type: ChartType
    width: int = 600
    height: int = 400
    show_legend: bool = True
    show_labels: bool = True
    animation: bool = True
    responsive: bool = True
    colors: list[str] | None = None

    # Chart-specific options
    cutout: int = 0  # For doughnut charts (percentage)
    stacked: bool = False  # For bar charts
    tension: float = 0.0  # For line charts (0 = straight, 0.4 = curved)


# Default color palette
DEFAULT_COLORS = [
    "#4e79a7",  # Blue
    "#f28e2b",  # Orange
    "#e15759",  # Red
    "#76b7b2",  # Teal
    "#59a14f",  # Green
    "#edc948",  # Yellow
    "#b07aa1",  # Purple
    "#ff9da7",  # Pink
    "#9c755f",  # Brown
    "#bab0ac",  # Gray
    "#86bcb6",  # Light teal
    "#8cd17d",  # Light green
    "#b6992d",  # Gold
    "#499894",  # Dark teal
    "#d4a6c8",  # Light purple
]

# Category-specific colors (matching common budget categories)
CATEGORY_COLORS = {
    "Housing": "#2c3e50",
    "Utilities": "#3498db",
    "Groceries": "#27ae60",
    "Transportation": "#e67e22",
    "Healthcare": "#e74c3c",
    "Insurance": "#9b59b6",
    "Entertainment": "#f39c12",
    "Dining Out": "#1abc9c",
    "Clothing": "#d35400",
    "Personal Care": "#c0392b",
    "Education": "#2980b9",
    "Savings": "#16a085",
    "Debt Payment": "#8e44ad",
    "Gifts": "#f1c40f",
    "Subscriptions": "#34495e",
    "Miscellaneous": "#7f8c8d",
}


class ChartGenerator:
    """Generate interactive charts using Chart.js.

    Creates HTML with embedded JavaScript for interactive charts
    that can be viewed in any modern browser.

    Example:
        ```python
        generator = ChartGenerator()

        # Create pie chart
        data = [
            ChartDataPoint("Food", 500, "#27ae60"),
            ChartDataPoint("Housing", 1500, "#2c3e50"),
            ChartDataPoint("Transport", 300, "#e67e22"),
        ]

        html = generator.create_pie_chart(
            data,
            ChartConfig(title="Monthly Spending")
        )

        # Save to file
        with open("chart.html", "w") as f:
            f.write(html)
        ```
    """

    # Chart.js CDN URL
    CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"

    def __init__(
        self,
        theme: str = "default",
        colors: list[str] | None = None,
    ) -> None:
        """Initialize chart generator.

        Args:
            theme: Color theme (default, dark, colorful).
            colors: Custom color palette.
        """
        self.theme = theme
        self.colors = colors or DEFAULT_COLORS

    def _get_color(self, index: int, category: str | None = None) -> str:
        """Get color for a data point."""
        if category and category in CATEGORY_COLORS:
            return CATEGORY_COLORS[category]
        return self.colors[index % len(self.colors)]

    def _create_html_wrapper(
        self,
        chart_js: str,
        config: ChartConfig,
        include_cdn: bool = True,
    ) -> str:
        """Create HTML wrapper for a chart."""
        cdn_script = (
            f'<script src="{self.CHARTJS_CDN}"></script>' if include_cdn else ""
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(config.title)}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: {self._get_background_color()};
            color: {self._get_text_color()};
        }}
        .chart-container {{
            position: relative;
            width: {config.width}px;
            height: {config.height}px;
            margin: 0 auto;
            background: {self._get_card_background()};
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            margin-bottom: 20px;
            font-weight: 500;
        }}
    </style>
    {cdn_script}
</head>
<body>
    <h1>{html.escape(config.title)}</h1>
    <div class="chart-container">
        <canvas id="chart"></canvas>
    </div>
    <script>
    {chart_js}
    </script>
</body>
</html>"""

    def _get_background_color(self) -> str:
        """Get background color for theme."""
        if self.theme == "dark":
            return "#1a1a2e"
        return "#f5f5f5"

    def _get_text_color(self) -> str:
        """Get text color for theme."""
        if self.theme == "dark":
            return "#eee"
        return "#333"

    def _get_card_background(self) -> str:
        """Get card background color for theme."""
        if self.theme == "dark":
            return "#16213e"
        return "#fff"

    def create_pie_chart(
        self,
        data: Sequence[ChartDataPoint],
        config: ChartConfig | None = None,
    ) -> str:
        """Create a pie chart.

        Args:
            data: List of data points.
            config: Chart configuration.

        Returns:
            Complete HTML string.
        """
        if config is None:
            config = ChartConfig(title="Pie Chart", chart_type=ChartType.PIE)

        labels = [d.label for d in data]
        values = [d.value for d in data]
        colors = [d.color or self._get_color(i, d.category) for i, d in enumerate(data)]

        chart_type = "doughnut" if config.cutout > 0 else "pie"
        cutout_option = f"cutout: '{config.cutout}%'," if config.cutout > 0 else ""

        chart_js = f"""
const ctx = document.getElementById('chart').getContext('2d');
new Chart(ctx, {{
    type: '{chart_type}',
    data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
            data: {json.dumps(values)},
            backgroundColor: {json.dumps(colors)},
            borderWidth: 2,
            borderColor: '{self._get_card_background()}'
        }}]
    }},
    options: {{
        responsive: {str(config.responsive).lower()},
        animation: {{ animateRotate: {str(config.animation).lower()} }},
        {cutout_option}
        plugins: {{
            legend: {{
                display: {str(config.show_legend).lower()},
                position: 'right'
            }},
            tooltip: {{
                callbacks: {{
                    label: function(context) {{
                        const value = context.parsed;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${{value.toLocaleString('en-US', {{style: 'currency', currency: 'USD'}})}} (${{percentage}}%)`;
                    }}
                }}
            }}
        }}
    }}
}});
"""
        return self._create_html_wrapper(chart_js, config)

    def create_bar_chart(
        self,
        data: Sequence[ChartDataPoint],
        config: ChartConfig | None = None,
    ) -> str:
        """Create a bar chart.

        Args:
            data: List of data points.
            config: Chart configuration.

        Returns:
            Complete HTML string.
        """
        if config is None:
            config = ChartConfig(title="Bar Chart", chart_type=ChartType.BAR)

        labels = [d.label for d in data]
        values = [d.value for d in data]
        colors = [d.color or self._get_color(i, d.category) for i, d in enumerate(data)]

        index_axis = "'y'" if config.chart_type == ChartType.HORIZONTAL_BAR else "'x'"

        chart_js = f"""
const ctx = document.getElementById('chart').getContext('2d');
new Chart(ctx, {{
    type: 'bar',
    data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
            label: '{config.title}',
            data: {json.dumps(values)},
            backgroundColor: {json.dumps(colors)},
            borderRadius: 4
        }}]
    }},
    options: {{
        indexAxis: {index_axis},
        responsive: {str(config.responsive).lower()},
        animation: {{ duration: {1000 if config.animation else 0} }},
        plugins: {{
            legend: {{ display: false }},
            tooltip: {{
                callbacks: {{
                    label: function(context) {{
                        return context.parsed.{("x" if config.chart_type == ChartType.HORIZONTAL_BAR else "y")}.toLocaleString('en-US', {{style: 'currency', currency: 'USD'}});
                    }}
                }}
            }}
        }},
        scales: {{
            y: {{
                beginAtZero: true,
                ticks: {{
                    callback: function(value) {{
                        return '$' + value.toLocaleString();
                    }}
                }}
            }}
        }}
    }}
}});
"""
        return self._create_html_wrapper(chart_js, config)

    def create_line_chart(
        self,
        labels: Sequence[str],
        series: Sequence[ChartSeries],
        config: ChartConfig | None = None,
    ) -> str:
        """Create a line chart.

        Args:
            labels: X-axis labels.
            series: Data series.
            config: Chart configuration.

        Returns:
            Complete HTML string.
        """
        if config is None:
            config = ChartConfig(title="Line Chart", chart_type=ChartType.LINE)

        datasets = []
        for i, s in enumerate(series):
            color = s.color or self.colors[i % len(self.colors)]
            datasets.append(
                {
                    "label": s.name,
                    "data": s.data,
                    "borderColor": color,
                    "backgroundColor": f"{color}20",
                    "fill": config.chart_type == ChartType.AREA,
                    "tension": config.tension,
                }
            )

        chart_js = f"""
const ctx = document.getElementById('chart').getContext('2d');
new Chart(ctx, {{
    type: 'line',
    data: {{
        labels: {json.dumps(list(labels))},
        datasets: {json.dumps(datasets)}
    }},
    options: {{
        responsive: {str(config.responsive).lower()},
        animation: {{ duration: {1000 if config.animation else 0} }},
        plugins: {{
            legend: {{
                display: {str(config.show_legend).lower()}
            }},
            tooltip: {{
                mode: 'index',
                intersect: false
            }}
        }},
        scales: {{
            y: {{
                beginAtZero: true,
                ticks: {{
                    callback: function(value) {{
                        return '$' + value.toLocaleString();
                    }}
                }}
            }}
        }},
        interaction: {{
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }}
    }}
}});
"""
        return self._create_html_wrapper(chart_js, config)

    def create_stacked_bar_chart(
        self,
        labels: Sequence[str],
        series: Sequence[ChartSeries],
        config: ChartConfig | None = None,
    ) -> str:
        """Create a stacked bar chart.

        Args:
            labels: X-axis labels.
            series: Data series.
            config: Chart configuration.

        Returns:
            Complete HTML string.
        """
        if config is None:
            config = ChartConfig(
                title="Stacked Bar Chart",
                chart_type=ChartType.STACKED_BAR,
            )

        datasets = []
        for i, s in enumerate(series):
            color = s.color or self.colors[i % len(self.colors)]
            datasets.append(
                {
                    "label": s.name,
                    "data": s.data,
                    "backgroundColor": color,
                }
            )

        chart_js = f"""
const ctx = document.getElementById('chart').getContext('2d');
new Chart(ctx, {{
    type: 'bar',
    data: {{
        labels: {json.dumps(list(labels))},
        datasets: {json.dumps(datasets)}
    }},
    options: {{
        responsive: {str(config.responsive).lower()},
        plugins: {{
            legend: {{
                display: {str(config.show_legend).lower()}
            }}
        }},
        scales: {{
            x: {{ stacked: true }},
            y: {{
                stacked: true,
                beginAtZero: true,
                ticks: {{
                    callback: function(value) {{
                        return '$' + value.toLocaleString();
                    }}
                }}
            }}
        }}
    }}
}});
"""
        return self._create_html_wrapper(chart_js, config)


class DashboardGenerator:
    """Generate interactive HTML dashboards.

    Creates comprehensive budget dashboards with multiple charts,
    summary statistics, and drill-down capability.

    Example:
        ```python
        from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

        analyzer = BudgetAnalyzer("budget.ods")
        generator = DashboardGenerator(analyzer)

        html = generator.generate()

        with open("dashboard.html", "w") as f:
            f.write(html)
        ```
    """

    def __init__(
        self,
        analyzer: Any = None,
        theme: str = "default",
    ) -> None:
        """Initialize dashboard generator.

        Args:
            analyzer: BudgetAnalyzer instance (optional).
            theme: Visual theme (default, dark).
        """
        self.analyzer = analyzer
        self.theme = theme
        self.chart_gen = ChartGenerator(theme=theme)

    def generate(self) -> str:
        """Generate complete dashboard HTML.

        Returns:
            Complete HTML string.
        """
        # Get data from analyzer if available
        if self.analyzer:
            summary = self._get_summary_from_analyzer()
            category_data = self._get_category_data()
            trend_data = self._get_trend_data()
        else:
            # Demo data
            summary = self._demo_summary()
            category_data = self._demo_category_data()
            trend_data = self._demo_trend_data()

        return self._create_dashboard_html(summary, category_data, trend_data)

    def _get_summary_from_analyzer(self) -> dict[str, Any]:
        """Get summary data from analyzer."""
        summary = self.analyzer.get_summary()
        return {
            "total_budget": float(summary.total_budget),
            "total_spent": float(summary.total_spent),
            "total_remaining": float(summary.total_remaining),
            "percent_used": float(summary.percent_used),
        }

    def _get_category_data(self) -> list[ChartDataPoint]:
        """Get category spending data."""
        by_category = self.analyzer.by_category()
        return [
            ChartDataPoint(
                label=cat,
                value=float(amount),
                category=cat,
            )
            for cat, amount in by_category.items()
            if amount > 0
        ]

    def _get_trend_data(self) -> tuple[list[str], list[ChartSeries]]:
        """Get spending trend data from analyzer."""
        if not self.analyzer:
            return self._demo_trend_data()

        # Get monthly trends from analyzer
        trends = self.analyzer.get_monthly_trend(months=6)
        if not trends:
            return [], []

        # Extract period labels
        periods = [t.period for t in trends]

        # Collect all categories across all periods
        all_categories = set()
        for trend in trends:
            all_categories.update(trend.by_category.keys())

        # Create series for each category
        series = []
        for category in sorted(all_categories):
            data = [float(trend.by_category.get(category, 0)) for trend in trends]
            series.append(ChartSeries(name=category, data=data))

        return periods, series

    def _demo_summary(self) -> dict[str, Any]:
        """Generate demo summary data."""
        return {
            "total_budget": 5000.0,
            "total_spent": 3250.0,
            "total_remaining": 1750.0,
            "percent_used": 65.0,
        }

    def _demo_category_data(self) -> list[ChartDataPoint]:
        """Generate demo category data."""
        return [
            ChartDataPoint("Housing", 1500, category="Housing"),
            ChartDataPoint("Groceries", 450, category="Groceries"),
            ChartDataPoint("Transportation", 300, category="Transportation"),
            ChartDataPoint("Utilities", 200, category="Utilities"),
            ChartDataPoint("Entertainment", 150, category="Entertainment"),
            ChartDataPoint("Dining Out", 250, category="Dining Out"),
            ChartDataPoint("Healthcare", 100, category="Healthcare"),
            ChartDataPoint("Other", 300, category="Miscellaneous"),
        ]

    def _demo_trend_data(self) -> tuple[list[str], list[ChartSeries]]:
        """Generate demo trend data."""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        return months, [
            ChartSeries("Budget", [5000, 5000, 5000, 5200, 5200, 5200]),
            ChartSeries("Spent", [4500, 4200, 4800, 4100, 4600, 3250]),
        ]

    def _create_dashboard_html(
        self,
        summary: dict[str, Any],
        category_data: list[ChartDataPoint],
        trend_data: tuple[list[str], list[ChartSeries]],
    ) -> str:
        """Create the complete dashboard HTML."""
        bg_color = "#1a1a2e" if self.theme == "dark" else "#f0f2f5"
        text_color = "#eee" if self.theme == "dark" else "#333"
        card_bg = "#16213e" if self.theme == "dark" else "#fff"
        accent = "#4e79a7"

        # Calculate progress percentage for visual
        pct_used = min(100, max(0, summary["percent_used"]))
        progress_color = (
            "#27ae60" if pct_used < 80 else "#f39c12" if pct_used < 100 else "#e74c3c"
        )

        # Prepare chart data
        labels = [d.label for d in category_data]
        values = [d.value for d in category_data]
        colors = [
            CATEGORY_COLORS.get(
                d.category or d.label, DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
            )
            for i, d in enumerate(category_data)
        ]

        months, series = trend_data

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Budget Dashboard</title>
    <script src="{self.chart_gen.CHARTJS_CDN}"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: {bg_color};
            color: {text_color};
            padding: 20px;
        }}
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .header p {{
            opacity: 0.7;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: {card_bg};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            font-size: 0.875rem;
            text-transform: uppercase;
            opacity: 0.6;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        .card .value {{
            font-size: 1.75rem;
            font-weight: 600;
        }}
        .card.budget .value {{ color: {accent}; }}
        .card.spent .value {{ color: #e74c3c; }}
        .card.remaining .value {{ color: #27ae60; }}
        .progress-card {{
            grid-column: span 2;
        }}
        .progress-bar {{
            height: 12px;
            background: rgba(0,0,0,0.1);
            border-radius: 6px;
            margin-top: 15px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: {progress_color};
            border-radius: 6px;
            width: {pct_used}%;
            transition: width 1s ease;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .chart-card {{
            background: {card_bg};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .chart-card h2 {{
            font-size: 1.125rem;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        .category-list {{
            margin-top: 20px;
        }}
        .category-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(128,128,128,0.2);
        }}
        .category-item:last-child {{
            border-bottom: none;
        }}
        .category-name {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .category-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            opacity: 0.6;
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>Budget Dashboard</h1>
            <p>Financial overview and spending analysis</p>
        </div>

        <div class="summary-cards">
            <div class="card budget">
                <h3>Total Budget</h3>
                <div class="value">${summary["total_budget"]:,.2f}</div>
            </div>
            <div class="card spent">
                <h3>Total Spent</h3>
                <div class="value">${summary["total_spent"]:,.2f}</div>
            </div>
            <div class="card remaining">
                <h3>Remaining</h3>
                <div class="value">${summary["total_remaining"]:,.2f}</div>
            </div>
            <div class="card progress-card">
                <h3>Budget Used</h3>
                <div class="value">{summary["percent_used"]:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h2>Spending by Category</h2>
                <div class="chart-container">
                    <canvas id="pieChart"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <h2>Category Breakdown</h2>
                <div class="chart-container">
                    <canvas id="barChart"></canvas>
                </div>
                <div class="category-list">
                    {
            "".join(
                f'''
                    <div class="category-item">
                        <span class="category-name">
                            <span class="category-dot" style="background: {colors[i]}"></span>
                            {html.escape(d.label)}
                        </span>
                        <span>${d.value:,.2f}</span>
                    </div>
                    '''
                for i, d in enumerate(category_data)
            )
        }
                </div>
            </div>

            {self._create_trend_chart_section(months, series) if months else ""}
        </div>

        <footer>
            Generated by SpreadsheetDL | {date.today().strftime("%B %d, %Y")}
        </footer>
    </div>

    <script>
        // Pie Chart
        new Chart(document.getElementById('pieChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    data: {json.dumps(values)},
                    backgroundColor: {json.dumps(colors)},
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                const v = ctx.parsed;
                                const t = ctx.dataset.data.reduce((a,b) => a+b, 0);
                                return `${{v.toLocaleString('en-US', {{style:'currency', currency:'USD'}})}} (${{((v/t)*100).toFixed(1)}}%)`;
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Bar Chart
        new Chart(document.getElementById('barChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    data: {json.dumps(values)},
                    backgroundColor: {json.dumps(colors)},
                    borderRadius: 4
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
                        beginAtZero: true,
                        ticks: {{
                            callback: v => '$' + v.toLocaleString()
                        }}
                    }}
                }}
            }}
        }});

        {self._create_trend_chart_script(months, series) if months else ""}
    </script>
</body>
</html>"""

    def _create_trend_chart_section(
        self,
        months: list[str],
        series: list[ChartSeries],
    ) -> str:
        """Create trend chart HTML section."""
        return """
            <div class="chart-card" style="grid-column: span 2;">
                <h2>Budget vs Spending Trend</h2>
                <div class="chart-container" style="height: 250px;">
                    <canvas id="trendChart"></canvas>
                </div>
            </div>
        """

    def _create_trend_chart_script(
        self,
        months: list[str],
        series: list[ChartSeries],
    ) -> str:
        """Create trend chart JavaScript."""
        datasets = []
        colors = [DEFAULT_COLORS[0], DEFAULT_COLORS[1]]
        for i, s in enumerate(series):
            datasets.append(
                {
                    "label": s.name,
                    "data": s.data,
                    "borderColor": colors[i],
                    "backgroundColor": f"{colors[i]}20",
                    "fill": i == 1,
                    "tension": 0.3,
                }
            )

        return f"""
        new Chart(document.getElementById('trendChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(months)},
                datasets: {json.dumps(datasets)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: v => '$' + v.toLocaleString()
                        }}
                    }}
                }}
            }}
        }});
        """

    def save(self, output_path: Path | str) -> Path:
        """Generate and save dashboard to file.

        Args:
            output_path: Output file path.

        Returns:
            Path to saved file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html_content = self.generate()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path


# Convenience functions


def create_spending_pie_chart(
    categories: dict[str, float],
    title: str = "Spending by Category",
    output_path: Path | str | None = None,
) -> str:
    """Create a pie chart from category spending data.

    Args:
        categories: Dictionary of category -> amount.
        title: Chart title.
        output_path: Optional path to save HTML file.

    Returns:
        HTML string.
    """
    data = [
        ChartDataPoint(label=cat, value=amount, category=cat)
        for cat, amount in categories.items()
        if amount > 0
    ]

    generator = ChartGenerator()
    config = ChartConfig(title=title, chart_type=ChartType.PIE, cutout=60)
    html_content = generator.create_pie_chart(data, config)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    return html_content


def create_budget_dashboard(
    analyzer: Any = None,
    output_path: Path | str | None = None,
    theme: str = "default",
) -> str:
    """Create a complete budget dashboard.

    Args:
        analyzer: BudgetAnalyzer instance.
        output_path: Optional path to save HTML file.
        theme: Visual theme (default, dark).

    Returns:
        HTML string.
    """
    generator = DashboardGenerator(analyzer=analyzer, theme=theme)
    html_content = generator.generate()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    return html_content
