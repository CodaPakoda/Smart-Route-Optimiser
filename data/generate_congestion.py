import pandas as pd
import random

random.seed(42)

NUM_AREAS = 40

nodes = pd.read_csv("data/raw/nodes.csv")
all_node_ids = nodes["node_id"].tolist()

chosen_ids = random.sample(all_node_ids, NUM_AREAS)

tiers = (["low"] * 13) + (["medium"] * 13) + (["high"] * 14)
random.shuffle(tiers)

tier_config = {
    "low":    {"radius": (80, 120),  "level": (1.2, 1.4), "scale": 0.7},
    "medium": {"radius": (120, 180), "level": (1.4, 1.7), "scale": 1.0},
    "high":   {"radius": (180, 250), "level": (1.7, 2.2), "scale": 1.4},
}

# ---- Read the real hourly traffic curve (from Kaggle data, via analyze_kaggle_traffic.py) ----
hourly = pd.read_csv("data/raw/hourly_traffic_curve.csv")

# ---- Compute ratio-to-baseline for every (day_type, hour) directly from real data ----
hourly_ratios = {}
for day_type in ["weekday", "weekend"]:
    sub = hourly[hourly["day_type"] == day_type]
    baseline = sub["Total"].mean()
    for _, row in sub.iterrows():
        hourly_ratios[(day_type, int(row["hour"]))] = row["Total"] / baseline

areas = []
patterns = []
pattern_id = 1

for i, node_id in enumerate(chosen_ids):
    area_id = i + 1
    tier = tiers[i]
    cfg = tier_config[tier]
    radius = round(random.uniform(*cfg["radius"]), 1)
    base_level = round(random.uniform(*cfg["level"]), 2)
    scale = cfg["scale"]

    areas.append({
        "id": area_id,
        "node_id": node_id,
        "name": f"Zone_{area_id}_{tier}",
        "severity_tier": tier,
        "radius_meters": radius,
        "base_congestion_level": base_level
    })

    # One pattern per (day_type, hour) - full 24h curve, both day types
    for day_type in ["weekday", "weekend"]:
        for hour in range(24):
            ratio = hourly_ratios[(day_type, hour)]
            multiplier = 1 + (ratio - 1) * scale
            patterns.append({
                "id": pattern_id,
                "area_id": area_id,
                "day_type": day_type,
                "hour_start": hour,
                "hour_end": hour + 1,
                "congestion_multiplier": round(multiplier, 3)
            })
            pattern_id += 1

pd.DataFrame(areas).to_csv("data/raw/congested_areas.csv", index=False)
pd.DataFrame(patterns).to_csv("data/raw/traffic_patterns.csv", index=False)

print(f"Generated {len(areas)} congested areas and {len(patterns)} traffic patterns")
print(f"Patterns per area: 48 (24 hours x 2 day types), fully derived from data/raw/hourly_traffic_curve.csv")