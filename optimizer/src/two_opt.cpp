#include "two_opt.h"
#include "nearest_neighbor.h" // for computeRouteTime

vector<int> twoOptImprove(const vector<vector<double>>& matrix, vector<int> order) {
    int n = order.size();
    bool improved = true;

    while (improved) {
        improved = false;
        double bestTime = computeRouteTime(matrix, order);

        for (int i = 1; i < n - 1; i++) {
            for (int j = i + 1; j < n; j++) {
                vector<int> newOrder = order;
                reverse(newOrder.begin() + i, newOrder.begin() + j + 1);

                double newTime = computeRouteTime(matrix, newOrder);
                if (newTime >= 0 && newTime < bestTime) {
                    order = newOrder;
                    bestTime = newTime;
                    improved = true;
                }
            }
        }
    }

    return order;
}