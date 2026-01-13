import unittest
from pepkit.modelling.af.score.models import (
    PDOCKQ_MODEL,
    PDOCKQ2_MODEL,
    MPDOCKQ_MODEL,
)


class TestSigmoidModels(unittest.TestCase):
    def test_pdockq_model(self):
        x = 287.7600520094613
        expected = 0.7413584356854958
        out = PDOCKQ_MODEL(x)
        self.assertAlmostEqual(out, expected, places=3)

    def test_pdockq2_model(self):
        x = 71.4058
        expected = 0.357431752937616
        out = PDOCKQ2_MODEL(x)
        self.assertAlmostEqual(out, expected, places=3)

    def test_mpdockq_model(self):
        x = 124.9726026999018
        expected = 0.26200001032302317
        out = MPDOCKQ_MODEL(x)
        self.assertAlmostEqual(out, expected, places=3)


if __name__ == "__main__":
    unittest.main()
