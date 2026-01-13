from .config import IndexBasedConfig
from .base import IndexBasedFeature
from .utils import Utils


class PLDDT(IndexBasedFeature):
    def __init__(
        self,
        json,
        peptide_indices,
        protein_interface_indices,
        peptide_interface_indices,
        round_digits,
    ):
        super().__init__(
            json=json,
            peptide_indices=peptide_indices,
            protein_interface_indices=protein_interface_indices,
            peptide_interface_indices=peptide_interface_indices,
            round_digits=round_digits,
        )

    @classmethod
    def from_config(cls, config: IndexBasedConfig):
        return super().from_config(config)

    @staticmethod
    def get_plddt_from_indices(json, indices, round_digits) -> float:
        """
        Return
        -   Mean pLDDT across all residues with given indices.
        """

        plddt_values = json.get("plddt", [])
        # Extract pLDDT values for peptide residues using global indices
        # (1-based to 0-based)
        plddt = [plddt_values[i - 1] for i in indices if 0 < i <= len(plddt_values)]

        if not plddt:
            raise ValueError("No pLDDT values found for given indices")

        return round(Utils._avg(plddt), round_digits)

    @staticmethod
    # Get pLDDT for a chain from B-factor in PDB
    def get_plddt_from_bfactor(pdb, chain: str = "B", round_digits: int = 2) -> float:
        """
        Return the average pLDDT (per-residue) for the peptide chain in a
        ColabFold-generated pdb file.
        -   Mean pLDDT across all residues in 'chain'.
        """
        residue_plddt = {}

        for line in pdb:
            if line.startswith(("ATOM  ", "HETATM")) and line[21].strip() == chain:
                res_seq = Utils._parse_atom(line)[1]
                plddt = Utils._parse_atom(line)[3]
                residue_plldts = residue_plddt.setdefault(res_seq, [])
                residue_plldts.append(plddt)

        if not residue_plddt:
            raise ValueError(f"No atoms found for chain '{chain}'")

        # Average pLDDT per residue, then across residues
        per_residue_avg = [Utils._avg(vals) for vals in residue_plddt.values()]
        return round(Utils._avg(per_residue_avg), round_digits)

    def summary(self):
        """
        Return [mean, median, peptide_plddt, protein_interface_plddt,
          peptide_interface_plddt, interface_plddt]
        """
        self.validate_indices()
        plddt = self.json.get("plddt", [])
        if not plddt:
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        n = len(plddt)
        mean = sum(plddt) / n

        s = sorted(plddt)
        mid = n // 2
        median = s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2.0
        if self.peptide_indices is not None:
            peptide_plddt = self.get_plddt_from_indices(
                self.json, self.peptide_indices, self.round_digits
            )
            peptide_interface_plddt = self.get_plddt_from_indices(
                self.json, self.peptide_interface_indices, self.round_digits
            )
            protein_interface_plddt = self.get_plddt_from_indices(
                self.json, self.protein_interface_indices, self.round_digits
            )
            interface_plddt = (peptide_interface_plddt + protein_interface_plddt) / 2.0

        if self.round_digits is not None:
            mean = Utils._round(mean, self.round_digits)
            median = Utils._round(median, self.round_digits)
            peptide_plddt = Utils._round(peptide_plddt, self.round_digits)
            protein_interface_plddt = Utils._round(
                protein_interface_plddt, self.round_digits
            )
            peptide_interface_plddt = Utils._round(
                peptide_interface_plddt, self.round_digits
            )
            interface_plddt = Utils._round(interface_plddt, self.round_digits)

            return (
                mean,
                median,
                peptide_plddt,
                protein_interface_plddt,
                peptide_interface_plddt,
                interface_plddt,
            )
