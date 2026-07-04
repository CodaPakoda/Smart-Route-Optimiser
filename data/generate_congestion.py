import pandas as pd
import random

random.seed(42)  # reproducible results

NUM_AREAS = 40
PATTERNS_PER_AREA = 3  # 40 * 3 = 120 total

nodes = pd.read_csv("data/raw/nodes.csv")
all_node_ids = nodes["node_id"].tolist()

chosen_ids = random.sample(all_node_ids, NUM_AREAS)

tiers = (["low"] * 13) + (["medium"] * 13) + (["high"] * 14)
random.shuffle(tiers)

tier_config = {
    "low":    {"radius": (80, 120),  "level": (1.2, 1.4)},
    "medium": {"radius": (120, 180), "level": (1.4, 1.7)},
    "high":   {"radius": (180, 250), "level": (1.7, 2.2)},
}

areas = []
patterns = []
pattern_id = 1

for i, node_id in enumerate(chosen_ids):
    area_id = i + 1
    tier = tiers[i]
    cfg = tier_config[tier]
    radius = round(random.uniform(*cfg["radius"]), 1)
    base_level = round(random.uniform(*cfg["level"]), 2)

    areas.append({
        "id": area_id,
        "node_id": node_id,
        "name": f"Zone_{area_id}_{tier}",
        "severity_tier": tier,
        "radius_meters": radius,
        "base_congestion_level": base_level
    })

    # Pattern 1: weekday morning rush
    patterns.append({
        "id": pattern_id, "area_id": area_id, "day_type": "weekday",
        "hour_start": 8, "hour_end": 11,
        "congestion_multiplier": round(base_level * random.uniform(1.0, 1.3), 2)
    })
    pattern_id += 1

    # Pattern 2: weekday evening rush
    patterns.append({
        "id": pattern_id, "area_id": area_id, "day_type": "weekday",
        "hour_start": 17, "hour_end": 20,
        "congestion_multiplier": round(base_level * random.uniform(1.0, 1.3), 2)
    })
    pattern_id += 1

    # Pattern 3: weekend (either midday or evening)
    if random.random() < 0.5:
        hs, he = 12, 15
    else:
        hs, he = 17, 21
    patterns.append({
        "id": pattern_id, "area_id": area_id, "day_type": "weekend",
        "hour_start": hs, "hour_end": he,
        "congestion_multiplier": round(base_level * random.uniform(0.9, 1.2), 2)
    })
    pattern_id += 1

pd.DataFrame(areas).to_csv("data/raw/congested_areas.csv", index=False)
pd.DataFrame(patterns).to_csv("data/raw/traffic_patterns.csv", index=False)

print(f"Generated {len(areas)} congested areas and {len(patterns)} traffic patterns")