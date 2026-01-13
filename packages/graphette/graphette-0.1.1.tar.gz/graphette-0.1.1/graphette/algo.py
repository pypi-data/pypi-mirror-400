from collections import defaultdict, deque

from graphette.models import h, snap


def adjacency(edges, digraph=False):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        if not digraph:
            adj[v].append(u)
    return adj


def adj_remove_edge(adj, u, v):
    adj[u].remove(v)
    adj[v].remove(u)


def adj_add_edge(adj, u, v):
    adj[u].append(v)
    adj[v].append(u)


def adj_dfs_count(adj, v, visited):
    visited.add(v)
    for u in adj[v]:
        if u not in visited:
            adj_dfs_count(adj, u, visited)


def bfs(edges, start, digraph=False):
    adj = adjacency(edges, digraph=digraph)
    q, v = deque([start]), set([start])

    yield snap(h("g", "visited", n=v), e=edges, ev="init",
               s={'queue': list(q), 'visited': v})

    while q:
        cur = q.popleft()
        yield snap(h("g", "visited", n=v), h("orange", "current", n=[cur]),
                   ev="dequeue", e=edges, s={'queue': list(q), 'visited': list(v)})

        for neigh in adj[cur]:
            if neigh in v:
                continue

            v.add(neigh)
            q.append(neigh)
            yield snap(h("g", "visited", n=v), h("r", "discovered", n=[neigh]),
                       ev="discover", e=edges, s={'queue': list(q), 'visited': v})


def _is_valid_next_edge(adj, u, v):
    if len(adj[u]) == 1:
        return True

    visited_before = set()
    adj_dfs_count(adj, u, visited_before)

    adj_remove_edge(adj, u, v)
    visited_after = set()
    adj_dfs_count(adj, u, visited_after)

    adj_add_edge(adj, u, v)
    return len(visited_before) == len(visited_after)


def fleury(edges):
    adj = adjacency(edges)

    odd_vertices = [v for v in adj if len(adj[v]) % 2 == 1]
    start = odd_vertices[0] if odd_vertices else next(iter(adj))

    yield snap(ev="init", e=edges)

    path, u = [start], start
    while any(adj.values()):
        pe = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        yield snap(h("b", "path", n=path, e=pe), ev="traverse", e=edges)

        for v in list(adj[u]):
            yield snap(h("b", "path", n=path, e=pe), h("m", "current", n=[v], e=[(u, v)]),
                       e=edges, ev="check_edge")

            if _is_valid_next_edge(adj, u, v):
                adj_remove_edge(adj, u, v)
                path.append(v)
                u = v
                break
