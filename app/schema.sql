CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 100),
    category TEXT NOT NULL,
    found_location TEXT NOT NULL CHECK (length(trim(found_location)) BETWEEN 1 AND 100),
    storage_location TEXT NOT NULL CHECK (length(trim(storage_location)) BETWEEN 1 AND 100),
    found_date TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '' CHECK (length(description) <= 2000),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_items_category ON items (category);
