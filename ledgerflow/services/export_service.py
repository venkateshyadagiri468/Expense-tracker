import csv
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Dict, Any
from ledgerflow import config
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)

# Try importing reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab library not installed. PDF export will be unavailable.")


class ExportStrategy(ABC):
    @abstractmethod
    def export(
        self, report_name: str, report_data: Dict[str, Any], destination_dir: Path
    ) -> Path:
        """Exports the report data. Returns the output file path."""
        pass


class CSVExportStrategy(ExportStrategy):
    def export(
        self, report_name: str, report_data: Dict[str, Any], destination_dir: Path
    ) -> Path:
        filename = f"{report_name.replace(' ', '_').lower()}.csv"
        file_path = destination_dir / filename

        logger.info(f"Exporting CSV to {file_path}")

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write Summary Block
                writer.writerow(["LEDGERFLOW FINANCIAL REPORT", report_name.upper()])
                writer.writerow(
                    [
                        "Period",
                        f"{report_data['start_date']} to {report_data['end_date']}",
                    ]
                )
                writer.writerow([])
                writer.writerow(["FINANCIAL SUMMARY"])
                writer.writerow(
                    [
                        "Total Income",
                        f"{config.CURRENCY} {report_data['total_income']:.2f}",
                    ]
                )
                writer.writerow(
                    [
                        "Total Expense",
                        f"{config.CURRENCY} {report_data['total_expense']:.2f}",
                    ]
                )
                writer.writerow(
                    ["Net Savings", f"{config.CURRENCY} {report_data['savings']:.2f}"]
                )
                writer.writerow([])

                # Write Expenses List
                expenses = report_data.get("expenses", [])
                if expenses:
                    writer.writerow(["DETAILED EXPENSES"])
                    writer.writerow(
                        [
                            "Date",
                            "Title",
                            "Category",
                            "Payment Method",
                            "Amount",
                            "Note",
                        ]
                    )
                    for e in expenses:
                        writer.writerow(
                            [
                                e.expense_date,
                                e.title,
                                e.category_name or "Uncategorized",
                                e.payment_method,
                                f"{e.amount:.2f}",
                                e.note or "",
                            ]
                        )
                    writer.writerow([])

                # Write Income List
                incomes = report_data.get("incomes", [])
                if incomes:
                    writer.writerow(["DETAILED INCOMES"])
                    writer.writerow(["Date", "Source", "Amount"])
                    for i in incomes:
                        writer.writerow([i.received_date, i.source, f"{i.amount:.2f}"])
            return file_path
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}", exc_info=True)
            raise e


class PDFExportStrategy(ExportStrategy):
    def export(
        self, report_name: str, report_data: Dict[str, Any], destination_dir: Path
    ) -> Path:
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "The 'reportlab' package is required for PDF exports but was not found."
            )

        filename = f"{report_name.replace(' ', '_').lower()}.pdf"
        file_path = destination_dir / filename

        logger.info(f"Exporting PDF to {file_path}")

        try:
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=letter,
                rightMargin=54,
                leftMargin=54,
                topMargin=54,
                bottomMargin=54,
            )
            story = []
            styles = getSampleStyleSheet()

            # Custom Styles
            title_style = ParagraphStyle(
                "DocTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1A365D"),
                spaceAfter=15,
            )
            subtitle_style = ParagraphStyle(
                "DocSubTitle",
                parent=styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor("#4A5568"),
                spaceAfter=25,
            )
            section_style = ParagraphStyle(
                "DocSection",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#2B6CB0"),
                spaceBefore=15,
                spaceAfter=10,
            )

            # Header
            story.append(Paragraph("LedgerFlow Financial Report", title_style))
            story.append(
                Paragraph(
                    f"Report Period: {report_data['start_date']} to {report_data['end_date']} | Generated: {date.today()}",
                    subtitle_style,
                )
            )

            # Summary Table
            story.append(Paragraph("Financial Summary", section_style))
            summary_data = [
                ["Income", "Expenses", "Net Savings"],
                [
                    f"{config.CURRENCY} {report_data['total_income']:.2f}",
                    f"{config.CURRENCY} {report_data['total_expense']:.2f}",
                    f"{config.CURRENCY} {report_data['savings']:.2f}",
                ],
            ]
            summary_table = Table(summary_data, colWidths=[180, 180, 180])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#2D3748")),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
                        ("FONTSIZE", (0, 1), (-1, 1), 14),
                        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                        (
                            "TEXTCOLOR",
                            (2, 1),
                            (2, 1),
                            (
                                colors.HexColor("#38A169")
                                if report_data["savings"] >= 0
                                else colors.HexColor("#E53E3E")
                            ),
                        ),
                    ]
                )
            )
            story.append(summary_table)
            story.append(Spacer(1, 20))

            # Detailed Expenses
            expenses = report_data.get("expenses", [])
            if expenses:
                story.append(Paragraph("Detailed Expenses", section_style))
                expense_headers = [
                    "Date",
                    "Title",
                    "Category",
                    "Payment Method",
                    "Amount",
                ]
                expense_rows = [expense_headers]
                for e in expenses:
                    expense_rows.append(
                        [
                            str(e.expense_date),
                            e.title,
                            e.category_name or "Uncategorized",
                            e.payment_method,
                            f"{config.CURRENCY} {e.amount:.2f}",
                        ]
                    )

                # Render table
                expense_table = Table(expense_rows, colWidths=[80, 150, 110, 100, 100])
                t_style = [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ]

                # Alternating row colors
                for r in range(1, len(expense_rows)):
                    bg = colors.HexColor("#F7FAFC") if r % 2 == 0 else colors.white
                    t_style.append(("BACKGROUND", (0, r), (-1, r), bg))

                expense_table.setStyle(TableStyle(t_style))
                story.append(expense_table)
                story.append(Spacer(1, 20))

            # Build Document
            doc.build(story)
            return file_path
        except Exception as e:
            logger.error(f"Failed to export PDF: {e}", exc_info=True)
            raise e


class ExportService:
    def __init__(self, strategy: ExportStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: ExportStrategy):
        self.strategy = strategy

    def export_report(
        self, report_name: str, report_data: Dict[str, Any], destination_dir: Path
    ) -> Path:
        """Executes the injected strategy to export report data."""
        return self.strategy.export(report_name, report_data, destination_dir)
