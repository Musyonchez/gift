"""
main.py — Nairobi Matatu Path Finder: Demo, Comparison & Visualization
DSA 2020: Introduction to Artificial Intelligence — Project 2

Run:
    python main.py

Outputs:
    - Console: route results + comparison table for 5 source-destination pairs
    - fig1_network.png        : full matatu network map
    - fig2_route_<n>.png      : highlighted route per query
    - fig3_comparison.png     : bar chart comparing algorithms
"""

import time
import math
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (saves to file)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from graph import build_graph, COORDINATES, EDGES
from algorithms import bfs, dfs, astar


# ── Helper: lat/lon → plot (x, y) ────────────────────────────────────────────
# Flip lat so north is up; scale to km-ish for readable axes
def to_xy(lat, lon, ref_lat=-1.2833, ref_lon=36.8167):
    x = (lon - ref_lon) * 111.0 * math.cos(math.radians(ref_lat))
    y = (ref_lat - lat) * 111.0   # flip: more negative lat = further south
    return x, y


NODE_XY = {node: to_xy(*coord) for node, coord in COORDINATES.items()}


# ── Visualization helpers ────────────────────────────────────────────────────

def draw_base_network(ax, title="Nairobi Matatu Network"):
    """Draw all nodes and edges on the given axes."""
    # Edges
    for a, b, dist in EDGES:
        x1, y1 = NODE_XY[a]
        x2, y2 = NODE_XY[b]
        ax.plot([x1, x2], [y1, y2], color="#cccccc", linewidth=1.2, zorder=1)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my, f"{dist}", fontsize=6, color="#999999",
                ha="center", va="center", zorder=2)

    # Nodes
    for node, (x, y) in NODE_XY.items():
        ax.scatter(x, y, s=80, color="steelblue", zorder=3)
        ax.text(x, y + 0.25, node.replace("_", " "), fontsize=7,
                ha="center", va="bottom", zorder=4)

    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("West  ←  km  →  East")
    ax.set_ylabel("South  ←  km  →  North")
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.3)


def draw_route(ax, path, color, label, linewidth=2.5):
    """Draw a specific path on the axes."""
    for i in range(len(path) - 1):
        x1, y1 = NODE_XY[path[i]]
        x2, y2 = NODE_XY[path[i + 1]]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color,
                                   lw=linewidth), zorder=5)
    # Highlight start and end
    sx, sy = NODE_XY[path[0]]
    gx, gy = NODE_XY[path[-1]]
    ax.scatter(sx, sy, s=150, color="green", zorder=6, label="Start")
    ax.scatter(gx, gy, s=150, color="red",   zorder=6, label="Goal")


# ── Figure 1: Full network map ────────────────────────────────────────────────

def save_network_map():
    fig, ax = plt.subplots(figsize=(10, 8))
    draw_base_network(ax, "Fig 1: Nairobi Matatu Network (15 Stops)")
    plt.tight_layout()
    plt.savefig("fig1_network.png", dpi=150)
    plt.close()
    print("Saved: fig1_network.png")


# ── Run one query and print results ──────────────────────────────────────────

def run_query(graph, start, goal, fig_index):
    """Run BFS, DFS, A* on a single source-goal pair. Print + save route plot."""
    print(f"\n{'='*60}")
    print(f"  Route: {start.replace('_',' ')} -> {goal.replace('_',' ')}")
    print(f"{'='*60}")

    results = {}
    colors  = {"BFS": "#e67e22", "DFS": "#8e44ad", "A*": "#27ae60"}

    for name, fn in [("BFS", bfs), ("DFS", dfs), ("A*", astar)]:
        t0 = time.perf_counter()
        path, cost, expanded = fn(graph, start, goal)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        results[name] = {
            "path":     path,
            "cost":     cost,
            "expanded": expanded,
            "time_ms":  elapsed_ms,
        }

        if path:
            route_str = " -> ".join(p.replace("_", " ") for p in path)
            print(f"\n  {name}")
            print(f"    Route   : {route_str}")
            print(f"    Cost    : {cost:.1f} km")
            print(f"    Expanded: {expanded} nodes")
            print(f"    Runtime : {elapsed_ms:.4f} ms")
        else:
            print(f"\n  {name}: No path found.")

    # Fig 2.x — route comparison plot
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle(
        f"Route: {start.replace('_',' ')} -> {goal.replace('_',' ')}",
        fontsize=13, fontweight="bold"
    )

    for ax, (name, res) in zip(axes, results.items()):
        draw_base_network(ax, title="")
        if res["path"]:
            draw_route(ax, res["path"], colors[name], name)
            cost_str  = f"{res['cost']:.1f} km"
            exp_str   = f"{res['expanded']} nodes expanded"
            time_str  = f"{res['time_ms']:.4f} ms"
        else:
            cost_str = exp_str = time_str = "N/A"

        patch = mpatches.Patch(color=colors[name], label=name)
        ax.legend(handles=[patch], loc="lower left", fontsize=8)
        ax.set_title(
            f"{name}\n{cost_str} | {exp_str}\n{time_str}",
            fontsize=8
        )

    plt.tight_layout()
    fname = f"fig2_route_{fig_index}.png"
    plt.savefig(fname, dpi=150)
    plt.close()
    print(f"\n  Saved: {fname}")

    return results


