#pragma once
#include <bits/stdc++.h>
using namespace std;
#include "graph.h"
#include "congestion.h"

double astar(const Graph& graph, int start, int goal, vector<int>& path_out,
             const CongestionModel* congestion = nullptr,
             const string& day_type = "",
             int hour = -1,
             double assumed_speed_mps = 11.0);