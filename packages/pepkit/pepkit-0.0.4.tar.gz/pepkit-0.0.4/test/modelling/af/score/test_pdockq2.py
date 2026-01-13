# tests/test_pdockq2_unittest.py
from __future__ import annotations

import unittest
from pathlib import Path

from pepkit.modelling.af.post.analysis import Analysis
from pepkit.modelling.af.score.pdockq2 import PDockQ2

PDB_PATH = Path(
    "data/examples/7QWV_A_7QWV_B/7QWV_A_7QWV_B_relaxed_rank_001_alphafold2"
    + "_multimer_v3_model_3_seed_000.pdb"
)
JSON_PATH = Path(
    "data/examples/7QWV_A_7QWV_B/7QWV_A_7QWV_B_scores_rank_001_alphafold2"
    + "_multimer_v3_model_3_seed_000.json"
)


class TestPDockQ2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PDB_PATH.exists() or not JSON_PATH.exists():
            raise unittest.SkipTest(
                "PDB/JSON example not found; skipping pDockQ2 tests"
            )

        cls.analysis = Analysis(
            json_path=str(JSON_PATH),
            pdb_path=str(PDB_PATH),
            peptide_chain_position="last",
            distance_cutoff=8.0,
            round_digits=2,
        )
        cls.d = cls.analysis.single_analysis()

        cls.expected_score = 0.357431752937616
        cls.expected_mean_ptm = 0.86  # approximate

    def test_pdockq2_compute(self):
        sc2 = PDockQ2()
        out = sc2.compute(self.d)
        # score & x present
        self.assertAlmostEqual(out.score, self.expected_score, places=3)
        # extras should contain mean_ptm key (name depends on implementation)
        mean_ptm = (
            out.extras.get("mean_ptm_pdockq2") or out.extras.get("mean_ptm") or None
        )
        self.assertIsNotNone(mean_ptm, "mean_ptm not found in PDockQ2 extras")
        # approximate numeric check
        self.assertAlmostEqual(float(mean_ptm), self.expected_mean_ptm, places=2)


if __name__ == "__main__":
    unittest.main()
