"""Side-chain library: robust R-group extraction and tolerant matching.

Uses MonomerLibrary (fast-path) when available. See monomer_templates.py and
monomer_lib.py for monomer definitions.
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple, List, Set
from dataclasses import dataclass
from rdkit import Chem
from rdkit.Chem import AllChem

from .utils import is_carbonyl_carbon, find_calpha_indices, order_residues_via_backbone
from .monomer_lib import MonomerLibrary
from .monomer_templates import AA20


__all__ = ["AA20", "SidechainKey", "SidechainLibrary"]


@dataclass(frozen=True)
class SidechainKey:
    """Canonical identity of a residue side chain (R-group only)."""

    smiles: str
    natoms: int
    fp: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover - trivial
        state = "set" if self.fp else "none"
        return f"SidechainKey(smiles={self.smiles!r}, natoms={self.natoms}, fp={state})"


class SidechainLibrary:
    """Map R-group fragment keys to one-letter amino-acid codes with robust matching."""

    def __init__(self, use_monomer: bool = True) -> None:
        self._smiles_iso_to_aa: Dict[str, str] = {}
        self._smiles_noniso_to_aa: Dict[str, str] = {}
        self._fp_to_aa: Dict[str, str] = {}
        self._fp_noniso_to_aa: Dict[str, str] = {}
        self._mol_entries: List[Tuple[Chem.Mol, str]] = []
        self._monlib: Optional[MonomerLibrary] = (
            MonomerLibrary() if use_monomer else None
        )
        self._build()

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"SidechainLibrary(n_iso={len(self._smiles_iso_to_aa)})"

    @property
    def size(self) -> int:
        return len(self._smiles_iso_to_aa)

    # small helpers (kept short for flake8)
    @staticmethod
    def _identify_backbone_atoms(mol: Chem.Mol) -> Set[int]:
        calphas = find_calpha_indices(mol)
        backbone: Set[int] = set(calphas)
        for ca in calphas:
            a = mol.GetAtomWithIdx(ca)
            for nei in a.GetNeighbors():
                if is_carbonyl_carbon(nei):
                    backbone.add(nei.GetIdx())
        return backbone

    @staticmethod
    def _cut_backbone_bonds(rw: Chem.RWMol, ca_idx: int) -> None:
        ca = rw.GetAtomWithIdx(ca_idx)
        n_nei = None
        c_carb_nei = None
        for nei in ca.GetNeighbors():
            if nei.GetAtomicNum() == 7:
                n_nei = nei.GetIdx()
            elif is_carbonyl_carbon(nei):
                c_carb_nei = nei.GetIdx()
        if n_nei is not None:
            try:
                rw.RemoveBond(ca_idx, n_nei)
            except Exception:
                pass
        if c_carb_nei is not None:
            try:
                rw.RemoveBond(ca_idx, c_carb_nei)
            except Exception:
                pass

    @staticmethod
    def _collect_rgroup_atoms_avoiding_backbone(
        mol: Chem.Mol, ca_idx: int, forbidden: Set[int]
    ) -> Set[int]:
        ca_atom = mol.GetAtomWithIdx(ca_idx)
        seeds = [
            n.GetIdx() for n in ca_atom.GetNeighbors() if n.GetIdx() not in forbidden
        ]
        if not seeds:
            return set()
        adj: Dict[int, List[int]] = {}
        for a in mol.GetAtoms():
            i = a.GetIdx()
            adj[i] = [nb.GetIdx() for nb in a.GetNeighbors()]
        seen: Set[int] = set(forbidden)
        stack: List[int] = seeds[:]
        rgroup: Set[int] = set()
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            rgroup.add(v)
            for w in adj.get(v, []):
                if w not in seen:
                    stack.append(w)
        return rgroup

    @staticmethod
    def _make_submol_from_atomset(original: Chem.Mol, atomset: Set[int]) -> Chem.Mol:
        amap: Dict[int, int] = {}
        newmol = Chem.RWMol()
        for old_idx in sorted(atomset):
            a_old = original.GetAtomWithIdx(old_idx)
            a_new = Chem.Atom(a_old.GetAtomicNum())
            new_idx = newmol.AddAtom(a_new)
            amap[old_idx] = new_idx
        added = set()
        for old_idx in sorted(atomset):
            a_old = original.GetAtomWithIdx(old_idx)
            for b in a_old.GetBonds():
                i = b.GetBeginAtomIdx()
                j = b.GetEndAtomIdx()
                if i in atomset and j in atomset:
                    ni, nj = amap[i], amap[j]
                    key = (min(ni, nj), max(ni, nj))
                    if key in added:
                        continue
                    newmol.AddBond(ni, nj, b.GetBondType())
                    added.add(key)
        mol = newmol.GetMol()
        try:
            Chem.SanitizeMol(mol)
        except Exception:
            pass
        return mol

    @staticmethod
    def _normalize_smiles(self_mol: Chem.Mol, isomeric: bool) -> Optional[str]:
        try:
            s = Chem.MolToSmiles(self_mol, canonical=True, isomericSmiles=isomeric)
            mm = Chem.MolFromSmiles(s)
            if mm is not None:
                return Chem.MolToSmiles(mm, canonical=True, isomericSmiles=isomeric)
            return s
        except Exception:
            return None

    @staticmethod
    def _smiles_remove_stereo(smiles_iso: str) -> Optional[str]:
        try:
            m = Chem.MolFromSmiles(smiles_iso)
            if m is None:
                return None
            Chem.RemoveStereochemistry(m)
            return Chem.MolToSmiles(m, canonical=True, isomericSmiles=False)
        except Exception:
            return None

    @staticmethod
    def _fingerprint_bitstring(
        m: Chem.Mol, radius: int = 2, nBits: int = 2048
    ) -> Optional[str]:
        try:
            fp = AllChem.GetMorganFingerprintAsBitVect(m, radius, nBits=nBits)
            return fp.ToBitString()
        except Exception:
            return None

    # public API
    def make_key(self, mol: Chem.Mol, ca_idx: int) -> SidechainKey:
        forbidden = self._identify_backbone_atoms(mol)
        rw = Chem.RWMol(mol)
        self._cut_backbone_bonds(rw, ca_idx)
        r_atoms = self._collect_rgroup_atoms_avoiding_backbone(
            rw.GetMol(), ca_idx, forbidden
        )
        if not r_atoms:
            return SidechainKey(smiles="*", natoms=0, fp=None)
        sub = self._make_submol_from_atomset(rw.GetMol(), r_atoms)
        smi_iso = self._normalize_smiles(sub, isomeric=True) or Chem.MolToSmiles(
            sub, canonical=True, isomericSmiles=True
        )
        fp = self._fingerprint_bitstring(sub)
        return SidechainKey(smiles=smi_iso, natoms=sub.GetNumAtoms(), fp=fp)

    def lookup(self, key: SidechainKey) -> Optional[str]:
        if key.natoms == 0:
            return "G"
        # try monomer fast-path
        if self._monlib is not None:
            try:
                probe = Chem.MolFromSmiles(key.smiles)
                aa = self._monlib.match_rgroup(probe) if probe is not None else None
                if aa:
                    return aa
            except Exception:
                pass
        # tolerant path
        return (
            self._lookup_by_smiles_iso(key)
            or self._lookup_by_smiles_noniso(key)
            or self._lookup_by_fp_iso(key)
            or self._lookup_by_fp_noniso(key)
            or self._lookup_by_isomorphism(key)
        )

    # small lookup helpers (simple, low complexity)
    def _lookup_by_smiles_iso(self, key: SidechainKey) -> Optional[str]:
        return self._smiles_iso_to_aa.get(key.smiles)

    def _lookup_by_smiles_noniso(self, key: SidechainKey) -> Optional[str]:
        noniso = self._smiles_remove_stereo(key.smiles)
        if not noniso:
            return None
        return self._smiles_noniso_to_aa.get(noniso)

    def _lookup_by_fp_iso(self, key: SidechainKey) -> Optional[str]:
        return self._fp_to_aa.get(key.fp) if key.fp else None

    def _lookup_by_fp_noniso(self, key: SidechainKey) -> Optional[str]:
        try:
            m = Chem.MolFromSmiles(key.smiles)
            if m is None:
                return None
            m2 = Chem.Mol(m)
            Chem.RemoveStereochemistry(m2)
            fp = self._fingerprint_bitstring(m2)
            return self._fp_noniso_to_aa.get(fp) if fp else None
        except Exception:
            return None

    def _lookup_by_isomorphism(self, key: SidechainKey) -> Optional[str]:
        try:
            probe = Chem.MolFromSmiles(key.smiles)
            if probe is None:
                return None
            for ref_mol, ref_aa in self._mol_entries:
                if probe.HasSubstructMatch(
                    ref_mol, useChirality=False
                ) and ref_mol.HasSubstructMatch(probe, useChirality=False):
                    return ref_aa
        except Exception:
            return None
        return None

    # build helpers (small)
    def _build(self) -> None:
        for X in AA20:
            self._build_entry_for_residue(X)

    def _build_entry_for_residue(self, aa: str) -> None:
        tri = Chem.MolFromFASTA("G" + aa + "A")
        if tri is None:
            raise RuntimeError(f"Failed to build G{aa}A tripeptide.")
        cas = find_calpha_indices(tri)
        if not cas:
            raise RuntimeError(f"Could not find Cα atoms for template G{aa}A.")
        order = order_residues_via_backbone(tri, cas)
        if len(order) < 2:
            raise RuntimeError(f"Unexpected tripeptide topology for G{aa}A.")
        x_ca = order[1]

        forbidden = self._identify_backbone_atoms(tri)
        rw = Chem.RWMol(tri)
        self._cut_backbone_bonds(rw, x_ca)
        r_atoms = self._collect_rgroup_atoms_avoiding_backbone(
            rw.GetMol(), x_ca, forbidden
        )
        if not r_atoms:
            self._register_entry(aa="G", sub=None, smi_iso="*", smi_noniso="*")
            return

        sub = self._make_submol_from_atomset(rw.GetMol(), r_atoms)
        smi_iso = self._normalize_smiles(sub, isomeric=True) or Chem.MolToSmiles(
            sub, canonical=True, isomericSmiles=True
        )
        smi_noniso = self._smiles_remove_stereo(smi_iso)
        self._register_entry(aa=aa, sub=sub, smi_iso=smi_iso, smi_noniso=smi_noniso)

    def _register_entry(
        self, aa: str, sub: Optional[Chem.Mol], smi_iso: str, smi_noniso: Optional[str]
    ) -> None:
        if aa == "G" and (sub is None or smi_iso == "*"):
            self._smiles_iso_to_aa.setdefault("*", "G")
            self._smiles_noniso_to_aa.setdefault("*", "G")
            return
        if sub is None:
            raise RuntimeError("Non-glycine residue requires a sub-molecule.")
        fp_iso = self._fingerprint_bitstring(sub)
        fp_noniso = None
        if smi_noniso is not None:
            m_noniso = Chem.MolFromSmiles(smi_noniso)
            if m_noniso is not None:
                fp_noniso = self._fingerprint_bitstring(m_noniso)

        self._smiles_iso_to_aa.setdefault(smi_iso, aa)
        if smi_noniso:
            self._smiles_noniso_to_aa.setdefault(smi_noniso, aa)
        if fp_iso:
            self._fp_to_aa.setdefault(fp_iso, aa)
        if fp_noniso:
            self._fp_noniso_to_aa.setdefault(fp_noniso, aa)
        m_norm = Chem.MolFromSmiles(smi_iso) or sub
        self._mol_entries.append((m_norm, aa))
