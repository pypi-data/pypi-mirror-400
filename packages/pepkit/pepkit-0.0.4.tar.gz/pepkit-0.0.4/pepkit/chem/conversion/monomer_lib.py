from __future__ import annotations
from typing import Dict, Optional, Tuple
from rdkit import Chem

from .monomer_templates import canonical_monomer, R_GROUP  # type: ignore[attr-defined]

__all__ = ["MonomerLibrary"]


class MonomerLibrary:
    """Light-weight library of monomer templates for fast R-group matching.

    The library stores per amino acid:
      - the compiled RDKit Mol (monomer fragment),
      - canonical isomeric SMILES,
      - canonical non-isomeric SMILES (stereo removed) if available.

    Matching strategy:
      1. exact isomeric SMILES
      2. exact non-isomeric SMILES
      3. two-way substructure/isomorphism fallback (ignores chirality)
    """

    def __init__(self) -> None:
        # entries: aa -> (mol, iso_smiles, noniso_smiles)
        self._entries: Dict[str, Tuple[Optional[Chem.Mol], str, Optional[str]]] = {}
        self._build()

    # ---- build helpers (small) ----

    def _build(self) -> None:
        """Build monomer templates for canonical AAs (delegates per-AA work)."""
        for aa in R_GROUP.keys():
            self._build_entry_for_aa(aa)

    def _build_entry_for_aa(self, aa: str) -> None:
        """Build and register a single AA entry."""
        if aa == "G":
            # glycine: no R-group, use placeholder
            self._entries[aa] = (None, "*", "*")
            return

        smi = self._safe_canonical_monomer(aa)
        if smi is None:
            self._entries[aa] = (None, "*", "*")
            return

        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            self._entries[aa] = (None, "*", "*")
            return

        iso = self._canonicalize_iso(mol)
        noniso = self._compute_noniso(iso) if iso is not None else None
        self._entries[aa] = (
            mol,
            iso or Chem.MolToSmiles(mol, canonical=True, isomericSmiles=False),
            noniso,
        )

    def _safe_canonical_monomer(self, aa: str) -> Optional[str]:
        """Return the canonical monomer SMILES or None on failure."""
        try:
            return canonical_monomer(aa)
        except Exception:
            return None

    def _canonicalize_iso(self, mol: Chem.Mol) -> Optional[str]:
        """Return canonical isomeric SMILES (round-trip) or None."""
        try:
            iso = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
            mm = Chem.MolFromSmiles(iso)
            if mm is not None:
                return Chem.MolToSmiles(mm, canonical=True, isomericSmiles=True)
            return iso
        except Exception:
            try:
                return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=False)
            except Exception:
                return None

    def _compute_noniso(self, iso: str) -> Optional[str]:
        """Return non-isomeric canonical SMILES for an isomeric SMILES (or None)."""
        try:
            m = Chem.MolFromSmiles(iso)
            if m is None:
                return None
            Chem.RemoveStereochemistry(m)
            return Chem.MolToSmiles(m, canonical=True, isomericSmiles=False)
        except Exception:
            return None

    # ---- matching helpers (small) ----

    def _probe_to_smiles(self, probe: Chem.Mol) -> Tuple[Optional[str], Optional[str]]:
        """Compute (isomeric_smiles, nonisomeric_smiles) for probe, tolerant to errors."""
        try:
            probe_iso = Chem.MolToSmiles(probe, canonical=True, isomericSmiles=True)
        except Exception:
            return None, None
        probe_noniso = None
        try:
            mm = Chem.MolFromSmiles(probe_iso)
            if mm is not None:
                Chem.RemoveStereochemistry(mm)
                probe_noniso = Chem.MolToSmiles(
                    mm, canonical=True, isomericSmiles=False
                )
        except Exception:
            probe_noniso = None
        return probe_iso, probe_noniso

    def _match_by_iso(self, probe_iso: Optional[str]) -> Optional[str]:
        """Return AA if probe_iso exactly matches an entry iso SMILES."""
        if not probe_iso:
            return None
        for aa, (_mol, iso, _non) in self._entries.items():
            if iso == probe_iso:
                return aa
        return None

    def _match_by_noniso(self, probe_noniso: Optional[str]) -> Optional[str]:
        """Return AA if probe_noniso matches a non-isomeric entry SMILES."""
        if not probe_noniso:
            return None
        for aa, (_mol, _iso, non) in self._entries.items():
            if non is not None and non == probe_noniso:
                return aa
        return None

    def _structural_two_way_match(self, probe: Chem.Mol) -> Optional[str]:
        """Return AA if probe and template are two-way substructure matches
        (ignores chirality)."""
        try:
            for aa, (mol_t, _iso, _non) in self._entries.items():
                if mol_t is None:
                    continue
                if probe.HasSubstructMatch(mol_t) and mol_t.HasSubstructMatch(probe):
                    return aa
        except Exception:
            return None
        return None

    # ---- public match method (simple orchestration) ----

    def match_rgroup(self, probe: Optional[Chem.Mol]) -> Optional[str]:
        """Attempt to match probe R-group Mol to a canonical AA.

        :param probe: RDKit Mol (may be None for Gly).
        :returns: one-letter AA or None.
        """
        if probe is None:
            return "G"

        probe_iso, probe_noniso = self._probe_to_smiles(probe)
        # try iso SMILES
        aa = self._match_by_iso(probe_iso)
        if aa:
            return aa
        # try non-iso SMILES
        aa = self._match_by_noniso(probe_noniso)
        if aa:
            return aa
        # fallback structural two-way match
        return self._structural_two_way_match(probe)
