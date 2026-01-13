"""Assembler helpers for combinatorial peptide generation.

This module assembles capped monomer units (SMILES) into linear or cyclic
peptides. It is defensive: many operations are best-effort and will not raise
on sanitization issues. Callers may re-attempt RDKit sanitization if stricter
chemistry checks are required.
"""

from __future__ import annotations
from typing import List, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import rdchem

# Import monomer template helpers locally to avoid circular import issues.
from pepkit.chem.monomer_templates import (
    canonical_monomer,
    nca_monomer,
    infer_from_aa3,
)


def _mol_from_smiles(smi: str) -> Chem.Mol:
    """
    Create an RDKit Mol from a SMILES string.

    :param smi: SMILES string.
    :returns: RDKit Mol.
    :raises ValueError: If the SMILES cannot be parsed.
    """
    m = Chem.MolFromSmiles(smi)
    if m is None:
        raise ValueError(f"Invalid monomer SMILES: {smi!r}")
    return m


def _is_carbonyl_carbon(atom: Chem.Atom) -> bool:
    """
    Detect whether an atom is a carbonyl carbon (C with a double-bonded O neighbor).

    :param atom: RDKit Atom object.
    :returns: True if atom is a carbonyl carbon.
    """
    if atom.GetAtomicNum() != 6:
        return False
    for b in atom.GetBonds():
        nbr = b.GetOtherAtom(atom)
        if nbr.GetAtomicNum() == 8 and b.GetBondType() == rdchem.BondType.DOUBLE:
            return True
    return False


def _find_dummy_to(
    mol: Chem.Mol, partner_atomic: int, require_carbonyl: bool = False
) -> Tuple[int, int]:
    """
    Find a dummy ([*:]) atom attached to an atom of a given element.

    :param mol: RDKit Mol to inspect.
    :param partner_atomic: Partner atom atomic number to match (e.g. 7 for N).
    :param require_carbonyl: If True, enforce that partner is carbonyl carbon.
    :returns: Tuple (dummy_idx, partner_idx).
    :raises ValueError: If no suitable dummy is found.
    """
    for a in mol.GetAtoms():
        if a.GetAtomicNum() != 0:
            continue
        for n in a.GetNeighbors():
            if n.GetAtomicNum() != partner_atomic:
                continue
            if not require_carbonyl or _is_carbonyl_carbon(n):
                return a.GetIdx(), n.GetIdx()
    raise ValueError("Terminal dummy not found")


def _couple(prev: Chem.Mol, nxt: Chem.Mol) -> Chem.Mol:
    """
    Couple two capped monomer molecules by creating an amide bond.

    The function looks for:
      - prev: dummy attached to a carbonyl carbon (C-side)
      - nxt: dummy attached to an amide nitrogen (N-side)

    :param prev: RDKit Mol with C-side dummy.
    :param nxt: RDKit Mol with N-side dummy.
    :returns: Combined RDKit Mol (best-effort sanitized).
    :raises ValueError: If terminal dummies cannot be located.
    :raises RuntimeError: If bond creation fails.
    """
    p_dummy, p_c = _find_dummy_to(prev, partner_atomic=6, require_carbonyl=True)
    n_dummy, n_n = _find_dummy_to(nxt, partner_atomic=7, require_carbonyl=False)

    combo = Chem.CombineMols(prev, nxt)
    rw = Chem.RWMol(combo)
    offset = prev.GetNumAtoms()

    # Indices within combined mol
    p_dummy_idx = p_dummy
    p_c_idx = p_c
    n_dummy_idx = offset + n_dummy
    n_n_idx = offset + n_n

    # Add C-N bond (amide)
    try:
        rw.AddBond(p_c_idx, n_n_idx, rdchem.BondType.SINGLE)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to add bond between atoms {p_c_idx} and {n_n_idx}: {exc}"
        )

    # Remove dummy atoms (remove higher index first to avoid reindex issues)
    for idx in sorted((p_dummy_idx, n_dummy_idx), reverse=True):
        try:
            rw.RemoveAtom(idx)
        except Exception:
            # best-effort: continue
            pass

    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception:
        # leave molecule as-is if sanitization fails
        pass
    return out


