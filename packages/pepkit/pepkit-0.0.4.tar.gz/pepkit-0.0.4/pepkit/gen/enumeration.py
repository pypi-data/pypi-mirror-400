"""Orchestrator for combinatorial peptide library generation."""

from __future__ import annotations
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import pandas as pd

from pepkit.gen.utils import (
    expand_alphabet,
    tokens_to_fasta_if_possible,
    tokens_to_dsl,
)
from pepkit.gen.filters import passes_filters_canonical, passes_filters_dsl
from pepkit.gen.samplers import (
    iter_cartesian,
    sample_random_unique,
    guided_topk_sampler,
    mh_sampler,
)

# Optional converter / assembler imports (fail gracefully if not available)
try:
    from pepkit.chem.conversion import fasta_to_smiles  # canonical-only path
except Exception:  # pragma: no cover - import guard
    fasta_to_smiles = None  # type: ignore

try:
    from pepkit.gen.dsl import parse as pepdsl_parse  # type: ignore
    from pepkit.gen.assembler import build_peptide_from_spec  # type: ignore
    from rdkit import Chem  # type: ignore

    _HAS_ASSEMBLER: bool = True
except Exception:  # pragma: no cover - import guard
    pepdsl_parse = None  # type: ignore
    build_peptide_from_spec = None  # type: ignore
    Chem = None  # type: ignore
    _HAS_ASSEMBLER = False

# Optional descriptor importer (best-effort)
try:
    from pepkit.chem.desc.sequence import sequence_descriptors
except Exception:
    sequence_descriptors = None  # type: ignore


# ---------- small helpers (reduce complexity in main function) -------------


def _choose_iterator(
    mode: str,
    alphabet: List[str],
    length: int,
    sample_size: int,
    seed: Optional[int],
    score_fn: Optional[Callable[[Tuple[str, ...]], float]],
    guided_pool: int,
    temperature: float,
) -> Iterable[Tuple[str, ...]]:
    """Return an iterator of token tuples according to the selected mode."""
    if mode == "cartesian":
        return iter_cartesian(alphabet, length)
    if mode == "sample":
        return sample_random_unique(alphabet, length, n_samples=sample_size, seed=seed)
    if mode == "guided-topk":
        if score_fn is None:
            raise ValueError("guided-topk mode requires a score_fn.")
        best = guided_topk_sampler(
            alphabet=alphabet,
            length=length,
            n_candidates=guided_pool,
            topk=sample_size,
            score_fn=score_fn,
            seed=seed,
        )
        return iter(best)
    if mode == "mh":
        if score_fn is None:
            raise ValueError("mh mode requires a score_fn.")
        path = mh_sampler(
            alphabet=alphabet,
            length=length,
            steps=sample_size,
            score_fn=score_fn,
            seed=seed,
            temperature=temperature,
        )
        return iter(path)
    raise ValueError(f"Unknown mode: {mode}")


def _to_smiles_if_possible(is_canonical: bool, repr_str: str) -> Optional[str]:
    """
    Convert a representation (FASTA or DSL) to SMILES when possible.

    :param is_canonical: True if repr_str is a FASTA (canonical) sequence.
    :param repr_str: FASTA or DSL representation string.
    :returns: SMILES string or None if conversion not available/fails.
    """
    if is_canonical:
        if fasta_to_smiles is None:
            return None
        try:
            return fasta_to_smiles(repr_str)
        except Exception:
            return None

    if not _HAS_ASSEMBLER or pepdsl_parse is None or build_peptide_from_spec is None:
        return None
    try:
        spec = pepdsl_parse(repr_str)
        mol = build_peptide_from_spec(spec)
        return Chem.MolToSmiles(mol, isomericSmiles=True)  # type: ignore
    except Exception:
        return None


def _compute_seq_descriptors_if_available(seq: str) -> Dict[str, Any]:
    """
    Compute sequence descriptors for canonical sequences if the descriptor
    utility is available; otherwise return None-valued placeholders.
    """
    keys = {
        "seq_length": None,
        "seq_frac_hydrophobic": None,
        "seq_kd_mean": None,
        "seq_net_charge_pH7_4": None,
    }
    if sequence_descriptors is None:
        return keys
    try:
        desc = sequence_descriptors(seq)
        return {
            "seq_length": desc.length,
            "seq_frac_hydrophobic": desc.frac_hydrophobic,
            "seq_kd_mean": desc.kd_mean,
            "seq_net_charge_pH7_4": desc.net_charge_pH7_4,
        }
    except Exception:
        return keys


