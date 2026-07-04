#pragma once
#include <bits/stdc++.h>
using namespace std;

struct Node {
    int id;
    double lat;
    double lng;
};

struct Edge {
    int to;
    double time_sec;
};

class Graph {
public:
    unordered_map<int, Node> nodes;
    unordered_map<int, vector<Edge>> adjacency;

    void addNode(int id, double lat, double lng) {
        nodes[id] = Node{id, lat, lng};
        if (adjacency.find(id) == adjacency.end()) {
            adjacency[id] = {};
        }
    }

    void addEdge(int from, int to, double time_sec) {
        adjacency[from].push_back(Edge{to, time_sec});
    }
};

inline double haversine(double lat1, double lng1, double lat2, double lng2) {
    constexpr double R = 6371000.0;
    double phi1 = lat1 * M_PI / 180.0;
    double phi2 = lat2 * M_PI / 180.0;
    double dphi = (lat2 - lat1) * M_PI / 180.0;
    double dlambda = (lng2 - lng1) * M_PI / 180.0;

    double a = sin(dphi / 2) * sin(dphi / 2) +
               cos(phi1) * cos(phi2) *
               sin(dlambda / 2) * sin(dlambda / 2);
    double c = 2 * atan2(sqrt(a), sqrt(1 - a));
    return R * c;
}