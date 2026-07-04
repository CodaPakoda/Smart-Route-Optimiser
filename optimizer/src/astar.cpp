#include "astar.h"

struct PQEntry {
    int node;
    double f_score;
    bool operator>(const PQEntry& other) const { return f_score > other.f_score; }
};

double astar(const Graph& graph, int start, int goal, vector<int>& path_out,
             const CongestionModel* congestion,
             const string& day_type,
             int hour,
             double assumed_speed_mps) {
    unordered_map<int, double> g_score;
    unordered_map<int, int> came_from;
    priority_queue<PQEntry, vector<PQEntry>, greater<PQEntry>> open_set;

    for (const auto& [id, node] : graph.nodes) {
        g_score[id] = numeric_limits<double>::infinity();
    }
    g_score[start] = 0.0;

    auto heuristic = [&](int a, int b) -> double {
        const Node& na = graph.nodes.at(a);
        const Node& nb = graph.nodes.at(b);
        double dist_m = haversine(na.lat, na.lng, nb.lat, nb.lng);
        return dist_m / assumed_speed_mps;
    };

    open_set.push({start, heuristic(start, goal)});
    unordered_map<int, bool> visited;

    while (!open_set.empty()) {
        int current = open_set.top().node;
        open_set.pop();

        if (visited[current]) continue;
        visited[current] = true;

        if (current == goal) {
            path_out.clear();
            int node = goal;
            while (came_from.find(node) != came_from.end()) {
                path_out.push_back(node);
                node = came_from[node];
            }
            path_out.push_back(start);
            reverse(path_out.begin(), path_out.end());
            return g_score[goal];
        }

        auto it = graph.adjacency.find(current);
        if (it == graph.adjacency.end()) continue;

        const Node& currentNode = graph.nodes.at(current);

        for (const Edge& edge : it->second) {
            double edgeTime = edge.time_sec;

            if (congestion != nullptr) {
                const Node& toNode = graph.nodes.at(edge.to);
                double multFrom = congestion->getMultiplierForPoint(currentNode.lat, currentNode.lng, day_type, hour);
                double multTo = congestion->getMultiplierForPoint(toNode.lat, toNode.lng, day_type, hour);
                double mult = max(multFrom, multTo); // worst case if either end is congested
                edgeTime *= mult;
            }

            double tentative_g = g_score[current] + edgeTime;
            if (tentative_g < g_score[edge.to]) {
                g_score[edge.to] = tentative_g;
                came_from[edge.to] = current;
                open_set.push({edge.to, tentative_g + heuristic(edge.to, goal)});
            }
        }
    }

    return -1.0;
}