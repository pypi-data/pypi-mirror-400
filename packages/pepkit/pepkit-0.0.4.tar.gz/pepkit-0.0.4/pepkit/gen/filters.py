"""Filtering helpers for combinatorial generation."""

from __future__ import annotations
from typing import Optional

from ..chem.desc.sequence import sequence_descriptors


def passes_filters_canonical(
    seq: str,
    max_hydrophobic: Optional[float],
    max_abs_charge: Optional[float],
) -> bool:
    """Apply numeric filters to canonical FASTA sequence.

    :param seq: FASTA sequence.
    :param max_hydrophobic: Upper bound on hydrophobic fraction.
    :param max_abs_charge: Upper bound on absolute net charge at pH 7.4.
    :returns: True if sequence passes filters.
    """
    if not seq:
        return False
    desc = sequence_descriptors(seq)
    if max_hydrophobic is not None and desc.frac_hydrophobic > max_hydrophobic:
        return False
    if max_abs_charge is not None and abs(desc.net_charge_pH7_4) > max_abs_charge:
        return False
    return True


def passes_filters_dsl(
    dsl: str,
    include_motif: Optional[str],
    exclude_motif: Optional[str],
) -> bool:
    """Apply DSL string filters by motif presence/absence.

    :param dsl: PepDSL string.
    :param include_motif: Required substring (if provided).
    :param exclude_motif: Forbidden substring (if provided).
    :returns: True if string passes motif filters.
    """
    if include_motif and include_motif not in dsl:
        return False
    if exclude_motif and exclude_motif in dsl:
        return False
    return True
