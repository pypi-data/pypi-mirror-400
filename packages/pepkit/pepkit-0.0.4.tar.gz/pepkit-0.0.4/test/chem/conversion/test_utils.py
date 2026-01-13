"""Tests for pepkit.chem.utils helpers."""

import unittest
from rdkit import Chem

import pepkit.chem.conversion.utils as utils


class TestUtilsModule(unittest.TestCase):
    def test_is_carbonyl_carbon_basic(self):
        m = Chem.MolFromSmiles("NC(=O)C")
        self.assertIsNotNone(m)
        carb_atoms = [a for a in m.GetAtoms() if utils.is_carbonyl_carbon(a)]
        self.assertTrue(len(carb_atoms) >= 1)
        # pick a carbon that is not carbonyl (there is at least one)
        non_carbonyl = [
            a
            for a in m.GetAtoms()
            if a.GetAtomicNum() == 6 and not utils.is_carbonyl_carbon(a)
        ]
        self.assertTrue(len(non_carbonyl) >= 1)
        self.assertFalse(utils.is_carbonyl_carbon(non_carbonyl[0]))

    def test_find_calpha_and_order_simple_peptide(self):
        seq = "ACDE"
        m = Chem.MolFromFASTA(seq)
        self.assertIsNotNone(m)
        cas = utils.find_calpha_indices(m)
        # one Cα per residue
        self.assertEqual(len(cas), len(seq))
        order = utils.order_residues_via_backbone(m, cas)
        # should include same atoms once
        self.assertEqual(len(order), len(cas))
        self.assertEqual(set(order), set(cas))
        self.assertEqual(len(order), len(set(order)))

    def test_order_with_empty_calphas_returns_empty_list(self):
        # For an empty calphas input, function returns empty list (robust behavior)
        m = Chem.MolFromSmiles("CCO")
        self.assertEqual(utils.order_residues_via_backbone(m, []), [])

    def test_order_raises_on_disconnected_components(self):
        # Combine two peptide molecules into a single RDKit Mol (disconnected).
        m1 = Chem.MolFromFASTA("GGG")
        m2 = Chem.MolFromFASTA("GGG")
        combo = Chem.CombineMols(m1, m2)
        cas = utils.find_calpha_indices(combo)
        # There will be calphas from two separate chains -> no unique start -> raise
        with self.assertRaises(ValueError):
            utils.order_residues_via_backbone(combo, cas)


if __name__ == "__main__":
    unittest.main()
