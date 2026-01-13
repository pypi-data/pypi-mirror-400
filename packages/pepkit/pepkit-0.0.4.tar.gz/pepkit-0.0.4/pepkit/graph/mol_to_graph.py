from __future__ import annotations

from typing import Any, Dict, List, Optional
import random

from rdkit import Chem
from rdkit.Chem import AllChem
import networkx as nx

from pepkit.io.logging import setup_logging

logger = setup_logging()


class MolToGraph:
    """RDKit -> NetworkX helper with attribute selection and amino-acid stereo fields.

    Nodes include stereo fields useful for peptide work:
      - 'cip' : RDKit CIP code ('R'/'S') if available
      - 'alpha_carbon' : bool flag for detected backbone alpha carbon
      - 'aa_stereo' : interpreted amino-acid stereo descriptor ('L'/'D' or None)

    The class exposes a `transform` method (attribute selection) and a `mol_to_graph`
    method (light-weight or detailed graph creation).
    """

    def __init__(
        self,
        node_attrs: Optional[List[str]] = None,
        edge_attrs: Optional[List[str]] = None,
    ) -> None:
        self.node_attrs: List[str] = node_attrs or [
            "element",
            "aromatic",
            "hcount",
            "charge",
            "neighbors",
            "atom_map",
            "cip",
            "alpha_carbon",
            "aa_stereo",
        ]
        self.edge_attrs: List[str] = edge_attrs or ["order"]

    # -----------------------
    # Public API
    # -----------------------
    def transform(
        self,
        mol: Chem.Mol,
        drop_non_aam: bool = False,
        use_index_as_atom_map: bool = False,
        node_attrs: Optional[List[str]] = None,
        edge_attrs: Optional[List[str]] = None,
    ) -> nx.Graph:
        """Build a NetworkX graph including only selected attributes.

        Parameters mirror earlier designs:
        - `drop_non_aam` requires `use_index_as_atom_map` to be True when dropping
          unmapped atoms.
        """
        self._validate_transform_flags(
            drop_non_aam=drop_non_aam,
            use_index_as_atom_map=use_index_as_atom_map,
        )
        self._prepare_mol_inplace(mol)

        selected_node_attrs = self.node_attrs if node_attrs is None else node_attrs
        selected_edge_attrs = self.edge_attrs if edge_attrs is None else edge_attrs

        graph = nx.Graph()
        index_to_id = self._add_nodes(
            graph=graph,
            mol=mol,
            drop_non_aam=drop_non_aam,
            use_index_as_atom_map=use_index_as_atom_map,
            selected_node_attrs=selected_node_attrs,
        )
        self._add_edges(
            graph=graph,
            mol=mol,
            index_to_id=index_to_id,
            selected_edge_attrs=selected_edge_attrs,
        )
        return graph

    @classmethod
    def mol_to_graph(
        cls,
        mol: Chem.Mol,
        drop_non_aam: bool = False,
        light_weight: bool = False,
        use_index_as_atom_map: bool = False,
    ) -> nx.Graph:
        """Create either a light-weight or a detailed graph from an RDKit molecule."""
        if light_weight:
            return cls._create_light_weight_graph(
                mol, drop_non_aam, use_index_as_atom_map
            )
        return cls._create_detailed_graph(mol, drop_non_aam, use_index_as_atom_map)

    # -----------------------
    # transform() helpers
    # -----------------------
    @staticmethod
    def _validate_transform_flags(
        *, drop_non_aam: bool, use_index_as_atom_map: bool
    ) -> None:
        if drop_non_aam and not use_index_as_atom_map:
            raise ValueError(
                "Invalid flags: drop_non_aam=True requires use_index_as_atom_map=True "
                "to avoid dropping atoms without stable ids."
            )

    @staticmethod
    def _prepare_mol_inplace(mol: Chem.Mol) -> None:
        # Assign stereochemistry (CIP) where possible — non-fatal
        try:
            Chem.AssignStereochemistry(mol, force=True, cleanIt=True)
        except Exception as e:
            logger.debug("AssignStereochemistry failed: %s", e)

        # Precompute Gasteiger charges (non-fatal)
        try:
            AllChem.ComputeGasteigerCharges(mol)
        except Exception:
            logger.debug("Gasteiger computation failed in transform; continuing")

    @staticmethod
    def _atom_id(atom: Chem.Atom, *, use_index_as_atom_map: bool) -> int:
        atom_map = atom.GetAtomMapNum()
        if use_index_as_atom_map and atom_map != 0:
            return atom_map
        return atom.GetIdx() + 1

    @staticmethod
    def _filter_selected(attrs: Dict[str, Any], selected: Optional[List[str]]) -> Dict:
        if not selected:
            return attrs
        return {k: v for k, v in attrs.items() if k in selected}

    def _add_nodes(
        self,
        *,
        graph: nx.Graph,
        mol: Chem.Mol,
        drop_non_aam: bool,
        use_index_as_atom_map: bool,
        selected_node_attrs: Optional[List[str]],
    ) -> Dict[int, int]:
        index_to_id: Dict[int, int] = {}

        for atom in mol.GetAtoms():
            atom_map = atom.GetAtomMapNum()
            if drop_non_aam and atom_map == 0:
                continue

            atom_id = self._atom_id(atom, use_index_as_atom_map=use_index_as_atom_map)
            props = self._gather_atom_properties(atom)
            props = self._filter_selected(props, selected_node_attrs)

            graph.add_node(atom_id, **props)
            index_to_id[atom.GetIdx()] = atom_id

        return index_to_id

    def _add_edges(
        self,
        *,
        graph: nx.Graph,
        mol: Chem.Mol,
        index_to_id: Dict[int, int],
        selected_edge_attrs: Optional[List[str]],
    ) -> None:
        for bond in mol.GetBonds():
            begin = index_to_id.get(bond.GetBeginAtomIdx())
            end = index_to_id.get(bond.GetEndAtomIdx())
            if begin is None or end is None:
                continue

            bprops = self._gather_bond_properties(bond)
            bprops = self._filter_selected(bprops, selected_edge_attrs)
            graph.add_edge(begin, end, **bprops)

    # -----------------------
    # Alternative builders
    # -----------------------
    @classmethod
    def _create_light_weight_graph(
        cls,
        mol: Chem.Mol,
        drop_non_aam: bool = False,
        use_index_as_atom_map: bool = False,
    ) -> nx.Graph:
        graph = nx.Graph()
        for atom in mol.GetAtoms():
            atom_map = atom.GetAtomMapNum()
            atom_id = (
                atom_map
                if use_index_as_atom_map and atom_map != 0
                else atom.GetIdx() + 1
            )
            if drop_non_aam and atom_map == 0:
                continue
            props = {
                "element": atom.GetSymbol(),
                "aromatic": atom.GetIsAromatic(),
                "hcount": atom.GetTotalNumHs(),
                "charge": atom.GetFormalCharge(),
                "neighbors": sorted(nb.GetSymbol() for nb in atom.GetNeighbors()),
                "atom_map": atom_map,
            }
            props["cip"] = (
                atom.GetProp("_CIPCode") if atom.HasProp("_CIPCode") else None
            )
            props["alpha_carbon"] = cls._is_alpha_carbon(atom)
            props["aa_stereo"] = cls._infer_aa_stereo(atom, props.get("cip"))
            graph.add_node(atom_id, **props)

        for bond in mol.GetBonds():
            a = bond.GetBeginAtom()
            b = bond.GetEndAtom()
            a_id = (
                a.GetAtomMapNum()
                if use_index_as_atom_map and a.GetAtomMapNum() != 0
                else a.GetIdx() + 1
            )
            b_id = (
                b.GetAtomMapNum()
                if use_index_as_atom_map and b.GetAtomMapNum() != 0
                else b.GetIdx() + 1
            )
            if drop_non_aam and (a.GetAtomMapNum() == 0 or b.GetAtomMapNum() == 0):
                continue
            graph.add_edge(a_id, b_id, order=bond.GetBondTypeAsDouble())
        return graph

    @classmethod
    def _create_detailed_graph(
        cls,
        mol: Chem.Mol,
        drop_non_aam: bool = True,
        use_index_as_atom_map: bool = True,
    ) -> nx.Graph:
        try:
            AllChem.ComputeGasteigerCharges(mol)
        except Exception:
            logger.debug("ComputeGasteigerCharges failed in detailed graph creation")

        try:
            Chem.AssignStereochemistry(mol, force=True, cleanIt=True)
        except Exception as e:
            logger.debug(
                "AssignStereochemistry failed in detailed graph creation: %s", e
            )

        graph = nx.Graph()
        idx_map: Dict[int, int] = {}
        for atom in mol.GetAtoms():
            atom_map = atom.GetAtomMapNum()
            atom_id = (
                atom_map
                if use_index_as_atom_map and atom_map != 0
                else atom.GetIdx() + 1
            )
            if drop_non_aam and atom_map == 0:
                continue
            graph.add_node(atom_id, **cls._gather_atom_properties(atom))
            idx_map[atom.GetIdx()] = atom_id

        for bond in mol.GetBonds():
            b = idx_map.get(bond.GetBeginAtomIdx())
            e = idx_map.get(bond.GetEndAtomIdx())
            if b and e:
                graph.add_edge(b, e, **cls._gather_bond_properties(bond))
        return graph

    # -----------------------
    # Property collectors
    # -----------------------
    @staticmethod
    def _gather_atom_properties(atom: Chem.Atom) -> Dict[str, Any]:
        gcharge = (
            round(float(atom.GetProp("_GasteigerCharge")), 3)
            if atom.HasProp("_GasteigerCharge")
            else 0.0
        )

        cip: Optional[str] = None
        try:
            if atom.HasProp("_CIPCode"):
                cip = atom.GetProp("_CIPCode")
        except Exception:
            cip = None

        alpha = MolToGraph._is_alpha_carbon(atom)
        aa_stereo = MolToGraph._infer_aa_stereo(atom, cip)

        return {
            "element": atom.GetSymbol(),
            "aromatic": atom.GetIsAromatic(),
            "hcount": atom.GetTotalNumHs(),
            "charge": atom.GetFormalCharge(),
            "radical": atom.GetNumRadicalElectrons(),
            "isomer": cip or MolToGraph.get_stereochemistry(atom),
            "cip": cip,
            "alpha_carbon": alpha,
            "aa_stereo": aa_stereo,
            "partial_charge": gcharge,
            "hybridization": str(atom.GetHybridization()),
            "in_ring": atom.IsInRing(),
            "implicit_hcount": atom.GetNumImplicitHs(),
            "neighbors": sorted(nb.GetSymbol() for nb in atom.GetNeighbors()),
            "atom_map": atom.GetAtomMapNum(),
        }

    @staticmethod
    def _gather_bond_properties(bond: Chem.Bond) -> Dict[str, Any]:
        return {
            "order": bond.GetBondTypeAsDouble(),
            "bond_type": str(bond.GetBondType()),
            "ez_isomer": MolToGraph.get_bond_stereochemistry(bond),
            "conjugated": bond.GetIsConjugated(),
            "in_ring": bond.IsInRing(),
        }

    # -----------------------
    # Stereo helpers
    # -----------------------
    @staticmethod
    def get_stereochemistry(atom: Chem.Atom) -> str:
        ch = atom.GetChiralTag()
        if ch == Chem.ChiralType.CHI_TETRAHEDRAL_CCW:
            return "S"
        if ch == Chem.ChiralType.CHI_TETRAHEDRAL_CW:
            return "R"
        return "N"

    @staticmethod
    def get_bond_stereochemistry(bond: Chem.Bond) -> str:
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            return "N"
        st = bond.GetStereo()
        if st == Chem.BondStereo.STEREOE:
            return "E"
        if st == Chem.BondStereo.STEREOZ:
            return "Z"
        return "N"

    # -----------------------
    # Atom mapping helpers
    # -----------------------
    @staticmethod
    def has_atom_mapping(mol: Chem.Mol) -> bool:
        return any(atom.GetAtomMapNum() != 0 for atom in mol.GetAtoms())

    @staticmethod
    def random_atom_mapping(mol: Chem.Mol) -> Chem.Mol:
        indices = list(range(1, mol.GetNumAtoms() + 1))
        random.shuffle(indices)
        for atom, idx in zip(mol.GetAtoms(), indices):
            atom.SetAtomMapNum(idx)
        return mol

    # -----------------------
    # Peptide-specific helpers
    # -----------------------
    @staticmethod
    def _is_alpha_carbon(atom: Chem.Atom) -> bool:
        if atom.GetSymbol() != "C":
            return False
        neighbors = list(atom.GetNeighbors())
        has_n = any(nb.GetSymbol() == "N" for nb in neighbors)

        has_carbonyl_neighbor = False
        for nb in neighbors:
            if nb.GetSymbol() != "C":
                continue
            for b in nb.GetBonds():
                other = b.GetOtherAtom(nb)
                if other.GetSymbol() == "O" and b.GetBondType() == Chem.BondType.DOUBLE:
                    has_carbonyl_neighbor = True
                    break
            if has_carbonyl_neighbor:
                break

        return has_n and has_carbonyl_neighbor

    @staticmethod
    def _infer_aa_stereo(atom: Chem.Atom, cip: Optional[str]) -> Optional[str]:
        if cip not in ("R", "S"):
            return None
        if not MolToGraph._is_alpha_carbon(atom):
            return None

        neighbors = list(atom.GetNeighbors())
        carbonyl_carbons = set()
        for nb in neighbors:
            if nb.GetSymbol() == "C":
                for b in nb.GetBonds():
                    other = b.GetOtherAtom(nb)
                    if (
                        other.GetSymbol() == "O"
                        and b.GetBondType() == Chem.BondType.DOUBLE
                    ):
                        carbonyl_carbons.add(nb.GetIdx())

        sidechain_has_sulfur = any(
            nb.GetSymbol() == "S" and nb.GetIdx() not in carbonyl_carbons
            for nb in neighbors
        )

        if sidechain_has_sulfur:
            return "L" if cip == "R" else "D"
        return "L" if cip == "S" else "D"
