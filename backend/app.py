from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import networkx as nx
import random
from collections import deque

# ==============================================================================
# Flask App Setup
# ==============================================================================
app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


# ==============================================================================
# MODULE 1: ROUTE OPTIMIZATION (BFS, DFS, A*)
# ==============================================================================
# City network of Bangladesh
CITIES = ['Dhaka', 'Chittagong', 'Sylhet', 'Rajshahi', 'Khulna', 'Barisal', 'Rangpur']
EDGES = [
    ('Dhaka', 'Chittagong', 248),
    ('Dhaka', 'Sylhet', 241),
    ('Dhaka', 'Rajshahi', 255),
    ('Dhaka', 'Khulna', 289),
    ('Chittagong', 'Sylhet', 412),
    ('Rajshahi', 'Khulna', 234),
    ('Rajshahi', 'Rangpur', 110),
    ('Khulna', 'Barisal', 125)
]

# Build adjacency map for manual BFS/DFS
ADJ = {city: [] for city in CITIES}
for u, v, w in EDGES:
    ADJ[u].append((v, w))
    ADJ[v].append((u, w))

# Also build NetworkX graph for A*
G = nx.Graph()
G.add_nodes_from(CITIES)
for u, v, w in EDGES:
    G.add_edge(u, v, weight=w)

# --- Manual BFS Implementation ---
def bfs_path(start, end):
    """BFS: finds path with fewest number of stops (hops)"""
    if start == end:
        return [start]
    visited = {start}
    queue = deque([[start]])          # queue of paths
    while queue:
        path = queue.popleft()
        current = path[-1]
        for neighbor, _ in ADJ[current]:
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None

# --- Manual DFS Implementation ---
def dfs_path(start, end, visited=None, path=None):
    """DFS: explores deep routes first using recursion"""
    if visited is None:
        visited = set()
    if path is None:
        path = []
    visited.add(start)
    path = path + [start]
    if start == end:
        return path
    for neighbor, _ in ADJ[start]:
        if neighbor not in visited:
            result = dfs_path(neighbor, end, visited, path)
            if result:
                return result
    return None

@app.route('/api/find_route', methods=['POST'])
def get_route():
    data = request.json
    start_city = data.get('start')
    end_city   = data.get('end')
    algo       = data.get('algorithm')

    if not all([start_city, end_city, algo]):
        return jsonify({'error': 'Missing required fields'}), 400

    if start_city not in CITIES or end_city not in CITIES:
        return jsonify({'error': 'Invalid city name'}), 400

    try:
        if algo == 'bfs':
            path = bfs_path(start_city, end_city)
            algo_detail = "BFS uses a Queue. Explores level by level. Guarantees fewest stops."

        elif algo == 'dfs':
            path = dfs_path(start_city, end_city)
            algo_detail = "DFS uses Recursion (Stack). Explores deep paths first. Finds a valid path, not necessarily shortest."

        elif algo == 'astar':
            path = nx.astar_path(G, source=start_city, target=end_city, weight='weight')
            algo_detail = "A* uses f(n) = g(n) + h(n). Heuristic guides search. Guarantees shortest total distance."

        else:
            return jsonify({'error': 'Unknown algorithm. Use bfs, dfs, or astar'}), 400

        if not path:
            return jsonify({'error': f'No path found from {start_city} to {end_city}'}), 404

        # Calculate total distance
        total_distance = 0
        for i in range(len(path) - 1):
            if G.has_edge(path[i], path[i+1]):
                total_distance += G[path[i]][path[i+1]]['weight']

        return jsonify({
            'path': path,
            'total_distance': total_distance,
            'stops': len(path) - 1,
            'algorithm_detail': algo_detail
        })

    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        return jsonify({'error': str(e)}), 404


