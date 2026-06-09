# ============================================================
# AI-Based Network Pathfinding & Attack Simulation System
# Course: CSC 262 - Artificial Intelligence
# COMSATS University Islamabad, CUI Abbottabad
# ============================================================

import heapq
import time
import tkinter as tk
from tkinter import ttk, messagebox
import math
import random

# ─────────────────────────────────────────────
# 1. GRAPH / NETWORK DEFINITION
# ─────────────────────────────────────────────

# Node metadata: name → (type, x_pos, y_pos)
NODE_INFO = {
    "Internet":    ("Entry",    100, 300),
    "Firewall":    ("Firewall", 220, 300),
    "WebServer":   ("Server",   340, 180),
    "AppServer":   ("Server",   340, 300),
    "Workstation1":("Client",   340, 420),
    "Workstation2":("Client",   460, 480),
    "InternalFW":  ("Firewall", 460, 300),
    "DBServer":    ("Database", 580, 200),
    "AdminPC":     ("Client",   580, 360),
    "CoreDB":      ("Database", 700, 280),
}

# Weighted adjacency list: (neighbor, cost/vulnerability)
GRAPH = {
    "Internet":    [("Firewall", 2)],
    "Firewall":    [("Internet", 2), ("WebServer", 3), ("AppServer", 5), ("Workstation1", 7)],
    "WebServer":   [("Firewall", 3), ("AppServer", 2), ("InternalFW", 6)],
    "AppServer":   [("Firewall", 5), ("WebServer", 2), ("InternalFW", 3), ("Workstation1", 4)],
    "Workstation1":[("Firewall", 7), ("AppServer", 4), ("Workstation2", 2)],
    "Workstation2":[("Workstation1", 2), ("AdminPC", 5), ("InternalFW", 4)],
    "InternalFW":  [("WebServer", 6), ("AppServer", 3), ("Workstation2", 4), ("DBServer", 4), ("AdminPC", 3)],
    "DBServer":    [("InternalFW", 4), ("CoreDB", 2), ("AdminPC", 3)],
    "AdminPC":     [("InternalFW", 3), ("DBServer", 3), ("Workstation2", 5), ("CoreDB", 4)],
    "CoreDB":      [("DBServer", 2), ("AdminPC", 4)],
}

START = "Internet"
GOAL  = "CoreDB"

# ─────────────────────────────────────────────
# 2. HELPER UTILITIES
# ─────────────────────────────────────────────

def reconstruct_path(came_from, start, goal):
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    return path if path[0] == start else []

def path_cost(path, graph):
    cost = 0
    for i in range(len(path) - 1):
        for nb, w in graph[path[i]]:
            if nb == path[i+1]:
                cost += w
                break
    return cost

# ─────────────────────────────────────────────
# 3. BFS
# ─────────────────────────────────────────────

def bfs(graph, start, goal):
    from collections import deque
    t0 = time.perf_counter()
    queue = deque([[start]])
    visited = {start}
    nodes_expanded = 0

    while queue:
        path = queue.popleft()
        node = path[-1]
        nodes_expanded += 1

        if node == goal:
            elapsed = (time.perf_counter() - t0) * 1000
            came = {path[i+1]: path[i] for i in range(len(path)-1)}
            came[start] = None
            return path, path_cost(path, graph), nodes_expanded, elapsed

        for neighbor, _ in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return [], 0, nodes_expanded, (time.perf_counter() - t0) * 1000

# ─────────────────────────────────────────────
# 4. DFS
# ─────────────────────────────────────────────

def dfs(graph, start, goal):
    t0 = time.perf_counter()
    stack = [[start]]
    visited = set()
    nodes_expanded = 0

    while stack:
        path = stack.pop()
        node = path[-1]
        if node in visited:
            continue
        visited.add(node)
        nodes_expanded += 1

        if node == goal:
            elapsed = (time.perf_counter() - t0) * 1000
            return path, path_cost(path, graph), nodes_expanded, elapsed

        for neighbor, _ in reversed(graph.get(node, [])):
            if neighbor not in visited:
                stack.append(path + [neighbor])

    return [], 0, nodes_expanded, (time.perf_counter() - t0) * 1000

# ─────────────────────────────────────────────
# 5. UCS
# ─────────────────────────────────────────────

def ucs(graph, start, goal):
    t0 = time.perf_counter()
    # (cost, node, path)
    heap = [(0, start, [start])]
    visited = {}
    nodes_expanded = 0

    while heap:
        cost, node, path = heapq.heappop(heap)
        if node in visited:
            continue
        visited[node] = cost
        nodes_expanded += 1

        if node == goal:
            elapsed = (time.perf_counter() - t0) * 1000
            return path, cost, nodes_expanded, elapsed

        for neighbor, w in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(heap, (cost + w, neighbor, path + [neighbor]))

    return [], 0, nodes_expanded, (time.perf_counter() - t0) * 1000

