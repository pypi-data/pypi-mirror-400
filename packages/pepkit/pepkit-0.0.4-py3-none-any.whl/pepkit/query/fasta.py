import pandas as pd
from rcsbapi.data import DataQuery as Query
import requests, re
from typing import List, Tuple, Any, Callable
from joblib import Parallel, delayed

_letter_only = re.compile(r"[^A-Za-z]")


def _api(pdb_id: str, chain: str) -> str:
    """Return FASTA for one chain via RCSB Data-API; raise if not present."""
    instance = f"{pdb_id.upper()}.{chain.upper()}"
    q = Query(
        input_type="polymer_entity_instances",
        input_ids=[instance],
        return_data_list=[
            "polymer_entity.entity_poly.pdbx_seq_one_letter_code_can",
        ],
        add_rcsb_id=False,
    )
    hit = q.exec()["data"]["polymer_entity_instances"]
    if not hit:
        raise RuntimeError("chain missing in API")

    seq = _letter_only.sub(
        "", hit[0]["polymer_entity"]["entity_poly"]["pdbx_seq_one_letter_code_can"]
    )
    return f">{instance}\n{seq}\n"


def _fasta_parse(pdb_id: str, chain: str) -> str:
    """Parse whole-entry FASTA and keep block with [auth X] header tag."""
    url = f"https://www.rcsb.org/fasta/entry/{pdb_id.lower()}"
    fasta = requests.get(url, timeout=10).text
    tag = f"[auth {chain.upper()}]"

    for block in fasta.strip().split(">")[1:]:
        header, *seq_lines = block.splitlines()
        if tag in header:
            seq = _letter_only.sub("", "".join(seq_lines))
            return f">{pdb_id.upper()}.auth{chain}\n{seq}\n"

    raise RuntimeError("no header containing [auth …] for requested chain")


def get_chain_fasta(pdb_id: str, chain: str) -> str:
    """Return FASTA (header + cleaned sequence) for a single chain."""
    try:
        return _fasta_parse(pdb_id, chain)
    except Exception:
        return _api(pdb_id, chain)


def fetch_one(
    pdb_id: str,
    pep_chain: str,
    receptor_chain: str,
    get_chain_fasta: Callable[[str, str], str],
    use_both_chains: bool = False,
) -> Tuple[str, bool, Any]:
    chains = (pep_chain + receptor_chain) if use_both_chains else receptor_chain
    collected: List[str] = []
    for ch in chains:
        try:
            fasta = get_chain_fasta(pdb_id, ch)
            collected.append(fasta)
        except (RuntimeError, requests.RequestException) as e:
            return (pdb_id, False, str(e))
    return (pdb_id, True, collected)


def parallel_fetch_fastas(
    pdb_ids: List[str],
    pep_chains: List[str],
    receptor_chains: List[str],
    fa_train: str,
    error_train: str,
    get_chain_fasta: Callable[[str, str], str],
    n_jobs: int = 4,
    verbose: int = 10,
    use_both_chains: bool = False,
) -> List[Tuple[str, bool, Any]]:
    jobs = (
        delayed(fetch_one)(pid, pep, rec, get_chain_fasta, use_both_chains)
        for pid, pep, rec in zip(pdb_ids, pep_chains, receptor_chains)
    )
    results = Parallel(n_jobs=n_jobs, verbose=verbose)(jobs)

    error_pdbs: List[str] = []
    with open(fa_train, "a") as out_f:
        for pdb_id, success, payload in results:
            if success:
                for fasta in payload:
                    out_f.write(fasta)
                print(f"Successfully wrote all chains for {pdb_id}")
            else:
                error_pdbs.append(pdb_id)
                print(f"[skip] {pdb_id} → {payload}")

    if error_pdbs:
        with open(error_train, "w") as err_f:
            for pid in error_pdbs:
                err_f.write(f"{pid}\n")
        print(f"Logged {len(error_pdbs)} error PDB IDs to {error_train}")

    return results


def parse_fasta(fasta_file):
    """Parse FASTA file and return dictionary with header as key and sequence as value"""
    sequences = {}
    with open(fasta_file, "r") as f:
        header = None
        sequence = []
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    sequences[header] = "".join(sequence)
                header = line[1:]  # Remove '>' character
                sequence = []
            else:
                sequence.append(line)

        if header:
            sequences[header] = "".join(sequence)
    return sequences
