from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable, List, Literal, Sequence, Set, Tuple

from .base import BaseFeature
from .utils import Utils


@dataclass(frozen=True)
class ParsedAtom:
    chain: str
    res_seq: int
    xyz: Tuple[float, float, float]


GlobalKey = Tuple[str, int]


class IndexCalculator(BaseFeature):
    # -----------------------
    # Public API
    # -----------------------
    @staticmethod
    def get_peptide_indices(
        pdb_lines: List[str],
        peptide_chain_position: Literal["last", "first", "none"] = "last",
    ) -> Tuple[List[int], str]:
        """
        Return (global residue indices, peptide_chain).

        Global indexing is created by concatenating residues from chains in the
        order they appear in the PDB (first appearance order for each chain).
        """
        chains_order, per_chain_res_list = IndexCalculator._collect_chain_residues(
            pdb_lines
        )
        if not chains_order:
            raise ValueError("No chains found in provided PDB lines")

        peptide_chain = IndexCalculator._select_peptide_chain(
            pdb_lines=pdb_lines,
            chains_order=chains_order,
            peptide_chain_position=peptide_chain_position,
        )

        global_map = IndexCalculator._build_global_residue_map(
            chains_order=chains_order,
            per_chain_res_list=per_chain_res_list,
        )

        peptide_residues = per_chain_res_list.get(peptide_chain, [])
        peptide_global_indices = [
            global_map[(peptide_chain, res)] for res in peptide_residues
        ]
        return peptide_global_indices, peptide_chain

    @staticmethod
    def get_interface_indices(
        pdb_lines: List[str],
        peptide_chain: str,
        distance_cutoff: float = 5.0,
    ) -> Tuple[List[int], List[int], List[str], str, List[Tuple[int, int]]]:
        """
        Compute protein/peptide interface residue indices (global, 1-based) and
        interacting residue pairs (protein_global_idx, peptide_global_idx).
        """
        atoms, chains_order, per_chain_res_list = (
            IndexCalculator._collect_atoms_and_res(pdb_lines)
        )
        if not chains_order:
            raise ValueError("No chains found")

        global_map = IndexCalculator._build_global_residue_map(
            chains_order=chains_order,
            per_chain_res_list=per_chain_res_list,
        )

        protein_chains = [c for c in chains_order if c != peptide_chain]
        if not protein_chains:
            raise ValueError("No protein chains found")

        protein_atoms, peptide_atoms = IndexCalculator._split_atoms_by_role(
            atoms=atoms,
            peptide_chain=peptide_chain,
            protein_chains=protein_chains,
        )
        if not protein_atoms or not peptide_atoms:
            raise ValueError(
                "Could not find both protein and peptide chains in the PDB"
            )

        prot_keys, pep_keys, pairs = IndexCalculator._compute_interface_sets(
            protein_atoms=protein_atoms,
            peptide_atoms=peptide_atoms,
            global_map=global_map,
            distance_cutoff=distance_cutoff,
        )

        protein_indices = sorted(global_map[k] for k in prot_keys)
        peptide_indices = sorted(global_map[k] for k in pep_keys)
        interacting_pairs = sorted(pairs)

        return (
            protein_indices,
            peptide_indices,
            protein_chains,
            peptide_chain,
            interacting_pairs,
        )

    # -----------------------
    # CLI
    # -----------------------
    @staticmethod
    def args() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Extract peptide and interface residue indices from PDB"
        )
        parser.add_argument("--input", type=str, help="Path to the PDB file")
        parser.add_argument(
            "--chain",
            type=str,
            choices=["last", "first", "none"],
            default="last",
            help="Which chain to consider as peptide",
        )
        parser.add_argument(
            "--cutoff",
            type=float,
            default=8.0,
            help="Distance cutoff (Å) for defining interface residues",
        )
        return parser

    # -----------------------
    # Parsing helpers
    # -----------------------
    @staticmethod
    def _iter_parsed_atoms(pdb_lines: Sequence[str]) -> Iterable[ParsedAtom]:
        for line in pdb_lines:
            if not line.startswith(("ATOM  ", "HETATM")) or len(line) <= 21:
                continue
            try:
                chain, res_seq, xyz, _ = Utils._parse_atom(line)
            except Exception:
                continue
            yield ParsedAtom(chain=chain, res_seq=res_seq, xyz=xyz)

    @staticmethod
    def _collect_chain_residues(
        pdb_lines: Sequence[str],
    ) -> Tuple[List[str], dict[str, List[int]]]:
        chains_order: List[str] = []
        per_chain_res_list: dict[str, List[int]] = {}
        per_chain_seen: dict[str, Set[int]] = {}

        for a in IndexCalculator._iter_parsed_atoms(pdb_lines):
            if a.chain not in per_chain_res_list:
                chains_order.append(a.chain)
                per_chain_res_list[a.chain] = []
                per_chain_seen[a.chain] = set()

            if a.res_seq not in per_chain_seen[a.chain]:
                per_chain_res_list[a.chain].append(a.res_seq)
                per_chain_seen[a.chain].add(a.res_seq)

        return chains_order, per_chain_res_list

    @staticmethod
    def _collect_atoms_and_res(
        pdb_lines: Sequence[str],
    ) -> Tuple[List[ParsedAtom], List[str], dict[str, List[int]]]:
        atoms: List[ParsedAtom] = []
        chains_order: List[str] = []
        per_chain_res_list: dict[str, List[int]] = {}
        per_chain_seen: dict[str, Set[int]] = {}

        for a in IndexCalculator._iter_parsed_atoms(pdb_lines):
            atoms.append(a)

            if a.chain not in per_chain_res_list:
                chains_order.append(a.chain)
                per_chain_res_list[a.chain] = []
                per_chain_seen[a.chain] = set()

            if a.res_seq not in per_chain_seen[a.chain]:
                per_chain_res_list[a.chain].append(a.res_seq)
                per_chain_seen[a.chain].add(a.res_seq)

        return atoms, chains_order, per_chain_res_list

    @staticmethod
    def _select_peptide_chain(
        *,
        pdb_lines: Sequence[str],
        chains_order: Sequence[str],
        peptide_chain_position: Literal["last", "first", "none"],
    ) -> str:
        if peptide_chain_position == "last":
            return sorted(chains_order)[-1]
        if peptide_chain_position == "first":
            return sorted(chains_order)[0]
        if peptide_chain_position == "none":
            return Utils._extract_pep_chain(list(pdb_lines))
        raise ValueError(f"Unknown peptide_chain value: {peptide_chain_position}")

    @staticmethod
    def _build_global_residue_map(
        *,
        chains_order: Sequence[str],
        per_chain_res_list: dict[str, Sequence[int]],
    ) -> dict[GlobalKey, int]:
        global_map: dict[GlobalKey, int] = {}
        global_index = 1
        for chain in chains_order:
            for res in per_chain_res_list.get(chain, []):
                global_map[(chain, int(res))] = global_index
                global_index += 1
        return global_map

    # -----------------------
    # Interface helpers
    # -----------------------
    @staticmethod
    def _split_atoms_by_role(
        *,
        atoms: Sequence[ParsedAtom],
        peptide_chain: str,
        protein_chains: Sequence[str],
    ) -> Tuple[List[ParsedAtom], List[ParsedAtom]]:
        protein_set = set(protein_chains)
        protein_atoms = [a for a in atoms if a.chain in protein_set]
        peptide_atoms = [a for a in atoms if a.chain == peptide_chain]
        return protein_atoms, peptide_atoms

    @staticmethod
    def _within_cutoff2(
        a: Tuple[float, float, float],
        b: Tuple[float, float, float],
        d2_cut: float,
    ) -> bool:
        xa, ya, za = a
        xb, yb, zb = b
        return (xa - xb) ** 2 + (ya - yb) ** 2 + (za - zb) ** 2 <= d2_cut

    @staticmethod
    def _compute_interface_sets(
        *,
        protein_atoms: Sequence[ParsedAtom],
        peptide_atoms: Sequence[ParsedAtom],
        global_map: dict[GlobalKey, int],
        distance_cutoff: float,
    ) -> Tuple[Set[GlobalKey], Set[GlobalKey], Set[Tuple[int, int]]]:
        d2_cut = float(distance_cutoff) ** 2

        prot_if_res: Set[GlobalKey] = set()
        pep_if_res: Set[GlobalKey] = set()
        pairs: Set[Tuple[int, int]] = set()

        for pep in peptide_atoms:
            pep_key = (pep.chain, pep.res_seq)
            for prot in protein_atoms:
                if not IndexCalculator._within_cutoff2(prot.xyz, pep.xyz, d2_cut):
                    continue

                prot_key = (prot.chain, prot.res_seq)
                prot_if_res.add(prot_key)
                pep_if_res.add(pep_key)

                pairs.add((global_map[prot_key], global_map[pep_key]))

        return prot_if_res, pep_if_res, pairs


def main() -> None:
    parser = IndexCalculator.args()
    args = parser.parse_args()

    pdb_lines = Utils.process_pdb(args.input)

    peptide_indices, peptide_chain = IndexCalculator.get_peptide_indices(
        pdb_lines, peptide_chain_position=args.chain
    )
    print(f"Peptide chain: {peptide_chain}")
    print(f"Peptide residue global indices: {peptide_indices}")

    (
        protein_indices,
        pep_indices,
        protein_chains,
        pep_chain,
        interacting_pairs,
    ) = IndexCalculator.get_interface_indices(
        pdb_lines, peptide_chain=peptide_chain, distance_cutoff=args.cutoff
    )

    print(f"Protein chains: {protein_chains}")
    print(f"Protein interface residue global indices: {protein_indices}")
    print(f"Peptide interface residue global indices: {pep_indices}")
    print(
        "Interacting residue pairs (protein_index, peptide_index): "
        f"{interacting_pairs}"
    )


if __name__ == "__main__":
    main()
