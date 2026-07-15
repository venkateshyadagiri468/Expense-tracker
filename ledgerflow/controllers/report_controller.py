from typing import Dict, Any, Optional
from datetime import date
from ledgerflow import config
from ledgerflow.services.report_service import ReportService
from ledgerflow.services.analytics_service import AnalyticsService
from ledgerflow.services.budget_service import BudgetService
from ledgerflow.services.export_service import (
    ExportService,
    CSVExportStrategy,
    PDFExportStrategy,
)
from ledgerflow.charts import chart_generator
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class ReportController:
    def __init__(
        self,
        report_service: ReportService,
        analytics_service: AnalyticsService,
        budget_service: BudgetService,
    ):
        self.report_service = report_service
        self.analytics_service = analytics_service
        self.budget_service = budget_service

    def get_report_data(
        self, period_type: str, year: int, month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fetches report data depending on the period selection."""
        period_type = period_type.lower()
        if period_type == "daily":
            return self.report_service.get_daily_report()
        elif period_type == "weekly":
            return self.report_service.get_weekly_report()
        elif period_type == "monthly":
            return self.report_service.get_monthly_report(
                year, month or date.today().month
            )
        elif period_type == "yearly":
            return self.report_service.get_yearly_report(year)
        else:
            raise ValueError(f"Unknown report period type: {period_type}")

    def export_report(
        self, period_type: str, format_type: str, year: int, month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Routes report generation data to the selected export strategy."""
        try:
            report_data = self.get_report_data(period_type, year, month)
            format_type = format_type.lower()

            if format_type == "csv":
                strategy = CSVExportStrategy()
                dest_dir = config.EXPORT_CSV_DIR
            elif format_type == "pdf":
                strategy = PDFExportStrategy()
                dest_dir = config.EXPORT_PDF_DIR
            else:
                return {
                    "success": False,
                    "filepath": None,
                    "error": f"Invalid export format: {format_type}",
                }

            report_name = f"{period_type}_report_{year}"
            if month and period_type == "monthly":
                report_name += f"_{month:02d}"

            export_service = ExportService(strategy)
            filepath = export_service.export_report(report_name, report_data, dest_dir)

            return {"success": True, "filepath": filepath, "error": None}

        except Exception as e:
            logger.error(f"Failed to export report: {e}", exc_info=True)
            return {"success": False, "filepath": None, "error": str(e)}

    def generate_all_visualizations(self, year: int, month: int) -> Dict[str, Any]:
        """Triggers the rendering of all dashboard charts using Matplotlib Agg."""
        try:
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, month + 1, 1) - date.resolution

            # 1. Pie Chart
            top_cats = self.analytics_service.get_top_categories(start_date, end_date)
            pie_path = config.CHARTS_DIR / "category_distribution.png"
            chart_generator.generate_category_pie(top_cats, pie_path)

            # 2. Monthly Spending Bar
            trend_data = self.analytics_service.get_expense_trend(year)
            bar_path = config.CHARTS_DIR / "monthly_spending.png"
            chart_generator.generate_monthly_spending_bar(trend_data, bar_path)

            # 3. Line Chart Trend
            trend_path = config.CHARTS_DIR / "expense_trend.png"
            chart_generator.generate_expense_trend_line(trend_data, trend_path)

            # 4. Income vs Expense Stacked
            incomes_trend = []
            for m in range(1, 13):
                incomes_trend.append(
                    self.report_service.income_repo.get_total_income(
                        start_date=date(year, m, 1),
                        end_date=(
                            date(year, m + 1, 1) - date.resolution
                            if m < 12
                            else date(year, 12, 31)
                        ),
                    )
                )
            cash_flow_path = config.CHARTS_DIR / "income_vs_expenses.png"
            chart_generator.generate_income_vs_expense_bar(
                incomes_trend, trend_data, cash_flow_path
            )

            # 5. Budget Utilization Progress
            budgets = self.budget_service.list_all_budgets(year, month)
            budget_path = config.CHARTS_DIR / "budget_utilization.png"
            chart_generator.generate_budget_utilization_chart(budgets, budget_path)

            return {
                "success": True,
                "charts": {
                    "pie": pie_path,
                    "bar": bar_path,
                    "trend": trend_path,
                    "cash_flow": cash_flow_path,
                    "budget": budget_path,
                },
                "error": None,
            }
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}", exc_info=True)
            return {"success": False, "charts": {}, "error": str(e)}
