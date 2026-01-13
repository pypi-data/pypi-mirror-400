"""PeptideDecoder: OOP interface to convert peptide SMILES -> FASTA sequence."""

from __future__ import annotations
from typing import List, Optional, Tuple
from rdkit import Chem
from .utils import find_calpha_indices, order_residues_via_backbone
from .peptide_lib import SidechainLibrary

__all__ = ["PeptideDecoder"]


class PeptideDecoder:
    """Efficient peptide SMILES -> FASTA decoder using side-chain hashing.

    The decoder uses a SidechainLibrary to identify residues by their
    post-cut fragment SMILES around the Cα. The API is fluent:

    >>> dec = PeptideDecoder()
    >>> dec.from_smiles(smi).decode()
    >>> seq = dec.sequence

    :param lib: Optional prebuilt SidechainLibrary. If None, a singleton is
                constructed and reused across instances.
    """

    _lib_singleton: Optional[SidechainLibrary] = None

    def __init__(self, lib: Optional[SidechainLibrary] = None) -> None:
        self._mol: Optional[Chem.Mol] = None
        self._order: List[int] = []
        self._letters: List[str] = []
        if lib is not None:
            self._lib = lib
        else:
            if PeptideDecoder._lib_singleton is None:
                PeptideDecoder._lib_singleton = SidechainLibrary()
            self._lib = PeptideDecoder._lib_singleton

    def __repr__(self) -> str:  # pragma: no cover - trivial
        n = len(self._letters)
        return f"PeptideDecoder(len={n})"

    # ---------- fluent API ----------

    def from_smiles(self, smiles: str, sanitize: bool = True) -> "PeptideDecoder":
        """Load molecule from SMILES.

        :param smiles: Input SMILES string.
        :param sanitize: Whether to sanitize the molecule on load.
        :returns: self
        :raises ValueError: If SMILES cannot be parsed.
        """
        mol = Chem.MolFromSmiles(smiles, sanitize=sanitize)
        if mol is None:
            raise ValueError("Could not parse SMILES.")
        self._mol = mol
        self._order = []
        self._letters = []
        return self

    def decode(self) -> "PeptideDecoder":
        """Perform decoding: order residues and identify each via side-chain key.

        :returns: self
        :raises ValueError: If input is not a standard linear peptide or if a
                            residue cannot be identified.
        """
        if self._mol is None:
            raise ValueError("No molecule loaded. Call from_smiles() first.")
        mol = self._mol

        cas = find_calpha_indices(mol)
        if not cas:
            raise ValueError("No Cα atoms detected; not a standard peptide.")
        order = order_residues_via_backbone(mol, cas)
        letters: List[str] = []
        for ca in order:
            key = self._lib.make_key(mol, ca)
            aa = self._lib.lookup(key)
            if aa is None:
                raise ValueError(f"Unknown residue at Cα {ca} (key={key.smiles!r}).")
            letters.append(aa)

        self._order = order
        self._letters = letters
        return self

    # ---------- properties ----------

    @property
    def sequence(self) -> str:
        """Decoded one-letter sequence.

        :returns: Sequence string.
        :raises ValueError: If decode() hasn't been run yet.
        """
        if not self._letters:
            raise ValueError("Decoder not run. Call decode().")
        return "".join(self._letters)

    @property
    def order(self) -> Tuple[int, ...]:
        """Cα atom indices in N→C order.

        :returns: Tuple of atom indices.
        :raises ValueError: If decode() hasn't been run yet.
        """
        if not self._order:
            raise ValueError("Decoder not run. Call decode().")
        return tuple(self._order)

    @property
    def mol(self) -> Chem.Mol:
        """Loaded RDKit molecule.

        :returns: RDKit Mol instance.
        :raises ValueError: If from_smiles() hasn't been called.
        """
        if self._mol is None:
            raise ValueError("No molecule loaded. Call from_smiles() first.")
        return self._mol

    # ---------- convenience ----------

    def to_fasta(self, header: Optional[str] = None) -> str:
        """Render the decoded sequence in FASTA format.

        :param header: Optional header (without leading '>').
        :returns: FASTA formatted string.
        """
        seq = self.sequence
        hdr = f">{header}\n" if header else ">\n"
        return f"{hdr}{seq}\n"
