import unittest
from rdkit import Chem
import pepkit.chem.conversion.conversion as conv
from pepkit.chem.conversion.peptide_lib import AA20
from pepkit.chem.conversion.peptide_decoder import PeptideDecoder


class TestDecoderAndConversion(unittest.TestCase):
    def test_single_residue_roundtrip_all_aa(self):
        for aa in AA20:
            with self.subTest(aa=aa):
                # build SMILES from FASTA and ensure decoder recovers it
                smi = conv.fasta_to_smiles(aa)
                self.assertIsInstance(smi, str)
                self.assertTrue(Chem.MolFromSmiles(smi) is not None)
                seq = conv.smiles_to_fasta(smi, split=True)
                self.assertEqual(seq, aa)

    def test_leu_ile_distinct(self):
        sL = conv.fasta_to_smiles("L")
        sI = conv.fasta_to_smiles("I")
        # Ensure the two SMILES are strings and (very likely) different
        self.assertIsInstance(sL, str)
        self.assertIsInstance(sI, str)
        self.assertNotEqual(sL, sI, "Leu and Ile SMILES unexpectedly identical")

    def test_multi_residue_roundtrips_various_sequences(self):
        sequences = [
            "AATTA",
            "GPG",  # Proline ring
            "MFWYV",  # hydrophobic
            "ACDE",  # acid / cysteine mix
            "K",  # single Lys (redundant but ensures decoder works)
            "GPGGAP",  # multi-Pro+Gly sequence
            "WYR",  # aromatic-heavy
            "".join(AA20),  # full canonical set
        ]
        for seq in sequences:
            with self.subTest(seq=seq):
                smi = conv.fasta_to_smiles(seq)
                self.assertIsInstance(smi, str)
                # default FASTA block contains '>' and ends with seq newline
                fasta_block = conv.smiles_to_fasta(smi)
                self.assertTrue(fasta_block.startswith(">"))
                self.assertTrue(fasta_block.endswith(seq + "\n"))
                # split=True returns raw sequence
                raw = conv.smiles_to_fasta(smi, split=True)
                self.assertEqual(raw, seq)
                # test decoder object properties
                dec = PeptideDecoder().from_smiles(smi).decode()
                self.assertEqual(dec.sequence, seq)
                self.assertEqual(len(dec.order), len(seq))
                self.assertIsNotNone(dec.mol)

    def test_conversion_with_header_and_default(self):
        seq = "WYR"
        smi = conv.fasta_to_smiles(seq)
        header = "pep_test"
        fasta_block = conv.smiles_to_fasta(smi, header=header)
        self.assertEqual(fasta_block, f">{header}\n{seq}\n")
        # default header omitted -> empty header line
        fasta_def = conv.smiles_to_fasta(smi)
        self.assertTrue(fasta_def.startswith(">"))
        self.assertTrue(fasta_def.endswith(seq + "\n"))

    def test_decoder_accepts_single_residue(self):
        seq = "A"
        smi = conv.fasta_to_smiles(seq)
        dec = PeptideDecoder().from_smiles(smi).decode()
        self.assertEqual(dec.sequence, seq)
        self.assertEqual(len(dec.order), 1)

    def test_decoder_rejects_non_peptide(self):
        # Non-peptide SMILES should raise ValueError
        with self.assertRaises(ValueError):
            PeptideDecoder().from_smiles("CCO").decode()

    def test_fasta_to_smiles_invalid(self):
        with self.assertRaises(ValueError):
            conv.fasta_to_smiles("X")  # invalid amino-acid code

    def test_smiles_to_fasta_invalid_smiles(self):
        with self.assertRaises(ValueError):
            conv.smiles_to_fasta("not_a_smiles")

    def test_smiles_to_fasta_non_peptide_rejection_message(self):
        # ensure rejection for non-peptide includes a useful phrase
        with self.assertRaises(ValueError) as cm:
            conv.smiles_to_fasta("CCO")
        msg = str(cm.exception)
        self.assertTrue(
            ("standard peptide" in msg) or ("Cα" in msg) or ("No Cα" in msg)
        )

    def test_conversion_roundtrip_random_long_sequence(self):
        # sanity-check: longer mixture of canonical residues
        seq = "ACDEFGHIKLMNPQRSTVWY" * 2  # length 40
        smi = conv.fasta_to_smiles(seq)
        rec = conv.smiles_to_fasta(smi, split=True)
        self.assertEqual(rec, seq)

    def test_proline_edge_cases(self):
        # sequences with proline in different positions
        cases = ["P", "GP", "PG", "APGDA", "GPPG"]
        for seq in cases:
            with self.subTest(seq=seq):
                smi = conv.fasta_to_smiles(seq)
                self.assertIsInstance(smi, str)
                seq2 = conv.smiles_to_fasta(smi, split=True)
                self.assertEqual(seq2, seq)


if __name__ == "__main__":
    unittest.main()
