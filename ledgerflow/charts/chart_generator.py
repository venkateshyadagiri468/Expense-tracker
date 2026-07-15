import matplotlib

matplotlib.use("Agg")  # Headless backend to prevent GUI errors
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from ledgerflow import config
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)

# Premium color palette
COLORS = ["#2B6CB0", "#319795", "#D69E2E", "#9F7AEA", "#E53E3E", "#38A169", "#4A5568"]


def _save_and_clear(fig, filepath: Path) -> Path:
    """Helper to save figure and clean memory."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(filepath, dpi=300)
    plt.close(fig)
    logger.info(f"Chart saved successfully at {filepath}")
    return filepath


def generate_category_pie(
    category_data: List[Dict[str, Any]], filepath: Path
) -> Optional[Path]:
    """Generates a pie chart of expense distribution by category."""
    if not category_data:
        logger.warning("No category data available to generate pie chart.")
        return None

    labels = [item["category"] for item in category_data]
    sizes = [item["amount"] for item in category_data]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=COLORS[: len(labels)],
        wedgeprops=dict(width=0.4, edgecolor="w"),  # Donut chart
    )

    plt.setp(autotexts, size=9, weight="bold")
    plt.setp(texts, size=10)
    ax.set_title("Expense Distribution by Category", fontsize=14, weight="bold", pad=20)

    return _save_and_clear(fig, filepath)


def generate_monthly_spending_bar(
    monthly_spending: List[float], filepath: Path
) -> Path:
    """Generates a bar chart of monthly spending over a year."""
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(
        months, monthly_spending, color="#3182CE", edgecolor="black", alpha=0.8
    )

    # Customizing axes
    ax.set_ylabel(f"Spent ({config.CURRENCY})", fontsize=10, weight="bold")
    ax.set_title("Monthly Spending Overview", fontsize=12, weight="bold", pad=15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.annotate(
                f"{config.CURRENCY}{height:.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                weight="bold",
            )

    return _save_and_clear(fig, filepath)


def generate_expense_trend_line(trend_data: List[float], filepath: Path) -> Path:
    """Generates a line chart of expense trends over 12 months."""
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(
        months, trend_data, marker="o", color="#E53E3E", linewidth=2.5, label="Expenses"
    )

    ax.set_ylabel(f"Amount ({config.CURRENCY})", fontsize=10, weight="bold")
    ax.set_title("12-Month Expense Trend", fontsize=12, weight="bold", pad=15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle="--", alpha=0.5)

    for i, txt in enumerate(trend_data):
        if txt > 0:
            ax.annotate(
                f"{config.CURRENCY}{txt:.0f}",
                (months[i], trend_data[i]),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=8,
                weight="bold",
            )

    return _save_and_clear(fig, filepath)


def generate_income_vs_expense_bar(
    income_trend: List[float], expense_trend: List[float], filepath: Path
) -> Path:
    """Generates a side-by-side bar chart of Income vs. Expenses."""
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    x = np.arange(len(months))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(
        x - width / 2, income_trend, width, label="Income", color="#38A169", alpha=0.8
    )
    ax.bar(
        x + width / 2,
        expense_trend,
        width,
        label="Expenses",
        color="#E53E3E",
        alpha=0.8,
    )

    ax.set_ylabel(f"Amount ({config.CURRENCY})", fontsize=10, weight="bold")
    ax.set_title("Income vs. Expenses Cash Flow", fontsize=12, weight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.legend(frameon=True, facecolor="white", edgecolor="none")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    return _save_and_clear(fig, filepath)


def generate_budget_utilization_chart(
    budgets: List[Any], filepath: Path
) -> Optional[Path]:
    """Generates a horizontal progress-bar style chart showing budget limit vs spent."""
    if not budgets:
        logger.warning("No budget data available to generate utilization chart.")
        return None

    categories = [b.category_name or f"Cat {b.category_id}" for b in budgets]
    limits = [b.monthly_limit for b in budgets]
    spents = [b.spent for b in budgets]

    y_pos = np.arange(len(categories))

    fig, ax = plt.subplots(figsize=(8, 4))

    # Background limits
    ax.barh(
        y_pos,
        limits,
        align="center",
        color="#EDF2F7",
        edgecolor="#CBD5E0",
        label="Limit",
    )
    # Foreground spents
    colors = [
        "#E53E3E" if spent >= limit else "#38A169"
        for spent, limit in zip(spents, limits)
    ]
    ax.barh(y_pos, spents, align="center", color=colors, alpha=0.8, label="Spent")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=10, weight="bold")
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel(f"Amount ({config.CURRENCY})", fontsize=10, weight="bold")
    ax.set_title("Budget Utilization Status", fontsize=12, weight="bold", pad=15)
    ax.legend(frameon=True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    # Annotate percent values
    for i, (spent, limit) in enumerate(zip(spents, limits)):
        percentage = (spent / limit) * 100.0 if limit > 0 else 0.0
        ax.text(
            spent + (limit * 0.01),
            i,
            f"{percentage:.1f}%",
            va="center",
            ha="left",
            fontsize=8,
            weight="bold",
        )

    return _save_and_clear(fig, filepath)
