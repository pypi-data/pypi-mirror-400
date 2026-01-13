# graph/vg/vg.py
"""OOP VG (NetworkX-backed) with links and mod metadata.

Key points
----------
- `fasta_to_vg(...)` returns a raw :class:`networkx.Graph` (internal NX graph).
- `fasta_to_vgraph(...)` returns a :class:`VG` object but is deprecated.
- :class:`VG` exposes small properties to behave like a networkx.Graph
  (graph, nx, number_of_nodes, ...).
"""

from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any
import warnings
import networkx as nx

from .parser import parse_compact, three_to_one_compact, ParsedResidue  # type: ignore


class VG:
    """
    Vertex-centric peptide/residue graph (VG) built on top of networkx.Graph.

    Node attributes
    ---------------
    kind        : "residue" | "mod"
    label       : residue letter (residue) OR normalized token (mod)
    idx         : 1-based residue index (residue)
    parsed      : ParsedResidue (residue) -- parser output (kept for traceability)

    Mod-node attributes
    -------------------
    op          : "+" | "-" | ""   (operator used in bracket list)
    label_raw   : original token text inside brackets
    label_norm  : normalized token (e.g., "4OH" from "4-OH")

    Edge attributes
    ---------------
    relation    : "seq" | "has_mod" | "link"
    link_idxs   : list[int]  (for link edges; may be multiple indices merged)
    ports       : dict[node_id -> Optional[str]]  (port string for endpoints)
    """

    def __init__(self, g: Optional[nx.Graph] = None) -> None:
        """
        :param g: optional pre-built NetworkX graph (useful for
                  deserialization)
        """
        self.g: nx.Graph = g if g is not None else nx.Graph()

    # ---------------- properties that mimic networkx.Graph ----------------
    @property
    def graph(self) -> dict:
        """Return the graph attribute dict (same name as networkx.Graph.graph)."""
        return self.g.graph

    @property
    def nx(self) -> nx.Graph:
        """Alias to the underlying networkx.Graph."""
        return self.g

    def number_of_nodes(self) -> int:
        """Return number of nodes (delegates to networkx)."""
        return self.g.number_of_nodes()

    def number_of_edges(self) -> int:
        """Return number of edges (delegates to networkx)."""
        return self.g.number_of_edges()

    def nodes_iter(self):
        """Return nodes view like networkx (keeps compatibility)."""
        return self.g.nodes

    def edges_iter(self):
        """Return edges view like networkx (keeps compatibility)."""
        return self.g.edges

    # ---------------- constructors ----------------
    @classmethod
    def from_fasta(cls, fasta_or_seq: str, *, allow_three_letter: bool = False) -> "VG":
        """
        Build a VG from a compact FASTA-like sequence.

        :param fasta_or_seq: compact sequence string (optionally starting
                             with FASTA header)
        :param allow_three_letter: if True, convert three-letter AA tokens
                                   to one-letter before parsing
        :returns: VG instance
        :raises ValueError: on parse errors propagated from the parser
        """
        s = fasta_or_seq.strip()
        if s.startswith(">"):
            lines = s.splitlines()
            s = "".join(lines[1:]).strip()
        if allow_three_letter:
            s = three_to_one_compact(s)

        parsed = parse_compact(s)
        g = nx.Graph()

        # two helper steps: add residues+mods, then build link edges
        cls._add_residues_and_mods(parsed, g)
        cls._build_link_edges_from_parsed(g)

        return cls(g)

    @staticmethod
    def _add_residues_and_mods(parsed: List[ParsedResidue], g: nx.Graph) -> None:
        """
        Add residue nodes and mod nodes to `g`. Residue nodes get a `parsed`
        attribute so link/group reconstruction is possible later.
        """
        seq_idx = 0
        prev_rid: Optional[int] = None
        for p in parsed:
            seq_idx += 1
            rid = len(g) + 1
            g.add_node(rid, kind="residue", label=p.aa, idx=seq_idx, parsed=p)
            if prev_rid is not None:
                g.add_edge(prev_rid, rid, relation="seq")

            # add mods for this residue
            for mod_item in p.mods:
                op, tok_raw, tok_norm = _normalize_mod_tuple(mod_item)
                mid = len(g) + 1
                g.add_node(
                    mid,
                    kind="mod",
                    label=tok_norm,
                    label_raw=tok_raw,
                    label_norm=tok_norm,
                    op=op,
                )
                g.add_edge(rid, mid, relation="has_mod")
            prev_rid = rid

    @staticmethod
    def _build_link_edges_from_parsed(g: nx.Graph) -> None:
        """
        Inspect residue nodes' `parsed.links` and connect residues that
        share the same link index. Existing link edges are merged.
        """
        link_map: Dict[int, List[Tuple[int, Optional[str]]]] = {}
        for nid, data in g.nodes(data=True):
            if data.get("kind") != "residue":
                continue
            p: Optional[ParsedResidue] = data.get("parsed")
            if not p:
                continue
            for idx, port in p.links:
                link_map.setdefault(idx, []).append((nid, port))

        for link_idx, members in link_map.items():
            if len(members) < 2:
                # single endpoint: leave encoded in parsed field only
                continue
            # pairwise connect members of same link index
            for i in range(len(members)):
                u, port_u = members[i]
                for j in range(i + 1, len(members)):
                    v, port_v = members[j]
                    if g.has_edge(u, v) and g[u][v].get("relation") == "link":
                        edge = g[u][v]
                        edge.setdefault("link_idxs", [])
                        if link_idx not in edge["link_idxs"]:
                            edge["link_idxs"].append(link_idx)
                        edge.setdefault("ports", {})
                        edge["ports"].update({u: port_u, v: port_v})
                    else:
                        g.add_edge(
                            u,
                            v,
                            relation="link",
                            link_idxs=[link_idx],
                            ports={u: port_u, v: port_v},
                        )

    # ---------------- accessors / convenience ----------------
    def residues_in_order(self) -> List[int]:
        """
        Return residue node ids ordered by their `idx` attribute.

        :returns: list of node ids in sequence order
        """
        res = [
            (n, d.get("idx", 10**9))
            for n, d in self.g.nodes(data=True)
            if d.get("kind") == "residue"
        ]
        return [n for n, _ in sorted(res, key=lambda x: x[1])]

    def mod_nodes_for(self, residue_id: int) -> List[int]:
        """
        Return mod node ids attached to a residue.

        :param residue_id: node id of the residue
        :returns: list of mod node ids (may be empty)
        """
        return [
            nb
            for nb in self.g.neighbors(residue_id)
            if self.g.nodes[nb].get("kind") == "mod"
        ]

    def mod_labels_for(self, residue_id: int) -> List[str]:
        """
        Return normalized mod labels attached to a residue.

        :param residue_id: node id of residue
        :returns: list of mod label strings in arbitrary order
        """
        return [
            self.g.nodes[n].get("label", "") for n in self.mod_nodes_for(residue_id)
        ]

    def link_groups(self) -> Dict[int, List[Tuple[int, Optional[str]]]]:
        """
        Reconstruct link index -> list of (residue_node_id, port) as parsed.
        Reads `parsed` kept on residue nodes (faithful to original tags).
        """
        groups: Dict[int, List[Tuple[int, Optional[str]]]] = {}
        for nid, data in self.g.nodes(data=True):
            if data.get("kind") != "residue":
                continue
            p: Optional[ParsedResidue] = data.get("parsed")
            if not p:
                continue
            for idx, port in p.links:
                groups.setdefault(idx, []).append((nid, port))
        return groups

    def nodes(self, kind: Optional[str] = None) -> List[Tuple[int, Dict[str, Any]]]:
        """
        Return node list with attributes. If `kind` provided, filter by node kind.

        :param kind: optional filter ("residue"|"mod")
        """
        if kind is None:
            return list(self.g.nodes(data=True))
        return [(n, d) for n, d in self.g.nodes(data=True) if d.get("kind") == kind]

    def edges(
        self, relation: Optional[str] = None
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Return edge list. If `relation` provided, filter by edge relation attribute.

        :param relation: optional relation filter ("seq"|"has_mod"|"link")
        """
        if relation is None:
            return list(self.g.edges(data=True))
        return [
            (u, v, d)
            for u, v, d in self.g.edges(data=True)
            if d.get("relation") == relation
        ]

    # ---------------- serialization / debugging ----------------
    def to_simple_dict(self) -> Dict[str, Any]:
        """
        Lightweight serializable representation (nodes + edges). The `parsed`
        field is omitted to keep output JSON-friendly.
        """
        nodes = []
        for n, d in self.g.nodes(data=True):
            nd = dict(d)
            nd["id"] = n
            nd.pop("parsed", None)
            nodes.append(nd)
        edges = []
        for u, v, d in self.g.edges(data=True):
            ed = dict(d)
            ed.update({"u": u, "v": v})
            edges.append(ed)
        return {"nodes": nodes, "edges": edges}

    # ---------------- misc ----------------
    def __repr__(self) -> str:
        nr = len([1 for _, d in self.g.nodes(data=True) if d.get("kind") == "residue"])
        nm = len([1 for _, d in self.g.nodes(data=True) if d.get("kind") == "mod"])
        nl = len(
            [1 for _, _, d in self.g.edges(data=True) if d.get("relation") == "link"]
        )
        return f"VG(residues={nr}, mods={nm}, links={nl})"


# ---------------- convenience constructors ----------------
def fasta_to_vg(seq: str, *, allow_three_letter: bool = False) -> nx.Graph:
    """
    Convenience constructor that returns the raw networkx.Graph (not a VG object).

    :param seq: compact FASTA-like sequence
    :param allow_three_letter: allow three-letter AA tokens
    :returns: networkx.Graph representing the VG structure
    """
    vg_obj = VG.from_fasta(seq, allow_three_letter=allow_three_letter)
    return vg_obj.g  # return raw NX graph as requested


# ---------------- backward-compatible aliases / deprecations ----------------
def _warn_deprecated(old: str, new: str) -> None:
    warnings.warn(
        f"'{old}' is deprecated — use '{new}' instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def fasta_to_vgraph(seq: str, *, allow_three_letter: bool = False) -> VG:
    """
    Deprecated wrapper that returns a VG instance (use fasta_to_vg -> nx.Graph instead).
    """
    _warn_deprecated("fasta_to_vgraph", "fasta_to_vg (returns nx.Graph)")
    return VG.from_fasta(seq, allow_three_letter=allow_three_letter)


# alias class name VGraph -> VG (keeps older name working)
VGraph = VG  # simple alias


# ---------------- small helpers ----------------
def _normalize_mod_token(tok: str) -> str:
    """
    Normalize a mod token for internal storage:
      - strip surrounding whitespace
      - collapse internal whitespace
      - collapse numeric-dash pattern like "4-OH" -> "4OH"
      - otherwise keep token mostly intact
    """
    t = str(tok).strip()
    t = " ".join(t.split())
    if "-" in t and any(ch.isdigit() for ch in t):
        t = t.replace("-", "")
    return t


def _normalize_mod_tuple(item: Any) -> Tuple[str, str, str]:
    """
    Defensive normalization for parser.mod tuple-like objects.

    Accepts:
      - (op, raw)
      - (op, raw, norm)
      - raw (str)
      - single-item tuples
    Returns (op, raw, norm).
    """
    if isinstance(item, (list, tuple)):
        if len(item) == 2:
            op, tok_raw = item
            tok_norm = _normalize_mod_token(tok_raw)
            return op, tok_raw, tok_norm
        if len(item) >= 3:
            op, tok_raw, tok_norm = item[0], item[1], item[2]
            return op, tok_raw, tok_norm
        if len(item) == 1:
            tok_raw = str(item[0])
            tok_norm = _normalize_mod_token(tok_raw)
            return "", tok_raw, tok_norm
    # fallback: treat item as raw token
    tok_raw = str(item)
    tok_norm = _normalize_mod_token(tok_raw)
    return "", tok_raw, tok_norm


# public API
__all__ = [
    "VG",
    "VGraph",
    "fasta_to_vg",  # returns networkx.Graph
    "fasta_to_vgraph",  # deprecated, returns VG
]