# ─────────────────────────────────────────────
# 6. A* SEARCH
# ─────────────────────────────────────────────

# Heuristic: straight-line Euclidean distance (pixel coords) scaled to cost units
def heuristic(node, goal, node_info):
    x1, y1 = node_info[node][1], node_info[node][2]
    x2, y2 = node_info[goal][1], node_info[goal][2]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 80   # scale factor

def astar(graph, start, goal, node_info):
    t0 = time.perf_counter()
    h = lambda n: heuristic(n, goal, node_info)
    heap = [(h(start), 0, start, [start])]
    g_score = {start: 0}
    nodes_expanded = 0

    while heap:
        f, g, node, path = heapq.heappop(heap)
        if node in g_score and g < g_score.get(node, float('inf')) - 1e-9:
            continue
        nodes_expanded += 1

        if node == goal:
            elapsed = (time.perf_counter() - t0) * 1000
            return path, g, nodes_expanded, elapsed

        for neighbor, w in graph.get(node, []):
            tentative_g = g + w
            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g
                heapq.heappush(heap, (tentative_g + h(neighbor), tentative_g, neighbor, path + [neighbor]))

    return [], 0, nodes_expanded, (time.perf_counter() - t0) * 1000

# ─────────────────────────────────────────────
# 7. HILL CLIMBING
# ─────────────────────────────────────────────

def hill_climbing(graph, start, goal, node_info):
    t0 = time.perf_counter()
    current = start
    path = [current]
    visited = {current}
    nodes_expanded = 0
    h = lambda n: heuristic(n, goal, node_info)

    while current != goal:
        neighbors = [(h(nb), nb) for nb, _ in graph.get(current, []) if nb not in visited]
        nodes_expanded += 1

        if not neighbors:
            elapsed = (time.perf_counter() - t0) * 1000
            return path, path_cost(path, graph), nodes_expanded, elapsed  # stuck in local max

        neighbors.sort()
        best_h, best_nb = neighbors[0]

        if best_h >= h(current):
            # LOCAL MAXIMUM — cannot improve
            path.append(f"[STUCK@{current}]")
            elapsed = (time.perf_counter() - t0) * 1000
            return path, path_cost([n for n in path if not n.startswith("[")], graph), nodes_expanded, elapsed

        current = best_nb
        path.append(current)
        visited.add(current)

    elapsed = (time.perf_counter() - t0) * 1000
    return path, path_cost(path, graph), nodes_expanded, elapsed

# ─────────────────────────────────────────────
# 8. MINIMAX  +  ALPHA-BETA PRUNING
# ─────────────────────────────────────────────

def minimax(graph, node, depth, is_maximizer, goal, node_info, visited=None):
    if visited is None:
        visited = set()
    h = lambda n: -heuristic(n, goal, node_info)   # attacker wants LOWER heuristic

    if node == goal or depth == 0 or node in visited:
        return h(node), node

    visited = visited | {node}
    neighbors = [nb for nb, _ in graph.get(node, [])]

    if not neighbors:
        return h(node), node

    if is_maximizer:
        best_val, best_node = float('-inf'), None
        for nb in neighbors:
            val, _ = minimax(graph, nb, depth-1, False, goal, node_info, visited)
            if val > best_val:
                best_val, best_node = val, nb
        return best_val, best_node
    else:
        best_val, best_node = float('inf'), None
        for nb in neighbors:
            val, _ = minimax(graph, nb, depth-1, True, goal, node_info, visited)
            if val < best_val:
                best_val, best_node = val, nb
        return best_val, best_node

def alphabeta(graph, node, depth, alpha, beta, is_maximizer, goal, node_info, visited=None):
    if visited is None:
        visited = set()
    h = lambda n: -heuristic(n, goal, node_info)

    if node == goal or depth == 0 or node in visited:
        return h(node), node

    visited = visited | {node}
    neighbors = [nb for nb, _ in graph.get(node, [])]

    if not neighbors:
        return h(node), node

    if is_maximizer:
        best_val, best_node = float('-inf'), None
        for nb in neighbors:
            val, _ = alphabeta(graph, nb, depth-1, alpha, beta, False, goal, node_info, visited)
            if val > best_val:
                best_val, best_node = val, nb
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break   # Beta cut-off
        return best_val, best_node
    else:
        best_val, best_node = float('inf'), None
        for nb in neighbors:
            val, _ = alphabeta(graph, nb, depth-1, alpha, beta, True, goal, node_info, visited)
            if val < best_val:
                best_val, best_node = val, nb
            beta = min(beta, best_val)
            if beta <= alpha:
                break   # Alpha cut-off
        return best_val, best_node

