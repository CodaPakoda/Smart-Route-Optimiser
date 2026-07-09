# Smart Route Optimizer

Congestion-aware multi-stop route optimization on a real road network, built with a C++ algorithmic core (A*, nearest-neighbor, 2-opt), a Node/Express backend, SQLite, and a vanilla JS + Leaflet frontend.

## Overview

Given a set of stops, this system computes the optimal visiting order and route, accounting for real road distances and time-dependent traffic congestion, then compares it against the naive (input-order) route. It's built on a real OpenStreetMap road network around India Gate, New Delhi.

**Application workflow:** select stops on the map, choose a day type and hour, and compare the naive and optimized routes with the resulting time savings.

## Screenshots

<table>
<tr>
<td width="50%"><img src="assets/screenshot-config.png" alt="Configuration panel" width="100%"></td>
<td width="50%"><img src="assets/screenshot-map.png" alt="Route visualization on map" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Configure stops, day type, and hour</sub></td>
<td align="center"><sub>Optimized route drawn on the real road network</sub></td>
</tr>
</table>

<p align="center">
  <img src="assets/screenshot-results.png" alt="Results and optimized visit order" width="85%">
  <br>
  <sub>Naive vs. optimized comparison, with the resulting visit order</sub>
</p>

## Architecture

```
Frontend (EJS + vanilla JS + Leaflet)
        │  REST (JSON)
        ▼
Backend (Node/Express)
   - queries SQLite for graph + congestion data
   - calls C++ optimizer as a subprocess (JSON via stdin/stdout)
   - persists trip history
        │
        ▼
C++ Optimizer Core
   1. A* - congestion-aware shortest path between any two nodes
   2. Nearest-neighbor - initial visiting order for all stops
   3. 2-opt - local search improvement over that order
        ▲
        │ reads from
SQLite Database
   nodes, edges, congested_areas, traffic_patterns, trips
        ▲
        │ one-time, offline
data/build_graph.py + data/analyze_kaggle_traffic.py + data/generate_congestion.py
   - OSMnx: real road network extraction
   - Kaggle traffic volume data: real hourly congestion curve
   - Seeded congestion zone placement, data-derived time multipliers
```

The dataset is built once, offline. The live app never calls external APIs; every request is just a DB lookup plus C++ computation. This avoids live rate-limit dependency and keeps the app fast and reproducible.

## Why these algorithms

- **A\* with a haversine heuristic**: finds the congestion-aware shortest path between any two nodes on the road graph. The heuristic biases search toward the goal instead of exploring uniformly in all directions like Dijkstra does, which matters once congestion zones create uneven edge weights across multiple possible routes.
- **Nearest-neighbor**: a greedy heuristic for building an initial stop-visiting order. Fast, but not optimal, since it can get locally stuck in a suboptimal order.
- **2-opt**: local search that iteratively reverses segments of the route if doing so reduces total time, correcting nearest-neighbor's mistakes.
- **Why not exact TSP?** Exact TSP (e.g. Held-Karp DP) is O(n²·2ⁿ), which is infeasible to compute per-request as stop counts grow. Nearest-neighbor + 2-opt is a standard, well-understood tradeoff that gives near-optimal results in polynomial time.

## Complexity analysis

Let V = nodes in the full road graph (374), E = edges (1,174), and n = number of stops in a single trip request (typically 5-12).

| Step | Complexity | Notes |
|---|---|---|
| A* (single pairwise query) | O(E log V) | Binary heap priority queue; explores a subset of V/E in practice, worst case bounds by full graph |
| Distance matrix build | O(n² · E log V) | Runs A* once for every ordered pair of stops |
| Nearest-neighbor | O(n²) | For each of n steps, scans up to n remaining candidates |
| 2-opt (one full pass) | O(n²) | Checks every pair of positions in the current route |
| 2-opt (to convergence) | O(k · n²) | k = number of improving passes until no swap helps; k is small in practice since n is small (≤ 15-20 stops) |

The distance matrix build dominates overall runtime, since it's the only step touching the full road graph (V, E) rather than just the small stop count (n). This is why the design keeps the *main node* set small (40 nodes) even though the underlying road graph is much larger (374 nodes): the algorithm's practical cost scales with how many stops a user picks per request, not with the size of the city graph.

Space complexity is dominated by the road graph itself (O(V + E) for the adjacency list) plus O(n²) for the distance matrix, both small enough to keep everything in memory for a single request.

## Dataset

| Property | Value |
|---|---|
| Location | India Gate area, New Delhi (1.5km radius) |
| Total road nodes | 374 |
| Total road edges | 1,174 (bidirectional) |
| Main nodes (selectable stops) | 40 (12 major / 18 medium / 10 minor junctions, ranked by degree, min. 150m spacing) |
| Congestion areas | 40 (randomly sampled from all 374 road nodes, independent of main nodes) |
| Traffic patterns | 1,920 (40 areas x 24 hours x 2 day types, one real data-derived multiplier per hour) |