# ── Figure 3: Comparison bar chart ───────────────────────────────────────────

def save_comparison_chart(all_results, queries):
    """
    all_results: list of dicts (one per query), each {BFS:{...}, DFS:{...}, A*:{...}}
    queries: list of (start, goal) tuples
    """
    labels   = [f"{s.replace('_',' ')}->{g.replace('_',' ')}" for s, g in queries]
    algos    = ["BFS", "DFS", "A*"]
    colors_a = ["#e67e22", "#8e44ad", "#27ae60"]
    x        = np.arange(len(labels))
    width    = 0.25

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Fig 3: Algorithm Comparison Across 5 Route Queries", fontsize=12)

    metrics = [
        ("cost",     "Path Cost (km)",       "Cost (km)"),
        ("expanded", "Nodes Expanded",        "Nodes Expanded"),
        ("time_ms",  "Runtime (ms)",          "Time (ms)"),
    ]

    for ax, (key, title, ylabel) in zip(axes, metrics):
        for i, (algo, col) in enumerate(zip(algos, colors_a)):
            vals = []
            for res in all_results:
                v = res[algo][key]
                vals.append(v if v != float('inf') else 0)
            ax.bar(x + i * width, vals, width, label=algo, color=col, alpha=0.85)

        ax.set_title(title, fontsize=10)
        ax.set_ylabel(ylabel)
        ax.set_xticks(x + width)
        ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=7)
        ax.legend(fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("fig3_comparison.png", dpi=150)
    plt.close()
    print("\nSaved: fig3_comparison.png")


# ── Summary table ─────────────────────────────────────────────────────────────

def print_summary_table(all_results, queries):
    print("\n" + "=" * 90)
    print("SUMMARY TABLE — All Queries")
    print("=" * 90)
    header = f"{'Query':<28} {'Algo':>4}  {'Cost (km)':>10}  {'Nodes Exp.':>11}  {'Time (ms)':>11}"
    print(header)
    print("-" * 90)
    for (s, g), res in zip(queries, all_results):
        label = f"{s.replace('_',' ')} -> {g.replace('_',' ')}"
        for algo in ["BFS", "DFS", "A*"]:
            r = res[algo]
            cost = f"{r['cost']:.1f}" if r['cost'] != float('inf') else "N/A"
            print(f"  {label:<26} {algo:>4}  {cost:>10}  {r['expanded']:>11}  {r['time_ms']:>11.4f}")
        print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    graph = build_graph()

    # 5 route queries covering different parts of Nairobi
    queries = [
        ("CBD",      "Rongai"),
        ("CBD",      "Kasarani"),
        ("Westlands","Embakasi"),
        ("Kikuyu",   "TRM"),
        ("Langata",  "Kasarani"),
    ]

    print("\n" + "=" * 60)
    print("  NAIROBI MATATU INTELLIGENT PATH FINDER")
    print("  DSA 2020 — Project 2")
    print("=" * 60)

    save_network_map()

    all_results = []
    for i, (start, goal) in enumerate(queries, start=1):
        results = run_query(graph, start, goal, i)
        all_results.append(results)

    print_summary_table(all_results, queries)
    save_comparison_chart(all_results, queries)

    print("\n" + "=" * 60)
    print("  All figures saved. Analysis complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
