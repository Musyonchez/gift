"""
algorithms.py — BFS, DFS, and A* Search Algorithms
DSA 2020: Introduction to Artificial Intelligence — Project 2
"""

import math
import heapq
from collections import deque
from graph import COORDINATES


# ── Heuristic ────────────────────────────────────────────────────────────────

def straight_line_distance(node, goal):
    """
    Straight-line (Euclidean) distance heuristic in km.
    Converts lat/lon to approximate km using the haversine-lite approach.
    1 degree latitude  ≈ 111 km
    1 degree longitude ≈ 111 * cos(mean_lat) km
    """
    lat1, lon1 = COORDINATES[node]
    lat2, lon2 = COORDINATES[goal]
    mean_lat = math.radians((lat1 + lat2) / 2)
    dlat = (lat2 - lat1) * 111.0
    dlon = (lon2 - lon1) * 111.0 * math.cos(mean_lat)
    return math.sqrt(dlat ** 2 + dlon ** 2)


# ── BFS ──────────────────────────────────────────────────────────────────────

def bfs(graph, start, goal):
    """
    Breadth-First Search — explores level by level (shallowest nodes first).
    Guarantees shortest path by number of hops (not necessarily lowest cost).

    Returns:
        path (list): ordered list of nodes from start to goal
        cost (float): total distance in km along the found path
        nodes_expanded (int): number of nodes popped from the frontier
    """
    frontier = deque()
    frontier.append((start, [start], 0.0))
    visited = {start}
    nodes_expanded = 0

    while frontier:
        node, path, cost = frontier.popleft()
        nodes_expanded += 1

        if node == goal:
            return path, cost, nodes_expanded

        for neighbor, weight in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append((neighbor, path + [neighbor], cost + weight))

    return None, float('inf'), nodes_expanded


# ── DFS ──────────────────────────────────────────────────────────────────────

def dfs(graph, start, goal):
    """
    Depth-First Search — explores deepest nodes first (LIFO stack).
    Does NOT guarantee an optimal (shortest) path.

    Returns:
        path (list): ordered list of nodes from start to goal
        cost (float): total distance in km along the found path
        nodes_expanded (int): number of nodes popped from the frontier
    """
    frontier = [(start, [start], 0.0)]
    visited = set()
    nodes_expanded = 0

    while frontier:
        node, path, cost = frontier.pop()

        if node in visited:
            continue
        visited.add(node)
        nodes_expanded += 1

        if node == goal:
            return path, cost, nodes_expanded

        for neighbor, weight in graph[node]:
            if neighbor not in visited:
                frontier.append((neighbor, path + [neighbor], cost + weight))

    return None, float('inf'), nodes_expanded


# ── A* ───────────────────────────────────────────────────────────────────────

def astar(graph, start, goal):
    """
    A* Search — uses f(n) = g(n) + h(n) to find the optimal least-cost path.
    Heuristic h(n): straight-line distance from n to goal (admissible).

    Returns:
        path (list): ordered list of nodes from start to goal
        cost (float): total distance in km along the found path
        nodes_expanded (int): number of nodes popped from the frontier
    """
    h_start = straight_line_distance(start, goal)
    # Priority queue entries: (f_score, tie_breaker, g_score, node, path)
    frontier = [(h_start, 0, 0.0, start, [start])]
    visited = set()
    nodes_expanded = 0
    counter = 1  # tie-breaker to avoid comparing paths

    while frontier:
        f, _, g, node, path = heapq.heappop(frontier)

        if node in visited:
            continue
        visited.add(node)
        nodes_expanded += 1

        if node == goal:
            return path, g, nodes_expanded

        for neighbor, weight in graph[node]:
            if neighbor not in visited:
                new_g = g + weight
                h = straight_line_distance(neighbor, goal)
                new_f = new_g + h
                heapq.heappush(frontier, (new_f, counter, new_g, neighbor, path + [neighbor]))
                counter += 1

    return None, float('inf'), nodes_expanded


# ── Quick test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from graph import build_graph

    g = build_graph()
    start, goal = "CBD", "Rongai"

    for name, fn in [("BFS", bfs), ("DFS", dfs), ("A*", astar)]:
        path, cost, expanded = fn(g, start, goal)
        print(f"{name:4s} | Path: {' -> '.join(path)}")
        print(f"       Cost: {cost:.1f} km | Nodes expanded: {expanded}\n")
