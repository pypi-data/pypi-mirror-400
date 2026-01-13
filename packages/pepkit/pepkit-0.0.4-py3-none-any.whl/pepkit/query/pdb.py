from datetime import datetime
import re, requests, sys, os
import urllib.request
from pathlib import Path
from typing import Iterable, Optional, Set
from collections import defaultdict
import pandas as pd
import logging
from joblib import Parallel, delayed

sys.path.append(
    "/Users/vitran/Documents/Work/Github/Mod1_data"
)  # should not change path inside functions
from mod1_data.utils import retrieve_pdb, chains_within_cutoff

base = "/Users/vitran/Documents/Work/Github/Mod1_data"  # this is called hard-code which means not good practice
batch = "1.latest"

# Set up logging
# log_file = f"{base}/raw_data/14.rcsb/4.test_log/log_canonical.txt"
# os.makedirs(os.path.dirname(log_file), exist_ok=True)

# # Configure logging to both file and console
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(message)s',
#     handlers=[
#         logging.FileHandler(log_file),
#         logging.StreamHandler(sys.stdout)
#     ]
# )

# # mod1_data.utils.retrieve_pdb_chains # CHECK WHICH ONE WORKS BETTER? the utils was used to fetch all pdbs in mod1_data
# def retrieve_pdb_chains(
#     pdb_id: str, chains: str | list[str] | set[str], out_path: str | Path
# ) -> Path:
#     """
#     Download a PDB file by ID and keep only the specified chains (by chain ID).
#     Writes the filtered structure to 'out_path' (PDB format) and returns the path.
#     """
#     if not re.fullmatch(r"[0-9A-Za-z]{4}", pdb_id or ""):
#         raise ValueError(f"Invalid PDB ID: {pdb_id!r}")
#     if isinstance(chains, (str, bytes)):
#         chain_set = {c for c in str(chains) if c.strip()}
#     elif isinstance(chains, (list, tuple, set)):
#         chain_set = {str(c)[0] for c in chains if str(c).strip()}
#     else:
#         # scalar like int/float -> stringify
#         chain_set = {c for c in str(chains) if c.strip()}
#     if not chain_set:
#         raise ValueError("No chain IDs provided.")

#     pdb_id = pdb_id.upper()
#     out_path = Path(out_path)

#     url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
#     with urllib.request.urlopen(url) as resp:
#         pdb_text = resp.read().decode("latin-1").splitlines(keepends=True)

#     keep_prefixes = ("ATOM  ", "HETATM", "ANISOU", "TER   ")
#     filtered = []
#     for line in pdb_text:
#         if line.startswith(keep_prefixes):
#             if len(line) > 21 and line[21] in chain_set:
#                 filtered.append(line)

#         else:

#             filtered.append(line)

#     # ensure file ends with newline
#     if filtered and not filtered[-1].endswith("\n"):
#         filtered[-1] = filtered[-1] + "\n"

#     out_path.parent.mkdir(parents=True, exist_ok=True)
#     with open(out_path, "w", encoding="latin-1") as f:
#         f.writelines(filtered)
#     return out_path


