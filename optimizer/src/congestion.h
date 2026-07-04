#pragma once
#include <bits/stdc++.h>
using namespace std;
#include "graph.h"

struct CongestedArea {
    int id;
    double lat;
    double lng;
    double radius_meters;
    double base_congestion_level; // descriptive/reporting only, not used in calc
};

struct TrafficPattern {
    int area_id;
    string day_type;   // "weekday" or "weekend"
    int hour_start;
    int hour_end;
    double multiplier;
};

class CongestionModel {
public:
    vector<CongestedArea> areas;
    vector<TrafficPattern> patterns;

    // Looks up the active multiplier for a specific area at a given day_type/hour.
    // Returns 1.0 (no congestion effect) if no pattern matches.
    double getMultiplierForArea(int area_id, const string& day_type, int hour) const {
        for (const auto& p : patterns) {
            if (p.area_id == area_id && p.day_type == day_type &&
                hour >= p.hour_start && hour < p.hour_end) {
                return p.multiplier;
            }
        }
        return 1.0;
    }

    // Checks a point (lat/lng) against all congested areas, returns the worst
    // (max) applicable multiplier for the given day_type/hour.
    double getMultiplierForPoint(double lat, double lng, const string& day_type, int hour) const {
        double best = 1.0;
        for (const auto& area : areas) {
            double dist = haversine(lat, lng, area.lat, area.lng);
            if (dist <= area.radius_meters) {
                double m = getMultiplierForArea(area.id, day_type, hour);
                best = max(best, m);
            }
        }
        return best;
    }
};