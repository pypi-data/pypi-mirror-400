"""Tests for SidechainLibrary and SidechainKey in pepkit.chem.peptide_lib."""

import unittest
from rdkit import Chem

from pepkit.chem.conversion.peptide_lib import SidechainLibrary, AA20
import pepkit.chem.conversion.utils as utils


class TestSidechainLibrary(unittest.TestCase):
    def setUp(self):
        self.lib = SidechainLibrary()

    def test_library_contains_all_canonical_aas(self):
        # At least 20 keys must be present (one per canonical AA)
        self.assertGreaterEqual(self.lib.size, 20)

    def test_lookup_for_each_aa_using_tripeptides(self):
        # For each canonical amino acid X, build G-X-A and ensure lookup returns X
        for X in AA20:
            tri = Chem.MolFromFASTA("G" + X + "A")
            self.assertIsNotNone(tri, msg=f"Failed to build G{X}A")
            cas = utils.find_calpha_indices(tri)
            order = utils.order_residues_via_backbone(tri, cas)
            x_ca = order[1]
            key = self.lib.make_key(tri, x_ca)
            found = self.lib.lookup(key)
            self.assertEqual(found, X, msg=f"Lookup mismatch for {X}: key={key}")

    def test_make_key_produces_distinct_smiles_for_different_residues(self):
        # Compare two different residues (A vs V)
        tri_A = Chem.MolFromFASTA("GAG")
        tri_V = Chem.MolFromFASTA("GVG")
        cas_A = utils.find_calpha_indices(tri_A)
        cas_V = utils.find_calpha_indices(tri_V)
        order_A = utils.order_residues_via_backbone(tri_A, cas_A)
        order_V = utils.order_residues_via_backbone(tri_V, cas_V)
        keyA = self.lib.make_key(tri_A, order_A[1])
        keyV = self.lib.make_key(tri_V, order_V[1])
        # keys (smiles) should differ for different sidechains
        self.assertNotEqual(keyA.smiles, keyV.smiles)

    def test_glycine_center_lookup(self):
        # Test that glycine center is recognized in sequence G G A (center = G)
        tri = Chem.MolFromFASTA("GGA")
        cas = utils.find_calpha_indices(tri)
        order = utils.order_residues_via_backbone(tri, cas)
        g_ca = order[1]
        key = self.lib.make_key(tri, g_ca)
        # For glycine, lookup should return 'G' (fallback or explicit)
        res = self.lib.lookup(key)
        self.assertEqual(res, "G")


if __name__ == "__main__":
    unittest.main()