def retrieve_pdb_chains(
    pdb_id: str,
    chains: str | Iterable[str],
    out_path: str | Path,
    *,
    keep_het_resnames: Optional[Iterable[str]] = None,
    keep_hets_in_chain: bool = True,
) -> Path:
    """
    Download a PDB file by ID and keep only the specified chain(s).

    - By default HETATM lines are excluded, except:
        - HETATM with residue name in 'keep_het_resnames' (if provided),
        - OR HETATM whose chain is in 'chains' and whose resSeq matches a resSeq
        observed for ATOM records in the chosen chain(s) (controlled by
        'keep_hets_in_chain', default True). This keeps modified residues such
        as MSE/SEP/TPO that are recorded as HETATM but belong to the chain.
    - ANISOU lines are kept when their corresponding atom serial is kept.
    - CONECT lines are filtered to reference only kept atom serials.

    Parameters
    ----------
    pdb_id
        4-character PDB code.
    chains
        single string (e.g. "A" or "AB") or iterable of chain IDs.
    out_path
        where to write the filtered PDB file.
    keep_het_resnames
        optional iterable of uppercase residue names to always keep (e.g. ["MSE","SEP"]).
        If None, a small default set commonly used for chain modifications will be used.
    keep_hets_in_chain
        if True, keep HETATM whose chain matches and whose resSeq matches any kept ATOM resSeq.
    """
    if not re.fullmatch(r"[0-9A-Za-z]{4}", pdb_id or ""):
        raise ValueError(f"Invalid PDB ID: {pdb_id!r}")

    # normalize chain input
    if isinstance(chains, (str, bytes)):
        s = str(chains).strip()
        if ("," in s) or (" " in s):
            parts = re.split(r"[,\s]+", s)
            chain_set = {p[0].upper() for p in parts if p}
        else:
            chain_set = {c.upper() for c in s if c.strip()}
    else:
        chain_set = {str(c).strip()[0].upper() for c in chains if str(c).strip()}

    if not chain_set:
        raise ValueError("No chain IDs provided.")

    # default whitelist of common chain-modification hetero residues
    if keep_het_resnames is None:
        keep_het_resnames = {
            "MSE",  # selenomethionine
            "SEC",  # selenocysteine
            "SEP",  # phosphoserine
            "TPO",  # phosphothreonine
            "PTR",  # phosphotyrosine
            "CSO",  # oxidized cysteine variants
            "MLY",  # methyl-lysine variants
            "ASH",  # protonation variants
        }
    keep_het_resnames = {r.upper() for r in keep_het_resnames}

    pdb_id = pdb_id.upper()
    out_path = Path(out_path)

    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    with urllib.request.urlopen(url) as resp:
        pdb_lines = resp.read().decode("latin-1").splitlines(keepends=True)

    header_and_others = []
    conect_lines = []
    filtered_lines = []

    # Keep track of kept serials (ATOM and any HETATM we decide to keep)
    kept_serials: Set[int] = set()
    # Keep track of resSeq numbers (integers) observed for kept ATOMs in requested chains
    kept_resseqs: Set[int] = set()

    # First pass: keep ATOM, TER, collect resSeqs and ATOM serial numbers; buffer HETATM and CONECT
    hetatm_buffer = []  # store HETATM lines for second-pass decision

    for line in pdb_lines:
        rec = line[0:6]
        if rec == "ATOM  ":
            chain = line[21:22].upper() if len(line) > 21 else ""
            if chain in chain_set:
                filtered_lines.append(line)
                # atom serial (columns 7-11)
                try:
                    serial = int(line[6:11].strip())
                    kept_serials.add(serial)
                except Exception:
                    pass
                # resSeq (columns 23-26 -> indices 22:26)
                try:
                    resseq = int(line[22:26].strip())
                    kept_resseqs.add(resseq)
                except Exception:
                    pass
        elif rec == "ANISOU":
            # hold ANISOU for now; will append only if its serial is in kept_serials later
            header_and_others.append(line)
        elif rec == "TER   ":
            chain = line[21:22].upper() if len(line) > 21 else ""
            if chain in chain_set:
                filtered_lines.append(line)
        elif rec == "HETATM":
            hetatm_buffer.append(line)
        elif rec == "CONECT":
            conect_lines.append(line)
        else:
            # preserve header, REMARK, SEQRES, etc.
            header_and_others.append(line)

    # Append preserved header/remarks before coordinates (common convention)
    filtered_lines = header_and_others + filtered_lines

    # Decide which HETATM to keep
    for line in hetatm_buffer:
        # parse chain, resname, resseq, serial
        chain = line[21:22].upper() if len(line) > 21 else ""
        resname = line[17:20].strip().upper() if len(line) > 17 else ""
        try:
            serial = int(line[6:11].strip())
        except Exception:
            serial = None
        try:
            resseq = int(line[22:26].strip())
        except Exception:
            resseq = None

        keep = False
        if chain in chain_set:
            # condition 1: resname is whitelisted
            if resname in keep_het_resnames:
                keep = True
            # condition 2: the het's resSeq matches an ATOM resSeq in the kept chain
            elif (
                keep_hets_in_chain and (resseq is not None) and (resseq in kept_resseqs)
            ):
                keep = True

        if keep:
            filtered_lines.append(line)
            if serial is not None:
                kept_serials.add(serial)

    # Now include ANISOU lines that correspond to kept serials (we preserved them in header_and_others)
    # header_and_others contains ANISOUs and headers; move kept ANISOUs into filtered_lines in original order
    # Preserved header_and_others earlier at top; we need to reintegrate ANISOUs that correspond to kept atoms:
    # To keep original ordering, scan original pdb_lines and append ANISOU for kept serials at that point.
    final_lines = []
    for line in filtered_lines:
        final_lines.append(line)

    # Re-scan original file and insert ANISOU lines for kept serials at their original positions
    # (This preserves relative order of ANISOU vs ATOM/HETATM)
    # build a map of line positions for faster insertion by walking original lines and emitting only those
    emitted = (
        []
    )  # rebuild the whole content by iterating original pdb_lines and emitting only allowed records
    for line in pdb_lines:
        rec = line[0:6]
        if rec == "ATOM  ":
            # emit only if this ATOM serial is in kept_serials
            try:
                serial = int(line[6:11].strip())
            except Exception:
                serial = None
            if serial is not None and serial in kept_serials:
                emitted.append(line)
        elif rec == "ANISOU":
            try:
                serial = int(line[6:11].strip())
            except Exception:
                serial = None
            if serial is not None and serial in kept_serials:
                emitted.append(line)
        elif rec == "HETATM":
            # emit only if its serial is in kept_serials
            try:
                serial = int(line[6:11].strip())
            except Exception:
                serial = None
            if serial is not None and serial in kept_serials:
                emitted.append(line)
        elif rec == "TER   ":
            chain = line[21:22].upper() if len(line) > 21 else ""
            if chain in chain_set:
                emitted.append(line)
        elif rec == "CONECT":
            # postpone CONECT until after knowing all kept_serials
            continue
        else:
            # headers and other non-coordinate records: keep
            emitted.append(line)

    # Process CONECT lines: keep only references to atoms that remain.
    for line in conect_lines:
        parts = line.strip().split()
        if len(parts) <= 1:
            continue
        try:
            serials = [int(p) for p in parts[1:]]
        except ValueError:
            continue
        kept = [s for s in serials if s in kept_serials]
        if not kept:
            continue
        # build a fixed-width CONECT line: 'CONECT' then serials right-justified width 5 each
        new_line = "CONECT" + "".join(f"{s:5d}" for s in kept) + "\n"
        emitted.append(new_line)

    # Ensure trailing newline
    if emitted and not emitted[-1].endswith("\n"):
        emitted[-1] = emitted[-1] + "\n"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="latin-1") as fh:
        fh.writelines(emitted)

    return


