from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .base import BaseFeature
from .config import BaseConfig

# Keep the same key style as indices.py
GlobalKey = Tuple[str, int]


@dataclass(frozen=True)
class ResidueRepAtom:
    """
    Representative atom coordinate for a residue (pDockQ-style):
    - CB for non-GLY
    - CA for GLY or if CB missing
    """

    chain: str
    res_seq: int
    res_name: str
    atom_name: str  # "CA" or "CB"
    xyz: Tuple[float, float, float]


@dataclass(frozen=True)
class ContactResult:
    """
    Result of a pDockQ-style contact computation between two chains.

    n_contacts:
        Total number of residue–residue contacts (unique pairs), as used in pDockQ.
    pairs:
        Residue-level contact pairs in (chain,res_seq) keys.
    pairs_global:
        Same pairs but mapped to global indices (1-based) if requested.
    interface_a / interface_b:
        Interface residues on each side (as keys), derived from the pairs.
    """

    chain_a: str
    chain_b: str
    cutoff: float
    n_contacts: int
    pairs: List[Tuple[GlobalKey, GlobalKey]]
    pairs_global: Optional[List[Tuple[int, int]]]
    interface_a: List[GlobalKey]
    interface_b: List[GlobalKey]


class ContactCounter(BaseFeature):
    """
    Contact counter tailored for pDockQ.

    IMPORTANT:
    - pDockQ "N_contacts" counts *residue–residue* contacts using one rep atom
      per residue: rep(res) = CB, except GLY uses CA; if CB missing, use CA.
    - A residue pair (i,j) is a contact if distance(rep_i, rep_j) <= cutoff.

    This differs from IndexCalculator.get_interface_indices(), which marks
    contacts if *any atom–atom* pair is within cutoff.
    """

    def __init__(
        self,
        pdb_lines: List[str],
        peptide_chain_position: str = "last",
        distance_cutoff: float = 8.0,
    ):
        super().__init__(
            pdb_lines=pdb_lines,
            peptide_chain_position=peptide_chain_position,
            distance_cutoff=distance_cutoff,
        )

    @classmethod
    def from_config(cls, config: BaseConfig) -> "ContactCounter":
        return cls(
            pdb_lines=config.pdb_lines,
            peptide_chain_position=config.peptide_chain_position,
            distance_cutoff=config.cutoff,
        )

    # -----------------------
    # Public API
    # -----------------------
    def contact_count_pair(
        self,
        chain_a: str,
        chain_b: str,
        *,
        return_global: bool = False,
        use_grid: bool = True,
    ) -> ContactResult:
        """
        Compute pDockQ-style residue contacts between two chains.

        Parameters
        ----------
        chain_a, chain_b:
            Chain IDs to compare.
        return_global:
            If True, also return pairs mapped to global residue indices (1-based).
        use_grid:
            If True, use a simple spatial grid hash for speed; otherwise O(N*M).

        Returns
        -------
        ContactResult
        """
        self.validate()

        reps, chains_order, per_chain_res_order = self._collect_rep_atoms(
            self.pdb_lines
        )
        if chain_a not in reps or chain_b not in reps:
            raise ValueError(
                f"Chains not found in PDB: {chain_a}, {chain_b}. "
                f"Found: {sorted(reps.keys())}"
            )

        A = reps[chain_a]
        B = reps[chain_b]
        if not A or not B:
            return ContactResult(
                chain_a=chain_a,
                chain_b=chain_b,
                cutoff=float(self.distance_cutoff),
                n_contacts=0,
                pairs=[],
                pairs_global=[] if return_global else None,
                interface_a=[],
                interface_b=[],
            )

        d2_cut = float(self.distance_cutoff) ** 2

        if use_grid:
            pairs = self._contacts_grid(
                A, B, d2_cut=d2_cut, cutoff=float(self.distance_cutoff)
            )
        else:
            pairs = self._contacts_naive(A, B, d2_cut=d2_cut)

        # Interface residue sets
        iface_a: Set[GlobalKey] = set()
        iface_b: Set[GlobalKey] = set()
        for ka, kb in pairs:
            iface_a.add(ka)
            iface_b.add(kb)

        pairs_sorted = sorted(pairs)
        iface_a_sorted = sorted(iface_a)
        iface_b_sorted = sorted(iface_b)

        pairs_global: Optional[List[Tuple[int, int]]] = None
        if return_global:
            global_map = self._build_global_residue_map(
                chains_order, per_chain_res_order
            )
            pairs_global = [(global_map[a], global_map[b]) for a, b in pairs_sorted]

        return ContactResult(
            chain_a=chain_a,
            chain_b=chain_b,
            cutoff=float(self.distance_cutoff),
            n_contacts=len(pairs_sorted),
            pairs=pairs_sorted,
            pairs_global=pairs_global,
            interface_a=iface_a_sorted,
            interface_b=iface_b_sorted,
        )

    def contact_count_peptide_protein(
        self,
        *,
        peptide_chain: Optional[str] = None,
        peptide_chain_position: str = "last",
        return_global: bool = False,
        use_grid: bool = True,
    ) -> ContactResult:
        """
        Convenience wrapper for peptide-vs-protein scoring (single peptide chain vs
        all other chains).

        - If peptide_chain is provided, use it.
        - Else choose peptide chain by position (last/first among chain IDs).

        The "protein side" is all remaining chains merged into a pseudo partner.
        """
        self.validate()
        reps, chains_order, per_chain_res_order = self._collect_rep_atoms(
            self.pdb_lines
        )
        if not reps:
            raise ValueError("No ATOM/HETATM records found.")

        chain_ids = list(reps.keys())
        if peptide_chain is None:
            peptide_chain = (
                chain_ids[-1] if peptide_chain_position == "last" else chain_ids[0]
            )
        if peptide_chain not in reps:
            raise ValueError(
                f"Peptide chain '{peptide_chain}' not found. Found: {chain_ids}"
            )

        # Merge other chains into a pseudo partner
        pep = reps[peptide_chain]
        others: List[ResidueRepAtom] = []
        for cid, rr in reps.items():
            if cid == peptide_chain:
                continue
            others.extend(rr)

        partner = "_PROT"
        A = pep
        B = [
            ResidueRepAtom(
                chain=partner,
                res_seq=r.res_seq,
                res_name=r.res_name,
                atom_name=r.atom_name,
                xyz=r.xyz,
            )
            for r in others
        ]

        d2_cut = float(self.distance_cutoff) ** 2
        pairs = (
            self._contacts_grid(A, B, d2_cut=d2_cut, cutoff=float(self.distance_cutoff))
            if use_grid
            else self._contacts_naive(A, B, d2_cut=d2_cut)
        )

        iface_a: Set[GlobalKey] = set()
        iface_b: Set[GlobalKey] = set()
        for ka, kb in pairs:
            iface_a.add(ka)
            iface_b.add(kb)

        pairs_sorted = sorted(pairs)
        iface_a_sorted = sorted(iface_a)
        iface_b_sorted = sorted(iface_b)

        pairs_global: Optional[List[Tuple[int, int]]] = None
        if return_global:
            # There is no unique global mapping for merged partner residues.
            pairs_global = None
            self.log_warning(
                "return_global=True is not supported for merged protein mode; "
                "set peptide_chain and call contact_count_pair() per chain."
            )

        return ContactResult(
            chain_a=peptide_chain,
            chain_b=partner,
            cutoff=float(self.distance_cutoff),
            n_contacts=len(pairs_sorted),
            pairs=pairs_sorted,
            pairs_global=pairs_global,
            interface_a=iface_a_sorted,
            interface_b=iface_b_sorted,
        )

    # -----------------------
    # Parsing and mapping
    # -----------------------
    @staticmethod
    def _parse_pdb_atom_line(
        line: str,
    ) -> Optional[Tuple[str, int, str, str, Tuple[float, float, float]]]:
        """
        Minimal fixed-width PDB parser (no BioPython).
        Returns (chain, res_seq, res_name, atom_name, (x,y,z)) or None.
        """
        if not line.startswith(("ATOM  ", "HETATM")):
            return None
        if len(line) < 54:
            return None

        try:
            atom_name = line[12:16].strip().upper()
            res_name = line[17:20].strip().upper()
            chain = line[21].strip()
            res_seq = int(line[22:26].strip())
            x = float(line[30:38].strip())
            y = float(line[38:46].strip())
            z = float(line[46:54].strip())
        except Exception:
            # Fallback: split-based (less reliable but helps weird formatting)
            try:
                parts = line.split()
                atom_name = parts[2].upper()
                res_name = parts[3].upper()
                chain = parts[4]
                res_seq = int(parts[5])
                x, y, z = float(parts[6]), float(parts[7]), float(parts[8])
            except Exception:
                return None

        if not chain:
            chain = "_"
        return chain, res_seq, res_name, atom_name, (x, y, z)

    # Split into two small helpers to reduce complexity
    @classmethod
    def _collect_ca_cb_positions(cls, pdb_lines: Sequence[str]) -> Tuple[
        Dict[Tuple[str, int], Dict[str, Tuple[float, float, float]]],
        Dict[Tuple[str, int], str],
        List[str],
        Dict[str, List[int]],
    ]:
        """
        Scan PDB lines and collect CA/CB coordinates per residue.
        Returns:
            tmp[(chain,res_seq)][atom_name] = (x,y,z)
            resname[(chain,res_seq)] = res_name
            chains_order, per_chain_res_order
        """
        chains_order: List[str] = []
        per_chain_res_order: Dict[str, List[int]] = {}
        seen_res: Dict[str, Set[int]] = {}

        tmp: Dict[Tuple[str, int], Dict[str, Tuple[float, float, float]]] = {}
        resname: Dict[Tuple[str, int], str] = {}

        for line in pdb_lines:
            parsed = cls._parse_pdb_atom_line(line)
            if parsed is None:
                continue
            chain, rseq, rname, aname, xyz = parsed

            if chain not in per_chain_res_order:
                chains_order.append(chain)
                per_chain_res_order[chain] = []
                seen_res[chain] = set()

            if rseq not in seen_res[chain]:
                per_chain_res_order[chain].append(rseq)
                seen_res[chain].add(rseq)

            key = (chain, rseq)
            resname[key] = rname
            tmp.setdefault(key, {})
            if aname in {"CA", "CB"}:
                tmp[key][aname] = xyz

        return tmp, resname, chains_order, per_chain_res_order

    @classmethod
    def _build_rep_atoms_from_tmp(
        cls,
        tmp: Dict[Tuple[str, int], Dict[str, Tuple[float, float, float]]],
        resname: Dict[Tuple[str, int], str],
        chains_order: List[str],
        per_chain_res_order: Dict[str, List[int]],
    ) -> Dict[str, List[ResidueRepAtom]]:
        """
        From collected CA/CB positions choose representative atoms per residue.
        """
        reps: Dict[str, List[ResidueRepAtom]] = {c: [] for c in chains_order}
        for chain in chains_order:
            for rseq in per_chain_res_order[chain]:
                key = (chain, rseq)
                rname = resname.get(key, "UNK")
                ca = tmp.get(key, {}).get("CA")
                cb = tmp.get(key, {}).get("CB")

                if rname == "GLY":
                    if ca is None:
                        continue
                    reps[chain].append(ResidueRepAtom(chain, rseq, rname, "CA", ca))
                else:
                    if cb is not None:
                        reps[chain].append(ResidueRepAtom(chain, rseq, rname, "CB", cb))
                    elif ca is not None:
                        reps[chain].append(ResidueRepAtom(chain, rseq, rname, "CA", ca))
                    else:
                        # no CA/CB found for this residue -> skip
                        continue
        return reps

    @classmethod
    def _collect_rep_atoms(
        cls, pdb_lines: Sequence[str]
    ) -> Tuple[Dict[str, List[ResidueRepAtom]], List[str], Dict[str, List[int]]]:
        """
        Build representative atoms per residue for each chain.

        Returns:
          reps[chain] = list of ResidueRepAtom (one per residue, in first-seen order)
          chains_order = first-seen chain order in file
          per_chain_res_order[chain] = first-seen residue order (res_seq ints)
        """
        tmp, resname, chains_order, per_chain_res_order = cls._collect_ca_cb_positions(
            pdb_lines
        )
        reps = cls._build_rep_atoms_from_tmp(
            tmp, resname, chains_order, per_chain_res_order
        )
        return reps, chains_order, per_chain_res_order

    @staticmethod
    def _build_global_residue_map(
        chains_order: Sequence[str],
        per_chain_res_order: Dict[str, Sequence[int]],
    ) -> Dict[GlobalKey, int]:
        """
        Global indexing: concatenate residues by chain appearance order, then
        residue appearance order. 1-based, consistent with indices.py style.
        """
        global_map: Dict[GlobalKey, int] = {}
        idx = 1
        for c in chains_order:
            for r in per_chain_res_order.get(c, []):
                global_map[(c, int(r))] = idx
                idx += 1
        return global_map

    # -----------------------
    # Distance + contact enumeration
    # -----------------------
    @staticmethod
    def _within_cutoff2(
        a: Tuple[float, float, float], b: Tuple[float, float, float], d2_cut: float
    ) -> bool:
        xa, ya, za = a
        xb, yb, zb = b
        dx = xa - xb
        dy = ya - yb
        dz = za - zb
        return (dx * dx + dy * dy + dz * dz) <= d2_cut

    @classmethod
    def _contacts_naive(
        cls,
        A: Sequence[ResidueRepAtom],
        B: Sequence[ResidueRepAtom],
        *,
        d2_cut: float,
    ) -> Set[Tuple[GlobalKey, GlobalKey]]:
        pairs: Set[Tuple[GlobalKey, GlobalKey]] = set()
        for ra in A:
            ka = (ra.chain, ra.res_seq)
            for rb in B:
                kb = (rb.chain, rb.res_seq)
                if cls._within_cutoff2(ra.xyz, rb.xyz, d2_cut):
                    pairs.add((ka, kb))
        return pairs

    @classmethod
    def _contacts_grid(
        cls,
        A: Sequence[ResidueRepAtom],
        B: Sequence[ResidueRepAtom],
        *,
        d2_cut: float,
        cutoff: float,
    ) -> Set[Tuple[GlobalKey, GlobalKey]]:
        """
        Spatial hash (uniform grid) to avoid O(N*M) for large chains.
        """
        cell = float(cutoff)
        inv = 1.0 / cell

        def cell_id(xyz: Tuple[float, float, float]) -> Tuple[int, int, int]:
            x, y, z = xyz
            return (int(x * inv), int(y * inv), int(z * inv))

        grid: Dict[Tuple[int, int, int], List[ResidueRepAtom]] = {}
        for rb in B:
            cid = cell_id(rb.xyz)
            grid.setdefault(cid, []).append(rb)

        pairs: Set[Tuple[GlobalKey, GlobalKey]] = set()
        for ra in A:
            ka = (ra.chain, ra.res_seq)
            cx, cy, cz = cell_id(ra.xyz)
            # check neighbor cells
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        bucket = grid.get((cx + dx, cy + dy, cz + dz))
                        if not bucket:
                            continue
                        for rb in bucket:
                            if cls._within_cutoff2(ra.xyz, rb.xyz, d2_cut):
                                kb = (rb.chain, rb.res_seq)
                                pairs.add((ka, kb))
        return pairs

    # -----------------------
    # CLI (optional)
    # -----------------------
    @staticmethod
    def args() -> argparse.ArgumentParser:
        p = argparse.ArgumentParser(
            description="Compute pDockQ-style residue contact count (CB/CA only)."
        )
        p.add_argument("--input", type=str, required=True, help="Path to PDB file")
        p.add_argument("--chain-a", type=str, required=True, help="Chain A")
        p.add_argument("--chain-b", type=str, required=True, help="Chain B")
        p.add_argument(
            "--cutoff",
            type=float,
            default=8.0,
            help="Contact cutoff in Å (default: 8.0)",
        )
        p.add_argument(
            "--global", action="store_true", help="Also print global-index pairs"
        )
        p.add_argument(
            "--no-grid", action="store_true", help="Disable grid acceleration"
        )
        return p
