const express = require('express');
const router = express.Router();
const db = require('../db/connection');

router.get('/stop-candidates', (req, res) => {
    const rows = db.prepare('SELECT node_id, lat, lng FROM nodes WHERE is_stop_candidate = 1').all();
    res.json(rows);
});

module.exports = router;