THREE_TO_ONE = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLN": "Q",
    "GLU": "E",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
}


def _to_one_letter(resname):
    r = resname.upper()
    return THREE_TO_ONE.get(r, "X")


def log_print(message):
    """Print to both console and log file"""
    print(message)
    logging.info(message)


def _parse_seqres_line(line: str):
    chain = line[11].strip()
    residues = line[19:].strip().split()
    return chain, residues


def _parse_het_line(line: str):
    chain = line[12].strip()
    het_name = line[7:10].strip()
    return chain, het_name


def get_het_names(pdb_id: str) -> dict:
    """
    Get heteroatom names with their associated chains.
    Returns dict where keys are het names and values are sets of chains.
    """
    pdb = pdb_id.strip().lower()
    if len(pdb) > 4:
        pdb = pdb[:4]

    url = f"https://files.rcsb.org/view/{pdb.upper()}.pdb"
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch PDB {pdb} ({r.status_code}) from RCSB.")

    text = r.text.splitlines()
    hets = {}

    for line in text:
        if line.startswith("HET "):
            het_chain, het_name = _parse_het_line(line)
            if het_name not in hets:
                hets[het_name] = set()
            hets[het_name].add(het_chain)

    return hets if hets else {}


# def get_chain_seqres(pdb_id: str, chain: str) -> str:
#     pdb = pdb_id.strip().lower()
#     if len(pdb) > 4:
#         pdb = pdb[:4]
#     # fetch PDB file
#     url = f'https://files.rcsb.org/view/{pdb.upper()}.pdb'
#     r = requests.get(url, timeout=60)
#     if r.status_code != 200:
#         raise RuntimeError(f'Failed to fetch PDB {pdb} ({r.status_code}) from RCSB.')
#     text = r.text.splitlines()