def run_minimax_path(graph, start, goal, node_info, use_alphabeta=False):
    """Simulate attacker walking step-by-step using Minimax decisions."""
    t0 = time.perf_counter()
    path = [start]
    visited = set()
    nodes_expanded = 0
    current = start
    DEPTH = 4

    while current != goal and len(path) < 25:
        visited.add(current)
        nodes_expanded += 1
        neighbors = [nb for nb, _ in graph.get(current, []) if nb not in visited]
        if not neighbors:
            break
        if use_alphabeta:
            _, best = alphabeta(graph, current, DEPTH, float('-inf'), float('inf'),
                                True, goal, node_info, visited.copy())
        else:
            _, best = minimax(graph, current, DEPTH, True, goal, node_info, visited.copy())

        if best is None or best in visited:
            # fallback: pick neighbor with best heuristic
            h = lambda n: heuristic(n, goal, node_info)
            best = min(neighbors, key=h)

        path.append(best)
        current = best

    elapsed = (time.perf_counter() - t0) * 1000
    return path, path_cost(path, graph), nodes_expanded, elapsed

# ─────────────────────────────────────────────
# 9. RUN ALL & BUILD COMPARISON TABLE
# ─────────────────────────────────────────────

def run_all_algorithms():
    results = {}

    results["BFS"]         = bfs(GRAPH, START, GOAL)
    results["DFS"]         = dfs(GRAPH, START, GOAL)
    results["UCS"]         = ucs(GRAPH, START, GOAL)
    results["A*"]          = astar(GRAPH, START, GOAL, NODE_INFO)
    results["Hill Climbing"]= hill_climbing(GRAPH, START, GOAL, NODE_INFO)
    results["Minimax"]     = run_minimax_path(GRAPH, START, GOAL, NODE_INFO, use_alphabeta=False)
    results["Alpha-Beta"]  = run_minimax_path(GRAPH, START, GOAL, NODE_INFO, use_alphabeta=True)

    print(f"\n{'='*90}")
    print(f"{'Algorithm':<16} {'Path':<42} {'Cost':>6} {'Nodes':>7} {'Time(ms)':>10}")
    print(f"{'='*90}")
    for algo, (path, cost, expanded, ms) in results.items():
        path_str = " → ".join(str(p) for p in path)
        if len(path_str) > 40:
            path_str = path_str[:37] + "..."
        print(f"{algo:<16} {path_str:<42} {cost:>6.1f} {expanded:>7} {ms:>10.3f}")
    print(f"{'='*90}\n")
    return results

# ─────────────────────────────────────────────
# 10. TKINTER GUI
# ─────────────────────────────────────────────

NODE_COLORS = {
    "Entry":    "#e74c3c",
    "Firewall": "#e67e22",
    "Server":   "#3498db",
    "Client":   "#2ecc71",
    "Database": "#9b59b6",
}

