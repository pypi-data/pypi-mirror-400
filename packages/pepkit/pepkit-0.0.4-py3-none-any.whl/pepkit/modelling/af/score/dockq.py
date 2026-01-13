from __future__ import annotations

from pathlib import Path
from typing import Dict, Set, Tuple, Union

import numpy as np
from Bio.PDB import PDBParser
from Bio.PDB.Chain import Chain
from Bio.PDB.Residue import Residue


class DockQ:
    """
    Compute DockQ between a reference complex and a predicted complex.

    Outputs:
      - DockQ in [0, 1]
      - Fnat
      - LRMSD
      - iRMSD
    """

    def __init__(
        self,
        contact_cutoff: float = 5.0,
        lrmsd_scale: float = 8.5,
        irmsd_scale: float = 1.5,
        fnat_scale: float = 0.1,
        heavy_atom_contacts: bool = True,
        rmsd_atom: str = "CA",
    ) -> None:
        self.contact_cutoff = float(contact_cutoff)
        self.lrmsd_scale = float(lrmsd_scale)
        self.irmsd_scale = float(irmsd_scale)
        self.fnat_scale = float(fnat_scale)
        self.heavy_atom_contacts = bool(heavy_atom_contacts)
        self.rmsd_atom = str(rmsd_atom)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def score(
        self,
        ref_pdb: Union[str, Path],
        gen_pdb: Union[str, Path],
        receptor_chain_id: str,
        ligand_chain_id: str,
        model_index: int = 0,
    ) -> Dict[str, float]:
        ref_struct = self._parse_pdb(ref_pdb, "ref")
        gen_struct = self._parse_pdb(gen_pdb, "gen")

        ref_model = self._get_model(ref_struct, model_index)
        gen_model = self._get_model(gen_struct, model_index)

        ref_R = self._get_chain(ref_model, receptor_chain_id)
        ref_L = self._get_chain(ref_model, ligand_chain_id)
        gen_R = self._get_chain(gen_model, receptor_chain_id)
        gen_L = self._get_chain(gen_model, ligand_chain_id)

        ref_R_atoms = self._residue_atom_coords(ref_R, heavy=self.heavy_atom_contacts)
        ref_L_atoms = self._residue_atom_coords(ref_L, heavy=self.heavy_atom_contacts)

        native_contacts = self._compute_contacts(
            ref_R_atoms,
            ref_L_atoms,
            self.contact_cutoff,
        )

        if not native_contacts:
            return {
                "DockQ": 0.0,
                "Fnat": 0.0,
                "LRMSD": float("inf"),
                "iRMSD": float("inf"),
                "n_native_contacts": 0.0,
                "n_recovered_contacts": 0.0,
            }

        gen_R_atoms = self._residue_atom_coords(gen_R, heavy=self.heavy_atom_contacts)
        gen_L_atoms = self._residue_atom_coords(gen_L, heavy=self.heavy_atom_contacts)

        pred_contacts = self._compute_contacts(
            gen_R_atoms,
            gen_L_atoms,
            self.contact_cutoff,
        )

        recovered = native_contacts & pred_contacts
        fnat = len(recovered) / len(native_contacts)

        # LRMSD
        ref_R_ca, gen_R_ca = self._paired_atom_coords(ref_R, gen_R, self.rmsd_atom)
        R, t = self._kabsch_transform(gen_R_ca, ref_R_ca)

        ref_L_ca, gen_L_ca = self._paired_atom_coords(ref_L, gen_L, self.rmsd_atom)
        gen_L_ca = gen_L_ca @ R.T + t
        lrmsd = self._rmsd(gen_L_ca, ref_L_ca)

        # iRMSD
        I_R, I_L = self._interface_residue_keys(native_contacts)
        ref_int, gen_int = self._paired_interface_coords(
            ref_R,
            ref_L,
            gen_R,
            gen_L,
            I_R,
            I_L,
            self.rmsd_atom,
        )

        R_i, t_i = self._kabsch_transform(gen_int, ref_int)
        gen_int = gen_int @ R_i.T + t_i
        irmsd = self._rmsd(gen_int, ref_int)

        dockq = self._dockq(fnat, lrmsd, irmsd)

        return {
            "DockQ": float(dockq),
            "Fnat": float(fnat),
            "LRMSD": float(lrmsd),
            "iRMSD": float(irmsd),
            "n_native_contacts": float(len(native_contacts)),
            "n_recovered_contacts": float(len(recovered)),
        }

    # ------------------------------------------------------------------
    # Core formula
    # ------------------------------------------------------------------
    def _dockq(self, fnat: float, lrmsd: float, irmsd: float) -> float:
        return 1.0 / (
            1.0
            + (irmsd / self.irmsd_scale) ** 2
            + (lrmsd / self.lrmsd_scale) ** 2
            + ((1.0 - fnat) / self.fnat_scale) ** 2
        )

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    def _parse_pdb(self, pdb: Union[str, Path], sid: str):
        pdb = Path(pdb)
        if not pdb.exists():
            raise FileNotFoundError(pdb)
        return PDBParser(QUIET=True).get_structure(sid, str(pdb))

    @staticmethod
    def _get_model(structure, index: int):
        models = list(structure.get_models())
        if index >= len(models):
            raise ValueError("model_index out of range")
        return models[index]

    @staticmethod
    def _get_chain(model, cid: str) -> Chain:
        for chain in model.get_chains():
            if chain.id == cid:
                return chain
        raise KeyError(f"Chain '{cid}' not found")

    # ------------------------------------------------------------------
    # Residues / atoms
    # ------------------------------------------------------------------
    @staticmethod
    def _is_std_residue(res: Residue) -> bool:
        return res.id[0] == " "

    @staticmethod
    def _res_key(res: Residue) -> Tuple[int, str]:
        return res.id[1], res.id[2].strip() or ""

    def _residue_atom_coords(
        self,
        chain: Chain,
        heavy: bool,
    ) -> Dict[Tuple[int, str], np.ndarray]:
        out: Dict[Tuple[int, str], np.ndarray] = {}
        for res in chain:
            if not self._is_std_residue(res):
                continue
            coords = []
            for atom in res:
                if heavy and atom.element == "H":
                    continue
                coords.append(atom.coord.astype(np.float64))
            if coords:
                out[self._res_key(res)] = np.vstack(coords)
        return out

    def _paired_atom_coords(
        self,
        ref: Chain,
        gen: Chain,
        atom: str,
    ) -> Tuple[np.ndarray, np.ndarray]:
        ref_map = {
            self._res_key(r): r[atom].coord
            for r in ref
            if self._is_std_residue(r) and atom in r
        }
        gen_map = {
            self._res_key(r): r[atom].coord
            for r in gen
            if self._is_std_residue(r) and atom in r
        }

        keys = sorted(ref_map.keys() & gen_map.keys())
        if len(keys) < 3:
            raise ValueError("Not enough paired atoms for RMSD")

        return (
            np.vstack([ref_map[k] for k in keys]),
            np.vstack([gen_map[k] for k in keys]),
        )

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------
    def _compute_contacts(
        self,
        R: Dict[Tuple[int, str], np.ndarray],
        L: Dict[Tuple[int, str], np.ndarray],
        cutoff: float,
    ) -> Set[Tuple[Tuple[int, str], Tuple[int, str]]]:
        c2 = cutoff * cutoff
        contacts: Set[Tuple[Tuple[int, str], Tuple[int, str]]] = set()
        for rk, Ra in R.items():
            for lk, La in L.items():
                d2 = np.min(np.sum((Ra[:, None, :] - La[None, :, :]) ** 2, axis=2))
                if d2 <= c2:
                    contacts.add((rk, lk))
        return contacts

    @staticmethod
    def _interface_residue_keys(
        contacts: Set[Tuple[Tuple[int, str], Tuple[int, str]]],
    ) -> Tuple[Set[Tuple[int, str]], Set[Tuple[int, str]]]:
        IR, IL = set(), set()
        for r, l in contacts:
            IR.add(r)
            IL.add(l)
        return IR, IL

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------
    @staticmethod
    def _kabsch_transform(P: np.ndarray, Q: np.ndarray):
        Pc, Qc = P.mean(0), Q.mean(0)
        P0, Q0 = P - Pc, Q - Qc
        C = P0.T @ Q0
        V, _, Wt = np.linalg.svd(C)
        D = np.diag([1.0, 1.0, np.sign(np.linalg.det(V @ Wt))])
        R = V @ D @ Wt
        t = Qc - Pc @ R.T
        return R, t

    @staticmethod
    def _rmsd(P: np.ndarray, Q: np.ndarray) -> float:
        return float(np.sqrt(np.mean(np.sum((P - Q) ** 2, axis=1))))