# ==============================================================================
# MODULE 2: FLEET SCHEDULING (GENETIC ALGORITHM - Pure Python)
# ==============================================================================
GA_CITIES     = ['Warehouse', 'Dhaka', 'Chittagong', 'Sylhet', 'Rajshahi']
DISTANCE_MAP  = [
    [0, 10,  8,  9,  7],
    [10, 0, 20, 21, 12],
    [8, 20,  0, 15, 17],
    [9, 21, 15,  0, 18],
    [7, 12, 17, 18,  0]
]
NUM_VEHICLES = 2

def calc_total_distance(individual):
    """Fitness function: total distance for all vehicle routes"""
    total  = 0
    routes = [[] for _ in range(NUM_VEHICLES)]
    for i, city_idx in enumerate(individual):
        routes[i % NUM_VEHICLES].append(city_idx)
    for route in routes:
        if not route:
            continue
        total += DISTANCE_MAP[0][route[0]]          # Warehouse → first city
        for i in range(len(route) - 1):
            total += DISTANCE_MAP[route[i]][route[i+1]]
        total += DISTANCE_MAP[route[-1]][0]          # last city → Warehouse
    return total

def tournament_select(population, k=3):
    """Select best individual from k random candidates"""
    candidates = random.sample(population, k)
    return min(candidates, key=calc_total_distance)

def ordered_crossover(p1, p2):
    """Combine two parent routes → one child route (preserves city order)"""
    size = len(p1)
    a, b = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[a:b] = p1[a:b]
    fill  = [x for x in p2 if x not in child]
    idx   = 0
    for i in range(size):
        if child[i] is None:
            child[i] = fill[idx]
            idx += 1
    return child

def mutate(individual, prob=0.15):
    """Randomly swap two cities with probability prob"""
    ind = individual[:]
    if random.random() < prob:
        i, j = random.sample(range(len(ind)), 2)
        ind[i], ind[j] = ind[j], ind[i]
    return ind

def run_genetic_algorithm():
    city_indices = list(range(1, len(GA_CITIES)))  # [1,2,3,4]
    POP_SIZE     = 60
    GENERATIONS  = 80

    # Step 1: Create initial population
    population = [random.sample(city_indices, len(city_indices)) for _ in range(POP_SIZE)]

    # Track the best solution found (Elitism)
    best = min(population, key=calc_total_distance)

    generation_log = []

    for gen in range(GENERATIONS):
        new_pop = [best[:]]    # Elitism: carry best into next generation
        while len(new_pop) < POP_SIZE:
            p1    = tournament_select(population)
            p2    = tournament_select(population)
            child = ordered_crossover(p1, p2)
            child = mutate(child)
            new_pop.append(child)
        population   = new_pop
        current_best = min(population, key=calc_total_distance)
        if calc_total_distance(current_best) < calc_total_distance(best):
            best = current_best[:]

        # Log every 20th generation for display
        if gen % 20 == 0 or gen == GENERATIONS - 1:
            generation_log.append({
                'generation': gen + 1,
                'best_distance': calc_total_distance(best)
            })

    return best, calc_total_distance(best), generation_log

