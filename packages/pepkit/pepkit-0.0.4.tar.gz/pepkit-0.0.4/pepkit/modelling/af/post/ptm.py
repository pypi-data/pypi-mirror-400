from .base import IndexBasedFeature
from .config import IndexBasedConfig
from .utils import Utils
import argparse


class PTM(IndexBasedFeature):
    def __init__(self, json, peptide_chain, round_digits):
        super().__init__(
            json=json,
            peptide_indices=None,
            protein_interface_indices=None,
            peptide_interface_indices=None,
            round_digits=round_digits,
        )
        self.peptide_chain = peptide_chain

    @classmethod
    def from_config(cls, config: IndexBasedConfig):
        return super().from_config(config)

    @staticmethod
    def get_ptm(json, peptide_chain, round_digits=2):
        """
        Extract pTM and per-chain pTM scores from a JSON record.
        Calculate composite pTM as 0.8*iptm + 0.2*ptm.
        """
        global_iptm = json.get("iptm", None)
        global_ptm = json.get("ptm", None)
        actif_ptm = json.get("actifptm", None)
        per_chain = json.get("per_chain_ptm", {}) or {}
        chain_ids = sorted(per_chain.keys())
        ptm = [global_ptm] + [per_chain[c] for c in chain_ids]
        composite_ptm = (
            0.8 * global_iptm + 0.2 * global_ptm
            if global_iptm is not None and global_ptm is not None
            else None
        )

        if not peptide_chain:
            if round_digits is not None:
                ptm = [Utils._round(v, round_digits) for v in ptm]
                global_iptm = Utils._round(global_iptm, round_digits)
                composite_ptm = Utils._round(composite_ptm, round_digits)
            return ptm, global_iptm, composite_ptm, None, None, None
        else:
            peptide_ptm = (
                per_chain[peptide_chain] if peptide_chain in per_chain else None
            )
            proteins = [per_chain[c] for c in chain_ids if c != peptide_chain]
            protein_ptm = sum(proteins) / len(proteins) if proteins else None

            if round_digits is not None:
                ptm = [Utils._round(v, round_digits) for v in ptm]
                peptide_ptm = Utils._round(peptide_ptm, round_digits)
                protein_ptm = Utils._round(protein_ptm, round_digits)
                global_iptm = Utils._round(global_iptm, round_digits)
                composite_ptm = Utils._round(composite_ptm, round_digits)
                actif_ptm = Utils._round(actif_ptm, round_digits)
            return ptm, global_iptm, composite_ptm, peptide_ptm, protein_ptm, actif_ptm

    def summary(self):
        return self.get_ptm(
            self.json, self.peptide_chain, round_digits=self.round_digits
        )

    @staticmethod
    def args():
        parser = argparse.ArgumentParser(
            description="Extract pTM and per-chain pTM scores from JSON"
        )
        parser.add_argument(
            "--input",
            type=str,
            required=True,
            help="Input JSON file path",
        )
        parser.add_argument(
            "--round-digits",
            type=int,
            default=2,
            help="Number of digits to round the pTM scores to",
        )
        parser.add_argument(
            "--peptide-chain",
            type=str,
            default=None,
            help="Chain ID of the peptide",
        )
        return parser


if __name__ == "__main__":
    args = PTM.args().parse_args()
    record = Utils.process_json(args.input)

    ptm, global_iptm, composite_ptm, peptide_ptm, protein_ptm, actif_ptm = PTM.get_ptm(
        record, peptide_chain=args.peptide_chain, round_digits=args.round_digits
    )
    labels = ["global_ptm"] + [f"chain_{i+1}_ptm" for i in range(len(ptm) - 1)]
    for label, value in zip(labels, ptm):
        print(f"{label}: {value}")
    print(f"global_iptm: {global_iptm}")
    print(f"composite_ptm: {composite_ptm}")
    if args.peptide_chain:
        print(f"peptide_ptm ({args.peptide_chain}): {peptide_ptm}")
        print(f"protein_ptm: {protein_ptm}")
        print(f"actif_ptm: {actif_ptm}")

    # Example usage:
    # python -m pepkit.modelling.af.post.ptm --input data/features/raw/
    # data/examples/7QWV_A_7QWV_B/7QWV_A_7QWV_B_scores_rank_001_alphafold2_multimer_v3_model_3_seed_000.json
    # --round-digits 2
