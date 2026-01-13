"""Low-level RDKit helpers used by the peptide decoder."""

from __future__ import annotations
from typing import Dict, List, Optional
from rdkit import Chem
from rdkit.Chem import rdchem

__all__ = [
    "is_carbonyl_carbon",
    "find_calpha_indices",
    "order_residues_via_backbone",
]


def is_carbonyl_carbon(atom: Chem.Atom) -> bool:
    """Return True iff ``atom`` is a carbonyl carbon C(=O).

    :param atom: RDKit atom instance.
    :returns: True if atom is carbon and has a double-bonded oxygen neighbor.
    """
    if atom.GetAtomicNum() != 6:
        return False
    for b in atom.GetBonds():
        o = b.GetOtherAtom(atom)
        if o.GetAtomicNum() == 8 and b.GetBondType() == rdchem.BondType.DOUBLE:
            return True
    return False


def find_calpha_indices(mol: Chem.Mol) -> List[int]:
    """Heuristically locate peptide Cα atoms.

    Detection rule: carbon atom bonded to at least one nitrogen and at least
    one carbonyl carbon.

    :param mol: RDKit molecule.
    :returns: Sorted unique list of candidate Cα atom indices.
    """
    idxs: List[int] = []
    for a in mol.GetAtoms():
        if a.GetAtomicNum() != 6:
            continue
        neighs = list(a.GetNeighbors())
        has_n = any(n.GetAtomicNum() == 7 for n in neighs)
        has_carb = any(is_carbonyl_carbon(n) for n in neighs)
        if has_n and has_carb:
            idxs.append(a.GetIdx())
    return sorted(set(idxs))


# --- small helpers to keep complexity low ---


def _build_c_to_nextn(mol: Chem.Mol) -> Dict[int, int]:
    """Map carbonyl carbon index -> following amide N index."""
    result: Dict[int, int] = {}
    for a in mol.GetAtoms():
        if a.GetAtomicNum() != 6 or not is_carbonyl_carbon(a):
            continue
        c_idx = a.GetIdx()
        for n in a.GetNeighbors():
            if n.GetAtomicNum() == 7:
                result[c_idx] = n.GetIdx()
                break
    return result


def _build_n_to_ca(mol: Chem.Mol, calpha_set: set) -> Dict[int, int]:
    """Map amide N index -> its Cα index (if present in calpha_set)."""
    result: Dict[int, int] = {}
    for a in mol.GetAtoms():
        if a.GetAtomicNum() != 7:
            continue
        n_idx = a.GetIdx()
        for c in a.GetNeighbors():
            if (
                c.GetAtomicNum() == 6
                and not is_carbonyl_carbon(c)
                and c.GetIdx() in calpha_set
            ):
                result[n_idx] = c.GetIdx()
                break
    return result


def _build_ca_to_carb(mol: Chem.Mol, calphas: List[int]) -> Dict[int, int]:
    """Map Cα index -> its (preceding) carbonyl carbon index or -1 if none."""
    result: Dict[int, int] = {}
    for ca in calphas:
        atom = mol.GetAtomWithIdx(ca)
        carb = [nei.GetIdx() for nei in atom.GetNeighbors() if is_carbonyl_carbon(nei)]
        result[ca] = carb[0] if carb else -1
    return result


def _find_unique_start(ca_to_next: Dict[int, Optional[int]]) -> int:
    """
    Compute indegrees and return the unique start Cα (indegree==0).

    :param ca_to_next: mapping Cα -> next Cα (or None).
    :raises ValueError: if there is not exactly one start.
    """
    indeg: Dict[int, int] = {ca: 0 for ca in ca_to_next.keys()}
    for nxt in ca_to_next.values():
        if nxt is not None:
            indeg[nxt] = indeg.get(nxt, 0) + 1
    starts = [ca for ca, d in indeg.items() if d == 0]
    if len(starts) != 1:
        raise ValueError(
            "Ambiguous/invalid peptide ends; cyclic/branched not supported."
        )
    return starts[0]


def order_residues_via_backbone(mol: Chem.Mol, calphas: List[int]) -> List[int]:
    """Return N→C order of provided Cα indices by following peptide links.

    The function builds mappings C(=O) -> N -> Cα and traverses the chain. It
    raises ValueError for cyclic or branched backbones.

    :param mol: RDKit molecule.
    :param calphas: Candidate Cα indices (list).
    :returns: Ordered list of Cα indices from N-terminus to C-terminus.
    :raises ValueError: If ambiguous or non-linear chain detected.
    """
    if not calphas:
        return []

    calpha_set = set(calphas)

    c_to_nextn = _build_c_to_nextn(mol)
    n_to_ca = _build_n_to_ca(mol, calpha_set)
    ca_to_carb = _build_ca_to_carb(mol, calphas)

    # Build mapping Cα -> next Cα
    ca_to_next: Dict[int, Optional[int]] = {}
    for ca in calphas:
        c_idx = ca_to_carb.get(ca, -1)
        if c_idx in c_to_nextn:
            n_idx = c_to_nextn[c_idx]
            ca_to_next[ca] = n_to_ca.get(n_idx, None)
        else:
            ca_to_next[ca] = None

    # Find start and walk
    start = _find_unique_start(ca_to_next)

    order: List[int] = []
    cur = start
    seen = set()
    while cur is not None and cur not in seen:
        order.append(cur)
        seen.add(cur)
        cur = ca_to_next.get(cur, None)

    if len(order) != len(calphas):
        raise ValueError("Backbone traversal failed (non-linear or disconnected).")
    return order