class NetworkGUI:
    CANVAS_W, CANVAS_H = 820, 500
    R = 28  # node radius

    def __init__(self, root):
        self.root = root
        root.title("AI Network Pathfinding & Attack Simulation")
        root.configure(bg="#1a1a2e")
        self._build_ui()
        self.results = {}
        self.current_path = []

    def _build_ui(self):
        # ── Top bar ──
        top = tk.Frame(self.root, bg="#16213e", pady=6)
        top.pack(fill="x")
        tk.Label(top, text="🛡  AI Network Attack Simulation", font=("Helvetica", 15, "bold"),
                 fg="#e94560", bg="#16213e").pack(side="left", padx=12)

        # ── Canvas ──
        self.canvas = tk.Canvas(self.root, width=self.CANVAS_W, height=self.CANVAS_H,
                                bg="#0f3460", highlightthickness=0)
        self.canvas.pack(padx=10, pady=6)

        # ── Controls ──
        ctrl = tk.Frame(self.root, bg="#1a1a2e")
        ctrl.pack(fill="x", padx=10)

        tk.Label(ctrl, text="Algorithm:", fg="white", bg="#1a1a2e",
                 font=("Helvetica", 10, "bold")).pack(side="left")
        self.algo_var = tk.StringVar(value="A*")
        algos = ["BFS", "DFS", "UCS", "A*", "Hill Climbing", "Minimax", "Alpha-Beta"]
        cb = ttk.Combobox(ctrl, textvariable=self.algo_var, values=algos, width=16, state="readonly")
        cb.pack(side="left", padx=6)

        tk.Button(ctrl, text="▶  Run", command=self.run_selected,
                  bg="#e94560", fg="white", font=("Helvetica", 10, "bold"),
                  relief="flat", padx=10).pack(side="left", padx=4)
        tk.Button(ctrl, text="⚡ Run All", command=self.run_all,
                  bg="#533483", fg="white", font=("Helvetica", 10, "bold"),
                  relief="flat", padx=10).pack(side="left", padx=4)
        tk.Button(ctrl, text="↺  Reset", command=self.reset,
                  bg="#0f3460", fg="white", font=("Helvetica", 10, "bold"),
                  relief="flat", padx=10).pack(side="left", padx=4)

        # ── Results table ──
        tbl_frame = tk.Frame(self.root, bg="#1a1a2e")
        tbl_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        cols = ("Algorithm", "Path", "Cost", "Nodes Expanded", "Time (ms)")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=7)
        widths = [110, 360, 60, 110, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#16213e", foreground="white",
                         rowheight=22, fieldbackground="#16213e", font=("Courier", 9))
        style.configure("Treeview.Heading", background="#0f3460", foreground="#e94560",
                         font=("Helvetica", 9, "bold"))
        style.map("Treeview", background=[("selected", "#533483")])

        sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._draw_network()

    # ── Draw the graph ──
    def _draw_network(self, highlight_path=None):
        self.canvas.delete("all")
        hp = set()
        hp_edges = set()
        if highlight_path:
            valid = [n for n in highlight_path if not n.startswith("[")]
            hp = set(valid)
            hp_edges = set(zip(valid, valid[1:]))

        # Draw edges
        for node, neighbors in GRAPH.items():
            x1, y1 = NODE_INFO[node][1], NODE_INFO[node][2]
            for nb, w in neighbors:
                x2, y2 = NODE_INFO[nb][1], NODE_INFO[nb][2]
                edge = (node, nb)
                color = "#e94560" if edge in hp_edges or (nb, node) in hp_edges else "#334155"
                width = 3 if color == "#e94560" else 1
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
                mx, my = (x1+x2)//2, (y1+y2)//2
                self.canvas.create_text(mx, my-8, text=str(w),
                                        fill="#94a3b8", font=("Helvetica", 7))

        # Draw nodes
        for node, (ntype, x, y) in NODE_INFO.items():
            base = NODE_COLORS.get(ntype, "#888")
            if node in hp:
                outline, ow = "#ffffff", 3
            elif node == START:
                outline, ow = "#e94560", 3
            elif node == GOAL:
                outline, ow = "#f0d000", 3
            else:
                outline, ow = "#334155", 1

            self.canvas.create_oval(x-self.R, y-self.R, x+self.R, y+self.R,
                                    fill=base, outline=outline, width=ow)
            label = node if len(node) <= 9 else node[:8]
            self.canvas.create_text(x, y, text=label,
                                    fill="white", font=("Helvetica", 7, "bold"))

        # Legend
        legend_x, legend_y = 15, 15
        for ntype, color in NODE_COLORS.items():
            self.canvas.create_rectangle(legend_x, legend_y, legend_x+12, legend_y+12,
                                         fill=color, outline="")
            self.canvas.create_text(legend_x+16, legend_y+6, text=ntype,
                                    anchor="w", fill="white", font=("Helvetica", 8))
            legend_y += 18

    # ── Run selected algorithm ──
    def run_selected(self):
        algo = self.algo_var.get()
        if algo == "BFS":
            r = bfs(GRAPH, START, GOAL)
        elif algo == "DFS":
            r = dfs(GRAPH, START, GOAL)
        elif algo == "UCS":
            r = ucs(GRAPH, START, GOAL)
        elif algo == "A*":
            r = astar(GRAPH, START, GOAL, NODE_INFO)
        elif algo == "Hill Climbing":
            r = hill_climbing(GRAPH, START, GOAL, NODE_INFO)
        elif algo == "Minimax":
            r = run_minimax_path(GRAPH, START, GOAL, NODE_INFO, use_alphabeta=False)
        else:
            r = run_minimax_path(GRAPH, START, GOAL, NODE_INFO, use_alphabeta=True)

        path, cost, expanded, ms = r
        self._draw_network(highlight_path=path)
        self._add_row(algo, path, cost, expanded, ms)

    # ── Run all ──
    def run_all(self):
        self.tree.delete(*self.tree.get_children())
        results = run_all_algorithms()
        for algo, (path, cost, expanded, ms) in results.items():
            self._add_row(algo, path, cost, expanded, ms)
        # Highlight A* path
        self._draw_network(highlight_path=results["A*"][0])

    def _add_row(self, algo, path, cost, expanded, ms):
        path_str = " → ".join(str(p) for p in path)
        self.tree.insert("", "end", values=(algo, path_str, f"{cost:.1f}", expanded, f"{ms:.3f}"))

    def reset(self):
        self.tree.delete(*self.tree.get_children())
        self._draw_network()


# ─────────────────────────────────────────────
# 11. ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n=== Running all algorithms (CLI output) ===")
    run_all_algorithms()

    print("Launching GUI...")
    root = tk.Tk()
    app = NetworkGUI(root)
    root.mainloop()
