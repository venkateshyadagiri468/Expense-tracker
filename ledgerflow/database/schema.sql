-- Seed/Database Schema for LedgerFlow

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT,
    color TEXT
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    category_id INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    expense_date DATE NOT NULL,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    received_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER UNIQUE NOT NULL,
    monthly_limit REAL NOT NULL CHECK(monthly_limit > 0),
    alert_percentage INTEGER NOT NULL DEFAULT 80 CHECK(alert_percentage BETWEEN 1 AND 100),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
