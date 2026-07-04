const express = require('express');
const router = express.Router();
const db = require('../db/connection');
const { runOptimizer } = require('../services/optimizerBridge');

router.post('/optimize-route', (req, res) => {
    try {
        const { stops, day_type, hour } = req.body;

        if (!stops || stops.length < 2) {
            return res.status(400).json({ error: 'At least 2 stops are required' });
        }

        // ---- Load full graph (needed for A* traversal) ----
        const nodes = db.prepare('SELECT node_id as id, lat, lng FROM nodes').all();
        const edges = db.prepare('SELECT from_node_id as `from`, to_node_id as `to`, base_time_sec as time_sec FROM edges').all();

        // ---- Load congestion data ----
        const congested_areas = db.prepare(`
            SELECT ca.id, n.lat, n.lng, ca.radius_meters, ca.base_congestion_level
            FROM congested_areas ca
            JOIN nodes n ON ca.node_id = n.node_id
        `).all();

        const traffic_patterns = db.prepare(`
            SELECT area_id, day_type, hour_start, hour_end, congestion_multiplier as multiplier
            FROM traffic_patterns
        `).all();

        // ---- Build payload and call optimizer ----
        const payload = { nodes, edges, congested_areas, traffic_patterns, stops, day_type, hour };
        const result = runOptimizer(payload);

        // ---- Save trip ----
        const insert = db.prepare(`
            INSERT INTO trips (user_id, stops_json, ordered_route_json, naive_time_sec, optimized_time_sec, day_type, hour_used)
            VALUES (NULL, ?, ?, ?, ?, ?, ?)
        `);
        insert.run(
            JSON.stringify(stops),
            JSON.stringify(result.optimized_order),
            result.naive_time_sec,
            result.optimized_time_sec,
            day_type,
            hour
        );

        res.json(result);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;