def _process_token_tuple(
    tokens: Tuple[str, ...],
    length: int,
    include_motif: Optional[str],
    exclude_motif: Optional[str],
    max_hydrophobic: Optional[float],
    max_abs_charge: Optional[float],
    convert_smiles: bool,
) -> Optional[Dict[str, Any]]:
    """
    Convert a token tuple into a row dict, applying motif and physchem filters.

    :param tokens: Token tuple.
    :param length: Sequence length.
    :param include_motif: Required substring (applies to FASTA or DSL).
    :param exclude_motif: Forbidden substring.
    :param max_hydrophobic: numeric filter (canonical only).
    :param max_abs_charge: numeric filter (canonical only).
    :param convert_smiles: whether to attempt SMILES conversion.
    :returns: row dict or None if filtered out.
    """
    fasta = tokens_to_fasta_if_possible(list(tokens))
    if fasta is None:
        repr_str = tokens_to_dsl(list(tokens))
        is_canonical = False
    else:
        repr_str = fasta
        is_canonical = True

    # motif filters (applies to both canonical and DSL)
    if include_motif and include_motif not in repr_str:
        return None
    if exclude_motif and exclude_motif in repr_str:
        return None

    # numeric filters only for canonical FASTA
    if is_canonical:
        if not passes_filters_canonical(repr_str, max_hydrophobic, max_abs_charge):
            return None
    else:
        if not passes_filters_dsl(repr_str, include_motif, exclude_motif):
            return None

    row: Dict[str, Any] = {
        "sequence_repr": repr_str,
        "is_canonical": is_canonical,
        "length": length,
    }

    if is_canonical:
        row.update(_compute_seq_descriptors_if_available(repr_str))

    if convert_smiles:
        row["smiles"] = _to_smiles_if_possible(is_canonical, repr_str)
    else:
        row["smiles"] = None

    return row


# ---------- public API (thin orchestration) --------------------------------


def generate_combinatorial_library(
    *,
    min_length: int,
    max_length: int,
    allow_nca: bool = False,
    allow_d: bool = False,
    extra_tokens: Optional[List[str]] = None,
    mode: str = "cartesian",
    max_combinations: int = 100_000,
    sample_size: int = 1000,
    guided_pool: int = 10_000,
    temperature: float = 1.0,
    seed: Optional[int] = None,
    include_motif: Optional[str] = None,
    exclude_motif: Optional[str] = None,
    max_hydrophobic: Optional[float] = None,
    max_abs_charge: Optional[float] = None,
    convert_smiles: bool = True,
    score_fn: Optional[Callable[[Tuple[str, ...]], float]] = None,
) -> pd.DataFrame:
    """
    Generate a combinatorial peptide library.

    :param min_length: Minimum sequence length (inclusive).
    :param max_length: Maximum sequence length (inclusive).
    :param allow_nca: Include NCA tokens (DSL).
    :param allow_d: Include D-forms (DSL tokens: 'dA', 'dC', ...).
    :param extra_tokens: Custom tokens to include.
    :param mode: Generation mode: 'cartesian' | 'sample' | 'guided-topk' | 'mh'.
    :param max_combinations: Hard cap on number of rows to prevent explosion.
    :param sample_size: Number of sequences per length in sampling modes.
    :param guided_pool: For 'guided-topk', number of random candidates to evaluate.
    :param temperature: For 'mh', soft acceptance temperature.
    :param seed: RNG seed.
    :param include_motif: Required substring (applies to FASTA or DSL rendering).
    :param exclude_motif: Forbidden substring.
    :param max_hydrophobic: Upper bound on hydrophobic fraction (canonical only).
    :param max_abs_charge: Upper bound on absolute net charge (canonical only).
    :param convert_smiles: If True, compute SMILES when possible.
    :param score_fn: Optional scoring function for guided modes: f(tokens)->float.
    :returns: DataFrame with columns:
              sequence_repr, is_canonical, length, smiles (optional),
              and seq_* descriptors for canonical sequences.
    """
    alphabet = expand_alphabet(allow_nca=allow_nca, allow_d=allow_d, extra=extra_tokens)
    records: List[Dict[str, Any]] = []
    lengths = range(min_length, max_length + 1)

    # conservative global guard
    total_upper = sum(len(alphabet) ** L for L in lengths)
    if mode == "cartesian" and total_upper > max_combinations:
        raise ValueError(
            "Cartesian product size ({}) exceeds max_combinations ({}). "
            "Use mode='sample' or a guided mode.".format(total_upper, max_combinations)
        )

    for L in lengths:
        it = _choose_iterator(
            mode=mode,
            alphabet=alphabet,
            length=L,
            sample_size=sample_size,
            seed=seed,
            score_fn=score_fn,
            guided_pool=guided_pool,
            temperature=temperature,
        )
        count_len = 0
        for tokens in it:
            row = _process_token_tuple(
                tokens=tokens,
                length=L,
                include_motif=include_motif,
                exclude_motif=exclude_motif,
                max_hydrophobic=max_hydrophobic,
                max_abs_charge=max_abs_charge,
                convert_smiles=convert_smiles,
            )
            if row is None:
                continue

            records.append(row)
            count_len += 1

            if len(records) >= max_combinations:
                break
            if mode != "cartesian" and count_len >= sample_size:
                break
        if len(records) >= max_combinations:
            break

    df = pd.DataFrame(records)
    if df.empty:
        return df
    df = df.drop_duplicates(subset=["sequence_repr", "smiles"]).reset_index(drop=True)
    return df
