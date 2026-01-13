import unittest
from pathlib import Path

from pepkit.modelling.af.post.contact import ContactCounter
from pepkit.modelling.af.post.utils import Utils


PDB_PATH = Path(
    "data/examples/7QWV_A_7QWV_B/7QWV_A_7QWV_B_relaxed_rank_001_alphafold2"
    + "_multimer_v3_model_3_seed_000.pdb"
)
JSON_PATH = Path(
    "data/examples/7QWV_A_7QWV_B/7QWV_A_7QWV_B_scores_rank_001_alphafold2"
    + "_multimer_v3_model_3_seed_000.json"
)


class TestContactCounter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PDB_PATH.exists():
            raise unittest.SkipTest(f"PDB not found at {PDB_PATH}; skipping tests")
        cls.pdb_path = PDB_PATH
        cls.pdb_lines = Utils.process_pdb(str(cls.pdb_path))
        cls.cc = ContactCounter(pdb_lines=cls.pdb_lines, distance_cutoff=8.0)

        # expected values (from your example)
        cls.expected_n_contacts = 32
        cls.expected_iface_a = 18
        cls.expected_iface_b = 10
        cls.expected_first10_pairs = [
            (("A", 17), ("B", 7)),
            (("A", 38), ("B", 3)),
            (("A", 40), ("B", 14)),
            (("A", 84), ("B", 4)),
            (("A", 86), ("B", 8)),
            (("A", 86), ("B", 11)),
            (("A", 88), ("B", 8)),
            (("A", 88), ("B", 11)),
            (("A", 88), ("B", 12)),
            (("A", 88), ("B", 15)),
        ]
        cls.expected_first10_global = [
            (17, 155),
            (38, 151),
            (40, 162),
            (84, 152),
            (86, 156),
            (86, 159),
            (88, 156),
            (88, 159),
            (88, 160),
            (88, 163),
        ]

    def test_contact_count_pair_matches_expected(self):
        res = self.cc.contact_count_pair("A", "B", return_global=True, use_grid=True)
        self.assertEqual(res.n_contacts, self.expected_n_contacts)
        self.assertEqual(len(res.interface_a), self.expected_iface_a)
        self.assertEqual(len(res.interface_b), self.expected_iface_b)
        self.assertGreaterEqual(len(res.pairs), 10)
        self.assertEqual(res.pairs[:10], self.expected_first10_pairs)
        self.assertIsNotNone(res.pairs_global)
        self.assertGreaterEqual(len(res.pairs_global), 10)
        self.assertEqual(res.pairs_global[:10], self.expected_first10_global)

    def test_grid_equals_naive(self):
        r_grid = self.cc.contact_count_pair(
            "A", "B", return_global=False, use_grid=True
        )
        r_naive = self.cc.contact_count_pair(
            "A", "B", return_global=False, use_grid=False
        )
        self.assertEqual(r_grid.n_contacts, r_naive.n_contacts)
        self.assertEqual(set(r_grid.pairs), set(r_naive.pairs))
        self.assertEqual(set(r_grid.interface_a), set(r_naive.interface_a))
        self.assertEqual(set(r_grid.interface_b), set(r_naive.interface_b))


if __name__ == "__main__":
    unittest.main()
