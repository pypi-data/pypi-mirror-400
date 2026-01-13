from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Optional

THREE_TO_ONE = {
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
AA1 = set(list("ACDEFGHIKLMNPQRSTVWY"))
AA3 = set(THREE_TO_ONE.keys())
NCA_NAMES = {"Orn", "Dap", "Dab", "Nle", "Aib", "Hyp", "Sar"}
SMI_RE = re.compile(r"\[smiles\s*:\s*([^\]]+)\]", re.IGNORECASE)


@dataclass
class Token:
    kind: str  # 'AA1','AA3','NCA','SMI'
    code: str  # 'A', 'Lys', 'Orn' or SMILES
    is_d: bool = False


@dataclass
class SequenceSpec:
    tokens: List[Token]
    n_cap: Optional[str] = None  # 'Ac' or None
    c_cap: Optional[str] = None  # 'NH2' or None
    cyclize_head_to_tail: bool = False


# --- small helpers to keep parse() simple / low complexity -----------------


def _extract_cyclize_and_trim(text: str) -> (bool, str):
    """Detect cyclo(...) wrapper and return (cyclize_flag, inner_text)."""
    s = (text or "").strip()
    if s.lower().startswith("cyclo(") and s.endswith(")"):
        inner = s[s.find("(") + 1 : -1]  # noqa
        return True, inner.strip()
    return False, s


def _extract_caps(text: str) -> (Optional[str], Optional[str], str):
    """
    Detect N-/C- caps like 'Ac-' prefix and '-NH2' suffix.
    Returns (n_cap, c_cap, trimmed_text).
    """
    s = text
    n_cap = None
    c_cap = None
    if s.startswith("Ac-"):
        n_cap = "Ac"
        s = s[3:]
    if s.endswith("-NH2"):
        c_cap = "NH2"
        s = s[:-4]
    return n_cap, c_cap, s


def _extract_smiles_placeholders(text: str, smiles_blocks: List[str]) -> str:
    """
    Replace SMILES blocks '[SMILES: ...]' with placeholders and store the
    captured SMILES strings into smiles_blocks (in order).
    """

    def _store(m):
        smiles_blocks.append(m.group(1))
        return f"__SMI{len(smiles_blocks)-1}__"

    return SMI_RE.sub(_store, text)


def _parse_raw_token(raw: str, smiles_blocks: List[str]) -> Token:
    """
    Parse a single raw token (after splitting on '-') into a Token object.

    :param raw: raw token string (may be placeholder like '__SMI0__').
    :param smiles_blocks: list where SMILES captures are stored.
    :returns: Token instance.
    :raises ValueError: if token is unrecognized.
    """
    if raw.startswith("__SMI") and raw.endswith("__"):
        # placeholder -> restore SMILES content
        try:
            idx = int(raw[5:-2])
        except Exception:
            raise ValueError(f"Malformed SMILES placeholder: {raw!r}")
        try:
            smi = smiles_blocks[idx]
        except IndexError:
            raise ValueError(f"SMILES placeholder index out of range: {raw!r}")
        return Token(kind="SMI", code=smi)

    # Detect D- prefix (case-insensitive)
    is_d = False
    if raw and raw[0].lower() == "d" and len(raw) > 1:
        is_d = True
        core = raw[1:]
    else:
        core = raw

    # 1-letter AA?
    if len(core) == 1 and core.upper() in AA1:
        return Token(kind="AA1", code=core.upper(), is_d=is_d)

    # Normalize to Title case for 3-letter / named tokens
    title = core[:1].upper() + core[1:].lower()

    if title in AA3:
        return Token(kind="AA3", code=title, is_d=is_d)

    if title in NCA_NAMES:
        return Token(kind="NCA", code=title, is_d=is_d)

    raise ValueError(f"Unrecognized token '{raw}'")


# --- public parse function (keeps complexity low by delegating) -------------


def parse(seq_text: str) -> SequenceSpec:
    """
    Parse a PepDSL-like sequence string into a SequenceSpec.

    Supported token forms:
      - Single-letter canonical AAs: "ACDE"
      - Dash-separated tokens: "A-C-D", "A-Orn-dK"
      - 3-letter codes: "Ala-Lys"
      - NCA names: "Orn", "Dab", ...
      - Inline SMILES blocks: "[SMILES: CCCC]"
      - Cyclization: "cyclo(...)" wrapper
      - N-terminal acetylation: "Ac-" prefix
      - C-terminal amidation: "-NH2" suffix
      - D-residues: "dK" or "dOrn"

    :param seq_text: Input sequence string.
    :returns: SequenceSpec with tokens, caps and cyclization flag.
    :raises ValueError: On unrecognized tokens or malformed SMILES placeholders.
    """
    cyclize, body = _extract_cyclize_and_trim(seq_text)
    n_cap, c_cap, body = _extract_caps(body)

    smiles_blocks: List[str] = []
    body_with_placeholders = _extract_smiles_placeholders(body, smiles_blocks)

    # split on '-' after stripping whitespace
    raw_tokens = [t for t in body_with_placeholders.replace(" ", "").split("-") if t]

    tokens: List[Token] = []
    for rt in raw_tokens:
        token = _parse_raw_token(rt, smiles_blocks)
        tokens.append(token)

    return SequenceSpec(
        tokens=tokens,
        n_cap=n_cap,
        c_cap=c_cap,
        cyclize_head_to_tail=cyclize,
    )