def _token_to_monomer(token) -> Chem.Mol:
    """
    Convert a token-like object to a capped monomer RDKit Mol.

    The token is expected to have attributes:
      - kind: "AA1" | "AA3" | "NCA" | "SMI"
      - code: code string (e.g. "A", "Orn", or SMILES)
      - is_d: bool flag for D-isomer

    :param token: Token-like object.
    :returns: RDKit Mol for the capped monomer.
    :raises ValueError: For unsupported token kinds or codes.
    """
    kind = getattr(token, "kind", None)
    code = getattr(token, "code", None)
    is_d = getattr(token, "is_d", False)

    if kind == "AA1":
        smi = canonical_monomer(code, d_isomer=is_d)
    elif kind == "AA3":
        smi = infer_from_aa3(code, d_isomer=is_d)
        if smi is None:
            raise ValueError(f"Unsupported AA3 token: {code!r}")
    elif kind == "NCA":
        smi = nca_monomer(code, d_isomer=is_d)
    elif kind == "SMI":
        smi = code
    else:
        raise ValueError(f"Unknown token kind: {kind!r}")

    return _mol_from_smiles(smi)


def assemble_linear(spec) -> Chem.Mol:
    """
    Assemble a linear peptide from a SequenceSpec-like object.

    :param spec: Object exposing `.tokens` (iterable of token-like objects).
    :returns: RDKit Mol for the assembled linear peptide (best-effort sanitized).
    :raises ValueError: If `spec.tokens` is empty or invalid.
    """
    tokens = getattr(spec, "tokens", None)
    if not tokens:
        raise ValueError("Empty sequence")

    monomers = [_token_to_monomer(t) for t in tokens]
    current = monomers[0]
    for nxt in monomers[1:]:
        current = _couple(current, nxt)

    try:
        Chem.SanitizeMol(current)
    except Exception:
        pass
    return current


def _apply_n_cap(
    rw: Chem.RWMol, n_dummy_idx: Optional[int], n_cap: Optional[str]
) -> None:
    """
    Apply N-terminal cap to the dummy atom index in the RWMol.

    :param rw: RWMol with a terminal dummy present.
    :param n_dummy_idx: Index of the dummy atom or None.
    :param n_cap: None or 'Ac'.
    :raises ValueError: If an unknown cap is requested.
    """
    if n_dummy_idx is None:
        return
    if n_cap is None:
        try:
            rw.GetAtomWithIdx(n_dummy_idx).SetAtomicNum(1)  # H
        except Exception:
            pass
        return
    if n_cap == "Ac":
        try:
            rw.GetAtomWithIdx(n_dummy_idx).SetAtomicNum(6)  # crude C surrogate
        except Exception:
            pass
        return
    raise ValueError(f"Unknown N-cap: {n_cap!r}")


def _apply_c_cap(
    rw: Chem.RWMol, c_dummy_idx: Optional[int], c_cap: Optional[str]
) -> None:
    """
    Apply C-terminal cap to the dummy atom index in the RWMol.

    :param rw: RWMol with a terminal dummy present.
    :param c_dummy_idx: Index of the dummy atom or None.
    :param c_cap: None or 'NH2'.
    :raises ValueError: If an unknown cap is requested.
    """
    if c_dummy_idx is None:
        return
    if c_cap is None:
        try:
            rw.GetAtomWithIdx(c_dummy_idx).SetAtomicNum(8)  # O (OH)
        except Exception:
            pass
        return
    if c_cap == "NH2":
        try:
            rw.GetAtomWithIdx(c_dummy_idx).SetAtomicNum(7)  # N (NH2)
        except Exception:
            pass
        return
    raise ValueError(f"Unknown C-cap: {c_cap!r}")


def cap_terminals(
    mol: Chem.Mol, n_cap: Optional[str], c_cap: Optional[str]
) -> Chem.Mol:
    """
    Replace terminal dummy atoms with capping atoms.

    :param mol: RDKit Mol containing terminal dummy atoms.
    :param n_cap: N-terminal cap: None or "Ac".
    :param c_cap: C-terminal cap: None or "NH2".
    :returns: RDKit Mol with caps applied (best-effort sanitized).
    :raises ValueError: If cap parameters are invalid.
    """
    rw = Chem.RWMol(mol)

    try:
        n_dummy_idx, _ = _find_dummy_to(rw, partner_atomic=7, require_carbonyl=False)
    except Exception:
        n_dummy_idx = None

    try:
        c_dummy_idx, _ = _find_dummy_to(rw, partner_atomic=6, require_carbonyl=True)
    except Exception:
        c_dummy_idx = None

    _apply_n_cap(rw, n_dummy_idx, n_cap)
    _apply_c_cap(rw, c_dummy_idx, c_cap)

    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception:
        pass
    return out


