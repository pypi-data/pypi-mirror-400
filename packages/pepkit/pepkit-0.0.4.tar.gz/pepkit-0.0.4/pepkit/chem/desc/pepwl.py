# pepwl.py
"""
PepWL — NetworkX-based Weisfeiler–Lehman peptide fingerprint with readable motifs.

This module provides the `PepWL` class: a deterministic, explainable WL
fingerprint implementation that uses NetworkX graphs (backbone + crosslinks),
produces binary and count fingerprints, supports multi-hash (k bits per label),
and includes TF–IDF corpus helpers.

Sphinx-style docstrings are used throughout (``:param:``, ``:type:``).

Example
-------
A short usage example (Sphinx / reST style):

.. code-block:: python

    from pepwl import PepWL

    # create two PepWL instances with identical fingerprint configuration
    fp_size = 2048
    n_hashes = 2
    wl_h = 3

    fasta = '''>pep1
    PEPTIDEKGAIV'''
    p1 = PepWL(fp_size=fp_size, wl_h=wl_h, n_hashes=n_hashes).from_fasta(fasta)

    # crosslink example (E at idx=1 connected to K at idx=7 via sidechain "sc")
    p2 = PepWL(fp_size=fp_size, wl_h=wl_h, n_hashes=n_hashes).from_sequence(
        "PEPTIDEKGAIV", crosslinks=[(1, 7, "sc")]
    )

    # similarity (binary Tanimoto)
    print("Tanimoto:", p1.similarity_tanimoto(p2))

    # TF–IDF across a corpus (must use same fp_size & n_hashes)
    idf = PepWL.fit_idf([p1, p2])
    v1 = p1.tfidf_counts(idf)
    v2 = p2.tfidf_counts(idf)
    # cosine requires numpy to be installed
    from pepwl import PepWL as _PepWL  # static helper available
    print("Cosine(tfidf):", _PepWL.cosine_from_counts(v1, v2))

"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple, Iterable
from collections import defaultdict, Counter
import hashlib
import textwrap
import networkx as nx

try:
    import numpy as np
    from numpy.linalg import norm
except Exception:
    np = None

from .sequence import FeatureSpec

Index = int
WLLabel = str
Edge = Tuple[int, int, str]


# ---------------------- hashing helpers ------------------------------------ #
def _sha1_hex(s: str) -> str:
    """Return SHA-1 hex digest for a string (deterministic)."""
    return hashlib.sha1(s.encode("utf8")).hexdigest()


def _hash_indices(label: str, n_bits: int, n_hashes: int = 1) -> List[int]:
    """
    Produce `n_hashes` deterministic bin indices for `label`.

    :param label: input label string to hash
    :type label: str
    :param n_bits: fingerprint length (number of bins)
    :type n_bits: int
    :param n_hashes: how many independent hashes / bins to produce
    :type n_hashes: int
    :returns: list of integer indices in range `[0, n_bits)`
    :rtype: List[int]
    """
    idxs = []
    for i in range(n_hashes):
        digest = hashlib.sha1((label + f"::h{i}").encode("utf8")).digest()
        idxs.append(int.from_bytes(digest, "big") % n_bits)
    return idxs


# ============================ PepWL class ================================== #
class PepWL:
    """
    NetworkX-based Weisfeiler–Lehman fingerprint with readable motifs and corpus
    helpers.

    Produces:
      - binary bit vector (presence of hashed WL labels -> bits)
      - optional count vector (occurrence multiplicity per hashed bin)
      - readable motif strings per WL radius for explainability
      - TF–IDF corpus helpers

    :param fp_size: number of fingerprint bins (recommended 1024–8192)
    :type fp_size: int
    :param wl_h: WL iterations (context radius; typical 2–3)
    :type wl_h: int
    :param n_hashes: number of independent hashes per WL label (reduce collisions)
    :type n_hashes: int
    :param include_physchem_in_motif: include phys-chem readable tokens in motifs
    :type include_physchem_in_motif: bool
    :param features: FeatureSpec object for initial node labels (phys-chem buckets)
    :type features: Optional[FeatureSpec]
    :param use_counts: whether to construct a count vector (for cosine/tf-idf)
    :type use_counts: bool

    :raises RuntimeError: if methods needing a graph are called before building one
    """

    def __init__(
        self,
        fp_size: int = 2048,
        wl_h: int = 3,
        n_hashes: int = 2,
        include_physchem_in_motif: bool = True,
        features: Optional[FeatureSpec] = None,
        use_counts: bool = True,
    ) -> None:
        self.fp_size = int(fp_size)
        self.wl_h = int(wl_h)
        self.n_hashes = int(n_hashes)
        self.include_physchem = bool(include_physchem_in_motif)
        self.features = features if features is not None else FeatureSpec()
        self.use_counts = bool(use_counts)

        # internal state (filled after compute())
        self.G: Optional[nx.Graph] = None
        self.seq: Optional[str] = None

        self.iter_labels: List[Dict[int, WLLabel]] = []
        self.iter_motifs: List[Dict[int, str]] = []
        self.label_counts: Counter = Counter()
        self.label_to_motif: Dict[WLLabel, str] = {}
        self.bit_to_motifs: Dict[int, Counter] = defaultdict(Counter)

        self.bit_vector: List[int] = []
        self.count_vector: Optional[List[int]] = None

    # --------------------- input / builders -------------------------------- #

    def parse_fasta_first_sequence(self, fasta: str) -> str:
        """Extract the first sequence from a FASTA string."""
        lines = [
            ln.strip()
            for ln in textwrap.dedent(fasta).strip().splitlines()
            if ln.strip()
        ]
        if not lines:
            raise ValueError("empty FASTA")
        if lines[0].startswith(">"):
            seq = "".join(lines[1:])
        else:
            seq = "".join(lines)
        return seq.strip().upper()

    def build_linear_graph(self, sequence: str) -> nx.Graph:
        """
        Build a simple linear NetworkX graph for a peptide sequence.

        Nodes: integers 0..n-1 with attribute 'res' (residue token).
        Backbone edges (i,i+1) have attribute 'etype'='bb'.
        """
        G = nx.Graph()
        seq = sequence.strip().upper()
        for i, aa in enumerate(seq):
            G.add_node(i, res=aa)
        for i in range(len(seq) - 1):
            G.add_edge(i, i + 1, etype="bb")
        return G

    def from_sequence(
        self, sequence: str, crosslinks: Optional[Sequence[Edge]] = None
    ) -> "PepWL":
        """Build graph from sequence and optional crosslinks, then compute WL."""
        self.seq = sequence.strip().upper()
        self.G = self.build_linear_graph(self.seq)
        if crosslinks:
            for i, j, et in crosslinks:
                self.G.add_edge(int(i), int(j), etype=str(et))
        self.compute()
        return self

    def from_fasta(
        self, fasta: str, crosslinks: Optional[Sequence[Edge]] = None
    ) -> "PepWL":
        """Convenience: build from a FASTA string (first record only)."""
        seq = self.parse_fasta_first_sequence(fasta)
        return self.from_sequence(seq, crosslinks=crosslinks)

    def from_networkx(self, G: nx.Graph, residue_attr: str = "res") -> "PepWL":
        """Use an existing NetworkX graph as input."""
        self.G = G.copy()
        try:
            seq = "".join(self.G.nodes[n][residue_attr] for n in sorted(self.G.nodes()))
            self.seq = seq
        except Exception:
            self.seq = None
        self.compute()
        return self

    # --------------------- WL core (readable motifs) ----------------------- #

    def _initial_node_label(self, n: int) -> str:
        """
        Create human-readable initial node label using FeatureSpec.

        Kept inline for clarity; FeatureSpec produces consistent token labels.
        """
        aa = self.G.nodes[n].get("res", "X")
        # Use FeatureSpec helper when available (keeps tokenization consistent).
        # If FeatureSpec does not provide identity or other fields, fallback.
        if hasattr(self.features, "label_token"):
            return self.features.label_token(
                aa, hide_identity=not self.features.include_identity
            )
        # legacy fallback
        idtok = aa if self.features.include_identity else "X"
        charge = (
            "pos" if aa in ("K", "R", "H") else ("neg" if aa in ("D", "E") else "neut")
        )
        hydro = self.features.hydro.get(aa, "unk")
        mass = self.features.mass.get(aa, 0)
        mass_bin = f"m{int((mass // self.features.mass_bin) * self.features.mass_bin)}"
        hbd = self.features.hbd.get(aa, 0)
        return f"{idtok}|{charge}|{hydro}|{mass_bin}|hbd{hbd}"

    def _readable_aggregate(
        self, center: int, readable_prev: Dict[int, str], radius: int
    ) -> str:
        """Build a readable motif around `center` up to `radius`."""
        parts = [f"({self.G.nodes[center].get('res','?')})"]
        frontier = [center]
        visited = {center}
        for r in range(1, radius + 1):
            layer = []
            nxt = []
            for v in sorted(frontier):
                for u in sorted(self.G.neighbors(v)):
                    if u in visited:
                        continue
                    et = self.G.edges[v, u].get("etype", "bb")
                    token = readable_prev.get(u, self.G.nodes[u].get("res", "?"))
                    layer.append(f"{et}:{token}")
                    nxt.append(u)
            if layer:
                layer.sort()
                parts.append(f"|r{r}:" + ",".join(layer))
            visited.update(nxt)
            frontier = nxt
        return " ".join(parts)

    def _initialize_labels(self):
        """Initialize readable_prev, labels_prev, iter_motifs and label_counts."""
        readable_prev: Dict[int, str] = {}
        labels_prev: Dict[int, str] = {}
        for n in sorted(self.G.nodes()):
            rlab = self._initial_node_label(n)
            readable_prev[n] = rlab
            labels_prev[n] = rlab
        self.iter_labels = [dict(labels_prev)]
        self.iter_motifs = [
            {n: f"({self.G.nodes[n].get('res','?')})" for n in sorted(self.G.nodes())}
        ]
        self.label_counts = Counter(labels_prev.values())
        return labels_prev, readable_prev

    def _wl_iteration(self, labels_prev: Dict[int, str], readable_prev: Dict[int, str]):
        """
        Perform one WL refinement iteration and return new labels, readable tokens,
        and human motifs for this iteration.
        """
        labels_new: Dict[int, str] = {}
        readable_new: Dict[int, str] = {}
        motifs_t: Dict[int, str] = {}

        for n in sorted(self.G.nodes()):
            neigh_hashed = []
            for u in sorted(self.G.neighbors(n)):
                et = self.G.edges[n, u].get("etype", "bb")
                neigh_hashed.append(f"{et}:{labels_prev[u]}")
            neigh_hashed.sort()
            payload = f"{labels_prev[n]}|{'|'.join(neigh_hashed)}"
            new_label = _sha1_hex(payload)
            labels_new[n] = new_label

            motifs_t[n] = self._readable_aggregate(n, readable_prev, radius=1)

            # create compact readable token to propagate (identity only)
            neigh_readable = []
            for u in sorted(self.G.neighbors(n)):
                et = self.G.edges[n, u].get("etype", "bb")
                token = readable_prev[u].split("|")[0]
                neigh_readable.append(f"{et}:{token}")
            if neigh_readable:
                neigh_readable.sort()
                readable_new[n] = f"{readable_prev[n]}|{'|'.join(neigh_readable)}"
            else:
                readable_new[n] = readable_prev[n]

        return labels_new, readable_new, motifs_t

    def _build_label_to_motif(self):
        """Map each hashed WL label to a representative human motif (first seen)."""
        label_to_motif: Dict[WLLabel, str] = {}
        for t, labmap in enumerate(self.iter_labels):
            motmap = self.iter_motifs[t]
            for node, lab in labmap.items():
                if lab not in label_to_motif:
                    label_to_motif[lab] = motmap.get(
                        node, f"({self.G.nodes[node].get('res','?')})"
                    )
        self.label_to_motif = label_to_motif

    def compute(self) -> "PepWL":
        """
        Run WL refinement, produce readable motifs and hashed WL labels,
        then assemble fingerprint vectors.

        :returns: self (with bit_vector, count_vector, and explain maps populated)
        """
        if self.G is None:
            raise RuntimeError(
                "No graph: use from_sequence/from_fasta/from_networkx first."
            )

        labels_prev, readable_prev = self._initialize_labels()

        # WL refinement loop: use helper to keep complexity down
        for t in range(1, self.wl_h + 1):
            labels_new, readable_new, motifs_t = self._wl_iteration(
                labels_prev, readable_prev
            )

            self.iter_labels.append(labels_new)
            # motifs_t currently computed at radius=1 per iteration; rename to include t
            self.iter_motifs.append(motifs_t)
            self.label_counts.update(labels_new.values())

            labels_prev = labels_new
            readable_prev = readable_new

        # representative motif for each hashed WL label
        self._build_label_to_motif()

        # assemble bit vector & counts
        self._assemble_vectors()
        return self

    def _assemble_vectors(self) -> None:
        """Create binary bit_vector and optional count_vector."""
        B = self.fp_size
        bits = [0] * B
        counts = [0] * B if self.use_counts else None

        for lab, motif in self.label_to_motif.items():
            idxs = _hash_indices(lab, B, self.n_hashes)
            for idx in idxs:
                bits[idx] = 1
                self.bit_to_motifs[idx][motif] += 1

        if counts is not None:
            for lab, freq in self.label_counts.items():
                idxs = _hash_indices(lab, B, self.n_hashes)
                for idx in idxs:
                    counts[idx] += freq

        self.bit_vector = bits
        self.count_vector = counts

    # ---------------------- exports & explainability ---------------------- #

    def to_bitstring(self) -> str:
        """Return the binary fingerprint as a '0101...' string."""
        return "".join("1" if b else "0" for b in self.bit_vector)

    def to_sparse_bits(self) -> List[int]:
        """Return sorted list of indices of set bits."""
        return [i for i, b in enumerate(self.bit_vector) if b]

    def explain_bit(self, idx: int, top: int = 8) -> List[Tuple[str, int]]:
        """Return the top (motif, count) contributors to the given bit."""
        return self.bit_to_motifs.get(idx, Counter()).most_common(top)

    def motif_positions(self, motif_text: str) -> List[Tuple[int, int]]:
        """Find positions (node index, radius/iteration) where a motif occurs."""
        hits = []
        for t, motmap in enumerate(self.iter_motifs):
            for pos, mot in motmap.items():
                if mot == motif_text:
                    hits.append((pos, t))
        return hits

    def top_bits_with_motifs(self, top_bits: int = 10, top_motifs: int = 4):
        """Return the top `top_bits` bits ranked by total motif counts,
        together with their top motifs."""
        populated = [
            (i, sum(self.bit_to_motifs[i].values())) for i in self.to_sparse_bits()
        ]
        populated.sort(key=lambda x: x[1], reverse=True)
        out = []
        for i, _ in populated[:top_bits]:
            out.append((i, self.explain_bit(i, top=top_motifs)))
        return out

    # --------------------------- similarity -------------------------------- #

    @staticmethod
    def tanimoto_from_bits(bits_a: Iterable[int], bits_b: Iterable[int]) -> float:
        """Tanimoto (Jaccard) similarity between two binary bit sets."""
        A = set(bits_a)
        B = set(bits_b)
        if not A and not B:
            return 1.0
        inter = len(A & B)
        union = len(A | B)
        return inter / union if union else 0.0

    def similarity_tanimoto(self, other: "PepWL") -> float:
        """Compute Tanimoto similarity against another PepWL instance."""
        return self.tanimoto_from_bits(self.to_sparse_bits(), other.to_sparse_bits())

    @staticmethod
    def cosine_from_counts(cnt_a: Sequence[float], cnt_b: Sequence[float]) -> float:
        """Cosine similarity between two numeric count vectors. Requires `numpy`."""
        if np is None:
            raise RuntimeError("numpy required for cosine")
        a = np.asarray(cnt_a, dtype=float)
        b = np.asarray(cnt_b, dtype=float)
        na = norm(a)
        nb = norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))

    def similarity_cosine(self, other: "PepWL") -> float:
        """Cosine similarity between this instance and another using count vectors."""
        if self.count_vector is None or other.count_vector is None:
            raise RuntimeError(
                "count_vector missing; create PepWL with use_counts=True"
            )
        if len(self.count_vector) != len(other.count_vector):
            raise ValueError(
                "count_vector length mismatch: ensure same fp_size & n_hashes."
            )
        return self.cosine_from_counts(self.count_vector, other.count_vector)

    # ------------------------ TF–IDF (corpus) -------------------------------- #

    @staticmethod
    def fit_idf(instances: Sequence["PepWL"]) -> Dict[WLLabel, float]:
        """
        Compute smoothed IDF weights for WL labels across a corpus.

        All instances must share the same `fp_size` and `n_hashes`.
        """
        if not instances:
            return {}
        fp0 = instances[0].fp_size
        nh0 = instances[0].n_hashes
        for inst in instances:
            if inst.fp_size != fp0 or inst.n_hashes != nh0:
                raise ValueError(
                    "All PepWL instances must have same fp_size and n_hashes to fit IDF."
                )
        N = len(instances)
        df = Counter()
        for inst in instances:
            df.update(set(inst.label_counts.keys()))
        idf = {}
        for lab, d in df.items():
            val = (N + 1.0) / (d + 1.0)
            idf[lab] = (np.log(val) + 1.0) if np is not None else val
        return idf

    def tfidf_counts(self, idf: Dict[WLLabel, float]) -> List[float]:
        """Produce a TF–IDF numeric vector (aligned to this instance's `fp_size`)."""
        if self.count_vector is None:
            raise RuntimeError("use_counts=False — cannot create tfidf vector.")
        B = self.fp_size
        vec = [0.0] * B
        for lab, tf in self.label_counts.items():
            w = float(tf) * float(idf.get(lab, 1.0))
            for idx in _hash_indices(lab, B, self.n_hashes):
                vec[idx] += w
        return vec
