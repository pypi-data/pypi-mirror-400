# tests/test_mpdockq_unittest.py
from __future__ import annotations

import unittest
from pathlib import Path

from pepkit.modelling.af.post.analysis import Analysis
from pepkit.modelling.af.score.mpdockq import MPDockQ

PDB_PATH = Path(
    "data/examples/7QWV_A_7QWV_B/7QWV_A_7QWV_B_relaxed_rank_001_alphafold2"
    + "_multimer_v3_model_3_seed_000.pdb"
)
JSON_PATH = Path(
    "data/examples/7QWV_A_7QWV_B/7QWV_A_7QWV_B_scores_rank_001_alphafold2"
    + "_multimer_v3_model_3_seed_000.json"
)


class TestMPDockQ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PDB_PATH.exists() or not JSON_PATH.exists():
            raise unittest.SkipTest(
                "PDB/JSON example not found; skipping mpDockQ tests"
            )

        cls.analysis = Analysis(
            json_path=str(JSON_PATH),
            pdb_path=str(PDB_PATH),
            peptide_chain_position="last",
            distance_cutoff=8.0,
            round_digits=2,
        )
        cls.d = cls.analysis.single_analysis()

        cls.expected_score = 0.26200001032302317
        cls.expected_x = 124.9726026999018

    def test_mpdockq_compute_and_warning(self):
        sc = MPDockQ(warn_if_lt3=True)
        # compute should warn (RuntimeWarning) for 2-chain structures
        with self.assertWarns(RuntimeWarning):
            out = sc.compute(self.d)
        self.assertAlmostEqual(out.score, self.expected_score, places=3)
        self.assertAlmostEqual(out.x, self.expected_x, places=3)


if __name__ == "__main__":
    unittest.main()