#     residues = []
#     for line in text:
#         if not line.startswith('SEQRES'):
#             continue
#         line_chain, triplets = _parse_seqres_line(line)
#         if line_chain == chain:
#             residues.extend(triplets)


#     if residues:
#         seq = ''.join(_to_one_letter(r) for r in residues)
#         return seq
#     else:
#         return ""
def get_chain_seqres_triplets(pdb_id: str, chain: str) -> str:
    pdb = pdb_id.strip().lower()
    if len(pdb) > 4:
        pdb = pdb[:4]
    # fetch PDB file
    url = f"https://files.rcsb.org/view/{pdb.upper()}.pdb"
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch PDB {pdb} ({r.status_code}) from RCSB.")
    text = r.text.splitlines()

    residues = []
    for line in text:
        if not line.startswith("SEQRES"):
            continue
        line_chain, triplets = _parse_seqres_line(line)
        if line_chain == chain:
            residues.extend(triplets)

    if residues:
        return residues
    else:
        return []


def get_chain_seqres(pdb_id: str, chain: str) -> str:
    triplets = get_chain_seqres_triplets(pdb_id, chain)
    if triplets:
        seq = "".join(_to_one_letter(r) for r in triplets)
        return seq
    else:
        return ""


def canonical_check_seqres(pdb_id: str, chain: str) -> bool:
    pdb = pdb_id.strip().lower()
    if len(pdb) > 4:
        pdb = pdb[:4]
    residues = get_chain_seqres_triplets(pdb, chain)
    for res in residues:
        if res.upper() not in THREE_TO_ONE:
            return False
    return True


def get_all_chainid(pdb_id: str) -> str:
    pdb = pdb_id.strip().lower()
    if len(pdb) > 4:
        pdb = pdb[:4]
    # fetch PDB file
    url = f"https://files.rcsb.org/view/{pdb.upper()}.pdb"
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch PDB {pdb} ({r.status_code}) from RCSB.")
    text = r.text.splitlines()

    chain_ids = set()
    for line in text:
        if line.startswith("ATOM  "):
            chain = line[21].strip()
            if chain:
                chain_ids.add(chain)
    return chain_ids


def extract_pep_chain(pdb_id: str, max_diff: int = 10) -> Optional[str]:
    """
    Return a peptide chain ID from a PDB file.

    Logic:
      - Count unique residues per chain from ATOM records (resseq + iCode).
      - Consider only chains with > 2 unique residues.
      - Let shortest_len = min(lengths of valid chains).
      - Gather chains with length <= shortest_len + max_diff.
      - If multiple chains in that group: choose the one with largest length
        (tie-break by chain ID). Otherwise return the single shortest chain.
    """
    counts = defaultdict(set)  # chain: set of (resseq_str, iCode)
    chains = set()
    chains = list(get_all_chainid(pdb_id))
    try:
        for ch in chains:
            seq = get_chain_seqres(pdb_id, ch)
            # print(f"Chain {ch}: {seq}")
            if seq:
                for i, res in enumerate(seq, start=1):
                    counts[ch].add((i, " "))
    except Exception as e:
        raise RuntimeError(f"Error processing PDB {pdb_id}: {e}") from e

    # valid chains: more than 2 unique residues
    valid = {ch: len(s) for ch, s in counts.items() if len(s) > 2}
    if not valid:
        return None

    # shortest chain length
    shortest_len = min(valid.values())

    # chains within max_diff of shortest
    candidates = {ch: ln for ch, ln in valid.items() if ln <= (shortest_len + max_diff)}

    if not candidates:
        # defensive fallback; should not happen because shortest chain is always in candidates
        return sorted(valid.items(), key=lambda x: (x[1], x[0]))[0][0]

    if len(candidates) == 1:
        # only the shortest chain qualifies
        return next(iter(candidates.keys()))

    # multiple candidates -> pick the most complete (largest observed residue count)
    # tie-break by chain ID for determinism
    selected = sorted(candidates.items(), key=lambda x: (-x[1], x[0]))[0][0]
    return selected


