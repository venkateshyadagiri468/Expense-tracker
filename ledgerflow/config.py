from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "ledger.db"

EXPORT_CSV_DIR = BASE_DIR / "exports" / "csv"
EXPORT_PDF_DIR = BASE_DIR / "exports" / "pdf"
REPORTS_MONTHLY_DIR = BASE_DIR / "reports" / "monthly"
REPORTS_YEARLY_DIR = BASE_DIR / "reports" / "yearly"
CHARTS_DIR = BASE_DIR / "charts"

# Ensure dirs exist
for directory in [
    DB_DIR,
    EXPORT_CSV_DIR,
    EXPORT_PDF_DIR,
    REPORTS_MONTHLY_DIR,
    REPORTS_YEARLY_DIR,
    CHARTS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Application Configuration
CURRENCY = "₹"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log Configuration
LOG_FILE = BASE_DIR / "ledgerflow.log"
LOG_LEVEL = "INFO"

# Default categories to seed the database
DEFAULT_CATEGORIES = [
    {"name": "Food", "icon": "🍔", "color": "#FF5733"},
    {"name": "Travel", "icon": "🚗", "color": "#3357FF"},
    {"name": "Shopping", "icon": "🛍️", "color": "#FF33A1"},
    {"name": "Bills", "icon": "🧾", "color": "#33FF57"},
    {"name": "Entertainment", "icon": "🎬", "color": "#F3FF33"},
]