**Data sources:**
- Road network: [OSMnx](https://osmnx.readthedocs.io/) extraction from OpenStreetMap (real intersections, real road distances and estimated travel times)
- Congestion timing: derived from the [Traffic Prediction Dataset](https://www.kaggle.com/datasets/hasibullahaman/traffic-prediction-dataset) on Kaggle, real vehicle-count data (cars, bikes, buses, trucks) collected via computer vision at a road intersection in 15-minute intervals over a month. `data/analyze_kaggle_traffic.py` computes the average traffic volume for every (day type, hour) combination and expresses it as a ratio to that day type's 24-hour baseline. `data/generate_congestion.py` reads this curve directly and applies it to every congestion area, scaled by that area's severity tier (low/medium/high).
- Congestion zone *locations* are still simulated: 40 nodes are randomly sampled from the road graph, since no real geographic congestion data exists for this specific area. The *timing and relative severity* of congestion at those zones is what's grounded in real data, not the zones' placement.
- Edges are treated as bidirectional (one-way street restrictions simplified) to guarantee route connectivity across any stop selection.

## Results

Naive (input order) vs. optimized (nearest-neighbor + 2-opt) route time, across varied stop counts and traffic conditions:

| Scenario | Stops | Day | Hour | Naive (min) | Optimized (min) | Improvement |
|---|---|---|---|---|---|---|
| A | 5 | Weekday | 9 | 6.4 | 6.4 | 0.0% |
| B | 8 | Weekday | 10 | 24.0 | 9.0 | 62.6% |
| C | 10 | Weekday | 18 | 29.8 | 14.5 | 51.3% |
| D | 6 | Weekend | 14 | 12.8 | 9.6 | 25.1% |
| E | 12 | Weekend | 19 | 37.6 | 18.4 | 51.2% |

Across representative test scenarios, the optimizer reduced total travel time by 25-63%, with an average improvement of approximately 47.5% where optimization opportunities existed. Scenario A shows 0% improvement; with only 5 stops, the naive input order happened to already be near-optimal for that particular combination, which is expected and realistic since not every input has room for improvement.

The naive baseline still uses real, congestion-aware A* pathfinding between each consecutive stop, it is not artificially weakened. The only difference between naive and optimized is whether the stop order itself is improved by nearest-neighbor + 2-opt.

## Tech stack

- **Algorithms/core**: C++17, CMake, [nlohmann/json](https://github.com/nlohmann/json)
- **Backend**: Node.js, Express, better-sqlite3
- **Frontend**: EJS, vanilla JS, Leaflet.js
- **Database**: SQLite
- **Data pipeline**: Python, OSMnx, pandas

## Setup

```bash
# 1. Build the C++ optimizer
cd optimizer
mkdir -p build && cd build
cmake .. && make
cd ../..

# 2. Build the dataset (one-time)
python3 data/build_graph.py
python3 data/analyze_kaggle_traffic.py
python3 data/generate_congestion.py
python3 data/load_db.py

# 3. Run the backend (serves frontend + API on same port)
cd backend
npm install
npm start
```

Open `http://localhost:3000/`.

Note: `data/analyze_kaggle_traffic.py` requires `data/raw/kaggle_traffic.csv`, downloaded separately from the [Traffic Prediction Dataset](https://www.kaggle.com/datasets/hasibullahaman/traffic-prediction-dataset) on Kaggle (not included in this repo).

## Limitations & future work

- Congestion zone *locations* are simulated (randomly sampled), not real; only the timing and relative severity of congestion is grounded in real data, as noted above.
- One-way street restrictions are ignored (edges treated as bidirectional) to guarantee connectivity across arbitrary stop selections.
- Congestion detection uses a simple radius check around zone centroids rather than real road-polyline intersection.
- Exact TSP (e.g. bitmask DP for small n) could replace the heuristic for very small stop counts where optimality matters more than speed.
- Precomputing full distance matrices for the whole main-node set (rather than per-request) could reduce latency further for high-traffic use.
- The C++/Node bridge uses one-shot subprocess calls; a long-running service with a persistent connection would remove per-request process-spawn overhead at larger scale.

## Project structure

```
route-optimiser/
├── data/              # dataset build scripts (OSMnx, Kaggle traffic analysis, congestion generation, DB loader)
├── optimizer/         # C++ core (A*, nearest-neighbor, 2-opt)
├── backend/           # Express server, API routes, SQLite, EJS frontend
├── assets/            # README screenshots
└── README.md
```