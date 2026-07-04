#include "matrix.h"

vector<vector<double>> buildDistanceMatrix(const Graph& graph, const vector<int>& stops,
                                            const CongestionModel* congestion,
                                            const string& day_type,
                                            int hour) {
    int n = stops.size();
    vector<vector<double>> matrix(n, vector<double>(n, 0.0));

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i == j) {
                matrix[i][j] = 0.0;
                continue;
            }
            vector<int> path;
            double t = astar(graph, stops[i], stops[j], path, congestion, day_type, hour);
            matrix[i][j] = t;
        }
    }
    return matrix;
}