"""Convenience conversion functions exported by pepkit.chem."""

from __future__ import annotations
from typing import Optional
from rdkit import Chem
from .peptide_decoder import PeptideDecoder

__all__ = ["smiles_to_fasta", "fasta_to_smiles"]


def smiles_to_fasta(
    smiles: str, header: Optional[str] = None, split: bool = False
) -> str:
    """Convert peptide SMILES to FASTA or raw sequence.

    By default this returns a FASTA-formatted string:
        >[header]
        SEQUENCE

    If ``split=True`` the function returns the raw one-letter sequence
    (e.g. "GPG") without any FASTA header.

    :param smiles: Input SMILES representing a linear peptide.
    :param header: Optional header (without '>'). Ignored when ``split=True``.
    :param split: If True, return the raw sequence string instead of FASTA.
    :returns: FASTA-formatted string (default) or raw sequence (if split=True).
    :raises ValueError: On parse/decoding failure.
    """
    decoder = PeptideDecoder().from_smiles(smiles).decode()
    seq = decoder.sequence
    if split:
        return seq
    hdr = f">{header}\n" if header else ">\n"
    return f"{hdr}{seq}\n"


def fasta_to_smiles(fasta: str) -> str:
    """Convert one-letter FASTA (no header) to canonical SMILES using RDKit.

    Rejects non-canonical sequences containing the placeholder 'X'.

    :param fasta: Amino-acid sequence in one-letter code.
    :returns: Canonical SMILES string.
    :raises ValueError: If the sequence contains 'X' or RDKit cannot parse it.
    """
    if "X" in fasta.upper():
        raise ValueError("Non-canonical residue 'X' found in FASTA.")
    mol = Chem.MolFromFASTA(fasta)
    if mol is None:
        raise ValueError(f"Could not parse FASTA: {fasta!r}")
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
