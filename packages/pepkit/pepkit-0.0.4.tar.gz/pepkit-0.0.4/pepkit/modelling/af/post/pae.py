from __future__ import annotations

import argparse
from typing import Any, Iterable, List, Optional, Sequence, Tuple

from .base import IndexBasedFeature
from .config import IndexBasedConfig
from .utils import Utils


class PAE(IndexBasedFeature):
    def __init__(
        self,
        json: dict,
        peptide_indices: Sequence[int],
        protein_interface_indices: Sequence[int],
        peptide_interface_indices: Sequence[int],
        interacting_pairs: Sequence[Tuple[int, int]],
        round_digits: Optional[int],
    ) -> None:
        super().__init__(
            json=json,
            peptide_indices=peptide_indices,
            protein_interface_indices=protein_interface_indices,
            peptide_interface_indices=peptide_interface_indices,
            round_digits=round_digits,
        )
        self.interacting_pairs = list(interacting_pairs)

    @classmethod
    def from_config(cls, config: IndexBasedConfig) -> "PAE":
        return super().from_config(config)

    # -----------------------
    # Matrix access helpers
    # -----------------------
    @staticmethod
    def _pae_matrix(json_record: dict) -> List[List[Any]]:
        pae_matrix = json_record.get("pae", [])
        if not pae_matrix:
            raise ValueError("No PAE matrix found in provided JSON data")
        return pae_matrix

    @staticmethod
    def _n_res(pae_matrix: Sequence[Sequence[Any]]) -> int:
        return len(pae_matrix)

    @staticmethod
    def _in_bounds(i: int, n: int) -> bool:
        return 0 < i <= n

    @staticmethod
    def _safe_float(x: Any) -> Optional[float]:
        if x is None:
            return None
        try:
            v = float(x)
        except Exception:
            return None
        if v != v or v in (float("inf"), float("-inf")):
            return None
        return v

    @staticmethod
    def _mean(values: Sequence[float]) -> float:
        if not values:
            raise ValueError("No PAE values found for given indices")
        return sum(values) / len(values)

    @staticmethod
    def _round(v: Optional[float], ndigits: Optional[int]) -> Optional[float]:
        if ndigits is None:
            return v
        return Utils._round(v, ndigits)

    # -----------------------
    # Public computations
    # -----------------------
    @staticmethod
    def get_residue_pae_from_indices(
        indices: Iterable[int],
        json_record: dict,
        round_digits: Optional[int],
    ) -> float:
        """
        Mean PAE across all residues with given indices.
        Uses full rows for each residue i and averages all included values.
        """
        pae_matrix = PAE._pae_matrix(json_record)
        n = PAE._n_res(pae_matrix)

        rows: List[List[Any]] = []
        for i in indices:
            if PAE._in_bounds(i, n):
                rows.append(list(pae_matrix[i - 1]))

        if not rows:
            raise ValueError("No PAE values found for given indices")

        flat: List[float] = []
        for row in rows:
            for x in row:
                v = PAE._safe_float(x)
                if v is not None:
                    flat.append(v)

        mean = PAE._mean(flat)
        return PAE._round(mean, round_digits)  # type: ignore[return-value]

    @staticmethod
    def get_interface_pae_cartesian(
        prot_indices: Iterable[int],
        pep_indices: Iterable[int],
        json_record: dict,
        round_digits: Optional[int],
    ) -> float:
        """
        Mean PAE across all interface residue pairs between protein and peptide chains,
        computed over the Cartesian product prot_indices x pep_indices.
        """
        pae_matrix = PAE._pae_matrix(json_record)
        n = PAE._n_res(pae_matrix)

        vals: List[float] = []
        for i in prot_indices:
            if not PAE._in_bounds(i, n):
                continue
            row = pae_matrix[i - 1]
            for j in pep_indices:
                if not PAE._in_bounds(j, n):
                    continue
                v = PAE._safe_float(row[j - 1])
                if v is not None:
                    vals.append(v)

        mean = PAE._mean(vals)
        return PAE._round(mean, round_digits)  # type: ignore[return-value]

    @staticmethod
    def get_interface_pae_from_index_pairs(
        prot_indices: Iterable[int],
        pep_indices: Iterable[int],
        json_record: dict,
        round_digits: Optional[int],
    ) -> float:
        """
        Mean PAE across explicit residue index pairs.
        Each pair is (prot_indices[k], pep_indices[k]).
        """
        pae_matrix = PAE._pae_matrix(json_record)
        n = PAE._n_res(pae_matrix)

        vals: List[float] = []
        for i, j in zip(prot_indices, pep_indices):
            if not (PAE._in_bounds(i, n) and PAE._in_bounds(j, n)):
                continue
            v = PAE._safe_float(pae_matrix[i - 1][j - 1])
            if v is not None:
                vals.append(v)

        mean = PAE._mean(vals)
        return PAE._round(mean, round_digits)  # type: ignore[return-value]

    # -----------------------
    # Summary (refactored)
    # -----------------------
    def summary(
        self,
    ) -> Tuple[float, Optional[float], float, float, float, Optional[float]]:
        """
        From an NxN PAE matrix.

        Returns:
            (mean_pae, max_pae, peptide_pae, protein_interface_pae,
             peptide_interface_pae, mean_interface_pae)
        """
        self.validate_indices()

        pae = self.json.get("pae", [])
        if not pae:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        flat = self._flatten_pae(pae)
        if not flat:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        mean_pae = sum(flat) / len(flat)
        max_pae = self._safe_float(self.json.get("max_pae", None))

        peptide_pae = self.get_residue_pae_from_indices(
            self.peptide_indices,
            self.json,
            round_digits=self.round_digits,
        )
        protein_interface_pae = self.get_residue_pae_from_indices(
            self.protein_interface_indices,
            self.json,
            round_digits=self.round_digits,
        )
        peptide_interface_pae = self.get_residue_pae_from_indices(
            self.peptide_interface_indices,
            self.json,
            round_digits=self.round_digits,
        )

        mean_interface_pae = self._mean_interface_pae_from_pairs()

        mean_pae = self._round(mean_pae, self.round_digits) or 0.0
        max_pae = self._round(max_pae, self.round_digits)
        mean_interface_pae = self._round(mean_interface_pae, self.round_digits)

        return (
            mean_pae,
            max_pae,
            peptide_pae,
            protein_interface_pae,
            peptide_interface_pae,
            mean_interface_pae,
        )

    @classmethod
    def _flatten_pae(cls, pae: Any) -> List[float]:
        flat: List[float] = []
        for row in pae:
            if not isinstance(row, list):
                continue
            for x in row:
                v = cls._safe_float(x)
                if v is not None:
                    flat.append(v)
        return flat

    def _mean_interface_pae_from_pairs(self) -> Optional[float]:
        if not self.interacting_pairs:
            return None

        prot = [p for p, _ in self.interacting_pairs]
        pep = [q for _, q in self.interacting_pairs]
        # One pass over all pairs (no per-pair function calls)
        return self.get_interface_pae_from_index_pairs(
            prot, pep, self.json, round_digits=None
        )

    # -----------------------
    # CLI
    # -----------------------
    @staticmethod
    def args() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Extract PAE scores from JSON using residue indices"
        )
        parser.add_argument("--input", type=str, required=True, help="Input JSON file")
        parser.add_argument(
            "--indices",
            type=int,
            nargs="+",
            help="Residue indices to average PAE rows for",
        )
        parser.add_argument(
            "--interface",
            nargs="+",
            help=(
                "Interface residue pairs as a flat list: "
                "prot_resi pep_resi prot_resi pep_resi ..."
            ),
        )
        parser.add_argument(
            "--round",
            type=int,
            default=2,
            help="Number of decimals for rounding output",
        )
        return parser


def _pairwise_ints(vals: Sequence[str]) -> List[Tuple[int, int]]:
    ints = list(map(int, vals))
    if len(ints) % 2 != 0:
        raise ValueError(
            "Number of --interface arguments must be even "
            "(pairs of prot_resi pep_resi)."
        )
    return [(ints[i], ints[i + 1]) for i in range(0, len(ints), 2)]


def main() -> None:
    args = PAE.args().parse_args()
    record = Utils.process_json(args.input)

    if args.interface:
        pairs = _pairwise_ints(args.interface)
        prot = [p for p, _ in pairs]
        pep = [q for _, q in pairs]
        mean_val = PAE.get_interface_pae_from_index_pairs(
            prot, pep, record, round_digits=args.round
        )
        print(f"Mean interface PAE: {mean_val}")
        return

    if not args.indices:
        raise ValueError("Provide --indices or --interface")

    mean_val = PAE.get_residue_pae_from_indices(
        args.indices, record, round_digits=args.round
    )
    print(f"Mean PAE for given indices: {mean_val}")


if __name__ == "__main__":
    main()
