# Graph Algorithm Visualizer

Step-by-step graph algorithm visualization with NetworkX and Matplotlib.

![BFS Example](bfs.gif)

## Usage

```bash
pip install -r requirements.txt
python visualize.py  # run included BFS example
```

## Custom Algorithms

To make a custom visualization, create a generator that yields `snapshot()` at each step:

```python
from algo import snapshot, adjacency
from visualize import visualize, animate


def dfs(edges, start):
    adj = adjacency(edges)
    stack, visited, step = [start], set(), 0

    while stack:
        cur = stack.pop()
        if cur in visited: continue
        visited.add(cur)
        step += 1

        yield snapshot(step, edges=edges, event="visit",
                       state={'visited': list(visited)},
                       node_color={'orange': ('current', cur)},
                       nodes_color={'lightgreen': ('visited', visited)})

        stack.extend(n for n in adj[cur] if n not in visited)


states = dfs(edges, 'A')
visualize(states)  # interactive (← → to navigate)
animate(states, 'out.gif')  # supports all matplotlib.animation formats
```

### Snapshot Parameters

| Parameter | Description |
|-----------|-------------|
| `step`, `event` | Step number and label |
| `nodes`, `edges` | Current state of the graph |
| `state` | Algorithm state dict to display |
| `node_color` | `{color: (label, node)}` |
| `nodes_color` | `{color: (label, node_set)}` |
| `edges_color` | `{color: (label, edge_set)}` |

## Requirements

`matplotlib`, `networkx`, `toolz`