# def process_single_pdb(pdb: str, tmp: str, index: int, total: int, canonical_check: bool = True) -> tuple[Optional[dict], dict, list[str]]:
#     """
#     Process a single PDB ID to extract peptide and receptor chains.
#     Returns a tuple of (result_dict, error_dict, messages) where result_dict contains
#     the successful processing data or None if failed, and messages contains all log messages.
#     """
#     messages = []
#     messages.append(f"Processing {index+1}/{total}: {pdb}")
#     pdb_path = f"{tmp}/{pdb}.pdb"

#     try:
#         # Download PDB file
#         retrieve_pdb(pdb, tmp)
#         if not os.path.isfile(pdb_path):
#             messages.append(f"{pdb} not found")
#             return None, {pdb: "file_not_found"}, messages

#         # Extract peptide chain
#         try:
#             pep_chain = extract_pep_chain(pdb)
#         except ValueError:
#             messages.append(f"Error extracting peptide chain for {pdb}")
#             if os.path.exists(pdb_path):
#                 os.remove(pdb_path)
#             return None, {pdb: "pep_chain"}, messages

#         if not pep_chain:
#             messages.append(f"No peptide chain found for {pdb}")
#             if os.path.exists(pdb_path):
#                 os.remove(pdb_path)
#             return None, {pdb: "no_pep_chain"}, messages

#         # Check peptide length
#         try:
#             length = len(get_chain_seqres(pdb, pep_chain))
#             if length > 50:
#                 messages.append(f"Peptide chain too long ({length}) for {pdb}")
#                 if os.path.exists(pdb_path):
#                     os.remove(pdb_path)
#                 return None, {pdb: "length_too_long"}, messages
#         except ValueError:
#             messages.append(f"Error processing length for {pdb}")
#             if os.path.exists(pdb_path):
#                 os.remove(pdb_path)
#             return None, {pdb: "length"}, messages

#         # Find receptor chains within cutoff
#         try:
#             receptor_chain = chains_within_cutoff(pdb=pdb_path, pep_chain=pep_chain, cutoff=5.0)
#             receptor_chain = ''.join(receptor_chain)
#         except ValueError:
#             messages.append(f"Error processing receptor chain for {pdb}")
#             if os.path.exists(pdb_path):
#                 os.remove(pdb_path)
#             return None, {pdb: "receptor_chain"}, messages

#         if not receptor_chain:
#             messages.append(f"No receptor chain found in {pdb}")
#             if os.path.exists(pdb_path):
#                 os.remove(pdb_path)
#             return None, {pdb: "no_receptor_chain"}, messages

#         # Canonical check
#         if canonical_check:
#             try:
#                 hets = get_het_names(pdb)
#                 if hets:
#                     for het, chains in hets.items():
#                         chains_text = ','.join(sorted(chains))
#                         messages.append(f"Non-canonical residue {het} found in chains {chains_text}, complex {pdb}")
#                     if os.path.exists(pdb_path):
#                         os.remove(pdb_path)
#                     return None, {pdb: "non_canonical"}, messages
#             except ValueError:
#                 messages.append(f"Error during canonical check for {pdb}")
#                 if os.path.exists(pdb_path):
#                     os.remove(pdb_path)
#                 return None, {pdb: "canonical_check"}, messages

#             chains = receptor_chain + pep_chain
#             for chain in chains:
#                 try:
#                     canonical = canonical_check_seqres(pdb, chain)
#                     if not canonical:
#                         messages.append(f"Non-canonical residues found in chain {chain} of {pdb}")
#                         if os.path.exists(pdb_path):
#                             os.remove(pdb_path)
#                         return None, {pdb: "non_canonical"}, messages
#                 except ValueError:
#                     messages.append(f"Error during peptide canonical check for {pdb}")
#                     if os.path.exists(pdb_path):
#                         os.remove(pdb_path)
#                     return None, {pdb: "canonical_check_pep"}, messages

