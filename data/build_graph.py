import osmnx as ox
import pandas as pd
import networkx as nx

# ---- Config ----
CENTER_POINT = (28.6129, 77.2295)  # India Gate, New Delhi
RADIUS_M = 1500
MAJOR_COUNT = 12
MEDIUM_COUNT = 18
MINOR_COUNT = 10  # total stop candidates = 40

# ---- Step 1: Download real road network ----
print(f"Downloading road network within {RADIUS_M}m of {CENTER_POINT}")
G = ox.graph_from_point(CENTER_POINT, dist=RADIUS_M, network_type="drive")

# ---- Step 2: Project to metric CRS, consolidate intersections, project back ----
G_proj = ox.project_graph(G)
G_proj = ox.consolidate_intersections(G_proj, tolerance=20, rebuild_graph=True, dead_ends=False)
G = ox.project_graph(G_proj, to_crs="EPSG:4326")

# ---- Step 3: Add real speed/travel time estimates ----
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# ---- Step 4: Convert to node/edge tables (NO trimming) ----
nodes, edges = ox.graph_to_gdfs(G)
nodes = nodes.reset_index()[["osmid", "y", "x"]]
nodes = nodes.rename(columns={"osmid": "node_id", "y": "lat", "x": "lng"})

# ---- Step 5: Tier nodes by degree into stop candidates, enforcing minimum spacing ----
MIN_SPACING_M = 150

degrees = dict(G.degree())
nodes["degree"] = nodes["node_id"].map(degrees)
nodes_sorted = nodes.sort_values("degree", ascending=False).reset_index(drop=True)

def select_spaced_nodes(candidates_df, count, already_selected_coords):
    selected_ids = []
    for _, row in candidates_df.iterrows():
        if len(selected_ids) >= count:
            break
        too_close = False
        for (slat, slng) in already_selected_coords:
            d = ox.distance.great_circle(row["lat"], row["lng"], slat, slng)
            if d < MIN_SPACING_M:
                too_close = True
                break
        if not too_close:
            selected_ids.append(row["node_id"])
            already_selected_coords.append((row["lat"], row["lng"]))
    return selected_ids

selected_coords = []  # shared across tiers so medium/minor don't crowd near majors either

major_ids = select_spaced_nodes(nodes_sorted, MAJOR_COUNT, selected_coords)
medium_ids = select_spaced_nodes(nodes_sorted[~nodes_sorted["node_id"].isin(major_ids)], MEDIUM_COUNT, selected_coords)
minor_ids = select_spaced_nodes(nodes_sorted[~nodes_sorted["node_id"].isin(major_ids + medium_ids)], MINOR_COUNT, selected_coords)

stop_candidate_ids = set(major_ids) | set(medium_ids) | set(minor_ids)

nodes["is_stop_candidate"] = nodes["node_id"].isin(stop_candidate_ids).astype(int)
nodes = nodes.drop(columns=["degree"])

print(f"Total nodes: {len(nodes)}, stop candidates: {nodes['is_stop_candidate'].sum()}")
print(f"Major: {len(major_ids)}, Medium: {len(medium_ids)}, Minor: {len(minor_ids)}")

# ---- Step 6: Build edges (full graph, bidirectional) ----
edges = edges.reset_index()[["u", "v", "length", "travel_time"]]
edges = edges.rename(columns={
    "u": "from_node_id", "v": "to_node_id",
    "length": "distance_m", "travel_time": "base_time_sec"
})

reverse_edges = edges.rename(columns={"from_node_id": "to_node_id", "to_node_id": "from_node_id"})
edges = pd.concat([edges, reverse_edges], ignore_index=True)
edges = edges.sort_values("distance_m").drop_duplicates(subset=["from_node_id", "to_node_id"], keep="first")

# ---- Step 7: Save outputs ----
nodes.to_csv("data/raw/nodes.csv", index=False)
edges.to_csv("data/raw/edges.csv", index=False)
print(f"Saved {len(nodes)} nodes and {len(edges)} edges to data/raw/")

# ---- Sanity check ----
undirected_G = G.to_undirected()
print(f"Connected components: {nx.number_connected_components(undirected_G)}")
print(f"Strongly connected components: {nx.number_strongly_connected_components(G)}")

# ---- Verify all stop candidates are mutually reachable ----
stop_ids = nodes[nodes["is_stop_candidate"] == 1]["node_id"].tolist()
scc_list = list(nx.strongly_connected_components(G))
largest_scc = max(scc_list, key=len)

stops_in_largest = [s for s in stop_ids if s in largest_scc]
stops_outside = [s for s in stop_ids if s not in largest_scc]

print(f"Stop candidates inside largest strongly-connected component: {len(stops_in_largest)}/{len(stop_ids)}")
if stops_outside:
    print(f"WARNING - stop candidates outside largest component: {stops_outside}")

# ---- Check spacing between stop candidates ----
stop_nodes_df = nodes[nodes["is_stop_candidate"] == 1]
coords = list(zip(stop_nodes_df["lat"], stop_nodes_df["lng"]))

min_dist = float("inf")
close_pairs = []
for i in range(len(coords)):
    for j in range(i + 1, len(coords)):
        d = ox.distance.great_circle(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
        if d < min_dist:
            min_dist = d
        if d < 100:  # flag anything under 100m apart
            close_pairs.append((stop_nodes_df.iloc[i]["node_id"], stop_nodes_df.iloc[j]["node_id"], round(d, 1)))

print(f"Minimum distance between any two stop candidates: {round(min_dist, 1)}m")
print(f"Pairs under 100m apart: {len(close_pairs)}")
if close_pairs:
    print(close_pairs[:10])