import unittest
from rdkit import Chem
from pepkit.chem.conversion.conversion import fasta_to_smiles, smiles_to_fasta


class TestConversions(unittest.TestCase):
    def test_fasta_to_smiles_valid_single_aa(self):
        fasta = "A"
        smiles = fasta_to_smiles(fasta)
        self.assertIsInstance(smiles, str)
        self.assertTrue(smiles)
        mol = Chem.MolFromSmiles(smiles)
        self.assertIsNotNone(mol)
        self.assertEqual(Chem.MolToSmiles(mol, canonical=True), smiles)

    def test_fasta_to_smiles_valid_peptide(self):
        fasta = "ACDE"
        expected = Chem.MolToSmiles(Chem.MolFromFASTA(fasta), canonical=True)
        self.assertEqual(fasta_to_smiles(fasta), expected)

    def test_fasta_to_smiles_invalid_aa(self):
        with self.assertRaises(ValueError) as context:
            fasta_to_smiles("X")
        self.assertIn(
            "Non-canonical residue 'X' found in FASTA", str(context.exception)
        )

    def test_smiles_to_fasta_default_returns_fasta_block(self):
        """Default behavior: returns FASTA block with leading '>' line."""
        fasta = "ACD"
        smiles = Chem.MolToSmiles(Chem.MolFromFASTA(fasta), canonical=True)
        result = smiles_to_fasta(smiles)  # default: split=False
        # default header is empty line (">\nSEQ\n")
        self.assertEqual(result, f">{''}\n{fasta}\n")

    def test_smiles_to_fasta_split_true_returns_raw_sequence(self):
        """When split=True we expect just the raw sequence without FASTA header."""
        fasta = "ACD"
        smiles = Chem.MolToSmiles(Chem.MolFromFASTA(fasta), canonical=True)
        result = smiles_to_fasta(smiles, split=True)
        self.assertEqual(result, fasta)

    def test_smiles_to_fasta_valid_with_header(self):
        fasta = "WYR"
        smiles = Chem.MolToSmiles(Chem.MolFromFASTA(fasta), canonical=True)
        header = "testpep"
        result = smiles_to_fasta(smiles, header=header)
        self.assertEqual(result, f">{header}\n{fasta}\n")

    def test_smiles_to_fasta_invalid_smiles(self):
        with self.assertRaises(ValueError) as context:
            smiles_to_fasta("invalid_smiles")
        self.assertIn("Could not parse SMILES", str(context.exception))

    def test_smiles_to_fasta_non_peptide_smiles_raises(self):
        # Ethanol has no peptide sequence — decoder should reject it
        ethanol = "CCO"
        with self.assertRaises(ValueError) as context:
            smiles_to_fasta(ethanol)
        # Match a stable fragment of the decoder message
        self.assertTrue(
            ("standard peptide" in str(context.exception))
            or ("Cα" in str(context.exception))
            or ("No Cα" in str(context.exception))
        )


if __name__ == "__main__":
    unittest.main()
