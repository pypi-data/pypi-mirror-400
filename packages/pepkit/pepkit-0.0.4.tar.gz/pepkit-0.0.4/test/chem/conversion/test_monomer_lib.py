import unittest
from rdkit import Chem
from pepkit.chem.conversion.monomer_lib import MonomerLibrary
from pepkit.chem.conversion.monomer_templates import canonical_monomer, R_GROUP


class TestMonomerLibrary(unittest.TestCase):
    def setUp(self):
        self.lib = MonomerLibrary()

    def test_library_builds_and_contains_entries(self):
        # entries built for every key in R_GROUP
        for aa in R_GROUP.keys():
            with self.subTest(aa=aa):
                self.assertIn(aa, self.lib._entries)

    def test_match_each_monomer_iso(self):
        for aa in R_GROUP.keys():
            with self.subTest(aa=aa):
                if aa == "G":
                    self.assertEqual(self.lib.match_rgroup(None), "G")
                    continue
                smi = canonical_monomer(aa)
                probe = Chem.MolFromSmiles(smi)
                self.assertIsNotNone(
                    probe, msg=f"Failed to build probe for {aa}: {smi!r}"
                )
                matched = self.lib.match_rgroup(probe)
                self.assertEqual(
                    matched,
                    aa,
                    msg=f"MonomerLibrary failed to match {aa} (got {matched})",
                )

    def test_match_nonisomeric_probe(self):
        # Remove stereochemistry from each probe and ensure non-iso match still works
        for aa in R_GROUP.keys():
            with self.subTest(noniso=aa):
                if aa == "G":
                    self.assertEqual(self.lib.match_rgroup(None), "G")
                    continue
                probe = Chem.MolFromSmiles(canonical_monomer(aa))
                self.assertIsNotNone(probe)
                probe2 = Chem.Mol(probe)
                Chem.RemoveStereochemistry(probe2)
                matched = self.lib.match_rgroup(probe2)
                self.assertEqual(
                    matched, aa, msg=f"Non-iso probe failed for {aa}: got {matched}"
                )

    def test_unknown_probe_returns_none(self):
        # A clearly non-peptidic probe (benzene) should not match
        benz = Chem.MolFromSmiles("c1ccccc1")
        self.assertIsNotNone(benz)
        self.assertIsNone(self.lib.match_rgroup(benz))


if __name__ == "__main__":
    unittest.main()
