const { spawnSync } = require('child_process');
const path = require('path');

const OPTIMIZER_PATH = path.join(__dirname, '../../../optimizer/build/optimizer');

function runOptimizer(payload) {
    const result = spawnSync(OPTIMIZER_PATH, [], {
        input: JSON.stringify(payload),
        encoding: 'utf-8'
    });

    if (result.status !== 0) {
        throw new Error(`Optimizer failed: ${result.stderr}`);
    }

    return JSON.parse(result.stdout);
}

module.exports = { runOptimizer };