#include "nearest_neighbor.h"
#include <limits>

vector<int> nearestNeighborOrder(const vector<vector<double>>& matrix) {
    int n = matrix.size();
    vector<bool> visited(n, false);
    vector<int> order;

    int current = 0;
    visited[0] = true;
    order.push_back(0);

    for (int step = 1; step < n; step++) {
        double best = numeric_limits<double>::infinity();
        int best_idx = -1;

        for (int j = 0; j < n; j++) {
            if (!visited[j] && matrix[current][j] >= 0 && matrix[current][j] < best) {
                best = matrix[current][j];
                best_idx = j;
            }
        }

        if (best_idx == -1) break; // no reachable unvisited node left
        visited[best_idx] = true;
        order.push_back(best_idx);
        current = best_idx;
    }

    return order;
}

double computeRouteTime(const vector<vector<double>>& matrix, const vector<int>& order) {
    double total = 0.0;
    for (size_t i = 0; i + 1 < order.size(); i++) {
        double t = matrix[order[i]][order[i + 1]];
        if (t < 0) return -1.0; // broken path
        total += t;
    }
    return total;
}