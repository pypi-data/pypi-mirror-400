import matplotlib.animation as animation
import matplotlib.pyplot as plt
import networkx as nx
from toolz import curry

from graphette.models import Config


def to_nx(state, digraph=False):
    G = nx.DiGraph() if digraph else nx.Graph()
    G.add_nodes_from(state.nodes)
    G.add_edges_from(state.edges)
    return G


@curry
def draw(config, pos, states, ax, idx):
    ax.clear()
    s = states[idx]
    G = to_nx(s, digraph=config.digraph)

    node_colors = s.node_colors(G.nodes())
    edge_colors = s.edge_colors(G.edges(), digraph=config.digraph)

    nx.draw_networkx(
        G, pos=pos, ax=ax,
        node_color=node_colors,
        edge_color=edge_colors,
        **config.draw_kwargs
    )

    _draw_legend(config, ax, s)
    _draw_title(ax, s, idx)
    ax.axis("off")
    ax.figure.tight_layout()
    ax.figure.canvas.draw_idle()


def _draw_legend(config, ax, state):
    handles = [
        plt.Line2D([0], [0], color="w", markerfacecolor=color,
                   label=label, **config.handle_kwargs)
        for color, label in state.legend_entries().items()
    ]
    ax.legend(handles=handles, loc="upper right")


def _draw_title(ax, state, idx):
    title = f"Step {idx + 1}"
    if state.event:
        title += f" - {state.event}"
    if state.state:
        state_str = ", ".join(f"{k}: {v}" for k, v in state.state.items())
        title += f"\n{state_str}"
    ax.set_title(title)


def visualize(states, *, config: Config = None):
    config = config or Config()
    states = list(states)

    G_init = to_nx(states[0], digraph=config.digraph)
    pos = nx.spring_layout(G_init, seed=config.seed, **config.layout_kwargs)

    fig, ax = plt.subplots(**config.fig_kwargs)
    draw_fn = draw(config, pos, states)

    current_idx = 0
    draw_fn(ax, current_idx)

    def on_key(event):
        nonlocal current_idx
        delta = {'right': 1, 'left': -1}.get(event.key, 0)
        current_idx = (current_idx + delta) % len(states)
        draw_fn(ax, current_idx)

    fig.canvas.mpl_connect("key_press_event", on_key)
    return fig, draw_fn


def animate(states, filename, *, writer=None, config=None, kwargs=None):
    writer = writer or animation.PillowWriter(fps=1)
    fig, renderer = visualize(states, config=config)
    ani = animation.FuncAnimation(
        fig, renderer, frames=len(renderer.states), **(kwargs or {})
    )
    ani.save(filename, writer=writer)


if __name__ == "__main__":
    from graphette.algo import bfs

    edges = [('A', 'B'), ('A', 'C'),
             ('B', 'D'), ('B', 'E'),
             ('F', 'C'), ('F', 'E')]
    states = bfs(edges, 'A')

    fig, _ = visualize(states, config=Config(seed=42))
    plt.show()
