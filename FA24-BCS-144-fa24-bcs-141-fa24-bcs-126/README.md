# AI-Based Network Pathfinding & Attack Simulation System

Course: Artificial Intelligence (CSC 262)
Institute: COMSATS University Islamabad, CUI Abbottabad
Instructor: Zeenat Zulfiqar
Student: Ali Murtaza | FA24-BCS-144

---

## Project Overview

This project simulates an attacker traversing a computer network modelled as a
weighted graph. Seven AI search algorithms are implemented from scratch to find
the optimal attack path from an entry point (Internet) to a critical target (CoreDB).

Algorithms Implemented:
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Uniform Cost Search (UCS)
- A* Search
- Hill Climbing
- Minimax
- Alpha-Beta Pruning

---

## Project Structure

```
FA24-BCS-144 Assignment/
├── network_pathfinding.py           # Main source code (all algorithms + GUI)
├── network_pathfinding_colab.ipynb  # Google Colab notebook version
├── network_pathfinding_colab.pdf    # PDF of the Colab notebook
├── main.tex                         # LaTeX report source
├── main.pdf                         # Compiled project report
├── overleaf_link.txt                # Overleaf project link
└── README.md                        # This file
```

---

## Dependencies

All libraries used are part of the Python standard library — no external
packages need to be installed.

| Library            | Purpose                              |
|--------------------|--------------------------------------|
| heapq              | Priority queue for UCS and A*        |
| collections.deque  | Queue for BFS                        |
| time               | Execution time measurement           |
| math               | Euclidean distance for heuristic     |
| tkinter            | GUI (built into Python)              |

Python version required: Python 3.7 or higher

---

## How to Run

### Option 1 - Run with GUI (Recommended)

```bash
python network_pathfinding.py
```

This launches a full graphical interface where you can:
- Select any algorithm from the dropdown
- Click Run to visualise the attack path
- Click Run All to see the full comparison table

### Option 2 - Run in Google Colab

1. Go to colab.research.google.com
2. Upload network_pathfinding_colab.ipynb
3. Click Runtime -> Run All

### Option 3 - CLI only (no GUI)

Open network_pathfinding.py and change the last lines to:

```python
if __name__ == "__main__":
    run_all_algorithms()
```

Then run:
```bash
python network_pathfinding.py
```

---

## GUI Features

- Visual graph of the 10-node network with colour-coded node types
- Dropdown to select any of the 7 algorithms
- Red path highlighting on the graph canvas
- Live metrics table (path, cost, nodes expanded, time)
- Run All button for full side-by-side comparison

---

## Network Topology

| Node         | Type        | Role                  |
|--------------|-------------|-----------------------|
| Internet     | Entry Point | Attacker start node   |
| Firewall     | Firewall    | Perimeter defence     |
| WebServer    | Server      | Public web server     |
| AppServer    | Server      | Internal app server   |
| Workstation1 | Client      | Employee PC (Zone A)  |
| Workstation2 | Client      | Employee PC (Zone B)  |
| InternalFW   | Firewall    | Internal firewall     |
| DBServer     | Database    | Intermediate DB       |
| AdminPC      | Client      | Admin workstation     |
| CoreDB       | Database    | Target node           |

---

## Sample Output

```
Algorithm        Path                                       Cost   Nodes   Time(ms)
BFS              Internet -> Firewall -> WebServer -> ...   17.0      10      0.047
DFS              Internet -> Firewall -> WebServer -> ...   24.0      10      0.014
UCS              Internet -> Firewall -> AppServer -> ...   16.0      10      0.070
A*               Internet -> Firewall -> AppServer -> ...   16.0      11      0.128
Hill Climbing    Internet -> Firewall -> AppServer -> ...   17.0       5      0.026
Minimax          Internet -> Firewall -> AppServer -> ...   16.0       5      0.027
Alpha-Beta       Internet -> Firewall -> AppServer -> ...   16.0       5      0.021
```

---

## Notes

- The optimal path (cost 16) is found by UCS, A*, Minimax, and Alpha-Beta
- Hill Climbing may get stuck at a local maximum on modified network layouts
- Alpha-Beta Pruning produces the same result as Minimax but runs faster
