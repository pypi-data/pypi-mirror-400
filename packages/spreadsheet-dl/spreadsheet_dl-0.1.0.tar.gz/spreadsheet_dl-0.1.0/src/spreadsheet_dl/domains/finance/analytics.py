"""Analytics Dashboard - Advanced budget analytics and visualization data.

Provides trend analysis, forecasting, and insights for budget data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pandas as pd

from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer, BudgetSummary

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class TrendData:
    """Trend data for a metric over time."""

    periods: list[str]
    values: list[float]
    trend_direction: str  # "increasing", "decreasing", "stable"
    change_percent: float
    forecast_next: float | None = None


@dataclass
class CategoryInsight:
    """Insights for a spending category."""

    category: str
    current_spending: Decimal
    budget: Decimal
    percent_used: float
    trend: str  # "increasing", "decreasing", "stable"
    average_transaction: Decimal
    transaction_count: int
    largest_transaction: Decimal
    recommendation: str | None = None


@dataclass
class DashboardData:
    """Complete dashboard data structure."""

    # Summary metrics
    total_budget: float
    total_spent: float
    total_remaining: float
    percent_used: float
    days_remaining: int
    daily_budget_remaining: float

    # Status indicators
    budget_status: str  # "healthy", "caution", "warning", "critical"
    status_message: str

    # Top-level stats
    transaction_count: int
    average_transaction: float
    largest_expense: float
    spending_by_day: dict[str, float]

    # Category data
    categories: list[CategoryInsight]
    top_spending: list[tuple[str, float]]

    # Trend data
    spending_trend: TrendData
    category_trends: dict[str, TrendData]

    # Alerts
    alerts: list[str]
    recommendations: list[str]

    # Visualization data (chart-ready)
    charts: dict[str, Any]


class AnalyticsDashboard:
    """Generate comprehensive analytics dashboard data.

    Provides all data needed for a budget analytics dashboard,
    including trends, insights, and visualization-ready data.
    """

    def __init__(
        self,
        analyzer: BudgetAnalyzer,
        month: int | None = None,
        year: int | None = None,
    ) -> None:
        """Initialize dashboard.

        Args:
            analyzer: Budget analyzer with loaded data.
            month: Target month (defaults to current).
            year: Target year (defaults to current).
        """
        self.analyzer = analyzer
        today = date.today()
        self.month = month or today.month
        self.year = year or today.year
        self._summary: BudgetSummary | None = None

    @property
    def summary(self) -> BudgetSummary:
        """Get budget summary (cached)."""
        if self._summary is None:
            self._summary = self.analyzer.get_summary()
        return self._summary

    def generate_dashboard(self) -> DashboardData:
        """Generate complete dashboard data.

        Returns:
            DashboardData with all analytics.
        """
        summary = self.summary
        expenses = self.analyzer.expenses

        # Calculate days remaining in month
        today = date.today()
        if today.month == self.month and today.year == self.year:
            import calendar

            days_in_month = calendar.monthrange(self.year, self.month)[1]
            days_remaining = days_in_month - today.day + 1
        else:
            days_remaining = 0

        # Daily budget remaining
        daily_budget = (
            float(summary.total_remaining) / days_remaining if days_remaining > 0 else 0
        )

        # Transaction stats
        transaction_count = len(expenses) if not expenses.empty else 0
        avg_transaction = float(expenses["Amount"].mean()) if not expenses.empty else 0
        largest_expense = float(expenses["Amount"].max()) if not expenses.empty else 0

        # Spending by day of week
        spending_by_day = self._calculate_daily_spending(expenses)

        # Category insights
        category_insights = self._generate_category_insights(summary, expenses)

        # Spending trend
        spending_trend = self._calculate_spending_trend(expenses)

        # Category trends
        category_trends = self._calculate_category_trends(expenses)

        # Determine budget status
        budget_status, status_message = self._determine_budget_status(
            summary, days_remaining
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            summary, category_insights, days_remaining
        )

        # Generate chart data
        charts = self._generate_chart_data(summary, expenses, spending_by_day)

        return DashboardData(
            total_budget=float(summary.total_budget),
            total_spent=float(summary.total_spent),
            total_remaining=float(summary.total_remaining),
            percent_used=summary.percent_used,
            days_remaining=days_remaining,
            daily_budget_remaining=daily_budget,
            budget_status=budget_status,
            status_message=status_message,
            transaction_count=transaction_count,
            average_transaction=avg_transaction,
            largest_expense=largest_expense,
            spending_by_day=spending_by_day,
            categories=category_insights,
            top_spending=[(cat, float(amt)) for cat, amt in summary.top_categories],
            spending_trend=spending_trend,
            category_trends=category_trends,
            alerts=summary.alerts,
            recommendations=recommendations,
            charts=charts,
        )

    def _calculate_daily_spending(
        self,
        expenses: pd.DataFrame,
    ) -> dict[str, float]:
        """Calculate spending by day of week."""
        if expenses.empty or "Date" not in expenses.columns:
            return {
                "Monday": 0,
                "Tuesday": 0,
                "Wednesday": 0,
                "Thursday": 0,
                "Friday": 0,
                "Saturday": 0,
                "Sunday": 0,
            }

        expenses = expenses.copy()
        expenses["DayOfWeek"] = expenses["Date"].dt.day_name()
        daily = expenses.groupby("DayOfWeek")["Amount"].sum()

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        return {day: float(daily.get(day, 0)) for day in days}

    def _generate_category_insights(
        self,
        summary: BudgetSummary,
        expenses: pd.DataFrame,
    ) -> list[CategoryInsight]:
        """Generate insights for each category."""
        insights = []

        for cat_spending in summary.categories:
            cat = cat_spending.category
            cat_expenses = (
                expenses[expenses["Category"] == cat]
                if not expenses.empty
                else pd.DataFrame()
            )

            transaction_count = len(cat_expenses)
            avg_transaction = (
                Decimal(str(cat_expenses["Amount"].mean()))
                if not cat_expenses.empty
                else Decimal("0")
            )
            largest = (
                Decimal(str(cat_expenses["Amount"].max()))
                if not cat_expenses.empty
                else Decimal("0")
            )

            # Determine trend (would need historical data for real trend)
            trend = "stable"
            if cat_spending.percent_used > 80:
                trend = "increasing"
            elif cat_spending.percent_used < 30:
                trend = "decreasing"

            # Generate recommendation
            recommendation = None
            if cat_spending.percent_used >= 100:
                recommendation = f"Over budget by ${abs(cat_spending.remaining):.2f}. Review and reduce spending."
            elif cat_spending.percent_used >= 90:
                recommendation = f"Near budget limit. Consider pausing non-essential {cat} purchases."
            elif cat_spending.percent_used < 20 and cat != "Savings":
                recommendation = (
                    "Significantly under budget. Consider reallocating to savings."
                )

            insights.append(
                CategoryInsight(
                    category=cat,
                    current_spending=cat_spending.actual,
                    budget=cat_spending.budget,
                    percent_used=cat_spending.percent_used,
                    trend=trend,
                    average_transaction=avg_transaction,
                    transaction_count=transaction_count,
                    largest_transaction=largest,
                    recommendation=recommendation,
                )
            )

        return insights

    def _calculate_spending_trend(
        self,
        expenses: pd.DataFrame,
    ) -> TrendData:
        """Calculate overall spending trend."""
        if expenses.empty or "Date" not in expenses.columns:
            return TrendData(
                periods=[],
                values=[],
                trend_direction="stable",
                change_percent=0,
            )

        expenses = expenses.copy()
        expenses["Week"] = expenses["Date"].dt.isocalendar().week

        weekly = expenses.groupby("Week")["Amount"].sum()
        periods = [f"Week {w}" for w in weekly.index]
        values = [float(v) for v in weekly.values]

        # Determine trend
        if len(values) >= 2:
            change = (values[-1] - values[0]) / values[0] * 100 if values[0] else 0
            if change > 10:
                direction = "increasing"
            elif change < -10:
                direction = "decreasing"
            else:
                direction = "stable"
        else:
            direction = "stable"
            change = 0

        # Simple forecast (average of last 2 weeks * adjustment)
        forecast = None
        if len(values) >= 2:
            avg = sum(values[-2:]) / 2
            forecast = avg * 1.05 if direction == "increasing" else avg * 0.95

        return TrendData(
            periods=periods,
            values=values,
            trend_direction=direction,
            change_percent=change,
            forecast_next=forecast,
        )

    def _calculate_category_trends(
        self,
        expenses: pd.DataFrame,
    ) -> dict[str, TrendData]:
        """Calculate spending trends per category."""
        trends: dict[str, TrendData] = {}

        if expenses.empty or "Category" not in expenses.columns:
            return trends

        for category in expenses["Category"].unique():
            cat_expenses = expenses[expenses["Category"] == category].copy()
            cat_expenses["Week"] = cat_expenses["Date"].dt.isocalendar().week

            weekly = cat_expenses.groupby("Week")["Amount"].sum()
            periods = [f"Week {w}" for w in weekly.index]
            values = [float(v) for v in weekly.values]

            if len(values) >= 2:
                change = (values[-1] - values[0]) / values[0] * 100 if values[0] else 0
                if change > 15:
                    direction = "increasing"
                elif change < -15:
                    direction = "decreasing"
                else:
                    direction = "stable"
            else:
                direction = "stable"
                change = 0

            trends[category] = TrendData(
                periods=periods,
                values=values,
                trend_direction=direction,
                change_percent=change,
            )

        return trends

    def _determine_budget_status(
        self,
        summary: BudgetSummary,
        days_remaining: int,
    ) -> tuple[str, str]:
        """Determine overall budget health status."""
        pct = summary.percent_used

        if pct >= 100:
            return "critical", "Budget exceeded! Immediate action required."
        elif pct >= 90:
            return (
                "critical",
                f"Budget nearly exhausted with {days_remaining} days remaining.",
            )
        elif pct >= 75:
            return "warning", "Budget trending high. Monitor spending closely."
        else:
            return "healthy", "Budget on track. Good job managing expenses!"

    def _generate_recommendations(
        self,
        summary: BudgetSummary,
        insights: list[CategoryInsight],
        days_remaining: int,
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Overall budget recommendations
        if summary.percent_used > 100:
            overage = summary.total_spent - summary.total_budget
            recommendations.append(
                f"Reduce spending by ${overage:.2f} to get back on budget."
            )
        elif summary.percent_used > 90 and days_remaining > 5:
            daily_limit = float(summary.total_remaining) / days_remaining
            recommendations.append(
                f"Limit daily spending to ${daily_limit:.2f} for remaining {days_remaining} days."
            )

        # Category-specific recommendations
        over_budget = [i for i in insights if i.percent_used >= 100]
        if over_budget:
            cats = ", ".join(i.category for i in over_budget[:3])
            recommendations.append(
                f"Categories over budget: {cats}. Review and adjust."
            )

        # High spenders
        high_spenders = [
            i for i in insights if i.percent_used >= 80 and i.percent_used < 100
        ]
        if high_spenders:
            cats = ", ".join(i.category for i in high_spenders[:3])
            recommendations.append(
                f"Categories nearing limit: {cats}. Consider pausing."
            )

        # Savings check
        savings = next((i for i in insights if i.category == "Savings"), None)
        if savings and savings.current_spending < savings.budget * Decimal("0.5"):
            gap = savings.budget - savings.current_spending
            recommendations.append(
                f"Savings goal gap: ${gap:.2f}. Prioritize contributions."
            )

        return recommendations

    def _generate_chart_data(
        self,
        summary: BudgetSummary,
        expenses: pd.DataFrame,
        spending_by_day: dict[str, float],
    ) -> dict[str, Any]:
        """Generate chart-ready data structures."""
        charts = {}

        # Pie chart - spending by category
        charts["category_pie"] = {
            "labels": [c.category for c in summary.categories if c.actual > 0],
            "values": [float(c.actual) for c in summary.categories if c.actual > 0],
            "title": "Spending by Category",
        }

        # Bar chart - budget vs actual
        charts["budget_vs_actual"] = {
            "categories": [c.category for c in summary.categories],
            "budget": [float(c.budget) for c in summary.categories],
            "actual": [float(c.actual) for c in summary.categories],
            "title": "Budget vs Actual by Category",
        }

        # Gauge - overall budget usage
        charts["budget_gauge"] = {
            "value": summary.percent_used,
            "min": 0,
            "max": 100,
            "thresholds": [
                {"value": 75, "color": "green"},
                {"value": 90, "color": "yellow"},
                {"value": 100, "color": "red"},
            ],
            "title": "Budget Usage",
        }

        # Bar chart - spending by day of week
        charts["daily_spending"] = {
            "days": list(spending_by_day.keys()),
            "amounts": list(spending_by_day.values()),
            "title": "Spending by Day of Week",
        }

        # Line chart - cumulative spending over time
        if not expenses.empty and "Date" in expenses.columns:
            expenses = expenses.copy()
            expenses = expenses.sort_values("Date")
            expenses["Cumulative"] = expenses["Amount"].cumsum()
            charts["cumulative_spending"] = {
                "dates": [d.strftime("%Y-%m-%d") for d in expenses["Date"]],
                "values": [float(v) for v in expenses["Cumulative"]],
                "title": "Cumulative Spending Over Time",
            }
        else:
            charts["cumulative_spending"] = {
                "dates": [],
                "values": [],
                "title": "Cumulative Spending",
            }

        return charts

    def to_dict(self) -> dict[str, Any]:
        """Export dashboard as dictionary."""
        dashboard = self.generate_dashboard()
        return {
            "total_budget": dashboard.total_budget,
            "total_spent": dashboard.total_spent,
            "total_remaining": dashboard.total_remaining,
            "percent_used": dashboard.percent_used,
            "days_remaining": dashboard.days_remaining,
            "daily_budget_remaining": dashboard.daily_budget_remaining,
            "budget_status": dashboard.budget_status,
            "status_message": dashboard.status_message,
            "transaction_count": dashboard.transaction_count,
            "average_transaction": dashboard.average_transaction,
            "largest_expense": dashboard.largest_expense,
            "spending_by_day": dashboard.spending_by_day,
            "top_spending": dashboard.top_spending,
            "alerts": dashboard.alerts,
            "recommendations": dashboard.recommendations,
            "categories": [
                {
                    "category": c.category,
                    "spending": float(c.current_spending),
                    "budget": float(c.budget),
                    "percent_used": c.percent_used,
                    "trend": c.trend,
                    "transaction_count": c.transaction_count,
                    "recommendation": c.recommendation,
                }
                for c in dashboard.categories
            ],
            "charts": dashboard.charts,
        }


def generate_dashboard(
    ods_path: Path | str,
    month: int | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    """Convenience function to generate dashboard data.

    Args:
        ods_path: Path to ODS budget file.
        month: Target month.
        year: Target year.

    Returns:
        Dashboard data dictionary.
    """
    analyzer = BudgetAnalyzer(ods_path)
    dashboard = AnalyticsDashboard(analyzer, month, year)
    return dashboard.to_dict()
