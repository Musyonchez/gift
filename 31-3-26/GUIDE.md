# From Folder to Submission — Step-by-Step Guide
**DSA 2020 Project 2: Intelligent Path Finder for Nairobi Matatu Routes**

This guide takes you from picking up this folder to a fully submitted project. Follow every step in order.

---

## What You're Starting With

```
31-3-26/
├── graph.py              ← Nairobi matatu network (15 nodes, 24 edges, coordinates)
├── algorithms.py         ← BFS, DFS, and A* implementations
├── main.py               ← Demo runner: prints results, saves all figures
├── report.md             ← Written report (complete, ready to export to PDF)
├── requirements.txt      ← Python dependencies: matplotlib, numpy
├── README.md             ← Quick reference
├── fig1_network.png      ← Already generated (full network map)
├── fig2_route_1–5.png    ← Already generated (route comparisons)
├── fig3_comparison.png   ← Already generated (bar charts)
└── AI Term Projects 2026.pdf  ← Original assignment brief
```

## What You Need to Submit

The assignment brief says:

| Deliverable | Format |
|---|---|
| Working code showing optimal routes | Python `.py` files |
| Comparison table/graphs | Figures + table in report |
| Report discussing algorithm suitability | PDF |
| Demo of finding routes with explanations | Live demo or recorded video |

---

## Step 1 — Set Up Python Environment

### 1.1 Check Python is installed
Open a terminal (Git Bash, CMD, or PowerShell) and run:
```bash
python --version
```
You need Python 3.8 or higher. If not installed, download from https://python.org.

### 1.2 Create and activate the virtual environment
```bash
cd path/to/31-3-26

python -m venv venv
```

**Activate it:**
```bash
# Windows Git Bash
source venv/Scripts/activate

# Windows CMD
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

You'll see `(venv)` appear in your prompt — this means it's active.

### 1.3 Install dependencies
```bash
pip install -r requirements.txt
```

This installs `matplotlib` and `numpy`. Takes about 30 seconds.

---

## Step 2 — Run the Code

```bash
python main.py
```

**What happens:**
- Console prints route results for 5 source-destination pairs (BFS, DFS, A* side by side)
- Console prints a full summary comparison table
- 7 PNG figures are saved (or overwritten if they already exist):
  - `fig1_network.png` — full matatu network map
  - `fig2_route_1.png` through `fig2_route_5.png` — one figure per query, showing all 3 algorithms
  - `fig3_comparison.png` — bar charts comparing cost, nodes expanded, runtime

### Expected console output (abbreviated)
```
Route: CBD -> Rongai
  BFS  | Route: CBD -> Ngong Road -> Karen -> Rongai | 22.0 km | 16 nodes
  DFS  | Route: CBD -> Donholm -> South B -> ... -> Rongai | 44.0 km | 15 nodes
  A*   | Route: CBD -> Ngong Road -> Karen -> Rongai | 22.0 km | 10 nodes
```

If you get any errors, see the **Troubleshooting** section at the bottom.

---

## Step 3 — Understand the Code (for the Demo)

You need to be able to explain each file during the demo. Here's a quick summary:

### `graph.py`
- Defines `COORDINATES` — a dict of 15 Nairobi stop names → (lat, lon)
- Defines `EDGES` — list of (stop_a, stop_b, distance_km) tuples
- `build_graph()` converts this into an adjacency list: `{node: [(neighbor, cost), ...]}`

### `algorithms.py`
Three functions, each returning `(path, cost, nodes_expanded)`:

| Function | Data Structure | Optimal? | Key Line |
|---|---|---|---|
| `bfs(graph, start, goal)` | `deque` (FIFO queue) | By hops | `frontier.popleft()` |
| `dfs(graph, start, goal)` | `list` (LIFO stack) | No | `frontier.pop()` |
| `astar(graph, start, goal)` | `heapq` (min-heap) | Yes (cost) | `f = g + h` |

The A* heuristic (`straight_line_distance`) is in the same file — it uses lat/lon to compute Euclidean distance in km.

### `main.py`
- Calls all 3 algorithms on 5 route queries
- Measures runtime with `time.perf_counter()`
- Draws the network and routes using `matplotlib`
- Saves all figures to PNG

---

## Step 4 — Try Your Own Routes (Optional but Impressive for Demo)

Open `main.py` and find the `queries` list near the bottom:

```python
queries = [
    ("CBD",      "Rongai"),
    ("CBD",      "Kasarani"),
    ("Westlands","Embakasi"),
    ("Kikuyu",   "TRM"),
    ("Langata",  "Kasarani"),
]
```

Change or add any pair using the exact node names from `graph.py`:

```
CBD, Westlands, Parklands, Eastleigh, TRM, Kasarani,
South_B, South_C, Langata, Karen, Rongai, Ngong_Road,
Embakasi, Donholm, Kikuyu, Ngong_Town
```

Re-run `python main.py` and new figures will be generated.

You can also test a single route directly in the Python interpreter:
```python
python -c "
from graph import build_graph
from algorithms import bfs, dfs, astar
g = build_graph()
for name, fn in [('BFS', bfs), ('DFS', dfs), ('A*', astar)]:
    path, cost, exp = fn(g, 'CBD', 'Ngong_Town')
    print(f'{name}: {\" -> \".join(path)} | {cost} km | {exp} nodes')
