from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .base import BaseFeature
from .config import BaseConfig, IndexBasedConfig
from .indices import IndexCalculator
from .pae import PAE
from .plddt import PLDDT
from .ptm import PTM
from .utils import Utils

_DEFAULT_BASE_CONFIG = BaseConfig()
_DEFAULT_ANALYSIS_CONFIG = IndexBasedConfig()


@dataclass(frozen=True)
class AnalysisInputs:
    json_path: Optional[Path]
    pdb_path: Optional[Path]


@dataclass(frozen=True)
class EntryMeta:
    length: Optional[int]
    processing_time: Optional[float]


class Analysis(BaseFeature):
    """
    High-level feature aggregation for AF(-Multimer) outputs.

    Adds:
      - n_contacts_pdockq: pDockQ-style residue-residue contact count (CB/CA reps, cutoff)
      - mean_ptm_pdockq2: pDockQ2 contact-weighted mean pTM from PAE:
            mean_{contacts} 1/(1+(PAE/d0)^2)
        where contacts are the *same pDockQ contacts* used for n_contacts_pdockq.

    Notes:
      - Interface residues / interacting_pairs are computed via
      IndexCalculator (atom-atom).
      - pDockQ contacts are computed via ContactCounter (CB/CA-only).
    """

    def __init__(
        self,
        json_path: Optional[str],
        pdb_path: Optional[str],
        peptide_chain_position: str,
        distance_cutoff: float,
        round_digits: int,
        *,
        pdockq2_d0: float = 10.0,
        pdockq2_sym_pae: bool = True,
    ) -> None:
        super().__init__(
            pdb_lines=None,
            peptide_chain_position=peptide_chain_position,
            distance_cutoff=distance_cutoff,
        )
        self.json_path = Path(json_path) if json_path else None
        self.pdb_path = Path(pdb_path) if pdb_path else None
        self.round_digits = int(round_digits)

        # pDockQ2 transform parameters
        self.pdockq2_d0 = float(pdockq2_d0)
        self.pdockq2_sym_pae = bool(pdockq2_sym_pae)

    @classmethod
    def from_config(cls, config: Any) -> "Analysis":
        return cls(
            json_path=getattr(config, "json_path", None),
            pdb_path=getattr(config, "pdb_path", None),
            peptide_chain_position=getattr(config, "peptide_chain_position", "last"),
            distance_cutoff=getattr(config, "cutoff", 8.0),
            round_digits=getattr(config, "round_digits", 2),
            pdockq2_d0=getattr(config, "pdockq2_d0", 10.0),
            pdockq2_sym_pae=getattr(config, "pdockq2_sym_pae", True),
        )

    # -----------------------
    # Single-rank analysis
    # -----------------------
    def single_analysis(self) -> Dict[str, Any]:
        if self.json_path is None or self.pdb_path is None:
            raise ValueError("single_analysis requires both json_path and pdb_path")

        rec_json: Dict[str, Any] = Utils.process_json(self.json_path)
        pdb_lines: List[str] = Utils.process_pdb(self.pdb_path)

        (
            peptide_indices,
            peptide_chain,
            protein_interface_indices,
            peptide_interface_indices,
            interacting_pairs,
            protein_chains,
        ) = self._compute_interface_indices(pdb_lines)

        plddt_summary = self._compute_plddt(
            rec_json=rec_json,
            peptide_indices=peptide_indices,
            protein_interface_indices=protein_interface_indices,
            peptide_interface_indices=peptide_interface_indices,
        )
        pae_summary = self._compute_pae(
            rec_json=rec_json,
            peptide_indices=peptide_indices,
            protein_interface_indices=protein_interface_indices,
            peptide_interface_indices=peptide_interface_indices,
            interacting_pairs=interacting_pairs,
        )
        ptm_summary = self._compute_ptm(rec_json=rec_json, peptide_chain=peptide_chain)

        # pDockQ-style contacts (CB/CA) + pDockQ2 mean-ptm-from-PAE over those contacts
        dockq_inputs = self._compute_pdockq_contacts_and_ptm(
            pdb_lines=pdb_lines,
            rec_json=rec_json,
            peptide_chain=peptide_chain,
            protein_chains=protein_chains,
            d0_pae=self.pdockq2_d0,
            sym_pae=self.pdockq2_sym_pae,
        )

        return {
            **plddt_summary,
            **pae_summary,
            **ptm_summary,
            "protein_interface_residues": protein_interface_indices,
            "peptide_interface_residues": peptide_interface_indices,
            # helpful metadata
            "peptide_chain": peptide_chain,
            "protein_chains": protein_chains,
            "n_chains": 1 + len(protein_chains),
            # pDockQ / pDockQ2 inputs
            **dockq_inputs,
        }

    def _compute_interface_indices(
        self, pdb_lines: List[str]
    ) -> Tuple[List[int], str, List[int], List[int], List[Tuple[int, int]], List[str]]:
        peptide_indices, peptide_chain = IndexCalculator.get_peptide_indices(
            pdb_lines, peptide_chain_position=self.peptide_chain_position
        )

        (
            protein_interface_indices,
            peptide_interface_indices,
            protein_chains,
            _,
            interacting_pairs,
        ) = IndexCalculator.get_interface_indices(
            pdb_lines,
            peptide_chain=peptide_chain,
            distance_cutoff=self.distance_cutoff,
        )

        return (
            peptide_indices,
            peptide_chain,
            protein_interface_indices,
            peptide_interface_indices,
            interacting_pairs,
            protein_chains,
        )

    def _compute_plddt(
        self,
        *,
        rec_json: Dict[str, Any],
        peptide_indices: List[int],
        protein_interface_indices: List[int],
        peptide_interface_indices: List[int],
    ) -> Dict[str, Any]:
        plddt_obj = PLDDT(
            rec_json,
            peptide_indices,
            protein_interface_indices,
            peptide_interface_indices,
            round_digits=self.round_digits,
        )
        (
            mean_plddt,
            median_plddt,
            peptide_plddt,
            protein_interface_plddt,
            peptide_interface_plddt,
            interface_plddt,
        ) = plddt_obj.summary()

        return {
            "mean_plddt": mean_plddt,
            "median_plddt": median_plddt,
            "peptide_plddt": peptide_plddt,
            "protein_interface_plddt": protein_interface_plddt,
            "peptide_interface_plddt": peptide_interface_plddt,
            "interface_plddt": interface_plddt,
        }

    def _compute_pae(
        self,
        *,
        rec_json: Dict[str, Any],
        peptide_indices: List[int],
        protein_interface_indices: List[int],
        peptide_interface_indices: List[int],
        interacting_pairs: List[Tuple[int, int]],
    ) -> Dict[str, Any]:
        pae_obj = PAE(
            rec_json,
            peptide_indices=peptide_indices,
            protein_interface_indices=protein_interface_indices,
            peptide_interface_indices=peptide_interface_indices,
            interacting_pairs=interacting_pairs,
            round_digits=self.round_digits,
        )
        (
            mean_pae,
            max_pae,
            peptide_pae,
            protein_interface_pae,
            peptide_interface_pae,
            mean_interface_pae,
        ) = pae_obj.summary()

        return {
            "mean_pae": mean_pae,
            "max_pae": max_pae,
            "peptide_pae": peptide_pae,
            "protein_interface_pae": protein_interface_pae,
            "peptide_interface_pae": peptide_interface_pae,
            "mean_interface_pae": mean_interface_pae,
        }

    def _compute_ptm(
        self, *, rec_json: Dict[str, Any], peptide_chain: str
    ) -> Dict[str, Any]:
        ptm_obj = PTM(
            rec_json, peptide_chain=peptide_chain, round_digits=self.round_digits
        )
        ptm, global_iptm, composite_ptm, peptide_ptm, protein_ptm, actif_ptm = (
            ptm_obj.summary()
        )
        return {
            "ptm": ptm,
            "global_iptm": global_iptm,
            "composite_ptm": composite_ptm,
            "peptide_ptm": peptide_ptm,
            "protein_ptm": protein_ptm,
            "actif_ptm": actif_ptm,
        }

    def _compute_pdockq_contacts_and_ptm(
        self,
        *,
        pdb_lines: List[str],
        rec_json: Dict[str, Any],
        peptide_chain: str,
        protein_chains: List[str],
        d0_pae: float = 10.0,
        sym_pae: bool = True,
    ) -> Dict[str, Any]:
        """
        Compute:
          - n_contacts_pdockq: total pDockQ-style residue contacts (CB/CA reps)
          - mean_ptm_pdockq2: mean_{contacts} 1/(1+(PAE/d0)^2) over the *same* contacts

        Implementation detail:
          - We do peptide-vs-each-protein-chain pairwise via contact_count_pair(...,
          return_global=True)(no merged-protein mode => no warnings and we can align
          with PAE indexing).
        """
        from .contact import ContactCounter  # local import to avoid circular deps

        cc = ContactCounter(
            pdb_lines=pdb_lines,
            peptide_chain_position=self.peptide_chain_position,
            distance_cutoff=self.distance_cutoff,
        )

        # Collect all pDockQ contact pairs in global indices (1-based)
        # so we can index PAE (0-based).
        all_pairs_global: List[Tuple[int, int]] = []
        n_contacts_total = 0

        for prot_chain in protein_chains:
            if prot_chain == peptide_chain:
                continue
            r = cc.contact_count_pair(peptide_chain, prot_chain, return_global=True)
            n_contacts_total += int(r.n_contacts)
            if r.pairs_global:
                all_pairs_global.extend(r.pairs_global)

        # Compute mean_ptm_pdockq2 from JSON PAE
        pae = rec_json.get("pae", None)
        mean_ptm = float("nan")

        if pae is not None and all_pairs_global:
            vals: List[float] = []
            for gi, gj in all_pairs_global:
                i = int(gi) - 1
                j = int(gj) - 1
                try:
                    pae_ij = float(pae[i][j])
                    if sym_pae:
                        pae_ji = float(pae[j][i])
                        pae_use = 0.5 * (pae_ij + pae_ji)
                    else:
                        pae_use = pae_ij
                    vals.append(1.0 / (1.0 + (pae_use / float(d0_pae)) ** 2))
                except Exception:
                    continue
            if vals:
                mean_ptm = float(sum(vals) / len(vals))

        out: Dict[str, Any] = {
            "n_contacts_pdockq": int(n_contacts_total),
            "mean_ptm_pdockq2": (
                round(mean_ptm, self.round_digits) if mean_ptm == mean_ptm else mean_ptm
            ),
        }
        return out

    # -----------------------
    # Entry directory analysis
    # -----------------------
    def all_analysis(self, dir_path: Union[str, Path]) -> Dict[str, Any]:
        """
        For a single entry folder, return {"rank001": {...}, ..., "rank005": {...}}
        Skips ranks with no matching file. If multiple files match, takes the first
        lexicographically.
        """
        entry_dir = Path(dir_path)
        entry_result: Dict[str, Any] = {}

        try:
            meta = self._entry_meta(entry_dir)
            for i in range(1, 6):
                key = f"rank{i:03d}"
                inputs = self._rank_inputs(entry_dir, i)

                if inputs is None:
                    self._warn_missing_rank(entry_dir, i)
                    continue

                try:
                    entry_result[key] = Analysis(
                        json_path=str(inputs.json_path),
                        pdb_path=str(inputs.pdb_path),
                        peptide_chain_position=self.peptide_chain_position,
                        distance_cutoff=self.distance_cutoff,
                        round_digits=self.round_digits,
                        pdockq2_d0=self.pdockq2_d0,
                        pdockq2_sym_pae=self.pdockq2_sym_pae,
                    ).single_analysis()
                except Exception as e:
                    self.log_error(f"Error processing {entry_dir.name} rank {i}: {e}")
                    continue

            entry_result["length"] = meta.length
            entry_result["processing_time"] = meta.processing_time
            return entry_result

        except Exception as e:
            self.log_error(f"Error processing entry {entry_dir.name}: {e}")
            return {}

    def _entry_meta(self, entry_dir: Path) -> EntryMeta:
        length = Utils.get_length(entry_dir)

        log_matches = sorted(entry_dir.glob("*log.txt"))
        process_time = Utils.processing_time(log_matches[0]) if log_matches else None

        return EntryMeta(length=length, processing_time=process_time)

    @staticmethod
    def _rank_inputs(entry_dir: Path, rank_i: int) -> Optional[AnalysisInputs]:
        rank_tag = f"rank_{rank_i:03d}"
        json_matches = sorted(entry_dir.glob(f"*_scores_{rank_tag}_*.json"))
        pdb_matches = sorted(entry_dir.glob(f"*relaxed_{rank_tag}_*.pdb"))

        if not json_matches or not pdb_matches:
            return None
        return AnalysisInputs(json_path=json_matches[0], pdb_path=pdb_matches[0])

    @staticmethod
    def _warn_missing_rank(entry_dir: Path, rank_i: int) -> None:
        print(
            "Warning: No matching PDB or JSON file found for "
            f"{entry_dir.name} rank {rank_i}"
        )

    # -----------------------
    # Batch analysis
    # -----------------------
    def batch_analysis(self, batch_dir: Union[str, Path]) -> Dict[str, Any]:
        """
        For a batch directory, get all directories and return {entry_name: {...}, ...}.
        """
        batch_result: Dict[str, Any] = {}
        batch_path = Path(batch_dir)

        for entry_dir in sorted(batch_path.iterdir()):
            if not entry_dir.is_dir():
                continue

            analysis = Analysis(
                json_path=None,
                pdb_path=None,
                peptide_chain_position=self.peptide_chain_position,
                distance_cutoff=self.distance_cutoff,
                round_digits=self.round_digits,
                pdockq2_d0=self.pdockq2_d0,
                pdockq2_sym_pae=self.pdockq2_sym_pae,
            )
            batch_result[entry_dir.name] = analysis.all_analysis(entry_dir)

        return batch_result

    # -----------------------
    # CLI
    # -----------------------
    @staticmethod
    def args() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Extract summary metrics from JSON and PDB files"
        )
        parser.add_argument("--json", type=str, help="Path to the JSON file")
        parser.add_argument("--pdb", type=str, help="Path to the PDB file")
        parser.add_argument(
            "--chain",
            type=str,
            choices=["last", "first", "none"],
            default=_DEFAULT_BASE_CONFIG.peptide_chain_position,
            help="Which chain to consider as peptide",
        )
        parser.add_argument(
            "--cutoff",
            type=float,
            default=_DEFAULT_BASE_CONFIG.cutoff,
            help="Distance cutoff (Å) for defining interface residues",
        )
        parser.add_argument(
            "--round",
            type=int,
            default=_DEFAULT_ANALYSIS_CONFIG.round_digits,
            help="Number of decimal places to round metrics",
        )
        parser.add_argument(
            "--entry_dir",
            type=str,
            help="Path to the entry directory containing JSON and PDB files",
        )
        parser.add_argument(
            "--batch_dir",
            type=str,
            help="Path to the batch directory containing multiple entry directories",
        )
        # optional knobs for pDockQ2 mean-ptm-from-PAE
        parser.add_argument(
            "--pdockq2_d0",
            type=float,
            default=10.0,
            help="d0 for pDockQ2 PAE->pTM transform: 1/(1+(PAE/d0)^2)",
        )
        parser.add_argument(
            "--pdockq2_sym_pae",
            action="store_true",
            help=(
                "Use symmetric PAE: 0.5*(PAE[i,j]+PAE[j,i])"
                + " when computing mean_ptm_pdockq2"
            ),
        )
        return parser


