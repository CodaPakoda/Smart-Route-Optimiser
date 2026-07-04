CREATE TABLE nodes (
    node_id INTEGER PRIMARY KEY,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    is_stop_candidate INTEGER NOT NULL DEFAULT 0,
    label TEXT
);

CREATE TABLE edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node_id INTEGER NOT NULL REFERENCES nodes(node_id),
    to_node_id INTEGER NOT NULL REFERENCES nodes(node_id),
    distance_m REAL NOT NULL,
    base_time_sec REAL NOT NULL
);

CREATE TABLE congested_areas (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL REFERENCES nodes(node_id),
    name TEXT,
    severity_tier TEXT NOT NULL CHECK(severity_tier IN ('low','medium','high')),
    radius_meters REAL NOT NULL,
    base_congestion_level REAL NOT NULL
);

CREATE TABLE traffic_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_id INTEGER NOT NULL REFERENCES congested_areas(id),
    day_type TEXT NOT NULL CHECK(day_type IN ('weekday','weekend')),
    hour_start INTEGER NOT NULL,
    hour_end INTEGER NOT NULL,
    congestion_multiplier REAL NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT
);

CREATE TABLE saved_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    node_id INTEGER NOT NULL REFERENCES nodes(node_id),
    label TEXT
);

CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    stops_json TEXT NOT NULL,
    ordered_route_json TEXT,
    naive_time_sec REAL,
    optimized_time_sec REAL,
    day_type TEXT,
    hour_used INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);