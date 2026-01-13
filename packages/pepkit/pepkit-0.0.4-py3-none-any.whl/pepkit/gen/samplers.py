"""Sampling strategies for combinatorial sequence generation."""

from __future__ import annotations
import itertools
import random
from typing import Callable, Iterable, Iterator, List, Optional, Sequence, Tuple


def iter_cartesian(alphabet: Sequence[str], length: int) -> Iterable[Tuple[str, ...]]:
    """Deterministic cartesian iterator.

    :param alphabet: Token alphabet.
    :param length: Sequence length.
    :returns: Iterable over tuples of tokens.
    """
    return itertools.product(alphabet, repeat=length)


def sample_random_unique(
    alphabet: Sequence[str],
    length: int,
    n_samples: int,
    seed: Optional[int] = None,
) -> Iterator[Tuple[str, ...]]:
    """Uniform random unique samples without enumerating all.

    :param alphabet: Token alphabet.
    :param length: Sequence length.
    :param n_samples: Number of unique samples to yield.
    :param seed: RNG seed.
    :yields: Unique token tuples.
    """
    rng = random.Random(seed)
    seen = set()
    max_tries = max(n_samples * 20, n_samples + 1000)
    tries = 0
    while len(seen) < n_samples and tries < max_tries:
        tries += 1
        tup = tuple(rng.choice(alphabet) for _ in range(length))
        if tup in seen:
            continue
        seen.add(tup)
        yield tup


def guided_topk_sampler(
    alphabet: Sequence[str],
    length: int,
    n_candidates: int,
    topk: int,
    score_fn: Callable[[Tuple[str, ...]], float],
    seed: Optional[int] = None,
) -> List[Tuple[str, ...]]:
    """Guided sampling: draw random candidates and keep the top-k by score.

    :param alphabet: Token alphabet.
    :param length: Sequence length.
    :param n_candidates: Number of random candidates to evaluate.
    :param topk: Keep the best `topk` sequences.
    :param score_fn: Callable mapping token tuple -> score (higher is better).
    :param seed: RNG seed.
    :returns: Best `topk` token tuples by score.
    """
    rng = random.Random(seed)
    cand = [
        tuple(rng.choice(alphabet) for _ in range(length)) for _ in range(n_candidates)
    ]
    scored = [(score_fn(t), t) for t in cand]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:topk]]


def _mutate_one(
    base: Tuple[str, ...],
    alphabet: Sequence[str],
    rng: random.Random,
) -> Tuple[str, ...]:
    """Return a copy with a single random position replaced by a random token."""
    if not base:
        return base
    pos = rng.randrange(len(base))
    tok = rng.choice(alphabet)
    out = list(base)
    out[pos] = tok
    return tuple(out)


def mh_sampler(
    alphabet: Sequence[str],
    length: int,
    steps: int,
    score_fn: Callable[[Tuple[str, ...]], float],
    seed: Optional[int] = None,
    temperature: float = 1.0,
) -> List[Tuple[str, ...]]:
    """Simple Metropolis–Hastings sampler over token sequences.

    :param alphabet: Token alphabet.
    :param length: Sequence length.
    :param steps: Number of MH steps (returned list length equals steps).
    :param score_fn: Callable mapping token tuple -> score (higher is better).
    :param seed: RNG seed.
    :param temperature: Acceptance softness; higher accepts worse moves more often.
    :returns: Visited sequences (including repeats).
    """
    rng = random.Random(seed)
    cur = tuple(rng.choice(alphabet) for _ in range(length))
    cur_s = score_fn(cur)
    path: List[Tuple[str, ...]] = []
    for _ in range(steps):
        prop = _mutate_one(cur, alphabet, rng)
        prop_s = score_fn(prop)
        if prop_s >= cur_s:
            accept = True
        else:
            # exp((s_prop - s_cur)/T) with clamping
            delta = (prop_s - cur_s) / max(temperature, 1e-9)
            accept = rng.random() < min(1.0, max(0.0, pow(2.718281828, delta)))
        if accept:
            cur, cur_s = prop, prop_s
        path.append(cur)
    return path
