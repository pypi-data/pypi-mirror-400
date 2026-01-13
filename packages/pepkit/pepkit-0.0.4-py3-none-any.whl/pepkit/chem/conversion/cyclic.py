"""
Compact cyclic-peptide -> RDKit Mol/SMILES converter with mod handlers and
valence-safe crosslinking (removes explicit H when necessary before forming
a new bond).

Example:
    s = "C(1:SG)(2:SG)CV[OH+DL](2:O)L[4OH]I[OH](1:N)"
    smi = compact_to_smiles_with_mods(s, embed=False, debug=True)
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import AllChem

AA_SET = set("ACDEFGHIKLMNPQRSTVWY") | {"X"}

_LINK_RE = re.compile(r"^\s*(\d+)(?::([A-Za-z0-9_+\-]+))?\s*$")
_HEADER_LINK_RE = re.compile(
    r"^(\d+)\s*:\s*(\d+)(?:\.([A-Za-z0-9_+\-]+))?-(\d+)(?:\.([A-Za-z0-9_+\-]+))?$"
)

_BACKBONE_SMARTS = Chem.MolFromSmarts("N-C-C(=O)")

Port = Optional[str]
Endpoint = Tuple[int, Port]
LinksDict = Dict[int, Tuple[Endpoint, Endpoint]]


@dataclass(frozen=True)
class ResidueToken:
    pos: int
    aa: str
    mods: Tuple[str, ...]
    tags: Tuple[Tuple[int, Port], ...]


# ----------------------------
# Compact parser (refactored)
# ----------------------------
def _expect_aa_letter(s: str, i: int) -> str:
    ch = s[i].upper()
    if ch not in AA_SET:
        raise ValueError(f"Expected AA letter at index {i}, got {s[i]!r} in '{s}'")
    return ch


def _find_closing(s: str, start: int, close_ch: str) -> int:
    j = s.find(close_ch, start)
    if j == -1:
        raise ValueError(f"Unclosed '{close_ch}' in input")
    return j


def _parse_link_payload(payload: str) -> Tuple[int, Port]:
    m = _LINK_RE.match(payload)
    if not m:
        raise ValueError(f"Bad link tag content '{payload}'")
    lid = int(m.group(1))
    port = m.group(2) if m.group(2) else None
    return lid, port


def _parse_mod_payload(payload: str) -> List[str]:
    payload = payload.strip()
    if not payload:
        return []
    mods: List[str] = []
    for tok in re.split(r"[+\-]", payload):
        tok = tok.strip()
        if tok:
            mods.append(tok)
    return mods


def _consume_one_annotation(
    s: str,
    i: int,
    pos: int,
    link_map: DefaultDict[int, List[Endpoint]],
    tags: List[Tuple[int, Port]],
    mods: List[str],
) -> int:
    """Consume one (...) or [...] annotation starting at index i; return next index."""
    if s[i] == "(":
        j = _find_closing(s, i + 1, ")")
        lid, port = _parse_link_payload(s[i + 1 : j])  # noqa
        tags.append((lid, port))
        link_map[lid].append((pos, port))
        return j + 1

    if s[i] == "[":
        j = _find_closing(s, i + 1, "]")
        mods.extend(_parse_mod_payload(s[i + 1 : j]))  # noqa
        return j + 1

    return i


def _validate_link_map(link_map: Dict[int, List[Endpoint]]) -> None:
    for lid, endpoints in link_map.items():
        if len(endpoints) != 2:
            raise ValueError(
                f"Link id {lid} occurs {len(endpoints)} times (expected 2)."
            )


def parse_compact_cyclic(s: str) -> Dict:
    """
    Parse compact cyclic format like:
        C(1:SG)(2:SG)CV[OH+DL](2:O)L[4OH]I[OH](1:N)

    Returns dict with:
      - sequence: str
      - residues: list of residue dicts
      - links: dict[lid] -> [(pos, port), (pos, port)]
    """
    s = s.strip().replace("--", "")
    i, n = 0, len(s)
    pos = 0

    residues: List[Dict] = []
    link_map: DefaultDict[int, List[Endpoint]] = defaultdict(list)

    while i < n:
        aa = _expect_aa_letter(s, i)
        pos += 1
        i += 1

        tags: List[Tuple[int, Port]] = []
        mods: List[str] = []

        while i < n and s[i] in ("(", "["):
            i = _consume_one_annotation(s, i, pos, link_map, tags, mods)

        residues.append({"pos": pos, "aa": aa, "mods": mods, "tags": tags})

    _validate_link_map(dict(link_map))

    return {
        "sequence": "".join(r["aa"] for r in residues),
        "residues": residues,
        "links": dict(link_map),
    }


# ----------------------------
# FASTA header parser
# ----------------------------
def parse_header_links(header: str) -> LinksDict:
    m = re.search(r"links\s*=\s*([^|]+)", header)
    if not m:
        return {}

    field = m.group(1).strip()
    out: LinksDict = {}

    for chunk in (c.strip() for c in field.split(",")):
        if not chunk:
            continue
        m2 = _HEADER_LINK_RE.match(chunk)
        if not m2:
            raise ValueError(f"Bad links token: '{chunk}'")

        lid = int(m2.group(1))
        a_pos, a_port = int(m2.group(2)), m2.group(3)
        b_pos, b_port = int(m2.group(4)), m2.group(5)
        out[lid] = ((a_pos, a_port), (b_pos, b_port))

    return out


# ----------------------------
# Backbone detection & CA ordering (refactored)
# ----------------------------
def find_calpha_indices(mol: Chem.Mol) -> List[int]:
    if _BACKBONE_SMARTS is None:
        return []
    matches = mol.GetSubstructMatches(_BACKBONE_SMARTS)
    cas = [t[1] for t in matches]
    seen: set[int] = set()
    out: List[int] = []
    for c in cas:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _is_carbonyl_carbon(atom: Chem.Atom) -> bool:
    if atom.GetAtomicNum() != 6:
        return False
    mol = atom.GetOwningMol()
    aidx = atom.GetIdx()
    for nb in atom.GetNeighbors():
        if nb.GetAtomicNum() != 8:
            continue
        bond = mol.GetBondBetweenAtoms(aidx, nb.GetIdx())
        if bond is not None and bond.GetBondTypeAsDouble() >= 2.0:
            return True
    return False


def _carbonyl_carbon_of_ca(mol: Chem.Mol, ca_idx: int) -> Optional[int]:
    ca_atom = mol.GetAtomWithIdx(ca_idx)
    for nb in ca_atom.GetNeighbors():
        if _is_carbonyl_carbon(nb):
            return nb.GetIdx()
    return None


def _next_ca_from_carbonyl(
    mol: Chem.Mol, carbonyl_c_idx: int, ca_set: set[int]
) -> Optional[int]:
    """
    Try to follow peptide connectivity:
        CA - C(=O) - N - CA(next)
    """
    c_atom = mol.GetAtomWithIdx(carbonyl_c_idx)
    for nb in c_atom.GetNeighbors():
        if nb.GetAtomicNum() != 7:
            continue
        n_atom = nb
        for nb2 in n_atom.GetNeighbors():
            nb2_idx = nb2.GetIdx()
            if nb2_idx == carbonyl_c_idx:
                continue
            if nb2_idx in ca_set:
                return nb2_idx
    return None


def _build_backbone_edges(
    mol: Chem.Mol, ca_indices: List[int]
) -> Tuple[Dict[int, List[int]], Dict[int, int]]:
    ca_set = set(ca_indices)
    ca_to_c = {ca: _carbonyl_carbon_of_ca(mol, ca) for ca in ca_indices}

    edges: Dict[int, List[int]] = defaultdict(list)
    incoming: Dict[int, int] = defaultdict(int)

    for ca, cc in ca_to_c.items():
        if cc is None:
            continue
        next_ca = _next_ca_from_carbonyl(mol, cc, ca_set)
        if next_ca is None:
            continue
        edges[ca].append(next_ca)
        incoming[next_ca] += 1
        incoming.setdefault(ca, incoming.get(ca, 0))

    return edges, incoming


def _walk_linear_order(
    ca_indices: List[int], edges: Dict[int, List[int]], incoming: Dict[int, int]
) -> List[int]:
    starts = [ca for ca in ca_indices if incoming.get(ca, 0) == 0]
    if not starts:
        return list(ca_indices)

    ordered: List[int] = []
    visited: set[int] = set()

    cur = starts[0]
    while cur is not None and cur not in visited:
        ordered.append(cur)
        visited.add(cur)
        nxts = edges.get(cur, [])
        cur = nxts[0] if nxts else None

    for ca in ca_indices:
        if ca not in visited:
            ordered.append(ca)

    return ordered


def order_residues_via_backbone(mol: Chem.Mol, ca_indices: List[int]) -> List[int]:
    """
    Attempt to order CA atoms along the peptide backbone using local connectivity.
    Falls back to given ca_indices if a clear start cannot be determined.
    """
    edges, incoming = _build_backbone_edges(mol, ca_indices)
    return _walk_linear_order(ca_indices, edges, incoming)


# ----------------------------
# Port resolution (refactored)
# ----------------------------
def _bfs_find_atomic_num(
    mol: Chem.Mol,
    start_indices: Iterable[int],
    blocked: set[int],
    atomic_num: int,
) -> Optional[int]:
    seen = set(blocked)
    queue = [i for i in start_indices if i is not None and i not in seen]
    qi = 0

    while qi < len(queue):
        v = queue[qi]
        qi += 1
        if v in seen:
            continue
        seen.add(v)

        at = mol.GetAtomWithIdx(v)
        if at.GetAtomicNum() == atomic_num:
            return v

        for nb in at.GetNeighbors():
            nb_i = nb.GetIdx()
            if nb_i not in seen:
                queue.append(nb_i)

    return None


def _backbone_neighbor_indices(
    mol: Chem.Mol, ca_idx: int
) -> Tuple[Optional[int], Optional[int], List[int]]:
    ca_atom = mol.GetAtomWithIdx(ca_idx)
    neighs = [nb.GetIdx() for nb in ca_atom.GetNeighbors()]

    n_idx: Optional[int] = None
    c_carb_idx: Optional[int] = None

    for nb_idx in neighs:
        nb_atom = mol.GetAtomWithIdx(nb_idx)
        if nb_atom.GetAtomicNum() == 7 and n_idx is None:
            n_idx = nb_idx
        if _is_carbonyl_carbon(nb_atom) and c_carb_idx is None:
            c_carb_idx = nb_idx

    return n_idx, c_carb_idx, neighs


def _infer_cb_index(
    mol: Chem.Mol, neighs: List[int], n_idx: Optional[int], c_carb_idx: Optional[int]
) -> Optional[int]:
    for nb_idx in neighs:
        if nb_idx in (n_idx, c_carb_idx):
            continue
        if mol.GetAtomWithIdx(nb_idx).GetAtomicNum() == 6:
            return nb_idx
    return None


def _port_atom_index(mol: Chem.Mol, ca_idx: int, port: Port) -> Optional[int]:
    if port is None:
        return None

    n_idx, c_carb_idx, neighs = _backbone_neighbor_indices(mol, ca_idx)
    cb_idx = _infer_cb_index(mol, neighs, n_idx, c_carb_idx)

    p = port.upper()
    if p == "N":
        return n_idx
    if p in ("C", "CTERM"):
        return c_carb_idx
    if p == "CB":
        return cb_idx

    blocked = {ca_idx}
    if n_idx is not None:
        blocked.add(n_idx)
    if c_carb_idx is not None:
        blocked.add(c_carb_idx)

    if p == "SG":
        return _bfs_find_atomic_num(mol, neighs, blocked, 16)
    if p in ("OG", "OG1", "OH", "O"):
        return _bfs_find_atomic_num(mol, neighs, blocked, 8)

    return None


# ----------------------------
# Port heuristics
# ----------------------------
def _is_oxy_res(aa: str) -> bool:
    return aa in ("S", "T", "Y")


def _is_cys(aa: str) -> bool:
    return aa == "C"


def _has_mod(mods_by_pos: Dict[int, List[str]], pos: int, mod: str) -> bool:
    return any(m.upper() == mod for m in mods_by_pos.get(pos, []))


def _guess_ports_for_pair(
    a_pos: int,
    b_pos: int,
    seq: str,
    a_port_in: Port,
    b_port_in: Port,
    mods_by_pos: Dict[int, List[str]],
) -> Tuple[Port, Port]:
    n_res = len(seq)
    aa_a = seq[a_pos - 1]
    aa_b = seq[b_pos - 1]

    a_port = a_port_in
    b_port = b_port_in

    # N- to C- cyclization special-case
    if a_port is None and b_port is None and {a_pos, b_pos} == {1, n_res}:
        return ("N", "C") if a_pos == 1 else ("C", "N")

    if a_port is None and _is_cys(aa_a):
        a_port = "SG"
    if b_port is None and _is_cys(aa_b):
        b_port = "SG"

    if a_port is None and _is_oxy_res(aa_a):
        a_port = "OG"
    if b_port is None and _is_oxy_res(aa_b):
        b_port = "OG"

    if a_port is None and _has_mod(mods_by_pos, a_pos, "OH"):
        a_port = "OH"
    if b_port is None and _has_mod(mods_by_pos, b_pos, "OH"):
        b_port = "OH"

    if a_port is None and b_port is None:
        return ("N", "C") if a_pos < b_pos else ("C", "N")

    return a_port, b_port


# ----------------------------
# Mod handlers (unchanged behavior, minor style tweaks)
# ----------------------------
def _find_cb_of_ca(mol: Chem.Mol, ca_idx: int) -> Optional[int]:
    ca = mol.GetAtomWithIdx(ca_idx)
    for nb in ca.GetNeighbors():
        nb_idx = nb.GetIdx()
        atom = mol.GetAtomWithIdx(nb_idx)
        if atom.GetAtomicNum() != 6:
            continue
        if not _is_carbonyl_carbon(atom):
            return nb_idx
    return None


def _sanitize(m: Chem.Mol) -> Chem.Mol:
    try:
        Chem.SanitizeMol(m)
    except Exception:
        Chem.SanitizeMol(m, catchErrors=True)
    return m


def add_hydroxyl_to_cb(mol: Chem.Mol, ca_idx: int) -> Chem.Mol:
    cb = _find_cb_of_ca(mol, ca_idx)
    if cb is None:
        raise ValueError(f"Could not find CB for CA index {ca_idx}")

    rw = Chem.RWMol(mol)
    o_idx = rw.AddAtom(Chem.Atom(8))
    h_idx = rw.AddAtom(Chem.Atom(1))
    rw.AddBond(cb, o_idx, Chem.BondType.SINGLE)
    rw.AddBond(o_idx, h_idx, Chem.BondType.SINGLE)
    return _sanitize(rw.GetMol())


def add_4oh_to_sidechain(mol: Chem.Mol, ca_idx: int) -> Chem.Mol:
    ca = mol.GetAtomWithIdx(ca_idx)
    start_neighbors = [nb.GetIdx() for nb in ca.GetNeighbors()]

    seen: set[int] = {ca_idx}
    queue: List[Tuple[int, int]] = [(nb, 1) for nb in start_neighbors]
    candidate: Optional[int] = None

    while queue:
        idx, dist = queue.pop(0)
        if idx in seen:
            continue
        seen.add(idx)

        atom = mol.GetAtomWithIdx(idx)
        if atom.GetAtomicNum() == 6 and dist >= 2 and not _is_carbonyl_carbon(atom):
            candidate = idx
            break

        for nb in atom.GetNeighbors():
            nb_idx = nb.GetIdx()
            if nb_idx not in seen:
                queue.append((nb_idx, dist + 1))

    if candidate is None:
        candidate = _find_cb_of_ca(mol, ca_idx)
        if candidate is None:
            raise ValueError("Could not find sidechain carbon to attach 4OH")

    rw = Chem.RWMol(mol)
    o_idx = rw.AddAtom(Chem.Atom(8))
    h_idx = rw.AddAtom(Chem.Atom(1))
    rw.AddBond(candidate, o_idx, Chem.BondType.SINGLE)
    rw.AddBond(o_idx, h_idx, Chem.BondType.SINGLE)
    return _sanitize(rw.GetMol())


def add_n_methylation_on_n(mol: Chem.Mol, ca_idx: int) -> Chem.Mol:
    ca = mol.GetAtomWithIdx(ca_idx)
    n_idx = next(
        (nb.GetIdx() for nb in ca.GetNeighbors() if nb.GetAtomicNum() == 7), None
    )
    if n_idx is None:
        raise ValueError("Could not find backbone N for N-methylation")

    rw = Chem.RWMol(mol)
    c_idx = rw.AddAtom(Chem.Atom(6))
    h1 = rw.AddAtom(Chem.Atom(1))
    h2 = rw.AddAtom(Chem.Atom(1))
    h3 = rw.AddAtom(Chem.Atom(1))

    rw.AddBond(n_idx, c_idx, Chem.BondType.SINGLE)
    rw.AddBond(c_idx, h1, Chem.BondType.SINGLE)
    rw.AddBond(c_idx, h2, Chem.BondType.SINGLE)
    rw.AddBond(c_idx, h3, Chem.BondType.SINGLE)

    return _sanitize(rw.GetMol())


MOD_HANDLERS = {
    "OH": add_hydroxyl_to_cb,
    "4OH": add_4oh_to_sidechain,
    "NME": add_n_methylation_on_n,
}


# ----------------------------
# Valence-safe bond helpers (refactored)
# ----------------------------
def _tag_original_indices(mol: Chem.Mol) -> None:
    for a in mol.GetAtoms():
        a.SetProp("_orig_idx", str(a.GetIdx()))


def _find_current_index_by_orig(rw: Chem.RWMol, orig_idx: int) -> Optional[int]:
    key = str(orig_idx)
    for a in rw.GetAtoms():
        if a.HasProp("_orig_idx") and a.GetProp("_orig_idx") == key:
            return a.GetIdx()
    return None


def _remove_one_explicit_h_neighbor(rw: Chem.RWMol, atom_idx: int) -> bool:
    atom = rw.GetAtomWithIdx(atom_idx)
    for nb in atom.GetNeighbors():
        if nb.GetAtomicNum() == 1:
            rw.RemoveAtom(nb.GetIdx())
            return True
    return False


def _needs_h_strip(rw: Chem.RWMol, atom_idx: int) -> bool:
    at = rw.GetAtomWithIdx(atom_idx)
    return at.GetSymbol().upper() == "O" and at.GetDegree() >= 2


def _ensure_bondable_and_add(
    rw: Chem.RWMol,
    orig_a_idx: int,
    orig_b_idx: int,
    debug: bool = False,
) -> None:
    """
    Given original atom indices (before RW edits), find current indices,
    strip one explicit H from oxygen endpoints when needed, then add a single bond.
    """

    def cur(orig: int) -> int:
        idx = _find_current_index_by_orig(rw, orig)
        if idx is None:
            raise ValueError(f"Could not find current index for original {orig}")
        return idx

    # initial mapping
    cur_a = cur(orig_a_idx)
    cur_b = cur(orig_b_idx)

    # strip H where required (recompute indices after any removal)
    stripped_any = False
    if _needs_h_strip(rw, cur_a):
        if debug:
            print(f"[VALENCE] stripping H on O endpoint (orig={orig_a_idx})")
        stripped_any |= _remove_one_explicit_h_neighbor(rw, cur_a)

    if stripped_any:
        cur_a = cur(orig_a_idx)

    cur_b = cur(orig_b_idx)
    if _needs_h_strip(rw, cur_b):
        if debug:
            print(f"[VALENCE] stripping H on O endpoint (orig={orig_b_idx})")
        stripped_any |= _remove_one_explicit_h_neighbor(rw, cur_b)

    # recompute final indices and add bond
    cur_a = cur(orig_a_idx)
    cur_b = cur(orig_b_idx)
    rw.AddBond(cur_a, cur_b, order=Chem.BondType.SINGLE)


# ----------------------------
# Add crosslinks (valence-safe)
# ----------------------------
def _pos_to_ca_orig(order: List[int]) -> Dict[int, int]:
    # residue positions are 1-based
    return {i + 1: ca for i, ca in enumerate(order)}


def _resolve_link_endpoints(
    mol_snapshot: Chem.Mol,
    pos_to_ca: Dict[int, int],
    sequence: str,
    mods_by_pos: Dict[int, List[str]],
    a_pos: int,
    b_pos: int,
    a_port_raw: Port,
    b_port_raw: Port,
) -> Tuple[int, int, Port, Port]:
    a_port_eff, b_port_eff = _guess_ports_for_pair(
        a_pos=a_pos,
        b_pos=b_pos,
        seq=sequence,
        a_port_in=a_port_raw,
        b_port_in=b_port_raw,
        mods_by_pos=mods_by_pos,
    )

    ca_a_orig = pos_to_ca[a_pos]
    ca_b_orig = pos_to_ca[b_pos]
    orig_idx_a = _port_atom_index(mol_snapshot, ca_a_orig, a_port_eff)
    orig_idx_b = _port_atom_index(mol_snapshot, ca_b_orig, b_port_eff)

    if orig_idx_a is None or orig_idx_b is None:
        msg = (
            "Cannot resolve port atoms: "
            f"{a_pos}.{a_port_eff} ↔ {b_pos}.{b_port_eff} "
            f"(CA originals {ca_a_orig},{ca_b_orig})"
        )
        raise ValueError(msg)

    return orig_idx_a, orig_idx_b, a_port_eff, b_port_eff


def _add_crosslinks(
    mol: Chem.Mol,
    links: LinksDict,
    sequence: str,
    mods_by_pos: Optional[Dict[int, List[str]]] = None,
    debug: bool = False,
) -> Chem.Mol:
    if mods_by_pos is None:
        mods_by_pos = {}

    ca_indices = find_calpha_indices(mol)
    if not ca_indices:
        raise ValueError("No Cα atoms found - cannot order residues.")

    order = order_residues_via_backbone(mol, ca_indices)
    if not order:
        raise ValueError("Could not order residues along backbone.")

    # Snapshot indices (original), then operate on RW mol
    _tag_original_indices(mol)
    rw = Chem.RWMol(mol)

    n_res = len(order)
    pos_to_ca = _pos_to_ca_orig(order)

    for lid, ((a_pos, a_port_raw), (b_pos, b_port_raw)) in sorted(links.items()):
        if not (1 <= a_pos <= n_res and 1 <= b_pos <= n_res):
            raise ValueError(
                f"Link {lid} positions out of range: {a_pos}, {b_pos} (N={n_res})"
            )

        orig_idx_a, orig_idx_b, a_eff, b_eff = _resolve_link_endpoints(
            mol_snapshot=mol,
            pos_to_ca=pos_to_ca,
            sequence=sequence,
            mods_by_pos=mods_by_pos,
            a_pos=a_pos,
            b_pos=b_pos,
            a_port_raw=a_port_raw,
            b_port_raw=b_port_raw,
        )

        if debug:
            print(
                "[DEBUG] link "
                f"{lid}: pos{a_pos}.{a_port_raw}->{a_eff} "
                f"pos{b_pos}.{b_port_raw}->{b_eff} "
                f"orig atoms {orig_idx_a},{orig_idx_b}"
            )

        _ensure_bondable_and_add(rw, orig_idx_a, orig_idx_b, debug=debug)

    out = rw.GetMol()
    return _sanitize(out)


# ----------------------------
# Public wrappers
# ----------------------------
def compact_to_smiles(compact: str, embed: bool = False, debug: bool = False) -> str:
    parsed = parse_compact_cyclic(compact)
    seq = parsed["sequence"]
    mods_by_pos = {r["pos"]: r["mods"] for r in parsed["residues"] if r["mods"]}

    mol = Chem.MolFromFASTA(seq)
    if mol is None:
        raise ValueError(f"RDKit refused to build molecule from sequence '{seq}'")

    links: LinksDict = {lid: (eps[0], eps[1]) for lid, eps in parsed["links"].items()}
    mol2 = _add_crosslinks(
        mol, links, sequence=seq, mods_by_pos=mods_by_pos, debug=debug
    )

    if embed:
        mol2 = Chem.AddHs(mol2)
        AllChem.EmbedMolecule(mol2, randomSeed=0xC0FFEE)
        try:
            AllChem.UFFOptimizeMolecule(mol2)
        except Exception:
            pass

    return Chem.MolToSmiles(mol2, canonical=True, isomericSmiles=True)


def _apply_mods_in_order(
    mol: Chem.Mol,
    parsed_residues: List[Dict],
    debug: bool,
) -> Tuple[Chem.Mol, Dict[int, List[str]]]:
    ca_indices = find_calpha_indices(mol)
    order = order_residues_via_backbone(mol, ca_indices)
    if not order:
        raise ValueError("Could not order residues after initial build")

    mods_by_pos: Dict[int, List[str]] = {}

    for r in parsed_residues:
        pos = r["pos"]
        mods = r["mods"]
        if not mods:
            continue

        for m in mods:
            m_norm = m.upper()
            handler = MOD_HANDLERS.get(m_norm)
            if handler is None:
                if debug:
                    print(f"[DEBUG] No handler for mod '{m_norm}' at pos {pos} (skip)")
                continue

            ca_idx = order[pos - 1]
            if debug:
                print(f"[DEBUG] Applying mod '{m_norm}' at pos {pos} (CA idx {ca_idx})")

            mol = handler(mol, ca_idx)

            # Recompute ordering after each structural change
            ca_indices = find_calpha_indices(mol)
            order = order_residues_via_backbone(mol, ca_indices)

        mods_by_pos[pos] = mods

    return mol, mods_by_pos


def compact_to_smiles_with_mods(
    compact: str, embed: bool = False, debug: bool = False
) -> str:
    parsed = parse_compact_cyclic(compact)
    seq = parsed["sequence"]

    mol = Chem.MolFromFASTA(seq)
    if mol is None:
        raise ValueError(f"RDKit refused to build molecule from sequence '{seq}'")

    mol, mods_by_pos = _apply_mods_in_order(mol, parsed["residues"], debug=debug)

    links: LinksDict = {lid: (eps[0], eps[1]) for lid, eps in parsed["links"].items()}
    mol2 = _add_crosslinks(
        mol, links, sequence=seq, mods_by_pos=mods_by_pos, debug=debug
    )

    if embed:
        mol2 = Chem.AddHs(mol2)
        AllChem.EmbedMolecule(mol2, randomSeed=0xC0FFEE)
        try:
            AllChem.UFFOptimizeMolecule(mol2)
        except Exception:
            pass

    return Chem.MolToSmiles(mol2, canonical=True, isomericSmiles=True)


if __name__ == "__main__":
    example = "C(1:SG)(2:SG)CV[OH+DL](2:O)L[4OH]I[OH](1:N)"
    print("Input:", example)
    try:
        smi = compact_to_smiles_with_mods(example, embed=False, debug=True)
        print("SMILES:", smi)
    except Exception as e:
        print("ERROR:", e)
