"""Report Generator - Generate formatted reports from budget data.

Creates human-readable reports, summaries, and visualizations data
from analyzed budget files.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer, BudgetSummary


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    include_category_breakdown: bool = True
    include_trends: bool = True
    include_alerts: bool = True
    include_recommendations: bool = True
    trend_months: int = 6


class ReportGenerator:
    """Generate formatted reports from budget analysis.

    Creates text reports, markdown reports, and data structures
    suitable for visualization.
    """

    def __init__(
        self,
        ods_path: Path | str,
        config: ReportConfig | None = None,
    ) -> None:
        """Initialize report generator.

        Args:
            ods_path: Path to ODS budget file.
            config: Report configuration options.
        """
        self.analyzer = BudgetAnalyzer(ods_path)
        self.config = config or ReportConfig()

    def generate_text_report(self) -> str:
        """Generate a plain text budget report.

        Returns:
            Formatted text report.
        """
        summary = self.analyzer.get_summary()
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append(f"BUDGET REPORT - {datetime.now().strftime('%B %Y')}")
        lines.append("=" * 60)
        lines.append("")

        # Overall summary
        lines.append("OVERALL SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Budget:    ${summary.total_budget:>12,.2f}")
        lines.append(f"Total Spent:     ${summary.total_spent:>12,.2f}")
        lines.append(f"Remaining:       ${summary.total_remaining:>12,.2f}")
        lines.append(f"Budget Used:     {summary.percent_used:>12.1f}%")
        lines.append("")

        # Alerts
        if self.config.include_alerts and summary.alerts:
            lines.append("ALERTS")
            lines.append("-" * 40)
            for alert in summary.alerts:
                lines.append(f"  ! {alert}")
            lines.append("")

        # Category breakdown
        if self.config.include_category_breakdown:
            lines.append("CATEGORY BREAKDOWN")
            lines.append("-" * 40)
            lines.append(
                f"{'Category':<20} {'Budget':>10} {'Actual':>10} {'Remain':>10} {'%':>6}"
            )
            lines.append("-" * 60)
            for cat in summary.categories:
                status = "*" if cat.percent_used >= 90 else " "
                lines.append(
                    f"{cat.category:<20} ${cat.budget:>9,.0f} ${cat.actual:>9,.0f} "
                    f"${cat.remaining:>9,.0f} {cat.percent_used:>5.0f}%{status}"
                )
            lines.append("")

        # Top spending
        lines.append("TOP SPENDING CATEGORIES")
        lines.append("-" * 40)
        for i, (cat_name, amount) in enumerate(summary.top_categories, 1):
            lines.append(f"  {i}. {cat_name:<20} ${amount:>10,.2f}")
        lines.append("")

        # Daily average
        daily_avg = self.analyzer.get_daily_average()
        lines.append("SPENDING METRICS")
        lines.append("-" * 40)
        lines.append(f"Daily Average:   ${daily_avg:>12,.2f}")
        lines.append("")

        # Recommendations
        if self.config.include_recommendations:
            recs = self._generate_recommendations(summary)
            if recs:
                lines.append("RECOMMENDATIONS")
                lines.append("-" * 40)
                for rec in recs:
                    lines.append(f"  - {rec}")
                lines.append("")

        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        return "\n".join(lines)

    def generate_markdown_report(self) -> str:
        """Generate a Markdown formatted budget report.

        Returns:
            Markdown formatted report.
        """
        summary = self.analyzer.get_summary()
        lines = []

        # Header
        lines.append(f"# Budget Report - {datetime.now().strftime('%B %Y')}")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append("")

        # Summary table
        lines.append("## Summary")
        lines.append("")
        lines.append("| Metric | Amount |")
        lines.append("|--------|--------|")
        lines.append(f"| Total Budget | ${summary.total_budget:,.2f} |")
        lines.append(f"| Total Spent | ${summary.total_spent:,.2f} |")
        lines.append(f"| Remaining | ${summary.total_remaining:,.2f} |")
        lines.append(f"| Budget Used | {summary.percent_used:.1f}% |")
        lines.append("")

        # Alerts
        if self.config.include_alerts and summary.alerts:
            lines.append("## Alerts")
            lines.append("")
            for alert in summary.alerts:
                lines.append(f"- {alert}")
            lines.append("")

        # Category breakdown
        if self.config.include_category_breakdown:
            lines.append("## Category Breakdown")
            lines.append("")
            lines.append("| Category | Budget | Actual | Remaining | % Used |")
            lines.append("|----------|--------|--------|-----------|--------|")
            for cat in summary.categories:
                status = " **" if cat.percent_used >= 90 else ""
                end_status = "**" if cat.percent_used >= 90 else ""
                lines.append(
                    f"| {status}{cat.category}{end_status} | ${cat.budget:,.0f} | "
                    f"${cat.actual:,.0f} | ${cat.remaining:,.0f} | "
                    f"{cat.percent_used:.0f}% |"
                )
            lines.append("")

        # Top spending
        lines.append("## Top Spending")
        lines.append("")
        for i, (cat_name, amount) in enumerate(summary.top_categories, 1):
            lines.append(f"{i}. **{cat_name}**: ${amount:,.2f}")
        lines.append("")

        # Recommendations
        if self.config.include_recommendations:
            recs = self._generate_recommendations(summary)
            if recs:
                lines.append("## Recommendations")
                lines.append("")
                for rec in recs:
                    lines.append(f"- {rec}")
                lines.append("")

        return "\n".join(lines)

    def generate_visualization_data(self) -> dict[str, Any]:
        """Generate data suitable for chart visualization.

        Returns:
            Dictionary with data formatted for common chart libraries.
        """
        summary = self.analyzer.get_summary()
        breakdown = self.analyzer.get_category_breakdown()

        return {
            "pie_chart": {
                "title": "Spending by Category",
                "labels": list(breakdown.keys()),
                "values": [float(v) for v in breakdown.values()],
            },
            "bar_chart": {
                "title": "Budget vs Actual",
                "categories": [c.category for c in summary.categories],
                "budget": [float(c.budget) for c in summary.categories],
                "actual": [float(c.actual) for c in summary.categories],
            },
            "gauge": {
                "title": "Budget Used",
                "value": summary.percent_used,
                "max": 100,
            },
            "summary": {
                "total_budget": float(summary.total_budget),
                "total_spent": float(summary.total_spent),
                "total_remaining": float(summary.total_remaining),
                "percent_used": summary.percent_used,
            },
        }

    def _generate_recommendations(self, summary: BudgetSummary) -> list[str]:
        """Generate spending recommendations based on analysis."""
        recommendations = []

        # Overall spending check
        if summary.percent_used > 100:
            overage = summary.total_spent - summary.total_budget
            recommendations.append(
                f"You are ${overage:,.2f} over budget. Review all categories "
                "for potential cuts."
            )
        elif summary.percent_used > 90:
            recommendations.append(
                "Budget is nearly exhausted. Limit non-essential spending."
            )

        # Category-specific recommendations
        over_budget = [c for c in summary.categories if c.percent_used >= 100]
        near_budget = [c for c in summary.categories if 90 <= c.percent_used < 100]

        for cat in over_budget:
            recommendations.append(
                f"Reduce {cat.category} spending - over budget by "
                f"${abs(cat.remaining):,.2f}"
            )

        for cat in near_budget:
            recommendations.append(
                f"Monitor {cat.category} - at {cat.percent_used:.0f}% of budget"
            )

        # Savings recommendation
        savings_cats = [
            c
            for c in summary.categories
            if c.category == "Savings" and c.actual < c.budget
        ]
        if savings_cats:
            gap = savings_cats[0].budget - savings_cats[0].actual
            recommendations.append(
                f"Savings goal not met - contribute ${gap:,.2f} to reach target"
            )

        # Top spending insight
        if summary.top_categories:
            top_cat, top_amt = summary.top_categories[0]
            pct_of_total = (
                float(top_amt) / float(summary.total_spent) * 100
                if summary.total_spent
                else 0
            )
            if pct_of_total > 30:
                recommendations.append(
                    f"{top_cat} is {pct_of_total:.0f}% of total spending - "
                    "consider if this aligns with priorities"
                )

        return recommendations

    def save_report(
        self,
        output_path: Path | str,
        format: str = "markdown",
    ) -> Path:
        """Save report to file.

        Args:
            output_path: Path to save the report.
            format: Report format ('text', 'markdown', 'json').

        Returns:
            Path to the saved file.
        """
        output_path = Path(output_path)

        if format == "text":
            content = self.generate_text_report()
        elif format == "markdown":
            content = self.generate_markdown_report()
        elif format == "json":
            import json

            content = json.dumps(self.generate_visualization_data(), indent=2)
        else:
            raise ValueError(f"Unknown format: {format}")

        output_path.write_text(content)
        return output_path


def generate_monthly_report(
    ods_path: Path | str,
    output_dir: Path | str | None = None,
    format: str = "markdown",
) -> str | Path:
    """Convenience function to generate a monthly report.

    Args:
        ods_path: Path to ODS budget file.
        output_dir: Directory to save report (if None, returns string).
        format: Report format.

    Returns:
        Report content (str) or path to saved file (Path).
    """
    generator = ReportGenerator(ods_path)

    if output_dir is None:
        if format == "text":
            return generator.generate_text_report()
        elif format == "markdown":
            return generator.generate_markdown_report()
        else:
            import json

            return json.dumps(generator.generate_visualization_data(), indent=2)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    today = date.today()
    ext = {"text": ".txt", "markdown": ".md", "json": ".json"}.get(format, ".txt")
    filename = f"budget_report_{today.strftime('%Y_%m')}{ext}"

    return generator.save_report(output_dir / filename, format=format)
