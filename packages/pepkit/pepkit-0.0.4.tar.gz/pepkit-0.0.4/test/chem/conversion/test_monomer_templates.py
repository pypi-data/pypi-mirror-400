import unittest

from pepkit.chem.conversion.monomer_templates import (
    canonical_monomer,
    nca_monomer,
    infer_from_aa3,
)


class TestMonomerTemplates(unittest.TestCase):
    def test_canonical_monomer_examples(self):
        # Glycine: no side-chain substituent (simple pattern present)
        g = canonical_monomer("G")
        self.assertIsInstance(g, str)
        self.assertIn("NCC(=O)", g)

        # Alanine: contains the 'C' side-chain embedded in the monomer
        a = canonical_monomer("A")
        self.assertIsInstance(a, str)
        self.assertIn("C)C(=O)", a)

        # Proline: contains a pyrrolidine ring (backbone N present)
        p = canonical_monomer("P")
        self.assertIsInstance(p, str)
        self.assertIn("N1", p)
        self.assertIn("C(=O)", p)

        # D-isomer should produce a different SMILES than L-isomer for non-Pro residues
        a_d = canonical_monomer("A", d_isomer=True)
        self.assertNotEqual(a, a_d)

    def test_nca_monomer_and_errors(self):
        ornb = nca_monomer("Orn")
        self.assertIsInstance(ornb, str)
        self.assertIn("CCCN", ornb)

        with self.assertRaises(ValueError):
            nca_monomer("UnknownNCA")

    def test_infer_from_aa3(self):
        # Known three-letter code should map to canonical monomer prefix
        inferred = infer_from_aa3("Ala")
        self.assertIsNotNone(inferred)
        self.assertEqual(inferred, canonical_monomer("A"))

        # Unknown three-letter code returns None
        self.assertIsNone(infer_from_aa3("Xxx"))


if __name__ == "__main__":
    unittest.main()
