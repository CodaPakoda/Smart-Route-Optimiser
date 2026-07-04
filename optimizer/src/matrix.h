#pragma once
#include <bits/stdc++.h>
using namespace std;
#include "graph.h"
#include "astar.h"
#include "congestion.h"

vector<vector<double>> buildDistanceMatrix(const Graph& graph, const vector<int>& stops,
                                            const CongestionModel* congestion = nullptr,
                                            const string& day_type = "",
                                            int hour = -1);