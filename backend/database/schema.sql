-- VibeMatch Event Quiz — Database Schema (SQLite 3 / PostgreSQL Compatible)
PRAGMA journal_mode = WAL;

-- Events Catalog
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    city TEXT NOT NULL,
    category TEXT NOT NULL,
    format TEXT NOT NULL,
    date_str TEXT NOT NULL,
    time_str TEXT,
    location TEXT NOT NULL,
    price TEXT DEFAULT 'Вход свободный / депозит',
    vibe TEXT,
    description TEXT NOT NULL,
    tags TEXT, -- JSON array of tags: ["IT", "Networking"]
    match_keywords TEXT, -- comma-separated search terms for fast matching
    url TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leads & Submitted Quizzes
CREATE TABLE IF NOT EXISTS quiz_leads (
    id TEXT PRIMARY KEY, -- UUID
    name TEXT NOT NULL,
    age TEXT NOT NULL,
    city TEXT NOT NULL,
    hobbies TEXT NOT NULL, -- JSON array
    event_types TEXT NOT NULL, -- JSON array
    ready_to_meet TEXT NOT NULL,
    utm_source TEXT DEFAULT 'direct',
    utm_id TEXT,
    ai_recommendation TEXT, -- Cached LLM response
    is_subscribed INTEGER DEFAULT 0,
    subscribed_channel TEXT, -- 'telegram' | 'max' | NULL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_events_city ON events(city);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_format ON events(format);
CREATE INDEX IF NOT EXISTS idx_events_active ON events(is_active);
CREATE INDEX IF NOT EXISTS idx_leads_created ON quiz_leads(created_at);
