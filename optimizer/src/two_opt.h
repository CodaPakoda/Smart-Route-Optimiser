#pragma once
#include <bits/stdc++.h>
using namespace std;

// Improves a route order using 2-opt local search. Returns improved order.
vector<int> twoOptImprove(const vector<vector<double>>& matrix, vector<int> order);