def _write_json(path: Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4)


def main() -> None:
    args = Analysis.args().parse_args()

    if args.batch_dir:
        analysis = Analysis(
            json_path=None,
            pdb_path=None,
            peptide_chain_position=args.chain,
            distance_cutoff=args.cutoff,
            round_digits=args.round,
            pdockq2_d0=args.pdockq2_d0,
            pdockq2_sym_pae=bool(args.pdockq2_sym_pae),
        )
        result = analysis.batch_analysis(args.batch_dir)
        out_path = Path(args.batch_dir) / "result.json"
        _write_json(out_path, result)
        return

    if args.entry_dir:
        analysis = Analysis(
            json_path=None,
            pdb_path=None,
            peptide_chain_position=args.chain,
            distance_cutoff=args.cutoff,
            round_digits=args.round,
            pdockq2_d0=args.pdockq2_d0,
            pdockq2_sym_pae=bool(args.pdockq2_sym_pae),
        )
        result = analysis.all_analysis(args.entry_dir)
        print(json.dumps(result, indent=4))
        return

    analysis = Analysis(
        json_path=args.json,
        pdb_path=args.pdb,
        peptide_chain_position=args.chain,
        distance_cutoff=args.cutoff,
        round_digits=args.round,
        pdockq2_d0=args.pdockq2_d0,
        pdockq2_sym_pae=bool(args.pdockq2_sym_pae),
    )
    result = analysis.single_analysis()
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
