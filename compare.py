import pandas as pd
import heapq
import math
import time
from collections import defaultdict

# =========================================================
# READ CSV DATASET
# =========================================================

FILE_NAME = "Weight_Matrix.csv"

df = pd.read_csv(FILE_NAME)
# =========================================================
# BUILD GRAPH
# =========================================================

graph = defaultdict(dict)
vertices = set()

# =========================================================
# BUILD GRAPH FROM ADJACENCY MATRIX
# =========================================================

graph = defaultdict(dict)

# Danh sách thành phố
vertices = list(df.columns[1:])

for i, row in df.iterrows():

    u = row.iloc[0]  # tên thành phố ở cột đầu

    for v in vertices:

        w = row[v]

        # bỏ qua vô cực và chính nó
        if str(w).lower() != "inf" and u != v:

            w = float(w)

            graph[u][v] = w
# =========================================================
# DIJKSTRA
# =========================================================

def dijkstra(graph, start):
    distances = {v: math.inf for v in graph}
    previous = {v: None for v in graph}

    distances[start] = 0

    pq = [(0, start)]

    while pq:
        current_dist, current_vertex = heapq.heappop(pq)

        if current_dist > distances[current_vertex]:
            continue

        for neighbor, weight in graph[current_vertex].items():
            distance = current_dist + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))

    return distances, previous

# =========================================================
# BELLMAN-FORD
# =========================================================

def bellman_ford(graph, vertices, start):
    distances = {v: math.inf for v in vertices}
    previous = {v: None for v in vertices}

    distances[start] = 0

    edges = []

    for u in graph:
        for v, w in graph[u].items():
            edges.append((u, v, w))

    # Relax edges
    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if distances[u] != math.inf and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                previous[v] = u

    # Detect negative cycle
    for u, v, w in edges:
        if distances[u] != math.inf and distances[u] + w < distances[v]:
            raise ValueError("Graph contains a negative-weight cycle")

    return distances, previous

# =========================================================
# FLOYD-WARSHALL
# =========================================================

def floyd_warshall(vertices, graph):
    n = len(vertices)

    index = {vertex: i for i, vertex in enumerate(vertices)}

    dist = [[math.inf] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0

    for u in graph:
        for v, w in graph[u].items():
            i = index[u]
            j = index[v]

            dist[i][j] = w
            nxt[i][j] = v

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]

    return dist, nxt, index

# =========================================================
# PATH RECONSTRUCTION
# =========================================================

def reconstruct_path(previous, start, end):
    path = []

    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    if path[0] == start:
        return path

    return []

def reconstruct_fw_path(nxt, index, start, end):
    i = index[start]
    j = index[end]

    if nxt[i][j] is None:
        return []

    path = [start]

    while start != end:
        start = nxt[index[start]][j]
        path.append(start)

    return path
# =========================================================
# BENCHMARK
# =========================================================

sizes = [10, 50, 100, 200, 400, 500]

print("\n" + "=" * 60)
print(f"{'Vertices':<10} {'Dijkstra(s)':<15} {'Bellman(s)':<15} {'Floyd(s)':<15}")
print("=" * 60)

for n in sizes:

    # -----------------------------------------------------
    # CREATE SUBGRAPH
    # -----------------------------------------------------

    sub_vertices = vertices[:n]

    sub_graph = defaultdict(dict)

    for u in sub_vertices:
        for v, w in graph[u].items():

            if v in sub_vertices:
                sub_graph[u][v] = w

    source = sub_vertices[0]

    # -----------------------------------------------------
    # DIJKSTRA
    # -----------------------------------------------------

    start = time.perf_counter()

    dijkstra(sub_graph, source)

    dij_time = time.perf_counter() - start

    # -----------------------------------------------------
    # BELLMAN-FORD
    # -----------------------------------------------------

    start = time.perf_counter()

    bellman_ford(sub_graph, sub_vertices, source)

    bf_time = time.perf_counter() - start

    # -----------------------------------------------------
    # FLOYD-WARSHALL
    # -----------------------------------------------------

    start = time.perf_counter()

    floyd_warshall(sub_vertices, sub_graph)

    fw_time = time.perf_counter() - start

    # -----------------------------------------------------
    # PRINT RESULT
    # -----------------------------------------------------

    print(
        f"{n:<10}"
        f"{dij_time:<15.6f}"
        f"{bf_time:<15.6f}"
        f"{fw_time:<15.6f}"
    )
