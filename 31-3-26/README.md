# DSA 2020 — Project 2: Intelligent Path Finder for Nairobi Matatu Routes
**Lecturer:** Dr. Edward Ombui | Algorithms: BFS, DFS, A*

---

## Files

| File | Description |
|---|---|
| `graph.py` | 15-node Nairobi matatu network (nodes, coordinates, edges) |
| `algorithms.py` | BFS, DFS, and A* implementations |
| `main.py` | Demo runner — runs 5 queries, prints results, saves all figures |
| `report.md` | Full written report |
| `requirements.txt` | Python dependencies |
| `AI Term Projects 2026.pdf` | Original assignment brief |

**Generated on run:**
| File | Description |
|---|---|
| `fig1_network.png` | Full matatu network map |
| `fig2_route_1.png` … `fig2_route_5.png` | BFS/DFS/A* routes per query |
| `fig3_comparison.png` | Bar chart: cost, nodes expanded, runtime |

---

## Setup

### 1. Create and activate virtual environment
```bash
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
# or
venv\Scripts\activate.bat         # Windows CMD
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Run

```bash
python main.py
```

This will:
1. Print route results for 5 CBD/suburb queries to the console
2. Print a summary comparison table
3. Save 7 PNG figures to this folder

---

## Run individual modules

```bash
# Inspect the graph
python graph.py

# Test algorithms on CBD → Rongai
python algorithms.py
```

---

## Network Overview

15 stops, 24 edges, weights = approximate distance in km:

```
CBD ── Westlands ── Parklands ── Eastleigh ── TRM ── Kasarani
 |
South B ── South C ── Langata ── Karen ── Rongai
 |              |                    |
Donholm      Ngong Rd           Ngong Town ── Kikuyu
 |
Embakasi
```

---

## Key Results (from running main.py)

| Route | A* Cost | BFS Cost | DFS Cost |
|---|---|---|---|
| CBD → Rongai | 22 km | 22 km | 44 km |
| CBD → Kasarani | 14 km | 14 km | 78 km |
| Westlands → Embakasi | 18 km | 18 km | 43 km |
| Kikuyu → TRM | 25 km | 25 km | 75 km |
| Langata → Kasarani | 28 km | 28 km | 53 km |

A* always finds the optimal path while expanding the fewest nodes.
