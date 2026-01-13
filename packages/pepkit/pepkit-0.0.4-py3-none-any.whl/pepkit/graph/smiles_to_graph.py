from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import AllChem
import networkx as nx

from pepkit.io.logging import setup_logging
from .mol_to_graph import MolToGraph

logger = setup_logging()


class SMILES2GraphError(Exception):
    """Raised when SMILES -> RDKit Mol -> Graph conversion fails."""


class SMILES2Graph:
    """Wrapper converting SMILES strings to NetworkX graphs via MolToGraph.

    By default this class instantiates the MolToGraph implemented in
    `mol_to_graph.py`. You can pass an alternative helper via the `mol_to_graph`
    constructor argument.
    """

    def __init__(self, mol_to_graph: Optional[MolToGraph] = None):
        self.mtg = mol_to_graph or MolToGraph()

    @staticmethod
    def _safe_mol_from_smiles(
        smiles: str, sanitize: bool = True, kekulize: bool = False
    ) -> Chem.Mol:
        if not isinstance(smiles, str) or not smiles:
            raise SMILES2GraphError("Empty or non-string SMILES provided")

        mol = None
        try:
            mol = Chem.MolFromSmiles(smiles, sanitize=sanitize)
        except Exception:
            logger.debug("RDKit parse with sanitize failed, trying fallback")

        if mol is None:
            mol = Chem.MolFromSmiles(smiles, sanitize=False)
            if mol is None:
                raise SMILES2GraphError(f"RDKit failed to parse SMILES: {smiles!r}")
            try:
                Chem.SanitizeMol(mol)
            except Exception as e:
                raise SMILES2GraphError(f"Failed to sanitize SMILES {smiles!r}: {e}")

        if kekulize:
            try:
                Chem.Kekulize(mol, clearAromaticFlags=True)
            except Exception:
                logger.debug(
                    "Kekulize failed for %r — continuing without kekulize", smiles
                )

        return mol

    @staticmethod
    def _maybe_add_hs(mol: Chem.Mol, explicit: bool) -> Chem.Mol:
        return Chem.AddHs(mol) if explicit else mol

    @staticmethod
    def _maybe_compute_gasteiger(mol: Chem.Mol, compute: bool) -> None:
        if not compute:
            return
        try:
            AllChem.ComputeGasteigerCharges(mol)
        except Exception as e:
            logger.warning("Gasteiger charge computation failed: %s", e)

    @staticmethod
    def _assign_index_atom_map(mol: Chem.Mol, start: int = 1) -> None:
        for atom in mol.GetAtoms():
            atom.SetAtomMapNum(atom.GetIdx() + start)

    @staticmethod
    def _has_atom_map(mol: Chem.Mol) -> bool:
        return any(atom.GetAtomMapNum() != 0 for atom in mol.GetAtoms())

    def smiles_to_mol(
        self,
        smiles: str,
        *,
        sanitize: bool = True,
        kekulize: bool = False,
        explicit_h: bool = False,
        compute_charges: bool = False,
    ) -> Chem.Mol:
        mol = self._safe_mol_from_smiles(smiles, sanitize=sanitize, kekulize=kekulize)
        mol = self._maybe_add_hs(mol, explicit_h)
        self._maybe_compute_gasteiger(mol, compute_charges)
        return mol

    def mol_to_graph(
        self,
        mol: Chem.Mol,
        *,
        prefer_atom_map: bool = True,
        assign_index_map: bool = False,
        drop_non_aam: bool = False,
        light_weight: bool = False,
        node_attrs: Optional[List[str]] = None,
        edge_attrs: Optional[List[str]] = None,
    ) -> Tuple[nx.Graph, Chem.Mol]:
        if assign_index_map and not self._has_atom_map(mol):
            self._assign_index_atom_map(mol)

        use_index_as_atom_map = prefer_atom_map

        try:
            if hasattr(self.mtg, "transform"):
                graph = self.mtg.transform(
                    mol,
                    drop_non_aam=drop_non_aam,
                    use_index_as_atom_map=use_index_as_atom_map,
                    node_attrs=node_attrs,
                    edge_attrs=edge_attrs,
                )
            else:
                graph = self.mtg.mol_to_graph(
                    mol,
                    drop_non_aam=drop_non_aam,
                    light_weight=light_weight,
                    use_index_as_atom_map=use_index_as_atom_map,
                )
        except Exception as e:
            raise SMILES2GraphError(f"mol_to_graph failed: {e}")

        try:
            canonical = Chem.MolToSmiles(mol, isomericSmiles=True)
        except Exception:
            canonical = None
        graph.graph["rdkit_mol"] = mol
        graph.graph["canonical_smiles"] = canonical
        return graph, mol

    def smiles_to_graph(
        self,
        smiles: str,
        *,
        sanitize: bool = True,
        kekulize: bool = False,
        explicit_h: bool = False,
        compute_charges: bool = False,
        prefer_atom_map: bool = True,
        assign_index_map: bool = False,
        drop_non_aam: bool = False,
        light_weight: bool = False,
        node_attrs: Optional[List[str]] = None,
        edge_attrs: Optional[List[str]] = None,
    ) -> Tuple[nx.Graph, Chem.Mol]:
        mol = self.smiles_to_mol(
            smiles,
            sanitize=sanitize,
            kekulize=kekulize,
            explicit_h=explicit_h,
            compute_charges=compute_charges,
        )

        if (
            (drop_non_aam or prefer_atom_map)
            and not self._has_atom_map(mol)
            and assign_index_map
        ):
            self._assign_index_atom_map(mol)

        graph, mol = self.mol_to_graph(
            mol,
            prefer_atom_map=prefer_atom_map,
            assign_index_map=assign_index_map,
            drop_non_aam=drop_non_aam,
            light_weight=light_weight,
            node_attrs=node_attrs,
            edge_attrs=edge_attrs,
        )
        graph.graph["smiles_input"] = smiles
        return graph, mol

    def smiles_list_to_graphs(
        self,
        smiles_iter: Iterable[str],
        *,
        raise_on_error: bool = False,
        **single_kwargs,
    ) -> List[Tuple[Optional[nx.Graph], Optional[Chem.Mol], Optional[Exception]]]:
        results: List[
            Tuple[Optional[nx.Graph], Optional[Chem.Mol], Optional[Exception]]
        ] = []
        for s in smiles_iter:
            try:
                g, m = self.smiles_to_graph(s, **single_kwargs)
                results.append((g, m, None))
            except Exception as e:
                logger.error("Failed to convert SMILES %r: %s", s, e)
                if raise_on_error:
                    raise
                results.append((None, None, e))
        return results
