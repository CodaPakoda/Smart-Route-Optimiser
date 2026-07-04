import sqlite3
import json
import subprocess

DB_PATH = "backend/src/db/app.db"
OPTIMIZER_BINARY = "optimizer/build/optimizer"

# ---- Config for this test run ----
STOP_NODE_IDS = None  # if None, we'll auto-pick some below
NUM_STOPS = 8
DAY_TYPE = "weekday"
HOUR = 10

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ---- Load nodes (full graph, needed for A* traversal) ----
cur.execute("SELECT node_id, lat, lng FROM nodes")
nodes = [{"id": row[0], "lat": row[1], "lng": row[2]} for row in cur.fetchall()]

# ---- Load edges ----
cur.execute("SELECT from_node_id, to_node_id, base_time_sec FROM edges")
edges = [{"from": row[0], "to": row[1], "time_sec": row[2]} for row in cur.fetchall()]

# ---- Load congested areas ----
cur.execute("""
    SELECT ca.id, n.lat, n.lng, ca.radius_meters, ca.base_congestion_level
    FROM congested_areas ca
    JOIN nodes n ON ca.node_id = n.node_id
""")
congested_areas = [
    {"id": row[0], "lat": row[1], "lng": row[2], "radius_meters": row[3], "base_congestion_level": row[4]}
    for row in cur.fetchall()
]

# ---- Load traffic patterns ----
cur.execute("SELECT area_id, day_type, hour_start, hour_end, congestion_multiplier FROM traffic_patterns")
traffic_patterns = [
    {"area_id": row[0], "day_type": row[1], "hour_start": row[2], "hour_end": row[3], "multiplier": row[4]}
    for row in cur.fetchall()
]

# ---- Pick stops (only from stop candidates) ----
cur.execute("SELECT node_id FROM nodes WHERE is_stop_candidate = 1")
stop_candidate_ids = [row[0] for row in cur.fetchall()]

conn.close()

if STOP_NODE_IDS is None:
    step = max(1, len(stop_candidate_ids) // NUM_STOPS)
    stops = stop_candidate_ids[::step][:NUM_STOPS]
else:
    stops = STOP_NODE_IDS

print(f"Using stops: {stops}")

# ---- Assemble payload ----
payload = {
    "nodes": nodes,
    "edges": edges,
    "congested_areas": congested_areas,
    "traffic_patterns": traffic_patterns,
    "stops": stops,
    "day_type": DAY_TYPE,
    "hour": HOUR
}

# ---- Call the optimizer binary ----
result = subprocess.run(
    [OPTIMIZER_BINARY],
    input=json.dumps(payload),
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("Optimizer failed:")
    print(result.stderr)
else:
    output = json.loads(result.stdout)
    print(json.dumps(output, indent=2))