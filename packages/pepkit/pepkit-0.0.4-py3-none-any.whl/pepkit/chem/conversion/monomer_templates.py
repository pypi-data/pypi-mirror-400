from __future__ import annotations
from typing import Dict, Optional, Tuple

AA20: Tuple[str, ...] = (
    "A",
    "R",
    "N",
    "D",
    "C",
    "E",
    "Q",
    "G",
    "H",
    "I",
    "L",
    "K",
    "M",
    "F",
    "P",
    "S",
    "T",
    "W",
    "Y",
    "V",
)
# Compact R-group definitions used to build a capped monomer template.
# None for Gly/Pro special-casing.
R_GROUP: Dict[str, Optional[str]] = {
    "A": "C",
    "R": "CCCN=C(N)N",
    "N": "CNC=O",
    "D": "CC(=O)O",
    "C": "CS",
    "E": "CCC(=O)O",
    "Q": "CCNC=O",
    "G": None,
    "H": "Cc1ncc[nH]1",
    "I": "C(C)CC",
    "L": "CC(C)C",
    "K": "CCCCN",
    "M": "CCSC",
    "F": "Cc1ccccc1",
    "P": None,
    "S": "CO",
    "T": "C(O)C",
    "W": "Cc1c[nH]c2ccccc12",
    "Y": "Cc1ccc(O)cc1",
    "V": "C(C)C",
}


def canonical_monomer(one_letter: str, d_isomer: bool = False) -> str:
    """Return canonical capped monomer SMILES with dummy attachments.

    :param one_letter: Single-letter amino-acid code (case-insensitive).
    :param d_isomer: If True, return D-configuration when applicable.
    :returns: SMILES string with attachments like ``[*:1]N[C@H](R)C(=O)[*:2]``.
    :raises ValueError: If residue is unsupported.

    Example
    -------
    >>> canonical_monomer("A")
    '[*:1]N[C@H](C)C(=O)[*:2]'
    """
    aa = one_letter.upper()
    if aa == "G":
        return "[*:1]NCC(=O)[*:2]"
    if aa == "P":
        # Proline uses a ring that includes the backbone N; stereochemistry on Cα matters.
        return (
            "[*:1]N1CCC[C@H]1C(=O)[*:2]"
            if not d_isomer
            else "[*:1]N1CCC[C@@H]1C(=O)[*:2]"
        )
    r = R_GROUP.get(aa, None)
    if r is None:
        raise ValueError(f"Unsupported residue: {aa}")
    if d_isomer:
        return f"[*:1]N[C@@H]({r})C(=O)[*:2]"
    return f"[*:1]N[C@H]({r})C(=O)[*:2]"


# Some NCA templates; kept minimal and optional
NCA_SMILES: Dict[str, str] = {
    "Orn": "[*:1]N[C@H](CCCN)C(=O)[*:2]",
    "Dab": "[*:1]N[C@H](CCN)C(=O)[*:2]",
    "Dap": "[*:1]N[C@H](CN)C(=O)[*:2]",
    "Nle": "[*:1]N[C@H](CCCC)C(=O)[*:2]",
    "Aib": "[*:1]N[C](C)(C)C(=O)[*:2]",
    "Hyp": "[*:1]N1C[C@H](O)CC1C(=O)[*:2]",
    "Sar": "[*:1]N(C)C(C)=O[*:2]",
}


def nca_monomer(name: str, d_isomer: bool = False) -> str:
    """Return canonical SMILES for a named NCA monomer.

    :param name: NCA short name (e.g., "Orn").
    :param d_isomer: If True, flip stereochemistry marker [C@H] -> [C@@H].
    :raises ValueError: Unknown NCA.
    """
    nm = name[:1].upper() + name[1:]
    smi = NCA_SMILES.get(nm, None)
    if smi is None:
        raise ValueError(f"Unknown NCA: {name}")
    if d_isomer and "[C@H]" in smi:
        return smi.replace("[C@H]", "[C@@H]")
    return smi


def infer_from_aa3(aa3: str, d_isomer: bool = False) -> Optional[str]:
    """Convert a 3-letter AA name to canonical monomer SMILES or None if unknown."""
    MAP = {
        "Ala": "A",
        "Cys": "C",
        "Asp": "D",
        "Glu": "E",
        "Phe": "F",
        "Gly": "G",
        "His": "H",
        "Ile": "I",
        "Lys": "K",
        "Leu": "L",
        "Met": "M",
        "Asn": "N",
        "Pro": "P",
        "Gln": "Q",
        "Arg": "R",
        "Ser": "S",
        "Thr": "T",
        "Val": "V",
        "Trp": "W",
        "Tyr": "Y",
    }
    one = MAP.get(aa3, None)
    if one is None:
        return None
    return canonical_monomer(one, d_isomer=d_isomer)
