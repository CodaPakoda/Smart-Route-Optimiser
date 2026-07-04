import sqlite3
import json
import subprocess
import random

DB_PATH = "backend/src/db/app.db"
OPTIMIZER_BINARY = "optimizer/build/optimizer"

random.seed(7)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT node_id, lat, lng FROM nodes")
nodes = [{"id": row[0], "lat": row[1], "lng": row[2]} for row in cur.fetchall()]

cur.execute("SELECT from_node_id, to_node_id, base_time_sec FROM edges")
edges = [{"from": row[0], "to": row[1], "time_sec": row[2]} for row in cur.fetchall()]

cur.execute("""
    SELECT ca.id, n.lat, n.lng, ca.radius_meters, ca.base_congestion_level
    FROM congested_areas ca
    JOIN nodes n ON ca.node_id = n.node_id
""")
congested_areas = [
    {"id": row[0], "lat": row[1], "lng": row[2], "radius_meters": row[3], "base_congestion_level": row[4]}
    for row in cur.fetchall()
]

cur.execute("SELECT area_id, day_type, hour_start, hour_end, congestion_multiplier FROM traffic_patterns")
traffic_patterns = [
    {"area_id": row[0], "day_type": row[1], "hour_start": row[2], "hour_end": row[3], "multiplier": row[4]}
    for row in cur.fetchall()
]

cur.execute("SELECT node_id FROM nodes WHERE is_stop_candidate = 1")
stop_candidate_ids = [row[0] for row in cur.fetchall()]
conn.close()

def run_scenario(num_stops, day_type, hour, label):
    stops = random.sample(stop_candidate_ids, num_stops)
    payload = {
        "nodes": nodes, "edges": edges,
        "congested_areas": congested_areas, "traffic_patterns": traffic_patterns,
        "stops": stops, "day_type": day_type, "hour": hour
    }
    result = subprocess.run(
        [OPTIMIZER_BINARY], input=json.dumps(payload), capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"{label}: FAILED - {result.stderr}")
        return None
    output = json.loads(result.stdout)
    print(f"{label}:")
    print(f"  Stops: {num_stops} | Day: {day_type} | Hour: {hour}")
    print(f"  Naive:     {output['naive_time_sec']/60:.1f} min")
    print(f"  Optimized: {output['optimized_time_sec']/60:.1f} min")
    print(f"  Improvement: {output['improvement_pct']:.1f}%")
    print()
    return output

scenarios = [
    (5, "weekday", 9, "Scenario A - 5 stops, weekday rush hour"),
    (8, "weekday", 10, "Scenario B - 8 stops, weekday mid-morning"),
    (10, "weekday", 18, "Scenario C - 10 stops, weekday evening rush"),
    (6, "weekend", 14, "Scenario D - 6 stops, weekend afternoon"),
    (12, "weekend", 19, "Scenario E - 12 stops, weekend evening"),
]

results = []
for num_stops, day_type, hour, label in scenarios:
    r = run_scenario(num_stops, day_type, hour, label)
    if r:
        results.append((label, num_stops, day_type, hour, r))

print("=" * 50)
print("SUMMARY TABLE")
print("=" * 50)
print(f"{'Scenario':<12}{'Stops':<8}{'Day':<10}{'Hour':<6}{'Naive(min)':<12}{'Opt(min)':<12}{'Improvement':<12}")
for label, num_stops, day_type, hour, r in results:
    short_label = label.split(" - ")[0]
    print(f"{short_label:<12}{num_stops:<8}{day_type:<10}{hour:<6}{r['naive_time_sec']/60:<12.1f}{r['optimized_time_sec']/60:<12.1f}{r['improvement_pct']:<12.1f}")