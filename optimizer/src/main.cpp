#include <bits/stdc++.h>
using namespace std;
#include "json.hpp"
#include "graph.h"
#include "astar.h"
#include "matrix.h"
#include "nearest_neighbor.h"
#include "two_opt.h"
#include "congestion.h"

using json = nlohmann::json;

int main() {
    // ---- Read entire stdin into a string, then parse as JSON ----
    stringstream buffer;
    buffer << cin.rdbuf();
    json input = json::parse(buffer.str());

    // ---- Build graph from input ----
    Graph g;
    for (const auto& n : input["nodes"]) {
        g.addNode(n["id"].get<int>(), n["lat"].get<double>(), n["lng"].get<double>());
    }
    for (const auto& e : input["edges"]) {
        g.addEdge(e["from"].get<int>(), e["to"].get<int>(), e["time_sec"].get<double>());
    }

    // ---- Build congestion model from input ----
    CongestionModel congestion;
    for (const auto& a : input["congested_areas"]) {
        congestion.areas.push_back(CongestedArea{
            a["id"].get<int>(),
            a["lat"].get<double>(),
            a["lng"].get<double>(),
            a["radius_meters"].get<double>(),
            a["base_congestion_level"].get<double>()
        });
    }
    for (const auto& p : input["traffic_patterns"]) {
        congestion.patterns.push_back(TrafficPattern{
            p["area_id"].get<int>(),
            p["day_type"].get<string>(),
            p["hour_start"].get<int>(),
            p["hour_end"].get<int>(),
            p["multiplier"].get<double>()
        });
    }

    // ---- Read stops + context ----
    vector<int> stops;
    for (const auto& s : input["stops"]) {
        stops.push_back(s.get<int>());
    }
    string day_type = input["day_type"].get<string>();
    int hour = input["hour"].get<int>();

    // ---- Build congestion-adjusted distance matrix ----
    auto matrix = buildDistanceMatrix(g, stops, &congestion, day_type, hour);

    // ---- Naive: visit stops in input order ----
    vector<int> naiveOrder;
    for (int i = 0; i < (int)stops.size(); i++) naiveOrder.push_back(i);
    double naiveTime = computeRouteTime(matrix, naiveOrder);

    // ---- Optimized: nearest-neighbor + 2-opt ----
    vector<int> nnOrder = nearestNeighborOrder(matrix);
    vector<int> optimizedOrder = twoOptImprove(matrix, nnOrder);
    double optimizedTime = computeRouteTime(matrix, optimizedOrder);

    // ---- Build output JSON ----
    json output;

    auto orderToNodeIds = [&](const vector<int>& order) {
        vector<int> nodeIds;
        for (int idx : order) nodeIds.push_back(stops[idx]);
        return nodeIds;
    };

    output["naive_order"] = orderToNodeIds(naiveOrder);
    output["naive_time_sec"] = naiveTime;
    output["optimized_order"] = orderToNodeIds(optimizedOrder);
    output["optimized_time_sec"] = optimizedTime;

    if (naiveTime > 0) {
        output["improvement_pct"] = (naiveTime - optimizedTime) / naiveTime * 100.0;
    } else {
        output["improvement_pct"] = 0.0;
    }

    cout << output.dump(2) << endl;

    return 0;
}