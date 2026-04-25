// ==============================================================================
// MODULE 1: ROUTE OPTIMIZATION (BFS / DFS / A*)
// ==============================================================================
const cities = ['Dhaka', 'Chittagong', 'Sylhet', 'Rajshahi', 'Khulna', 'Barisal', 'Rangpur'];

window.onload = function () {
    const startSel = document.getElementById('start-city');
    const endSel   = document.getElementById('end-city');
    if (startSel && endSel) {
        cities.forEach(city => {
            startSel.add(new Option(city, city));
            endSel.add(new Option(city, city));
        });
        // Default: Dhaka → Khulna
        startSel.value = 'Dhaka';
        endSel.value   = 'Khulna';
    }
};

async function findRoute() {
    const startCity = document.getElementById('start-city').value;
    const endCity   = document.getElementById('end-city').value;
    const algorithm = document.getElementById('algorithm').value;
    const resultDiv = document.getElementById('result');

    if (startCity === endCity) {
        resultDiv.innerHTML = `<div class="result-box error">⚠️ Start and End cities cannot be the same.</div>`;
        return;
    }

    const algoNames = { bfs: 'BFS', dfs: 'DFS', astar: 'A*' };
    resultDiv.innerHTML = `<span class="loading">🔍 Running ${algoNames[algorithm]} Algorithm...</span>`;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/find_route', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ start: startCity, end: endCity, algorithm })
        });
        const data = await response.json();

        if (data.path) {
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <strong>✅ Route Found!</strong><br><br>
                    <strong>Path:</strong> ${data.path.join(' → ')}<br>
                    <strong>Total Distance:</strong> ${data.total_distance} km<br>
                    <strong>Stops:</strong> ${data.stops}<br><br>
                    <span class="algo-detail">📌 ${data.algorithm_detail}</span>
                </div>`;
        } else {
            resultDiv.innerHTML = `<div class="result-box error">❌ ${data.error || 'No path found.'}</div>`;
        }
    } catch (err) {
        resultDiv.innerHTML = `<div class="result-box error">❌ Cannot connect to server. Is Flask running?</div>`;
    }
}


// ==============================================================================
// MODULE 2: FLEET SCHEDULING (GENETIC ALGORITHM)
// ==============================================================================
async function scheduleFleet() {
    const resultDiv = document.getElementById('schedule-result');
    resultDiv.innerHTML = `<span class="loading">⏳ Running Genetic Algorithm (80 generations)... Please wait.</span>`;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/schedule_fleet', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({})
        });
        const data = await response.json();

        if (data.best_schedule) {
            // Build generation log table
            let genTable = '';
            if (data.generation_log && data.generation_log.length) {
                genTable = `<br><strong>Evolution Progress:</strong><br>`;
                data.generation_log.forEach(g => {
                    genTable += `&nbsp;&nbsp;Gen ${String(g.generation).padStart(3,'0')} → Best Distance: ${g.best_distance}<br>`;
                });
            }

            let routes = '';
            for (const [vehicle, route] of Object.entries(data.best_schedule)) {
                routes += `<strong>${vehicle}:</strong> ${route.join(' → ')}<br>`;
            }

            resultDiv.innerHTML = `
                <div class="result-box success">
                    <strong>✅ Optimal Schedule Found!</strong><br><br>
                    ${routes}
                    <br><strong>Total Distance:</strong> ${data.total_distance} units
                    ${genTable}
                    <br><span class="algo-detail">📌 ${data.algorithm_detail}</span>
                </div>`;
        } else {
            resultDiv.innerHTML = `<div class="result-box error">❌ ${data.error || 'Could not generate schedule.'}</div>`;
        }
    } catch (err) {
        resultDiv.innerHTML = `<div class="result-box error">❌ Cannot connect to server. Is Flask running?</div>`;
    }
}


// ==============================================================================
// MODULE 3: DRONE FREQUENCY ZONING (GRAPH COLORING)
// ==============================================================================
async function assignDroneFrequencies() {
    const resultDiv = document.getElementById('drone-result');
    resultDiv.innerHTML = `<span class="loading">📡 Running Graph Coloring Algorithm...</span>`;

    const zones     = ['Z1', 'Z2', 'Z3', 'Z4', 'Z5'];
    const conflicts = [['Z1','Z2'],['Z2','Z3'],['Z3','Z4'],['Z1','Z3'],['Z4','Z5']];

    try {
        const response = await fetch('http://127.0.0.1:5000/api/drone_frequency', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ zones, conflicts })
        });
        const data = await response.json();

        if (data.frequency_assignment) {
            // Build step-by-step coloring log
            let steps = '';
            if (data.coloring_steps) {
                steps = `<br><strong>Coloring Steps:</strong><br>`;
                data.coloring_steps.forEach(s => {
                    const blocked = s.blocked_freqs.length ? s.blocked_freqs.join(', ') : 'None';
                    steps += `&nbsp;&nbsp;<strong>${s.zone}</strong>: neighbors=[${s.neighbors.join(',')}] blocked=[${blocked}] → assigned <strong>${s.assigned_freq}</strong><br>`;
                });
            }

            let assignments = '';
            for (const [zone, freq] of Object.entries(data.frequency_assignment)) {
                assignments += `<strong>${zone}</strong> → ${freq}<br>`;
            }

            resultDiv.innerHTML = `
                <div class="result-box success">
                    <strong>✅ Frequency Assignment Complete!</strong><br><br>
                    ${assignments}
                    <br><strong>Total Frequencies Used:</strong> ${data.total_frequencies_used}
                    ${steps}
                    <br><span class="algo-detail">📌 ${data.algorithm_detail}</span>
                </div>`;
        } else {
            resultDiv.innerHTML = `<div class="result-box error">❌ ${data.error || 'Could not assign frequencies.'}</div>`;
        }
    } catch (err) {
        resultDiv.innerHTML = `<div class="result-box error">❌ Cannot connect to server. Is Flask running?</div>`;
    }
}
// ==============================================================================
// MODULE 4: CONTRACT BIDDING (MINIMAX + ALPHA-BETA PRUNING)
// ==============================================================================
async function bidContract() {
    const contractValue = parseInt(document.getElementById('contract-value').value) || 100;
    const aiBudget      = parseInt(document.getElementById('ai-budget').value)      || 120;
    const currentBid    = parseInt(document.getElementById('current-bid').value)    || 0;
    const resultDiv     = document.getElementById('bid-result');
 
    resultDiv.innerHTML = `<span class="loading">🤖 Running Minimax with Alpha-Beta Pruning...</span>`;
 
    try {
        const res  = await fetch('http://127.0.0.1:5000/api/bid_contract', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                contract_value: contractValue,
                ai_budget:      aiBudget,
                current_bid:    currentBid
            })
        });
        const data = await res.json();
 
        if (data.recommended_bid !== undefined) {
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <strong>✅ Optimal Bid Strategy Found!</strong><br><br>
                    <strong>Recommended Bid:</strong> $${data.recommended_bid}<br>
                    <strong>Expected Profit:</strong> $${data.expected_profit}<br>
                    <strong>Strategy:</strong> ${data.strategy}<br><br>
                    <span class="algo-detail">📌 ${data.algorithm_detail}</span>
                </div>`;
        } else {
            resultDiv.innerHTML = `<div class="result-box error">❌ ${data.error || 'Could not compute bid.'}</div>`;
        }
    } catch (err) {
        resultDiv.innerHTML = `<div class="result-box error">❌ Cannot connect to server. Is Flask running?</div>`;
    }
}
 
 
// ==============================================================================
// MODULE 5: WAREHOUSE MANAGEMENT (BACKTRACKING)
// ==============================================================================
async function placeWarehouseItems() {
    const itemsInput = document.getElementById('warehouse-items').value;
    const resultDiv  = document.getElementById('warehouse-result');
 
    const items = itemsInput.split(',').map(i => i.trim()).filter(i => i.length > 0);
 
    if (items.length === 0) {
        resultDiv.innerHTML = `<div class="result-box error">⚠️ Please enter at least one item.</div>`;
        return;
    }
    if (items.length > 4) {
        resultDiv.innerHTML = `<div class="result-box error">⚠️ Maximum 4 items allowed.</div>`;
        return;
    }
 
    resultDiv.innerHTML = `<span class="loading">🔄 Running Backtracking Algorithm...</span>`;
 
    try {
        const res  = await fetch('http://127.0.0.1:5000/api/warehouse_placement', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({items})
        });
        const data = await res.json();
 
        if (data.status === 'Success' && data.placement) {
            let placement = '';
            let steps     = '';
 
            for (const [item, zone] of Object.entries(data.placement)) {
                placement += `<strong>${item}</strong> → ${zone}<br>`;
            }
            if (data.backtrack_steps && data.backtrack_steps.length) {
                steps = `<br><strong>Backtracking Steps:</strong><br>`;
                data.backtrack_steps.forEach(s => {
                    steps += `&nbsp;&nbsp;${s.item} tried ${s.zone_tried} → ${s.result}<br>`;
                });
            }
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <strong>✅ Safe Placement Found!</strong><br><br>
                    ${placement}
                    ${steps}
                    <br><span class="algo-detail">📌 ${data.algorithm_detail}</span>
                </div>`;
        } else {
            resultDiv.innerHTML = `<div class="result-box error">❌ ${data.status} — ${data.message || 'Try fewer hazardous items.'}</div>`;
        }
    } catch (err) {
        resultDiv.innerHTML = `<div class="result-box error">❌ Cannot connect to server. Is Flask running?</div>`;
    }
}
 
 
// ==============================================================================
// MODULE 6: RISK & DELAY PREDICTION (BAYESIAN NETWORK)
// ==============================================================================
async function predictRisk() {
    const weatherBad     = document.getElementById('weather-bad').checked;
    const highDemand     = document.getElementById('high-demand').checked;
    const portCongestion = document.getElementById('port-congestion').checked;
    const resultDiv      = document.getElementById('risk-result');
 
    resultDiv.innerHTML = `<span class="loading">🌐 Running Bayesian Network Analysis...</span>`;
 
    try {
        const res  = await fetch('http://127.0.0.1:5000/api/predict_risk', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                weather_bad:     weatherBad,
                high_demand:     highDemand,
                port_congestion: portCongestion
            })
        });
        const data = await res.json();
 
        if (data.delay_probability !== undefined) {
            const boxClass = data.risk_level === 'High'   ? 'error'   :
                             data.risk_level === 'Medium' ? 'warning' : 'success';
 
            let breakdown = '';
            if (data.probability_breakdown) {
                breakdown = `<br><strong>Probability Breakdown:</strong><br>`;
                for (const [key, val] of Object.entries(data.probability_breakdown)) {
                    breakdown += `&nbsp;&nbsp;${key}: <strong>${val}</strong><br>`;
                }
            }
 
            resultDiv.innerHTML = `
                <div class="result-box ${boxClass}">
                    <strong>📊 Risk Analysis Complete!</strong><br><br>
                    <strong>Delay Probability:</strong> ${data.delay_probability}%<br>
                    <strong>Risk Level:</strong> ${data.risk_level}<br>
                    <strong>Estimated Extra Cost:</strong> $${data.estimated_extra_cost}<br>
                    <strong>Recommendation:</strong> ${data.recommendation}<br>
                    ${breakdown}
                    <br>🌧️ Bad Weather: ${data.contributing_factors.bad_weather ? 'Yes' : 'No'} &nbsp;|&nbsp;
                    📦 High Demand: ${data.contributing_factors.high_demand ? 'Yes' : 'No'} &nbsp;|&nbsp;
                    🚢 Port Congestion: ${data.contributing_factors.port_congestion ? 'Yes' : 'No'}<br><br>
                    <span class="algo-detail">📌 ${data.algorithm_detail}</span>
                </div>`;
        } else {
            resultDiv.innerHTML = `<div class="result-box error">❌ ${data.error || 'Could not predict risk.'}</div>`;
        }
    } catch (err) {
        resultDiv.innerHTML = `<div class="result-box error">❌ Cannot connect to server. Is Flask running?</div>`;
    }
}
 
