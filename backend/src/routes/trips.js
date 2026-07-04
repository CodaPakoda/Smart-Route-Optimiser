const express = require('express');
const router = express.Router();
const db = require('../db/connection');

router.get('/trips', (req, res) => {
    const rows = db.prepare('SELECT * FROM trips ORDER BY created_at DESC LIMIT 20').all();
    res.json(rows);
});

module.exports = router;