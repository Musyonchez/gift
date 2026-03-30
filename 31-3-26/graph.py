"""
graph.py — Nairobi Matatu Network Graph
DSA 2020: Introduction to Artificial Intelligence — Project 2
"""

# ── Node coordinates (latitude, longitude) ──────────────────────────────────
# 15 real Nairobi stops used as nodes in the matatu network
COORDINATES = {
    "CBD":        (-1.2833, 36.8167),
    "Westlands":  (-1.2675, 36.8040),
    "Parklands":  (-1.2600, 36.8100),
    "Eastleigh":  (-1.2722, 36.8500),
    "TRM":        (-1.2197, 36.8753),  # Thika Road Mall
    "Kasarani":   (-1.2167, 36.8917),
    "South_B":    (-1.3069, 36.8367),
    "South_C":    (-1.3167, 36.8167),
    "Langata":    (-1.3400, 36.7450),
    "Karen":      (-1.3167, 36.7133),
    "Rongai":     (-1.3933, 36.7467),
    "Ngong_Road": (-1.3000, 36.7950),
    "Embakasi":   (-1.3200, 36.8950),
    "Donholm":    (-1.2975, 36.8700),
    "Kikuyu":     (-1.2483, 36.6600),
    "Ngong_Town": (-1.3683, 36.6583),
}

# ── Edges (undirected) ───────────────────────────────────────────────────────
# Each tuple: (stop_a, stop_b, distance_km)
# Based on approximate matatu route distances in Nairobi
EDGES = [
    ("CBD",        "Westlands",  5),
    ("CBD",        "Parklands",  3),
    ("CBD",        "Eastleigh",  4),
    ("CBD",        "South_B",    6),
    ("CBD",        "Ngong_Road", 5),
    ("CBD",        "Donholm",    9),
    ("Westlands",  "Parklands",  2),
    ("Westlands",  "Kikuyu",    16),
    ("Westlands",  "TRM",        9),
    ("Parklands",  "Eastleigh",  4),
    ("Eastleigh",  "TRM",        8),
    ("Eastleigh",  "Kasarani",  10),
    ("TRM",        "Kasarani",   4),
    ("South_B",    "South_C",    2),
    ("South_B",    "Donholm",    6),
    ("South_C",    "Langata",    6),
    ("South_C",    "Ngong_Road", 4),
    ("Langata",    "Karen",      5),
    ("Karen",      "Ngong_Road", 9),
    ("Karen",      "Rongai",     8),
    ("Karen",      "Ngong_Town", 7),
    ("Rongai",     "Ngong_Town", 7),
    ("Donholm",    "Embakasi",   4),
    ("Kikuyu",     "Ngong_Town", 12),
]


def build_graph():
    """Build adjacency list from edge list. Returns dict: node -> [(neighbor, cost)]."""
    graph = {node: [] for node in COORDINATES}
    for a, b, dist in EDGES:
        graph[a].append((b, dist))
        graph[b].append((a, dist))
    return graph


def get_nodes():
    return list(COORDINATES.keys())


def get_edges():
    return EDGES


def path_cost(graph, path):
    """Return total distance (km) for a given path (list of node names)."""
    total = 0
    for i in range(len(path) - 1):
        neighbors = dict(graph[path[i]])
        if path[i + 1] in neighbors:
            total += neighbors[path[i + 1]]
        else:
            return float('inf')
    return total


if __name__ == "__main__":
    g = build_graph()
    print(f"Nodes ({len(COORDINATES)}): {', '.join(COORDINATES.keys())}")
    print(f"Edges: {len(EDGES)}")
    for node, neighbors in g.items():
        print(f"  {node}: {neighbors}")
