import json
import abc
from .config import BaseConfig, IndexBasedConfig


class BaseFeature:
    def __init__(self, pdb_lines, peptide_chain_position, distance_cutoff):
        self.pdb_lines = pdb_lines
        self.peptide_chain_position = peptide_chain_position
        self.distance_cutoff = distance_cutoff

    @classmethod
    def from_config(cls, config: BaseConfig):
        return cls(
            pdb_lines=config.pdb_lines,
            peptide_chain_position=config.peptide_chain_position,
            distance_cutoff=config.cutoff,
        )

    def validate(self):
        if not self.pdb_lines:
            raise ValueError("PDB data must be provided.")

    def log_warning(self, message):
        print(f"Warning: {message}")

    def log_error(self, message):
        print(f"Error: {message}")


class IndexBasedFeature(abc.ABC):
    def __init__(
        self,
        json: json,
        peptide_indices,
        protein_interface_indices,
        peptide_interface_indices,
        round_digits,
    ):
        self.json = json
        self.peptide_indices = peptide_indices
        self.protein_interface_indices = protein_interface_indices
        self.peptide_interface_indices = peptide_interface_indices
        self.round_digits = round_digits

    @classmethod
    def from_config(cls, config: IndexBasedConfig):
        return cls(
            json=config.json,
            peptide_indices=config.peptide_indices,
            protein_interface_indices=config.protein_interface_indices,
            peptide_interface_indices=config.peptide_interface_indices,
            round_digits=config.round_digits,
        )

    def log_warning(self, message):
        print(f"Warning: {message}")

    def log_error(self, message):
        print(f"Error: {message}")

    def validate_indices(self):
        if not self.peptide_indices:
            self.log_warning("No peptide indices provided.")
        if not self.protein_interface_indices:
            self.log_warning("No protein interface indices provided.")
        if not self.peptide_interface_indices:
            self.log_warning("No peptide interface indices provided.")

    @abc.abstractmethod
    def summary(self):
        pass
