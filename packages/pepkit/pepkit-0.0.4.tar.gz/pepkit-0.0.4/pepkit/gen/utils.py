"""Utility helpers for combinatorial generation."""

from __future__ import annotations
from typing import List, Optional

CANONICAL_20 = list("ACDEFGHIKLMNPQRSTVWY")
DEFAULT_NCA = ["Orn", "Dab", "Dap", "Nle", "Aib", "Hyp", "Sar"]


def expand_alphabet(
    allow_nca: bool,
    allow_d: bool,
    extra: Optional[List[str]] = None,
) -> List[str]:
    """Build the token alphabet.

    :param allow_nca: Include common NCA names (PepDSL tokens).
    :param allow_d: Include D-forms as 'dA', 'dC', ...
    :param extra: Extra custom tokens to include.
    :returns: List of tokens.
    """
    alpha = CANONICAL_20.copy()
    if allow_d:
        alpha += [f"d{x}" for x in CANONICAL_20]
    if allow_nca:
        alpha += DEFAULT_NCA.copy()
    if extra:
        alpha += list(extra)
    return alpha


def tokens_to_fasta_if_possible(tokens: List[str]) -> Optional[str]:
    """Convert tokens to FASTA if all are canonical 1-letter AAs.

    :param tokens: Token list.
    :returns: FASTA string or None if tokens are not purely canonical.
    """
    if not tokens:
        return None
    ok = all(len(t) == 1 and t in CANONICAL_20 for t in tokens)
    return "".join(tokens) if ok else None


def tokens_to_dsl(tokens: List[str]) -> str:
    """Join tokens into PepDSL string with '-'.

    :param tokens: Token list.
    :returns: PepDSL string (e.g., 'A-C-Orn-dK').
    """
    return "-".join(tokens)