#         # Clean up the PDB file
#         if os.path.exists(pdb_path):
#             os.remove(pdb_path)

#         result = {
#             "pdb_id": pdb,
#             "pep_chain": pep_chain,
#             "receptor_chain": receptor_chain,
#             "length": length
#         }
#         messages.append(f"Successfully processed {pdb}: peptide chain {pep_chain}, receptor chains {receptor_chain}")
#         return result, {}, messages

#     except FileNotFoundError:
#         messages.append(f"PDB entry {pdb} not found at RCSB")
#         if os.path.exists(pdb_path):
#             os.remove(pdb_path)
#         return None, {pdb: "pdb_not_found"}, messages
#     except Exception as e:
#         messages.append(f"Unexpected error processing {pdb}: {e}")
#         if os.path.exists(pdb_path):
#             os.remove(pdb_path)
#         return None, {pdb: f"unexpected_error: {str(e)}"}, messages


def process_single_pdb(
    pdb: str, tmp: str, index: int, total: int, canonical_check: bool = True
) -> tuple[Optional[dict], dict, list[str]]:
    """
    Process a single PDB ID to extract peptide and receptor chains.
    Returns a tuple of (result_dict, error_dict, messages) where result_dict contains
    the successful processing data or None if failed, and messages contains all log messages.
    """
    messages = []
    messages.append(f"Processing {index+1}/{total}: {pdb}")
    pdb_path = f"{tmp}/{pdb}.pdb"

    try:
        # Download PDB file
        retrieve_pdb(pdb, tmp)
        if not os.path.isfile(pdb_path):
            messages.append(f"{pdb} not found")
            return None, {pdb: "file_not_found"}, messages

        # Extract peptide chain
        try:
            pep_chain = extract_pep_chain(pdb)
        except ValueError:
            messages.append(f"Error extracting peptide chain for {pdb}")
            if os.path.exists(pdb_path):
                os.remove(pdb_path)
            return None, {pdb: "pep_chain"}, messages

        if not pep_chain:
            messages.append(f"No peptide chain found for {pdb}")
            if os.path.exists(pdb_path):
                os.remove(pdb_path)
            return None, {pdb: "no_pep_chain"}, messages

        # Check peptide length
        try:
            length = len(get_chain_seqres(pdb, pep_chain))
            if length > 50:
                messages.append(f"Peptide chain too long ({length}) for {pdb}")
                if os.path.exists(pdb_path):
                    os.remove(pdb_path)
                return None, {pdb: "length_too_long"}, messages
        except ValueError:
            messages.append(f"Error processing length for {pdb}")
            if os.path.exists(pdb_path):
                os.remove(pdb_path)
            return None, {pdb: "length"}, messages

        # Find receptor chains within cutoff
        try:
            receptor_chain = chains_within_cutoff(
                pdb=pdb_path, pep_chain=pep_chain, cutoff=5.0
            )
            receptor_chain = "".join(receptor_chain)
        except ValueError:
            messages.append(f"Error processing receptor chain for {pdb}")
            if os.path.exists(pdb_path):
                os.remove(pdb_path)
            return None, {pdb: "receptor_chain"}, messages

        if not receptor_chain:
            messages.append(f"No receptor chain found in {pdb}")
            if os.path.exists(pdb_path):
                os.remove(pdb_path)
            return None, {pdb: "no_receptor_chain"}, messages

        # Check each protein (receptor) chain length - each must be > 50
        try:
            protein_lengths = {}
            for chain in receptor_chain:
                chain_seq = get_chain_seqres(pdb, chain)
                chain_length = len(chain_seq)
                protein_lengths[chain] = chain_length

                if chain_length <= 50:
                    messages.append(
                        f"Protein chain {chain} too short ({chain_length}) for {pdb}"
                    )
                    if os.path.exists(pdb_path):
                        os.remove(pdb_path)
                    return None, {pdb: "protein_chain_too_short"}, messages

        except ValueError:
            messages.append(f"Error processing protein chain lengths for {pdb}")
            if os.path.exists(pdb_path):
                os.remove(pdb_path)
            return None, {pdb: "protein_length"}, messages

        # Canonical check
        if canonical_check:
            try:
                hets = get_het_names(pdb)
                if hets:
                    for het, chains in hets.items():
                        chains_text = ",".join(sorted(chains))
                        messages.append(
                            f"Non-canonical residue {het} found in chains {chains_text}, complex {pdb}"
                        )
                    if os.path.exists(pdb_path):
                        os.remove(pdb_path)
                    return None, {pdb: "non_canonical"}, messages
            except ValueError:
                messages.append(f"Error during canonical check for {pdb}")
                if os.path.exists(pdb_path):
                    os.remove(pdb_path)
                return None, {pdb: "canonical_check"}, messages

            chains = receptor_chain + pep_chain
            for chain in chains:
                try:
                    canonical = canonical_check_seqres(pdb, chain)
                    if not canonical:
                        messages.append(
                            f"Non-canonical residues found in chain {chain} of {pdb}"
                        )
                        if os.path.exists(pdb_path):
                            os.remove(pdb_path)
                        return None, {pdb: "non_canonical"}, messages
                except ValueError:
                    messages.append(f"Error during peptide canonical check for {pdb}")
                    if os.path.exists(pdb_path):
                        os.remove(pdb_path)
                    return None, {pdb: "canonical_check_pep"}, messages

        # Clean up the PDB file
        if os.path.exists(pdb_path):
            os.remove(pdb_path)

        result = {
            "pdb_id": pdb,
            "pep_chain": pep_chain,
            "receptor_chain": receptor_chain,
            "length": length,
            "protein_lengths": protein_lengths,
        }
        messages.append(
            f"Successfully processed {pdb}: peptide chain {pep_chain}, receptor chains {receptor_chain}"
        )
        return result, {}, messages

    except FileNotFoundError:
        messages.append(f"PDB entry {pdb} not found at RCSB")
        if os.path.exists(pdb_path):
            os.remove(pdb_path)
        return None, {pdb: "pdb_not_found"}, messages
    except Exception as e:
        messages.append(f"Unexpected error processing {pdb}: {e}")
        if os.path.exists(pdb_path):
            os.remove(pdb_path)
        return None, {pdb: f"unexpected_error: {str(e)}"}, messages


