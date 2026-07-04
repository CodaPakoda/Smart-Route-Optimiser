import sqlite3
import pandas as pd
import os

DB_PATH = "backend/src/db/app.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ---- Apply schema ----
with open("backend/src/db/schema.sql") as f:
    cur.executescript(f.read())

# ---- Load nodes ----
nodes = pd.read_csv("data/raw/nodes.csv")
nodes.to_sql("nodes", conn, if_exists="append", index=False)

# ---- Load edges ----
edges = pd.read_csv("data/raw/edges.csv")
edges.to_sql("edges", conn, if_exists="append", index=False)

# ---- Load congested areas ----
congested_areas = pd.read_csv("data/raw/congested_areas.csv")
congested_areas.to_sql("congested_areas", conn, if_exists="append", index=False)

# ---- Load traffic patterns ----
traffic_patterns = pd.read_csv("data/raw/traffic_patterns.csv")
traffic_patterns.to_sql("traffic_patterns", conn, if_exists="append", index=False)

conn.commit()

# ---- Sanity check counts ----
for table in ["nodes", "edges", "congested_areas", "traffic_patterns"]:
    count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")

conn.close()
print(f"Database created at {DB_PATH}")