"
```

---

## Step 5 — Export the Report to PDF

The report is in `report.md` and is complete — all real results are already filled in.

### Option A — VS Code (easiest)
1. Install the **Markdown PDF** extension: `Ctrl+Shift+X` → search "Markdown PDF" → Install
2. Open `report.md` in VS Code
3. Right-click anywhere in the file → **Markdown PDF: Export (pdf)**
4. PDF saved automatically in the same folder

### Option B — Pandoc
```bash
pandoc report.md -o report.pdf
```
(Requires Pandoc installed: https://pandoc.org)

### Option C — Word then PDF
1. Copy all text from `report.md`
2. Paste into Word — fix headings and tables manually
3. File → Save As → PDF

> Tables in markdown look like `|col|col|`. In Word, reformat as actual Word tables for a clean look.

---

## Step 6 — Prepare the Demo

The assignment requires a **demo of finding routes with explanations**. Here's how to structure it:

### What to show (5–10 minutes)
1. **Show the network map** (`fig1_network.png`) — explain the 15 stops and edges
2. **Run `python main.py` live** — walk through one route (e.g. CBD → Rongai) as it prints
3. **Explain each algorithm's output:**
   - BFS: "It explores all nearby stops first — finds optimal hops but expands 16 nodes"
   - DFS: "It dives deep immediately — found a 44 km path when the optimal is 22 km"
   - A*: "It uses straight-line distance as a guide — found optimal path, only 10 nodes expanded"
4. **Show `fig3_comparison.png`** — the bar charts make the efficiency gap visual
5. **Show one route figure** (e.g. `fig2_route_1.png`) — three side-by-side maps

### Key numbers to know
| Route | A\* | BFS | DFS |
|---|---|---|---|
| CBD → Rongai | 22 km, 10 nodes | 22 km, 16 nodes | **44 km**, 15 nodes |
| CBD → Kasarani | 14 km, 5 nodes | 14 km, 10 nodes | **78 km**, 12 nodes |
| Kikuyu → TRM | 25 km, 3 nodes | 25 km, 6 nodes | **75 km**, 14 nodes |

**The story:** A\* and BFS find the same optimal cost, but A\* does it with far fewer nodes expanded. DFS goes wildly off — up to 5x the optimal distance.

### Likely demo questions and answers
- *"Why is DFS so bad for routing?"* — It picks one direction and commits to it without any cost awareness. It might work by luck on simple graphs but fails here.
- *"Is the straight-line heuristic always valid?"* — It's admissible (never overestimates) because road distance ≥ straight-line distance. This guarantees A\* is optimal.
- *"What would make this more realistic?"* — Time-dependent edge weights for peak/off-peak traffic, one-way edges, transfer costs between matatu routes.

---

## Step 7 — Submission Checklist

### Code
- [ ] `graph.py`, `algorithms.py`, `main.py` all run without errors
- [ ] `python main.py` produces all 7 figures and the comparison table
- [ ] Node names in queries match exactly (e.g. `South_B` not `South B`)

### Report PDF
- [ ] All sections present: Introduction, Graph Model, Algorithms (BFS/DFS/A\*), Results, Analysis, Ethics, Limitations, Conclusion
- [ ] Comparison table included with real numbers (not placeholders)
- [ ] At least 3 figures referenced in the report
- [ ] Ethical reflection section written (Section 6 of report.md)
- [ ] Exported to PDF — not Word, not markdown

### Demo
- [ ] Can run `python main.py` live without errors
- [ ] Can explain what each algorithm does and why results differ
- [ ] Know the key numbers from the comparison table above
- [ ] Figures visible and readable (open PNGs beforehand)

### General
- [ ] Both pair members names on the report cover
- [ ] PDF filename is clear: e.g. `DSA2020_Project2_[YourName].pdf`
- [ ] Submitted to correct portal/email by deadline

---

## Grading Rubric Alignment (50 marks)

| Criterion | Marks | Where It's Covered |
|---|---|---|
| Problem Understanding & Relevance | 10 | Report sections 1, 5 — Nairobi context, Kenyan traffic discussion |
| Data Collection | 5 | `graph.py` — real Nairobi coordinates and route distances |
| Implementation Quality & Correctness | 15 | `algorithms.py` — correct BFS/DFS/A\*, runs error-free |
| Report Results, Analysis & Evaluation | 10 | Report section 4 — comparison table, fig3, algorithm analysis |
| Ethical & Societal Reflection | 5 | Report section 6 — equity, digital divide, data bias |
| Demo/Presentation & Teamwork | 5 | Step 6 above — live demo with explanations |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'matplotlib'`**
→ Virtual environment not active. Run `source venv/Scripts/activate` first, then re-run.

**`ModuleNotFoundError: No module named 'graph'`**
→ Wrong working directory. Run `cd path/to/31-3-26` first, then `python main.py`.

**Figures look blank or don't open**
→ The script saves PNGs automatically — open them from the folder directly (don't wait for a window to pop up, since the non-interactive backend is used).

**`UnicodeEncodeError` on Windows**
→ Already fixed in the current code. If you see it, run: `set PYTHONIOENCODING=utf-8` in CMD before running the script.

**A\* gives a different path than BFS**
→ This is normal when multiple paths have equal cost. Both are optimal — A\* just reached it differently.
