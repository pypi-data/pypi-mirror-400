from collections import deque, defaultdict

mappings ={
    (1, 1): [(2, 1), (2, 2)],
    # (1, 2): [(2, 2), (2, 3)],
    (2, 1): [(3, 1)],
    (2, 2): [(3, 2)],
    # (2, 3): [(3, 3), (3, 4)]
}

# construct the graph
graph = defaultdict(list)
for key, value in mappings.items():
    for v in value:
        graph[key].append(v)
        graph[v].append(key)

evolution_paths = []
visited = set()
for key in graph.keys():
    if key not in visited:
        path = []
        queue = deque([key])
        visited.add(key)
        while queue:
            node = queue.popleft()
            path.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
        evolution_paths.append(path)
        
print(evolution_paths)