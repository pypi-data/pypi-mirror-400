from typing import Literal, Optional


class BaseConfig:
    def __init__(
        self,
        pdb_lines: Optional[list] = None,
        json_path: Optional[str] = None,
        pdb_path: Optional[str] = None,
        cutoff: float = 5.0,
        peptide_chain_position: Literal["last", "first", "none"] = "last",
    ):
        self.pdb_lines = pdb_lines
        self.cutoff = cutoff
        self.peptide_chain_position = peptide_chain_position

    # def validate(self):
    #     assert self.cutoff > 0, "Cutoff must be positive"


class IndexBasedConfig:
    def __init__(
        self,
        json: Optional[dict] = None,
        peptide_indices: Optional[list[int]] = None,
        protein_interface_indices: Optional[list[int]] = None,
        peptide_interface_indices: Optional[list[int]] = None,
        round_digits: int = 3,
    ):
        self.json = json
        self.peptide_indices = peptide_indices
        self.protein_interface_indices = protein_interface_indices
        self.peptide_interface_indices = peptide_interface_indices
        self.round_digits = round_digits
