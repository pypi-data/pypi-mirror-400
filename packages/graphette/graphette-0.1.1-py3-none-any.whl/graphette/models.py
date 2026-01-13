from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class Highlight:
    label: str
    color: str
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)


@dataclass
class Snapshot:
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)
    event: str | None = None
    state: dict = field(default_factory=dict)
    highlights: list = field(default_factory=list)

    def node_colors(self, all_nodes, default="lightgray"):
        node_map = {}
        for h in self.highlights:
            for n in h.nodes:
                node_map[n] = h.color
        return [node_map.get(n, default) for n in all_nodes]

    def edge_colors(self, all_edges, default="black", digraph=False):
        edge_map = {}
        for h in self.highlights:
            for e in h.edges:
                edge_map[e] = h.color

        def _get_color(e):
            if e in edge_map: return edge_map[e]
            if not digraph and (e[1], e[0]) in edge_map:
                return edge_map[(e[1], e[0])]
            return default

        return [_get_color(e) for e in all_edges]

    def legend_entries(self):
        return {h.color: h.label for h in self.highlights if h.label}


def snap(*highlights, ev=None, n=None, e=None, s=None):
    return Snapshot(
        nodes=deepcopy(n or []),
        edges=deepcopy(e or []),
        event=ev,
        state=deepcopy(s or {}),
        highlights=deepcopy(highlights or []),
    )


def h(c, lb=None, *, n=None, e=None):
    return Highlight(label=lb, color=c, nodes=list(n or []), edges=list(e or []))


@dataclass
class Config:
    @staticmethod
    def draw_factory():
        return dict(node_size=1200, edgecolors="k", width=2, linewidths=2)

    @staticmethod
    def handle_factory():
        return dict(marker="o", markersize=10)

    draw_kwargs: dict = field(default_factory=draw_factory)
    handle_kwargs: dict = field(default_factory=handle_factory)
    fig_kwargs: dict = field(default_factory=dict)
    layout_kwargs: dict = field(default_factory=dict)
    seed: int | None = None
    digraph: bool = False

