# graph/vg/vis.py
"""Polygon-based VG visualiser with single-row legend at the bottom.

Legend is placed centered below the figure as a single row (ncol = number
of legend items). Use show_legend=False to hide it.
"""

from __future__ import annotations
from typing import Optional, Tuple, Dict, List, Sequence
import math

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Polygon, Patch
from matplotlib.lines import Line2D
from matplotlib import rcParams

from .vg import VG

rcParams.update({"font.size": 11})


class VGraphVisualizer:
    """Visualizer for VG objects (polygon layout + single-row bottom legend)."""

    def __init__(self, vg: VG):
        self.vg = vg

    # ---------------- layout helpers ----------------
    def _polygon_positions_from_order(
        self, residue_nodes: Sequence[int], radius: float = 4.0
    ) -> Dict[int, Tuple[float, float, float]]:
        n = max(1, len(residue_nodes))
        pos: Dict[int, Tuple[float, float, float]] = {}
        for k, nid in enumerate(residue_nodes):
            ang = 2.0 * math.pi * (k / n)
            x = radius * math.cos(ang)
            y = radius * math.sin(ang)
            pos[nid] = (x, y, ang)
        return pos

    def _layout_linear(
        self, residues: List[int], dx: float = 1.6
    ) -> Dict[int, Tuple[float, float, float]]:
        return {nid: (i * dx, 0.0, 0.0) for i, nid in enumerate(residues)}

    # ---------- simplified deterministic optimizer ----------
    def _greedy_optimize_order(
        self, residues: List[int], radius: float = 4.0, max_passes: int = 200
    ) -> List[int]:
        """
        Heuristic reorder for residues to reduce link crossings.

        Strategy:
          - For each residue compute the average sequence index of its link
            neighbors (the 'centroid').
          - Sort residues by centroid; tie-break by (-link_count, original_index).
          - If no link edges exist, return original order.

        This is deterministic, cheap, and has much lower cyclomatic complexity
        than an adjacent-swap optimizer while still improving clarity.
        """
        if len(residues) < 3:
            return residues[:]

        g = self.vg.g
        # map residue -> original position (0-based)
        idx_map = {res: i for i, res in enumerate(residues)}

        # collect link neighbors for residues only
        link_neighbors: Dict[int, List[int]] = {r: [] for r in residues}
        for u, v, d in g.edges(data=True):
            if d.get("relation") != "link":
                continue
            if u in link_neighbors and v in link_neighbors:
                link_neighbors[u].append(v)
                link_neighbors[v].append(u)

        # if there are no link edges, keep original order
        total_links = sum(len(v) for v in link_neighbors.values())
        if total_links == 0:
            return residues[:]

        # score residues by (centroid_of_neighbors, -link_count, original_index)
        scored: List[Tuple[Tuple[float, int, int], int]] = []
        for r in residues:
            neigh = link_neighbors.get(r, [])
            if neigh:
                centroid = sum(idx_map[n] for n in neigh) / len(neigh)
                link_count = len(neigh)
                key = (centroid, -link_count, idx_map[r])
            else:
                # no links -> keep near its original position
                key = (idx_map[r], 0, idx_map[r])
            scored.append((key, r))

        # sort by the computed key
        scored.sort(key=lambda x: x[0])
        return [r for _, r in scored]

    # ---------------- drawing helpers ----------------
    def _compute_positions(
        self, used_order: List[int], layout: str, radius: float
    ) -> Dict[int, Tuple[float, float, float]]:
        if layout == "linear":
            return self._layout_linear(used_order)
        # polygon and circular use same placement here
        return self._polygon_positions_from_order(used_order, radius=radius)

    def _place_mods(
        self,
        g: nx.Graph,
        used_order: List[int],
        pos_ang: Dict[int, Tuple[float, float, float]],
        radius: float,
    ) -> None:
        for rid in used_order:
            mods = [nb for nb in g.neighbors(rid) if g.nodes[nb].get("kind") == "mod"]
            if not mods:
                continue
            x0, y0, ang = pos_ang[rid]
            for j, mid in enumerate(sorted(mods)):
                r_mod = radius + 1.0 + 0.45 * j
                pos_ang[mid] = (r_mod * math.cos(ang), r_mod * math.sin(ang), ang)

    def _draw_nodes_and_labels(
        self,
        g: nx.Graph,
        pos2d: Dict[int, Tuple[float, float]],
        ax: plt.Axes,
        node_size: int,
        mod_size: int,
        col_res: str,
        col_mod: str,
    ) -> None:
        residue_nodes = [n for n, d in g.nodes(data=True) if d.get("kind") == "residue"]
        mod_nodes = [n for n, d in g.nodes(data=True) if d.get("kind") == "mod"]

        nx.draw_networkx_nodes(
            g,
            pos2d,
            nodelist=residue_nodes,
            node_shape="o",
            node_color=col_res,
            node_size=node_size,
            edgecolors="white",
            linewidths=1.2,
            ax=ax,
        )
        nx.draw_networkx_nodes(
            g,
            pos2d,
            nodelist=mod_nodes,
            node_shape="s",
            node_color=col_mod,
            node_size=mod_size,
            edgecolors="white",
            linewidths=1.0,
            ax=ax,
        )

        labels = {}
        for n, d in g.nodes(data=True):
            if d.get("kind") == "residue":
                labels[n] = d.get("label", "?")
            else:
                raw = d.get("label_raw", d.get("label", ""))
                norm = d.get("label", "")
                labels[n] = raw if raw and raw != norm else norm

        nx.draw_networkx_labels(
            g, pos2d, labels=labels, font_size=11, font_weight="bold", ax=ax
        )

    def _draw_seq_edges(
        self,
        ax: plt.Axes,
        g: nx.Graph,
        used_order: List[int],
        pos2d: Dict[int, Tuple[float, float]],
        seq_width: float,
        col_seq: str,
    ) -> None:
        if len(used_order) <= 1:
            return
        seq_edges = [
            (used_order[i], used_order[(i + 1) % len(used_order)])
            for i in range(len(used_order))
        ]
        nx.draw_networkx_edges(
            g, pos2d, edgelist=seq_edges, width=seq_width, edge_color=col_seq, ax=ax
        )

    def _draw_mod_edges(
        self,
        ax: plt.Axes,
        g: nx.Graph,
        pos2d: Dict[int, Tuple[float, float]],
        col_mod: str,
    ) -> None:
        mod_edges = [
            (u, v) for u, v, d in g.edges(data=True) if d.get("relation") == "has_mod"
        ]
        if mod_edges:
            nx.draw_networkx_edges(
                g,
                pos2d,
                edgelist=mod_edges,
                style="--",
                width=2.0,
                edge_color=col_mod,
                ax=ax,
            )

    def _draw_link_chords(
        self,
        ax: plt.Axes,
        g: nx.Graph,
        pos2d: Dict[int, Tuple[float, float]],
        pos_ang: Dict[int, Tuple[float, float, float]],
        link_width: float,
        col_link: str,
        annotate_links: bool,
        show_ports: bool,
        radius: float,
    ) -> None:
        link_edges = [
            (u, v, d) for u, v, d in g.edges(data=True) if d.get("relation") == "link"
        ]
        for u, v, d in link_edges:
            if u not in pos2d or v not in pos2d:
                continue
            x1, y1 = pos2d[u]
            x2, y2 = pos2d[v]
            ax.plot(
                [x1, x2],
                [y1, y2],
                linestyle=":",
                color=col_link,
                linewidth=link_width,
                zorder=2,
            )

            if annotate_links:
                mx, my = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
                dx, dy = x2 - x1, y2 - y1
                L = math.hypot(dx, dy) or 1.0
                nx_, ny_ = -dy / L, dx / L
                offset = max(0.35, 0.6 * (radius / 4.0))
                tx, ty = mx + nx_ * offset, my + ny_ * offset
                idx = d.get("link_idx") or (
                    ",".join(map(str, d.get("link_idxs", [])))
                    if d.get("link_idxs")
                    else ""
                )
                if idx:
                    ax.text(
                        tx,
                        ty,
                        str(idx),
                        color=col_link,
                        fontsize=11,
                        ha="center",
                        va="center",
                        bbox=dict(
                            boxstyle="round,pad=0.2", fc="white", ec=col_link, lw=0.8
                        ),
                        zorder=4,
                    )

            if show_ports:
                ports = d.get("ports", {}) or {}
                pu = ports.get(u)
                pv = ports.get(v)
                if pu:
                    ax.text(
                        pos_ang[u][0] + 0.16 * math.cos(pos_ang[u][2]),
                        pos_ang[u][1] + 0.16 * math.sin(pos_ang[u][2]),
                        str(pu),
                        fontsize=9,
                        color=col_link,
                        ha="left",
                        va="bottom",
                    )
                if pv:
                    ax.text(
                        pos_ang[v][0] + 0.16 * math.cos(pos_ang[v][2]),
                        pos_ang[v][1] + 0.16 * math.sin(pos_ang[v][2]),
                        str(pv),
                        fontsize=9,
                        color=col_link,
                        ha="left",
                        va="bottom",
                    )

    def _draw_legend(
        self,
        fig: plt.Figure,
        show: bool,
        col_res: str,
        col_mod: str,
        col_seq: str,
        col_link: str,
        link_width: float,
    ) -> None:
        if not show:
            return
        h_res = Patch(facecolor=col_res, edgecolor="white", label="residue")
        h_seq = Line2D([], [], color=col_seq, lw=3, label="sequence (edge)")
        h_mod = Patch(facecolor=col_mod, edgecolor="white", label="mod")
        h_mod_edge = Line2D(
            [], [], color=col_mod, lw=2, ls="--", label="mod attachment"
        )
        h_link = Line2D(
            [], [], color=col_link, lw=link_width, ls=":", label="link (chord)"
        )

        handles = [h_res, h_seq, h_mod, h_mod_edge, h_link]
        labels = [h.get_label() for h in handles]

        try:
            fig.subplots_adjust(bottom=0.14)
        except Exception:
            pass
        fig.legend(
            handles=handles,
            labels=labels,
            ncol=len(handles),
            loc="lower center",
            bbox_to_anchor=(0.5, 0.01),
            frameon=False,
            fontsize=10,
        )

    # ---------------- public draw ----------------
    def draw(
        self,
        ax: Optional[plt.Axes] = None,
        *,
        layout: str = "polygon",
        radius: float = 4.0,
        optimize_for_links: bool = False,
        max_opt_passes: int = 300,
        figsize: Tuple[float, float] = (10, 10),
        node_size: int = 1800,
        mod_size: int = 700,
        seq_width: float = 3.5,
        link_width: float = 6.0,
        show_ports: bool = True,
        annotate_links: bool = True,
        title: Optional[str] = None,
        theme: Optional[Dict[str, str]] = None,
        show_index: bool = False,
        show_legend: bool = True,
        return_order: bool = False,
    ):
        """Render VG with clean polygon layout and bottom legend."""
        g = self.vg.g
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure

        theme = theme or {}
        col_res = theme.get("res", "#1f5f8a")
        col_mod = theme.get("mod", "#d87f3a")
        col_seq = theme.get("seq", "#163746")
        col_link = theme.get("link", "#2ca02c")

        residues = [n for n, d in g.nodes(data=True) if d.get("kind") == "residue"]
        residues = sorted(residues, key=lambda n: g.nodes[n].get("idx", 0))

        used_order = residues[:]
        if optimize_for_links:
            used_order = self._greedy_optimize_order(
                residues, radius=radius, max_passes=max_opt_passes
            )

        pos_ang = self._compute_positions(used_order, layout, radius)
        self._place_mods(g, used_order, pos_ang, radius)

        # fallback for unplaced nodes
        unplaced = [n for n in g.nodes() if n not in pos_ang]
        if unplaced:
            fb = nx.spring_layout(g.subgraph(unplaced))
            maxx = max((abs(x) for x, y, _ in pos_ang.values()), default=radius)
            for i, nid in enumerate(unplaced):
                fx, fy = fb[nid]
                pos_ang[nid] = (maxx + 1.0 + fx, fy, 0.0)

        pos2d = {n: (pos_ang[n][0], pos_ang[n][1]) for n in pos_ang}
        polygon_vertices = [pos2d[n] for n in used_order]
        poly = Polygon(
            polygon_vertices,
            closed=True,
            fill=False,
            edgecolor=col_seq,
            linewidth=seq_width * 0.8,
            zorder=0,
        )
        ax.add_patch(poly)

        self._draw_nodes_and_labels(g, pos2d, ax, node_size, mod_size, col_res, col_mod)

        if show_index:
            for n, d in g.nodes(data=True):
                if d.get("kind") != "residue":
                    continue
                x, y = pos2d[n]
                idx = d.get("idx", None)
                if idx is not None:
                    ax.text(
                        x + 0.12,
                        y - 0.12,
                        str(idx),
                        fontsize=9,
                        fontweight="regular",
                        color="black",
                        alpha=0.85,
                    )

        self._draw_seq_edges(ax, g, used_order, pos2d, seq_width, col_seq)
        self._draw_mod_edges(ax, g, pos2d, col_mod)
        self._draw_link_chords(
            ax,
            g,
            pos2d,
            pos_ang,
            link_width,
            col_link,
            annotate_links,
            show_ports,
            radius,
        )

        ax.set_aspect("equal")
        ax.set_axis_off()
        if title is None:
            title = "Topology layout"
        ax.set_title(title, pad=16)

        self._draw_legend(
            fig, show_legend, col_res, col_mod, col_seq, col_link, link_width
        )

        fig.tight_layout()
        if return_order:
            return ax, used_order
        return ax
