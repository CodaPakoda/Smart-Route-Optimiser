#pragma once
#include <bits/stdc++.h>
using namespace std;

// Given an NxN time matrix, returns a visiting order (indices into the matrix)
// starting from index 0, greedily picking the nearest unvisited stop each time.
vector<int> nearestNeighborOrder(const vector<vector<double>>& matrix);

// Computes total time of a given order (does NOT return to start - open path)
double computeRouteTime(const vector<vector<double>>& matrix, const vector<int>& order);