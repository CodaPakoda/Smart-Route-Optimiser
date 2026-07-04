const express = require('express');
const path = require('path');

const nodesRouter = require('./routes/nodes');
const optimizeRouter = require('./routes/optimize');
const tripsRouter = require('./routes/trips');

const app = express();
app.use(express.json());

// ---- View engine (serves the frontend page) ----
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// ---- Static assets (app.js, style.css) ----
app.use(express.static(path.join(__dirname, 'public')));

// ---- Page route ----
app.get('/', (req, res) => {
    res.render('index');
});

// ---- API routes ----
app.use('/api', nodesRouter);
app.use('/api', optimizeRouter);
app.use('/api', tripsRouter);

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`App running on http://localhost:${PORT}`);
});