def process_pdbs(
    rcsb: list[str],
    tmp: str,
    n_jobs: int = 8,
    verbose: int = 10,
    canonical_check: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """
    Process a list of PDB IDs to extract peptide and receptor chains in parallel.

    Args:
        rcsb: List of PDB IDs to process.
        tmp: Temporary directory to store downloaded PDB files. These files will be deleted after processing.
        n_jobs: Number of parallel jobs. -1 uses all available cores.
        verbose: Verbosity level for joblib Parallel.

    Returns:
        A tuple of (DataFrame, error_dict) where DataFrame contains successful results
        and error_dict contains processing errors.
    """
    os.makedirs(tmp, exist_ok=True)

    log_print(
        f"Starting parallel processing of {len(rcsb)} PDB structures with {n_jobs} jobs"
    )
    log_print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Process PDBs in parallel
    jobs = (
        delayed(process_single_pdb)(
            pdb, tmp, i, len(rcsb), canonical_check=canonical_check
        )
        for i, pdb in enumerate(rcsb)
    )
    results = Parallel(n_jobs=n_jobs, verbose=verbose)(jobs)

    # Separate successful results from errors and log all messages
    successful_results = []
    all_errors = {}

    for result, error, messages in results:
        # Log all messages from this worker
        for message in messages:
            log_print(message)

        if result is not None:
            successful_results.append(result)
        all_errors.update(error)

    # Create DataFrame from successful results
    if successful_results:
        df = pd.DataFrame(successful_results)
    else:
        df = pd.DataFrame(columns=["pdb_id", "pep_chain", "receptor_chain", "length"])
    # Log error summary
    if all_errors:
        log_print(f"\nError breakdown:")
        error_counts = {}
        for pdb_id, error_type in all_errors.items():
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        for error_type, count in sorted(error_counts.items()):
            log_print(f"  {error_type}: {count}")
    log_print(
        f"Processing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    return df, all_errors