def cyclize_head_to_tail(mol: Chem.Mol) -> Chem.Mol:
    """
    Cyclize a linear peptide by connecting C-terminal carbonyl carbon to
    N-terminal amide nitrogen and removing terminal dummies.

    :param mol: RDKit Mol to cyclize.
    :returns: Cyclized RDKit Mol (best-effort sanitized).
    :raises ValueError: If termini cannot be located.
    :raises RuntimeError: If the head-to-tail bond cannot be created.
    """
    try:
        n_dummy_idx, n_n = _find_dummy_to(mol, partner_atomic=7, require_carbonyl=False)
        c_dummy_idx, c_c = _find_dummy_to(mol, partner_atomic=6, require_carbonyl=True)
    except Exception as exc:
        raise ValueError(f"Could not locate termini for cyclization: {exc}")

    rw = Chem.RWMol(mol)
    try:
        rw.AddBond(c_c, n_n, rdchem.BondType.SINGLE)
    except Exception as exc:
        raise RuntimeError(f"Failed to add head-to-tail bond: {exc}")

    for idx in sorted((n_dummy_idx, c_dummy_idx), reverse=True):
        try:
            rw.RemoveAtom(idx)
        except Exception:
            pass

    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception:
        pass
    return out


def _find_sulfur_indices(mol: Chem.Mol) -> List[int]:
    """
    Return indices of sulfur atoms in a molecule.

    :param mol: RDKit Mol.
    :returns: List of atom indices for sulfur atoms.
    """
    return [a.GetIdx() for a in mol.GetAtoms() if a.GetSymbol() == "S"]


def _pair_sulfurs(sulfur_indices: List[int], max_pairs: int) -> List[Tuple[int, int]]:
    """
    Greedily pair sulfur indices into disulfide pairs.

    :param sulfur_indices: List of sulfur atom indices.
    :param max_pairs: Maximum number of pairs to produce.
    :returns: List of (i, j) index pairs.
    """
    pairs: List[Tuple[int, int]] = []
    used = set()
    for i, si in enumerate(sulfur_indices):
        if si in used:
            continue
        for sj in sulfur_indices[i + 1 :]:  # noqa
            if sj in used:
                continue
            pairs.append((si, sj))
            used.add(si)
            used.add(sj)
            break
        if len(pairs) >= max_pairs:
            break
    return pairs


def _apply_disulfide_pairs(rw: Chem.RWMol, pairs: List[Tuple[int, int]]) -> None:
    """
    Apply S-S bonds for provided pairs in the RWMol.

    :param rw: RWMol to modify.
    :param pairs: List of (si, sj) sulfur index pairs.
    """
    for si, sj in pairs:
        # remove explicit hydrogens on sulfur neighbors (best-effort)
        for s_idx in (si, sj):
            atom = rw.GetAtomWithIdx(s_idx)
            hnei = [n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol() == "H"]
            for h in sorted(hnei, reverse=True):
                try:
                    rw.RemoveAtom(h)
                except Exception:
                    pass
        try:
            rw.AddBond(si, sj, rdchem.BondType.SINGLE)
        except Exception:
            pass


def add_disulfide(mol: Chem.Mol, max_pairs: int = 1) -> Chem.Mol:
    """
    Pair sulfur atoms and create disulfide bonds (naive greedy strategy).

    :param mol: RDKit Mol.
    :param max_pairs: Maximum number of disulfide bridges to introduce.
    :returns: Modified RDKit Mol (best-effort sanitized).
    """
    rw = Chem.RWMol(mol)
    sulfur = _find_sulfur_indices(rw)
    pairs = _pair_sulfurs(sulfur, max_pairs)
    _apply_disulfide_pairs(rw, pairs)

    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception:
        pass
    return out


def build_peptide_from_spec(spec) -> Chem.Mol:
    """
    High-level assembler entry point.

    :param spec: SequenceSpec-like object with attributes:
                 - tokens: iterable of token-like objects
                 - cyclize_head_to_tail: optional bool
                 - n_cap: optional string (e.g. "Ac" or None)
                 - c_cap: optional string (e.g. "NH2" or None)
    :returns: RDKit Mol for the assembled peptide.
    :raises ValueError: For empty sequences or invalid specs.
    """
    m = assemble_linear(spec)
    if getattr(spec, "cyclize_head_to_tail", False):
        m = cyclize_head_to_tail(m)
    else:
        m = cap_terminals(
            m,
            n_cap=getattr(spec, "n_cap", None),
            c_cap=getattr(spec, "c_cap", None),
        )
    return m
