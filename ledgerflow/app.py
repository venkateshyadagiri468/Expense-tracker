import sys
import os
from datetime import date

# Ensure package is importable if run from this directory or root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm

from ledgerflow import config
from ledgerflow.database.database import DatabaseManager
from ledgerflow.services.observer import EventManager
from ledgerflow.repositories.category_repository import CategoryRepository
from ledgerflow.repositories.expense_repository import ExpenseRepository
from ledgerflow.repositories.income_repository import IncomeRepository
from ledgerflow.repositories.budget_repository import BudgetRepository

from ledgerflow.services.category_service import CategoryService
from ledgerflow.services.expense_service import ExpenseService
from ledgerflow.services.income_service import IncomeService
from ledgerflow.services.budget_service import BudgetService
from ledgerflow.services.report_service import ReportService
from ledgerflow.services.analytics_service import AnalyticsService

from ledgerflow.controllers.expense_controller import ExpenseController
from ledgerflow.controllers.income_controller import IncomeController
from ledgerflow.controllers.report_controller import ReportController
from ledgerflow.controllers.dashboard_controller import DashboardController

console = Console()


class LedgerFlowApp:
    def __init__(self):
        # 1. Base dependencies
        self.db_mgr = DatabaseManager()
        self.event_mgr = EventManager()

        # 2. Repositories
        self.category_repo = CategoryRepository(self.db_mgr)
        self.expense_repo = ExpenseRepository(self.db_mgr)
        self.income_repo = IncomeRepository(self.db_mgr)
        self.budget_repo = BudgetRepository(self.db_mgr)

        # 3. Services
        self.category_service = CategoryService(self.category_repo)
        self.expense_service = ExpenseService(
            self.expense_repo, self.category_repo, self.event_mgr
        )
        self.income_service = IncomeService(self.income_repo)

        # Budget service acts as observer for expense changes
        self.budget_service = BudgetService(
            self.budget_repo, self.category_repo, self.event_mgr
        )

        self.report_service = ReportService(self.expense_repo, self.income_repo)
        self.analytics_service = AnalyticsService(self.expense_repo)

        # 4. Controllers
        self.expense_controller = ExpenseController(self.expense_service)
        self.income_controller = IncomeController(self.income_service)
        self.report_controller = ReportController(
            self.report_service, self.analytics_service, self.budget_service
        )
        self.dashboard_controller = DashboardController(
            self.expense_service, self.income_service, self.budget_service
        )

    def draw_dashboard(self):
        """Fetches and displays the main financial dashboard panel."""
        today = date.today()
        data = self.dashboard_controller.get_dashboard_summary(today.year, today.month)

        # Print Title Banner
        console.print(
            Panel(
                Align.center(
                    f"[bold cyan]LedgerFlow[/bold cyan] - Personal Finance Platform\n[dim]Month: {data['month_name']} {data['year']} | Production-Grade CLI[/dim]"
                ),
                style="bold blue",
                border_style="cyan",
            )
        )

        # Check for outstanding budget alerts/notifications
        alerts = self.budget_service.get_alerts(clear=True)
        if alerts:
            alert_text = "\n".join(alerts)
            console.print(
                Panel(
                    alert_text,
                    title="[bold red]System Notification[/bold red]",
                    border_style="red",
                )
            )

        # 1. Summary Cards
        balance_style = "bold green" if data["balance"] >= 0 else "bold red"
        summary_table = Table.grid(expand=True)
        summary_table.add_column(justify="center", ratio=1)
        summary_table.add_column(justify="center", ratio=1)
        summary_table.add_column(justify="center", ratio=1)

        summary_table.add_row(
            Panel(
                f"[dim]Income[/dim]\n[bold green]{config.CURRENCY} {data['income']:,.2f}[/bold green]",
                border_style="green",
            ),
            Panel(
                f"[dim]Expenses[/dim]\n[bold red]{config.CURRENCY} {data['expenses']:,.2f}[/bold red]",
                border_style="red",
            ),
            Panel(
                f"[dim]Savings (Balance)[/dim]\n[{balance_style}]{config.CURRENCY} {data['balance']:,.2f}[/{balance_style}]",
                border_style="blue",
            ),
        )
        console.print(summary_table)

        # 2. Main Dashboard Layout (Grid)
        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)  # Left column: Today's Expenses + Categories
        grid.add_column(ratio=1)  # Right column: Budgets progress

        # Left Content: Today's Expenses + Top Categories
        left_table = Table(title="Today's Transactions", expand=True, box=None)
        left_table.add_column("Details", style="cyan")
        left_table.add_column("Amount", justify="right", style="bold red")

        if data["todays_expenses"]:
            for e in data["todays_expenses"]:
                icon = next(
                    (
                        c.icon
                        for c in self.category_service.list_all_categories()
                        if c.id == e.category_id
                    ),
                    "💸",
                )
                left_table.add_row(
                    f"{icon} {e.title} ({e.payment_method})",
                    f"{config.CURRENCY} {e.amount:,.2f}",
                )
        else:
            left_table.add_row("[dim]No expenses recorded today.[/dim]", "")

        top_cat_table = Table(title="Top Spending Categories", expand=True, box=None)
        top_cat_table.add_column("Category", style="magenta")
        top_cat_table.add_column("Amount", justify="right", style="bold yellow")

        if data["top_categories"]:
            for c in data["top_categories"][:5]:
                top_cat_table.add_row(
                    c["name"], f"{config.CURRENCY} {c['amount']:,.2f}"
                )
        else:
            top_cat_table.add_row("[dim]No spending recorded this month.[/dim]", "")

        left_panel = Panel(
            Columns([left_table, top_cat_table], equal=True, expand=True),
            title="Activity Summary",
            border_style="magenta",
        )

        # Right Content: Budgets Status
        budget_summary = ""
        if data["budgets"]:
            for b in data["budgets"]:
                pct = b.percentage()
                # Draw a manual status bar
                filled_blocks = int(pct // 10)
                filled_blocks = min(filled_blocks, 10)
                empty_blocks = 10 - filled_blocks
                bar = "█" * filled_blocks + "░" * empty_blocks

                # Apply conditional coloring
                if pct >= 100:
                    bar_color = "red"
                elif pct >= b.alert_percentage:
                    bar_color = "yellow"
                else:
                    bar_color = "green"

                cat_display = f"{b.category_name or 'Category'}"
                budget_summary += f"{cat_display:<15} [bold {bar_color}]{bar}[/bold {bar_color}] {pct:.1f}% ({config.CURRENCY}{b.spent:,.0f}/{config.CURRENCY}{b.monthly_limit:,.0f})\n"
        else:
            budget_summary = "[dim]No budgets set for this month.[/dim]\n[italic]Tip: Select option 3 to set category spending limits.[/italic]"

        right_panel = Panel(
            Align.left(budget_summary),
            title="Monthly Budget Limits",
            border_style="yellow",
        )

        grid.add_row(left_panel, right_panel)
        console.print(grid)

    def prompt_add_expense(self):
        console.print("\n[bold green]=== Add New Expense ===[/bold green]")
        title = Prompt.ask("Enter expense title")
        amount = FloatPrompt.ask("Enter expense amount")

        # Category list selection
        categories = self.category_service.list_all_categories()
        if not categories:
            console.print(
                "[red]No categories found! Please seed or create a category first.[/red]"
            )
            return

        console.print("\nSelect Category:")
        for idx, cat in enumerate(categories, start=1):
            console.print(f"{idx}. {cat.icon or '•'} {cat.name}")
        cat_choice = IntPrompt.ask(
            "Choose category number",
            choices=[str(i) for i in range(1, len(categories) + 1)],
        )
        category_id = categories[cat_choice - 1].id

        # Payment method selection
        payment_methods = ["Cash", "Card", "UPI", "Bank Transfer"]
        console.print("\nSelect Payment Method:")
        for idx, pm in enumerate(payment_methods, start=1):
            console.print(f"{idx}. {pm}")
        pm_choice = IntPrompt.ask(
            "Choose payment method number", choices=["1", "2", "3", "4"]
        )
        payment_method = payment_methods[pm_choice - 1]

        # Date selection
        date_str = Prompt.ask(
            "Enter date (YYYY-MM-DD)", default=date.today().strftime("%Y-%m-%d")
        )
        note = Prompt.ask("Enter note (optional)", default="")

        res = self.expense_controller.add_expense(
            title=title,
            amount=amount,
            category_id=category_id,
            payment_method=payment_method,
            expense_date=date_str,
            note=note if note.strip() else None,
        )

        if res["success"]:
            console.print(
                f"[bold green]Success![/bold green] Expense '{res['data'].title}' saved successfully."
            )
        else:
            console.print(f"[bold red]Failed to add expense:[/bold red] {res['error']}")

    def prompt_add_income(self):
        console.print("\n[bold green]=== Add New Income ===[/bold green]")
        source = Prompt.ask("Enter income source")
        amount = FloatPrompt.ask("Enter income amount")
        date_str = Prompt.ask(
            "Enter date (YYYY-MM-DD)", default=date.today().strftime("%Y-%m-%d")
        )

        res = self.income_controller.add_income(
            source=source, amount=amount, received_date=date_str
        )

        if res["success"]:
            console.print(
                f"[bold green]Success![/bold green] Income of {config.CURRENCY}{res['data'].amount:,.2f} from '{res['data'].source}' saved."
            )
        else:
            console.print(f"[bold red]Failed to add income:[/bold red] {res['error']}")

    def prompt_set_budget(self):
        console.print("\n[bold green]=== Set Category Budget ===[/bold green]")
        categories = self.category_service.list_all_categories()
        if not categories:
            console.print("[red]No categories found![/red]")
            return

        console.print("\nSelect Category:")
        for idx, cat in enumerate(categories, start=1):
            console.print(f"{idx}. {cat.icon or '•'} {cat.name}")
        cat_choice = IntPrompt.ask(
            "Choose category number",
            choices=[str(i) for i in range(1, len(categories) + 1)],
        )
        category_id = categories[cat_choice - 1].id

        limit = FloatPrompt.ask("Enter monthly spending limit")
        alert_pct = IntPrompt.ask("Enter alert threshold percentage", default=80)

        try:
            budget = self.budget_service.set_budget(category_id, limit, alert_pct)
            console.print(
                f"[bold green]Success![/bold green] Budget of {config.CURRENCY}{budget.monthly_limit:,.2f} set for category."
            )
        except Exception as e:
            console.print(f"[bold red]Failed to set budget:[/bold red] {e}")

    def prompt_view_categories(self):
        console.print("\n[bold green]=== Categories ===[/bold green]")
        categories = self.category_service.list_all_categories()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Icon", width=6)
        table.add_column("Category Name", style="bold")
        table.add_column("Color Theme", style="italic")

        for cat in categories:
            table.add_row(str(cat.id), cat.icon or "", cat.name, cat.color or "")
        console.print(table)

        if Confirm.ask("Would you like to add a new category?"):
            name = Prompt.ask("Enter category name")
            icon = Prompt.ask("Enter icon emoji (optional)", default="•")
            color = Prompt.ask("Enter color hex code (optional)", default="#718096")
            try:
                self.category_service.create_category(name, icon, color)
                console.print("[bold green]Category created successfully![/bold green]")
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

    def prompt_view_reports(self):
        console.print("\n[bold green]=== Financial Reports ===[/bold green]")
        console.print("1. Daily Report")
        console.print("2. Weekly Report")
        console.print("3. Monthly Report")
        console.print("4. Yearly Report")
        console.print("5. Cash Flow Analysis")
        choice = IntPrompt.ask(
            "Select report option", choices=["1", "2", "3", "4", "5"]
        )

        today = date.today()

        try:
            if choice == 1:
                date_str = Prompt.ask(
                    "Enter date (YYYY-MM-DD)", default=today.strftime("%Y-%m-%d")
                )
                from ledgerflow.utils.date_utils import parse_date
                try:
                    parsed_d = parse_date(date_str)
                    report_data = self.report_service.get_daily_report(parsed_d)
                    self.display_report_table(f"Daily Report ({parsed_d})", report_data)
                except ValueError as ve:
                    console.print(f"[bold red]Error:[/bold red] {ve}")
            elif choice == 2:
                report_data = self.report_controller.get_report_data(
                    "weekly", today.year, today.month
                )
                self.display_report_table("Weekly Report (Current Week)", report_data)
            elif choice == 3:
                year = IntPrompt.ask("Enter Year", default=today.year)
                month = IntPrompt.ask("Enter Month (1-12)", default=today.month)
                report_data = self.report_controller.get_report_data(
                    "monthly", year, month
                )
                self.display_report_table(
                    f"Monthly Report ({year}-{month:02d})", report_data
                )
            elif choice == 4:
                year = IntPrompt.ask("Enter Year", default=today.year)
                report_data = self.report_controller.get_report_data("yearly", year)
                self.display_report_table(f"Yearly Report ({year})", report_data)
            elif choice == 5:
                year = IntPrompt.ask("Enter Year", default=today.year)
                cash_flow = self.report_service.get_cash_flow_report(year)

                table = Table(
                    title=f"Cash Flow Report - {year}",
                    show_header=True,
                    header_style="bold green",
                )
                table.add_column("Month", style="bold")
                table.add_column("Inflow (Income)", style="green", justify="right")
                table.add_column("Outflow (Expenses)", style="red", justify="right")
                table.add_column("Net Savings", justify="right")

                for row in cash_flow:
                    savings_style = (
                        "bold green" if row["net_savings"] >= 0 else "bold red"
                    )
                    table.add_row(
                        row["month_name"],
                        f"{config.CURRENCY} {row['income']:,.2f}",
                        f"{config.CURRENCY} {row['expense']:,.2f}",
                        f"[{savings_style}]{config.CURRENCY} {row['net_savings']:,.2f}[/{savings_style}]",
                    )
                console.print(table)
        except Exception as e:
            console.print(f"[bold red]Failed to load report data:[/bold red] {e}")

    def display_report_table(self, title: str, data: dict):
        console.print(
            Panel(
                f"Period: {data['start_date']} to {data['end_date']}\n"
                f"[bold green]Income: {config.CURRENCY}{data['total_income']:,.2f}[/bold green] | "
                f"[bold red]Expenses: {config.CURRENCY}{data['total_expense']:,.2f}[/bold red] | "
                f"[bold blue]Savings: {config.CURRENCY}{data['savings']:,.2f}[/bold blue]",
                title=title,
                border_style="blue",
            )
        )

        # Detailed Expenses Table
        if data["expenses"]:
            exp_table = Table(
                title="Details - Expenses", show_header=True, header_style="bold red"
            )
            exp_table.add_column("Date", width=12)
            exp_table.add_column("Title")
            exp_table.add_column("Category", style="magenta")
            exp_table.add_column("Payment", style="dim")
            exp_table.add_column("Amount", justify="right", style="bold red")

            for e in data["expenses"]:
                exp_table.add_row(
                    str(e.expense_date),
                    e.title,
                    e.category_name or "Uncategorized",
                    e.payment_method,
                    f"{config.CURRENCY} {e.amount:,.2f}",
                )
            console.print(exp_table)

    def prompt_export_report(self):
        console.print("\n[bold green]=== Export Financial Data ===[/bold green]")
        console.print("Select Period Type:")
        console.print("1. Daily")
        console.print("2. Weekly")
        console.print("3. Monthly")
        console.print("4. Yearly")
        period_choice = IntPrompt.ask(
            "Choose option number", choices=["1", "2", "3", "4"]
        )
        period_mapping = {1: "daily", 2: "weekly", 3: "monthly", 4: "yearly"}
        period_type = period_mapping[period_choice]

        console.print("\nSelect Export Format:")
        console.print("1. CSV Format")
        console.print("2. PDF Document")
        format_choice = IntPrompt.ask("Choose option number", choices=["1", "2"])
        format_type = "csv" if format_choice == 1 else "pdf"

        today = date.today()
        year = today.year
        month = today.month

        if period_type == "monthly":
            year = IntPrompt.ask("Enter Year", default=today.year)
            month = IntPrompt.ask("Enter Month (1-12)", default=today.month)
        elif period_type == "yearly":
            year = IntPrompt.ask("Enter Year", default=today.year)
            month = None

        with console.status(
            f"[bold green]Generating and exporting {format_type.upper()} report...",
            spinner="dots",
        ):
            res = self.report_controller.export_report(
                period_type, format_type, year, month
            )

        if res["success"]:
            console.print(
                f"[bold green]Success![/bold green] File exported to: [cyan]{res['filepath']}[/cyan]"
            )
        else:
            console.print(
                f"[bold red]Failed to export report:[/bold red] {res['error']}"
            )

    def prompt_generate_charts(self):
        today = date.today()
        year = IntPrompt.ask("\nEnter Year for charts generation", default=today.year)
        month = IntPrompt.ask(
            "Enter Month for charts generation (1-12)", default=today.month
        )

        with console.status(
            "[bold green]Generating visual statistics graphs...", spinner="dots"
        ):
            res = self.report_controller.generate_all_visualizations(year, month)

        if res["success"]:
            console.print(
                Panel(
                    f"[bold green]5 Financial Charts successfully generated in folder:[/bold green]\n"
                    f"[cyan]{config.CHARTS_DIR}[/cyan]\n\n"
                    f"1. Category distribution: [dim]category_distribution.png[/dim]\n"
                    f"2. Monthly spending limits: [dim]monthly_spending.png[/dim]\n"
                    f"3. 12-Month expense trend: [dim]expense_trend.png[/dim]\n"
                    f"4. Income vs Expense Cashflow: [dim]income_vs_expenses.png[/dim]\n"
                    f"5. Budget utilization progress: [dim]budget_utilization.png[/dim]",
                    title="Charts Generator",
                    border_style="green",
                )
            )
        else:
            console.print(
                f"[bold red]Failed to generate charts:[/bold red] {res['error']}"
            )

    def run(self):
        """Main application lifecycle loop."""
        while True:
            try:
                # Clear terminal screen
                os.system("cls" if os.name == "nt" else "clear")
                self.draw_dashboard()

                # Command Menu
                console.print("\n[bold cyan]Main Operations Menu:[/bold cyan]")
                console.print(
                    "1. [bold green]+[/bold green] Add Expense          2. [bold green]+[/bold green] Add Income"
                )
                console.print(
                    "3. [bold yellow]⚙[/bold yellow] Set Category Budget   4. [bold magenta]📁[/bold magenta] Categories Manager"
                )
                console.print(
                    "5. [bold blue]📊[/bold blue] View Financial Reports 6. [bold white]💾[/bold white] Export Data (CSV/PDF)"
                )
                console.print(
                    "7. [bold cyan]📈[/bold cyan] Render Trend Charts   8. [bold red]❌[/bold red] Exit Application"
                )

                choice = Prompt.ask(
                    "\nEnter selection number", choices=[str(i) for i in range(1, 9)]
                )

                if choice == "1":
                    self.prompt_add_expense()
                elif choice == "2":
                    self.prompt_add_income()
                elif choice == "3":
                    self.prompt_set_budget()
                elif choice == "4":
                    self.prompt_view_categories()
                elif choice == "5":
                    self.prompt_view_reports()
                elif choice == "6":
                    self.prompt_export_report()
                elif choice == "7":
                    self.prompt_generate_charts()
                elif choice == "8":
                    console.print(
                        "\n[bold green]Thank you for using LedgerFlow. Goodbye![/bold green]"
                    )
                    break

                # Pause after action
                Prompt.ask(
                    "\nPress [bold enter]Enter[/bold enter] to return to dashboard"
                )

            except KeyboardInterrupt:
                console.print("\n[bold green]Goodbye![/bold green]")
                break
            except Exception as e:
                console.print(
                    f"\n[bold red]An unexpected system error occurred:[/bold red] {e}"
                )
                Prompt.ask("Press Enter to continue")


if __name__ == "__main__":
    app = LedgerFlowApp()
    app.run()
