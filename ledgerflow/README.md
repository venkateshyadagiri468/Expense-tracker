# LedgerFlow — Production-Ready Personal Finance Engine

**LedgerFlow** is a secure, local-first financial engine designed for personal asset tracking, budget limit monitoring, and publication-ready reporting.

---

##  EXECUTIVE SUMMARY & PROBLEM STATEMENT

### The Problem
Most personal finance applications suffer from two critical flaws:
1. **Bloated cloud-dependent UIs** that leak highly private transactional data to external servers.
2. **"Toy" CLI applications** built without structural patterns, lacking durability, concurrency, transaction safety, or loose coupling.

### The LedgerFlow Solution
LedgerFlow solves this by implementing a **local-first, security-centric financial ledger** designed with strict **Clean Architecture (Layered)**. It decouples the presentation layer from the database engine, enforces SQLite constraint safety (including foreign keys), alerts the user in real-time when category budget thresholds are crossed via observer notifications, and exports audit-ready CSV/PDF sheets alongside vector visual trends.

---

## TECHNICAL STACK

* **Language**: Python 3.12+ (leveraging typed data models and context managers).
* **Database**: SQLite (configured with `PRAGMA foreign_keys = ON` to enforce strict relational integrity).
* **Interface**: Rich CLI Console (using layout divisions, real-time status bars, and formatted tables).
* **Visualizations**: Matplotlib (utilizing a headless `Agg` backend to avoid display server dependency conflicts).
* **Documents Generator**: ReportLab (rendering custom PDF stylesheets with summary tables and alternating row color schemes).
* **Testing Suite**: Pytest (executing isolated test runs against automatic in-memory SQLite files).

---

## ARCHITECTURE & SYSTEM FLOW

LedgerFlow strictly adheres to **Clean Architecture**. Control and data flow from the outer console shell down to the core database tables:

```
                  User
                   │
                   ▼
            Presentation Layer (app.py)
                   │
                   ▼
            Controller Layer (controllers/)
                   │
                   ▼
            Service Layer (services/) ───► EventManager (Observer)
                   │
                   ▼
            Repository Layer (repositories/)
                   │
                   ▼
            SQLite Database (ledger.db)
```

### End-to-End Operational Lifecycle
1. **User Action**: The user adds an expense of `₹500` under the category `Food`.
2. **Controller**: `ExpenseController` intercepts the parameters, wraps them in a validation boundary, and catches any parsing exceptions.
3. **Service Layer**: `ExpenseService` parses the date boundaries, confirms that the Category ID exists in the database, and creates the entity model.
4. **Data Access (Repository)**: `ExpenseRepository` executes a parameterized INSERT statement into the `expenses` table.
5. **Event Observer Triggers**: The `EventManager` publishes an `expense_created` event.
6. **Limit Assessment**: The `BudgetService` (which is subscribed to expense events) intercepts the transaction, queries the total spent for `Food` in the current month, assesses if the amount has breached the category's threshold (e.g., 80% limit), and buffers a warning notification.
7. **UI Refresh**: The `DashboardController` re-compiles the monthly balances and today's transactions, and the Rich Console renders the refreshed panels and warning widgets.

---

## DESIGN PATTERNS

| Design Pattern | Purpose & Implementation |
| --- | --- |
| **Repository Pattern** | Decouples SQL DML statements from business logic. Services interact with data solely through Repository interfaces. |
| **Service Layer Pattern** | Encapsulates all transactional checks, date boundary offsets, and budget rule validations. |
| **Singleton Pattern** | Enforces a single connection and setup instance for `DatabaseManager` with automatic default category seeding. |
| **Observer Pattern** | Decouples budget alerts from the core expense creation logic. `ExpenseService` emits events, and `BudgetService` listens. |
| **Strategy Pattern** | Standardizes file exporters. `ExportService` accepts interchangeable strategies (`CSVExportStrategy`, `PDFExportStrategy`) dynamically. |
| **Dependency Injection** | Loose coupling is achieved by passing database connections, repositories, and event managers during constructor instantiation. |

---

## FOLDER STRUCTURE

```
ledgerflow/
├── app.py                      # Presentation Layer (Rich interactive dashboard & CLI menu)
├── config.py                   # Central configurations & default parameters
├── requirements.txt            # System dependencies
├── README.md                   # Technical documentation manual
├── .gitignore                  # Git exclusions
│
├── database/
│   ├── database.py             # Singleton database connection manager
│   ├── schema.sql              # Database DDL table definitions
│   ├── migrations.py           # Verification framework migrations manager
│   └── ledger.db               # SQLite database file (auto-generated)
│
├── models/
│   ├── category.py             # Category dataclass model
│   ├── expense.py              # Expense model with repository hooks
│   ├── income.py               # Income model
│   └── budget.py               # Budget model with utilization calculators
│
├── repositories/
│   ├── base_repository.py      # Base repository class
│   ├── category_repository.py  # SQLite Category CRUD queries
│   ├── expense_repository.py   # SQLite Expense CRUD & query filters
│   ├── income_repository.py    # SQLite Income CRUD & sums
│   └── budget_repository.py    # SQLite Budget CRUD & spent aggregates
│
├── services/
│   ├── observer.py             # EventManager & Observer abstract classes
│   ├── category_service.py     # Business rules for categories
│   ├── expense_service.py      # Expense validation & event hooks
│   ├── income_service.py       # Income validation
│   ├── budget_service.py       # Budget checker observer
│   ├── report_service.py       # Period summary compiler
│   └── export_service.py       # Strategic CSV/PDF exporters
│
├── controllers/
│   ├── expense_controller.py   # Controller routing expense commands
│   ├── income_controller.py    # Controller routing income commands
│   ├── report_controller.py    # Export strategy & chart coordinator
│   └── dashboard_controller.py # Dashboard data compilation coordinator
│
├── utils/
│   ├── validators.py           # Currency, text, and format validators
│   ├── constants.py            # Currency & payment channel definitions
│   └── date_utils.py           # Date range boundaries calculations
│
├── exports/
│   ├── csv/                    # Generated CSV exports
│   └── pdf/                    # Generated PDF reports
│
├── reports/
│   ├── monthly/
│   └── yearly/
│
├── charts/
│   └── chart_generator.py      # Matplotlib Agg visual trend compiler
│
└── tests/                      # Automated Pytest suite
```

---

## SETUP & OPERATION MANUAL

### 1. Prerequisite Installations
Ensure Python 3.12+ and `pip` are installed on your host system.

### 2. Environment Virtualization
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### 3. Dependency Staging
```bash
pip install -r ledgerflow/requirements.txt
```

### 4. Running the Dashboard
```bash
PYTHONPATH=. python ledgerflow/app.py
```

### 5. Running Automated Test Cases
```bash
PYTHONPATH=. pytest ledgerflow/tests/
```

### 6. Linting & Formatting Verification
```bash
# Style check formatting
.venv/bin/black --check ledgerflow/

# Run static quality analysis
.venv/bin/ruff check ledgerflow/
```
