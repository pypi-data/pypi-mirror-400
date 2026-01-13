from __future__ import annotations
from typing import Dict

caa = {
    "A": "[CH3:1][C@H:2]([NH2:3])[C:4](=[O:5])[OH:6]",
    "R": (
        "[NH:1]=[C:2]([NH2:3])[NH:4][CH2:5][CH2:6][CH2:7][C@H:8]([NH2:9])"
        + "[C:10](=[O:11])[OH:12]"
    ),
    "N": "[NH2:1][C@H:2]([CH2:3][C:4](=[O:5])[NH2:6])[C:7](=[O:8])[OH:9]",
    "D": "[NH2:1][C@H:2]([CH2:3][C:4](=[O:5])[OH:6])[C:7](=[O:8])[OH:9]",
    "C": "[NH2:1][C@H:2]([CH2:3][SH:4])[C:5](=[O:6])[OH:7]",
    "Q": "[NH2:1][C@H:2]([CH2:3][CH2:4][C:5](=[O:6])[NH2:7])[C:8](=[O:9])[OH:10]",
    "E": "[NH2:1][C@H:2]([CH2:3][CH2:4][C:5](=[O:6])[OH:7])[C:8](=[O:9])[OH:10]",
    "G": "[NH2:1][CH2:2][C:3](=[O:4])[OH:5]",
    "H": "[NH2:1][C@H:2]([CH2:3][c:4]1[cH:5][nH:6][cH:7][n:8]1)[C:9](=[O:10])[OH:11]",
    "I": "[CH3:1][CH2:2][C@H:3]([CH3:4])[C@H:5]([NH2:6])[C:7](=[O:8])[OH:9]",
    "L": "[CH3:1][CH:2]([CH3:3])[CH2:4][C@H:5]([NH2:6])[C:7](=[O:8])[OH:9]",
    "K": "[NH2:1][CH2:2][CH2:3][CH2:4][CH2:5][C@H:6]([NH2:7])[C:8](=[O:9])[OH:10]",
    "M": "[NH2:1][C@H:2]([CH2:3][CH2:4][S:5][CH3:6])[C:7](=[O:8])[OH:9]",
    "F": (
        "[NH2:1][C@H:2]([CH2:3][c:4]1[cH:5][cH:6][cH:7][cH:8][cH:9]1)[C:10]"
        + "(=[O:11])[OH:12]"
    ),
    "P": "[O:1]=[C:2]([OH:3])[C@H:4]1[CH2:5][CH2:6][CH2:7][NH:8]1",
    "S": "[NH2:1][C@H:2]([CH2:3][OH:4])[C:5](=[O:6])[OH:7]",
    "T": "[CH3:1][C@H:2]([OH:3])[C@H:4]([NH2:5])[C:6](=[O:7])[OH:8]",
    "W": (
        "[NH2:1][C@H:2]([CH2:3][c:4]1[c:5]2[cH:6][cH:7][cH:8][cH:9][c:10]2"
        + "[nH:11][cH:12]1)[C:13](=[O:14])[OH:15]"
    ),
    "Y": (
        "[NH2:1][C@H:2]([CH2:3][c:4]1[cH:5][cH:6][c:7]([OH:8])[cH:9]"
        + "[cH:10]1)[C:11](=[O:12])[OH:13]"
    ),
    "V": "[NH2:1][C@H:2]([CH:3]([CH3:4])[CH3:5])[C:6](=[O:7])[OH:8]",
}

KD: Dict[str, float] = {
    "I": 4.5,
    "V": 4.2,
    "L": 3.8,
    "F": 2.8,
    "C": 2.5,
    "M": 1.9,
    "A": 1.8,
    "G": -0.4,
    "T": -0.7,
    "S": -0.8,
    "W": -0.9,
    "Y": -1.3,
    "P": -1.6,
    "H": -3.2,
    "E": -3.5,
    "Q": -3.5,
    "D": -3.5,
    "N": -3.5,
    "K": -3.9,
    "R": -4.5,
}

# Average residue masses (approximate, average isotopic mass)
_RESIDUE_MASS: Dict[str, float] = {
    "A": 89.09,
    "R": 174.20,
    "N": 132.12,
    "D": 133.10,
    "C": 121.15,
    "E": 147.13,
    "Q": 146.15,
    "G": 75.07,
    "H": 155.16,
    "I": 131.17,
    "L": 131.17,
    "K": 146.19,
    "M": 149.21,
    "F": 165.19,
    "P": 115.13,
    "S": 105.09,
    "T": 119.12,
    "W": 204.23,
    "Y": 181.19,
    "V": 117.15,
}

DEFAULT_HYDRO = {
    "A": "hydrophobic",
    "V": "hydrophobic",
    "I": "hydrophobic",
    "L": "hydrophobic",
    "M": "hydrophobic",
    "F": "hydrophobic",
    "W": "hydrophobic",
    "Y": "hydrophobic",
    "G": "neutral",
    "P": "neutral",
    "S": "polar",
    "T": "polar",
    "C": "polar",
    "N": "polar",
    "Q": "polar",
    "H": "polar",
    "K": "positively_charged",
    "R": "positively_charged",
    "D": "negatively_charged",
    "E": "negatively_charged",
}


PKA: Dict[str, float] = {
    "N_term": 9.6,
    "C_term": 2.1,
    "K": 10.5,
    "R": 12.5,
    "H": 6.0,
    "D": 3.9,
    "E": 4.1,
    "C": 8.3,
    "Y": 10.1,
}

__all__ = ["caa", "KD", "DEFAULT_HYDRO", "PKA", "_RESIDUE_MASS"]