@app.route('/api/schedule_fleet', methods=['POST'])
def schedule_fleet():
    try:
        best_individual, total_distance, gen_log = run_genetic_algorithm()

        routes = [[] for _ in range(NUM_VEHICLES)]
        for i, city_idx in enumerate(best_individual):
            routes[i % NUM_VEHICLES].append(GA_CITIES[city_idx])

        final_routes = {}
        for i, route in enumerate(routes):
            if route:
                final_routes[f"Vehicle {i+1}"] = ["Warehouse"] + route + ["Warehouse"]

        return jsonify({
            'best_schedule':   final_routes,
            'total_distance':  total_distance,
            'generation_log':  gen_log,
            'algorithm_detail': "Genetic Algorithm: Population=60, Generations=80, Crossover=Ordered, Mutation=Swap (15%)"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==============================================================================
# MODULE 3: DRONE FREQUENCY ZONING (GRAPH COLORING)
# ==============================================================================
@app.route('/api/drone_frequency', methods=['POST'])
def drone_frequency():
    data      = request.json
    zones     = data.get('zones',     ['Z1','Z2','Z3','Z4','Z5'])
    conflicts = data.get('conflicts', [
        ['Z1','Z2'], ['Z2','Z3'], ['Z3','Z4'],
        ['Z1','Z3'], ['Z4','Z5']
    ])

    # Build conflict (adjacency) graph
    conflict_graph = {z: [] for z in zones}
    for a, b in conflicts:
        if a in conflict_graph and b in conflict_graph:
            conflict_graph[a].append(b)
            conflict_graph[b].append(a)

    # Greedy Graph Coloring — assign minimum frequencies
    frequencies = {}
    all_freqs   = [
        'Freq-1 (2.4 GHz)',
        'Freq-2 (5.8 GHz)',
        'Freq-3 (900 MHz)',
        'Freq-4 (433 MHz)'
    ]

    coloring_steps = []
    for zone in zones:
        # Frequencies already used by neighboring zones
        used = {frequencies[n] for n in conflict_graph[zone] if n in frequencies}
        assigned = None
        for freq in all_freqs:
            if freq not in used:
                frequencies[zone] = freq
                assigned = freq
                break
        coloring_steps.append({
            'zone':           zone,
            'neighbors':      conflict_graph[zone],
            'blocked_freqs':  list(used),
            'assigned_freq':  assigned
        })

    return jsonify({
        'frequency_assignment':   frequencies,
        'total_frequencies_used': len(set(frequencies.values())),
        'coloring_steps':         coloring_steps,
        'conflict_edges':         conflicts,
        'algorithm_detail':       "Graph Coloring: Adjacent zones get different frequencies. Greedy approach assigns minimum frequencies needed."
    })

# ==============================================================================
# MODULE 4: CONTRACT BIDDING (MINIMAX + ALPHA-BETA PRUNING)
# ==============================================================================
def minimax(depth, is_maximizing, alpha, beta, contract_value, current_bid, ai_budget):
    if depth == 0 or current_bid >= contract_value:
        return contract_value - current_bid if current_bid <= contract_value else -current_bid
 
    if is_maximizing:
        best = -float('inf')
        for increment in [5, 10, 20]:
            new_bid = current_bid + increment
            if new_bid > ai_budget: continue
            score = minimax(depth-1, False, alpha, beta, contract_value, new_bid, ai_budget)
            best  = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best
    else:
        best = float('inf')
        for increment in [5, 10, 15]:
            new_bid = current_bid + increment
            score   = minimax(depth-1, True, alpha, beta, contract_value, new_bid, ai_budget)
            best    = min(best, score)
            beta    = min(beta, best)
            if beta <= alpha: break
        return best
 
@app.route('/api/bid_contract', methods=['POST'])
def bid_contract():
    data           = request.json
    contract_value = data.get('contract_value', 100)
    ai_budget      = data.get('ai_budget', 120)
    current_bid    = data.get('current_bid', 0)
 
    best_score = -float('inf')
    best_move  = 5
 
    for increment in [5, 10, 20]:
        new_bid = current_bid + increment
        if new_bid > ai_budget: continue
        score = minimax(4, False, -float('inf'), float('inf'), contract_value, new_bid, ai_budget)
        if score > best_score:
            best_score = score
            best_move  = increment
 
    recommended_bid = current_bid + best_move
    return jsonify({
        'recommended_bid':  recommended_bid,
        'expected_profit':  best_score,
        'strategy':         f"Bid ${recommended_bid} — Minimax evaluated all outcomes. Alpha-Beta pruning skipped unnecessary branches.",
        'algorithm_detail': "Minimax depth=4. AI=Maximizer, Competitor=Minimizer. Alpha-Beta cuts branches where β ≤ α."
    })
 
 
# ==============================================================================
# MODULE 5: WAREHOUSE MANAGEMENT (BACKTRACKING)
# ==============================================================================
WAREHOUSE_ZONES = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
HAZARDOUS       = ['Chemicals', 'Explosives', 'Flammables']
ZONE_ADJACENCY  = {
    'Zone A': ['Zone B'],
    'Zone B': ['Zone A', 'Zone C'],
    'Zone C': ['Zone B', 'Zone D'],
    'Zone D': ['Zone C']
}
 
def is_safe(assignment, zone, item):
    if item in HAZARDOUS:
        for adj_zone in ZONE_ADJACENCY.get(zone, []):
            placed = [k for k, v in assignment.items() if v == adj_zone]
            for placed_item in placed:
                if placed_item in HAZARDOUS:
                    return False
    return True
 
def backtrack(items, zones, assignment, steps):
    if len(assignment) == len(items):
        return assignment
    item = items[len(assignment)]
    for zone in zones:
        if zone not in assignment.values():
            safe = is_safe(assignment, zone, item)
            steps.append({
                'item': item, 'zone_tried': zone,
                'result': 'assigned' if safe else 'conflict — backtrack'
            })
            if safe:
                assignment[item] = zone
                result = backtrack(items, zones, assignment, steps)
                if result: return result
                del assignment[item]
    return None
 
@app.route('/api/warehouse_placement', methods=['POST'])
def warehouse_placement():
    data  = request.json
    items = data.get('items', ['Chemicals', 'Electronics', 'Explosives', 'Food'])
 
    if len(items) > 4:
        return jsonify({'status': 'Error', 'message': 'Max 4 items (4 zones available)'}), 400
 
    steps      = []
    assignment = {}
    result     = backtrack(items, WAREHOUSE_ZONES, assignment, steps)
 
    if result:
        return jsonify({
            'status':           'Success',
            'placement':        result,
            'backtrack_steps':  steps,
            'algorithm_detail': "Backtracking: tries each zone, backtracks on constraint violation. Hazardous items cannot be adjacent."
        })
    else:
        return jsonify({
            'status':  'No valid placement found',
            'message': 'Too many hazardous items for available non-adjacent zones.'
        }), 400
 
 
# ==============================================================================
# MODULE 6: RISK & DELAY PREDICTION (BAYESIAN NETWORK)
# ==============================================================================
@app.route('/api/predict_risk', methods=['POST'])
def predict_risk():
    data            = request.json
    weather_bad     = data.get('weather_bad',     False)
    high_demand     = data.get('high_demand',      False)
    port_congestion = data.get('port_congestion',  False)
 
    # Prior probability of delay
    p_delay = 0.10
 
    # Conditional probabilities (from Bayesian tables)
    if weather_bad:     p_delay += 0.35
    if high_demand:     p_delay += 0.20
    if port_congestion: p_delay += 0.25
 
    p_delay    = min(round(p_delay, 2), 0.99)
    risk_level = 'Low' if p_delay < 0.30 else ('Medium' if p_delay < 0.60 else 'High')
    extra_cost = round(1000 * p_delay, 2)
 
    # Probability breakdown
    breakdown = {
        'P(Delay) base':              '10%',
        'P(Delay | Bad Weather)':     '+35%' if weather_bad     else '0%',
        'P(Delay | High Demand)':     '+20%' if high_demand     else '0%',
        'P(Delay | Port Congestion)': '+25%' if port_congestion else '0%',
    }
 
    return jsonify({
        'delay_probability':    round(p_delay * 100, 1),
        'risk_level':           risk_level,
        'estimated_extra_cost': extra_cost,
        'probability_breakdown': breakdown,
        'contributing_factors': {
            'bad_weather':     weather_bad,
            'high_demand':     high_demand,
            'port_congestion': port_congestion
        },
        'recommendation': (
            'HIGH RISK: Consider alternative routes and add buffer time.'
            if p_delay >= 0.60 else
            'MEDIUM RISK: Monitor closely. Have contingency plan ready.'
            if p_delay >= 0.30 else
            'LOW RISK: Operations look stable. Proceed as planned.'
        ),
        'algorithm_detail': "Bayesian Network: P(Delay | Weather, Demand, Congestion). Conditional probability tables used for inference."
    })

# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True)