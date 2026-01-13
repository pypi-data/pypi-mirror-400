# graph/vg/parser.py
"""Compact peptide parser for VG with strict AA grammar, link tags and robust mods.

Grammar (as provided):
<pep>        ::= <residue>+
<residue>    ::= <AA> <link_tags>* <mods_opt>?
<link_tags>  ::= "(" <int> ( ":" <port> )? ")"
<mods_opt>   ::= "[" <mod> ( ("+" | "-") <mod> )* "]"
<AA>         ::= "A" | "R" | "N" | "D" | "C" | "Q" | "E" | "G"
               | "H" | "I" | "L" | "K" | "M" | "F" | "P" | "S"
               | "T" | "W" | "Y" | "V" | "X"
<mod>        ::= <alnum_token>         /* e.g. OH, 4OH, 4-OH, DL, NMe, Ac */
<port>       ::= <alnum_token>         /* e.g. SG, N, C, Oβ, Oy4 */
<int>        ::= [0-9]+

Notes
-----
- We accept mod tokens with internal dashes (e.g. 4-OH) and normalize them to '4OH',
  while preserving the original token text in node attributes.
- We optionally support 3-letter amino-acid names via a preprocessor (opt-in in VG).
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

# Strict AA (one-letter) per grammar
AA1_SET = set(list("ARNDCQEGHILKMFPSTWYVX"))

# Regex capturing a residue: AA + repeated link tags + optional [mods]
RES_RE = re.compile(
    r"""
    (?P<aa>[A-Za-z])                                   # AA (one letter, checked later)
    (?P<link>(?:\(\d+(?::[A-Za-z0-9_βγδ]+)?\))*)       # zero or more (int[:PORT])
    (?P<mods>\[(?:[^\]]*)\])?                          # optional [MODS]
    """,
    re.VERBOSE,
)

# Link tag inner parser
LINK_RE = re.compile(r"\((?P<idx>\d+)(?::(?P<port>[A-Za-z0-9_βγδ]+))?\)")

# 3-letter AA mapping (used only if allow_three_letter=True in VG.from_fasta)
AA3_TO_1: Dict[str, str] = {
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

# Lower/upper variants
AA3_TO_1.update({k.lower(): v for k, v in AA3_TO_1.items()})
AA3_TO_1.update({k.upper(): v for k, v in AA3_TO_1.items()})  # upper-case variants


@dataclass
class ParsedResidue:
    aa: str
    links: List[Tuple[int, Optional[str]]]  # list of (index, port)
    mods: List[Tuple[str, str, str]]  # list of (op, token_raw, token_norm)


# ---------- optional 3-letter preprocessor ----------
def three_to_one_compact(seq: str) -> str:
    """Convert 3-letter residue names to one-letter, token-aware
    (optional preprocessing)."""
    if not seq:
        return seq
    # We look for a 3-letter token followed by (, [, letter, or end-of-string.
    patt = re.compile(r"(?P<aa3>[A-Za-z]{3})(?=(\(|\[|[A-Za-z]|$))")

    def repl(m):
        aa3 = m.group("aa3")
        one = AA3_TO_1.get(aa3)
        return one if one else aa3

    return patt.sub(repl, seq)


# ---------- helpers ----------
def _normalize_mod_token(tok: str) -> str:
    """Normalize a mod token to an alnum core: '4-OH' -> '4OH'
    (keep greek digits/underscores)."""
    return re.sub(r"[-\s]", "", tok)


def _split_mods_keep_token(body: str) -> List[Tuple[str, str, str]]:
    """
    Split [ ... ] body into (op, token_raw, token_norm) items.

    Rules:
      - '+' always separates.
      - '-' separates unless it is alnum-surrounded (we keep it inside and
      normalize later).
      - First token may have op="".

    Examples:
      "4-OH+DL"  -> [("", "4-OH", "4OH"), ("+", "DL", "DL")]
      "OH-DL"    -> [("", "OH", "OH"), ("-", "DL", "DL")]
      "Ac+NMe"   -> [("", "Ac", "Ac"), ("+", "NMe", "NMe")]
    """
    items: List[Tuple[str, str, str]] = []
    i, n = 0, len(body)
    buf: List[str] = []
    curr_op = ""
    first = True
    while i < n:
        ch = body[i]
        if ch == "+":
            tok_raw = "".join(buf).strip()
            if tok_raw:
                items.append(
                    (
                        curr_op if not first else "",
                        tok_raw,
                        _normalize_mod_token(tok_raw),
                    )
                )
                first = False
            buf, curr_op = [], "+"
            i += 1
            continue
        if ch == "-":
            prev = body[i - 1] if i - 1 >= 0 else ""
            nxt = body[i + 1] if i + 1 < n else ""
            # keep '-' as part of token when surrounded by alnum characters
            if prev.isalnum() and nxt.isalnum():
                buf.append(ch)
                i += 1
                continue
            tok_raw = "".join(buf).strip()
            if tok_raw:
                items.append(
                    (
                        curr_op if not first else "",
                        tok_raw,
                        _normalize_mod_token(tok_raw),
                    )
                )
                first = False
            buf, curr_op = [], "-"
            i += 1
            continue
        buf.append(ch)
        i += 1

    tok_raw = "".join(buf).strip()
    if tok_raw:
        items.append(
            (curr_op if not first else "", tok_raw, _normalize_mod_token(tok_raw))
        )
    return items


# ---------- main parse ----------
def parse_compact(seq: str) -> List[ParsedResidue]:
    """Parse compact FASTA-like string (already 1-letter AAs) into structured residues."""
    pos = 0
    out: List[ParsedResidue] = []
    while pos < len(seq):
        m = RES_RE.match(seq, pos)
        if not m:
            raise ValueError(f"Parse error near: {seq[pos:pos+24]!r}")
        aa = m.group("aa")
        if aa not in AA1_SET:
            raise ValueError(
                f"Invalid AA letter {aa!r} at offset {pos} (strict grammar)."
            )
        links_raw = m.group("link") or ""
        mods_raw = m.group("mods") or ""

        # links
        link_items: List[Tuple[int, Optional[str]]] = []
        for lm in LINK_RE.finditer(links_raw):
            idx = int(lm.group("idx"))
            port = lm.group("port")
            link_items.append((idx, port))

        # mods
        mods_list: List[Tuple[str, str, str]] = []
        if mods_raw:
            body = mods_raw[1:-1]  # drop brackets
            mods_list = _split_mods_keep_token(body)

        out.append(ParsedResidue(aa=aa, links=link_items, mods=mods_list))
        pos = m.end()
    return out
