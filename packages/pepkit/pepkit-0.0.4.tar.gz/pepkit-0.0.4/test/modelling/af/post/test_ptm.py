import unittest
import subprocess
import sys
from pathlib import Path

from pepkit.modelling.af.post.ptm import PTM
from pepkit.io.files import read_json


PATH = Path(
    "data/examples/7QWV_A_7QWV_B/"
    "7QWV_A_7QWV_B_scores_rank_001_alphafold2_multimer_v3_model_3_seed_000.json"
)


class TestPTM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PATH.exists():
            raise FileNotFoundError(f"Missing AF2 scores JSON: {PATH}")

        cls.record = read_json(PATH)

    def test_ptm_global_values(self):
        ptm, global_iptm, composite_ptm, peptide_ptm, protein_ptm, actif_ptm = (
            PTM.get_ptm(self.record, peptide_chain=None, round_digits=2)
        )

        expected_global_ptm = round(self.record["ptm"], 2)
        expected_per_chain = [
            round(self.record["per_chain_ptm"][c], 2)
            for c in sorted(self.record["per_chain_ptm"])
        ]

        self.assertEqual(ptm, [expected_global_ptm] + expected_per_chain)

        if "iptm" in self.record:
            self.assertEqual(global_iptm, round(self.record["iptm"], 2))
            self.assertEqual(
                composite_ptm,
                round(
                    0.8 * self.record["iptm"] + 0.2 * self.record["ptm"],
                    2,
                ),
            )

        # No peptide chain → these must be None
        self.assertIsNone(peptide_ptm)
        self.assertIsNone(protein_ptm)
        self.assertIsNone(actif_ptm)

    def test_ptm_with_peptide_chain(self):
        per_chain = self.record["per_chain_ptm"]
        peptide_chain = sorted(per_chain.keys())[0]

        _, _, _, peptide_ptm, protein_ptm, actif_ptm = PTM.get_ptm(
            self.record,
            peptide_chain=peptide_chain,
            round_digits=2,
        )

        expected_peptide = round(per_chain[peptide_chain], 2)
        others = [v for k, v in per_chain.items() if k != peptide_chain]
        expected_protein = round(sum(others) / len(others), 2)

        self.assertEqual(peptide_ptm, expected_peptide)
        self.assertEqual(protein_ptm, expected_protein)

        if "actifptm" in self.record:
            self.assertEqual(actif_ptm, round(self.record["actifptm"], 2))
        else:
            self.assertIsNone(actif_ptm)

    def test_unknown_peptide_chain(self):
        per_chain = self.record["per_chain_ptm"]

        _, _, _, peptide_ptm, protein_ptm, _ = PTM.get_ptm(
            self.record,
            peptide_chain="Z",
            round_digits=2,
        )

        self.assertIsNone(peptide_ptm)
        self.assertEqual(
            protein_ptm,
            round(sum(per_chain.values()) / len(per_chain), 2),
        )

    def test_ptm_cli_output(self):
        cmd = [
            sys.executable,
            "-m",
            "pepkit.modelling.af.post.ptm",
            "--input",
            str(PATH),
            "--round-digits",
            "2",
        ]

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        parsed = {}
        for line in proc.stdout.strip().splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            parsed[key.strip()] = float(value.strip())

        expected = {
            "global_ptm": round(self.record["ptm"], 2),
            "global_iptm": round(self.record["iptm"], 2),
            "composite_ptm": round(
                0.8 * self.record["iptm"] + 0.2 * self.record["ptm"], 2
            ),
        }

        # Assertions
        for k, v in expected.items():
            self.assertIn(k, parsed)
            self.assertEqual(parsed[k], v)


if __name__ == "__main__":
    unittest.main()
