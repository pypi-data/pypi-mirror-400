from dataclasses import dataclass
from typing import Dict
from pepkit.chem.constants import KD, DEFAULT_HYDRO, _RESIDUE_MASS


@dataclass
class FeatureSpec:
    """
    Physico-chemical bucketing rules for residue/monomer tokens.

    This class is token-agnostic: keys may be one-letter AAs (A, C, …), 3-letter
    codes, or custom monomer symbols (e.g., 'Aib', 'Iva'). Missing keys fall back
    to neutral/unknown buckets.

    :param hydro: token -> hydrophobicity bucket label (e.g., 'hydrophobic', 'polar').
    :type hydro: Dict[str, str]
    :param mass: token -> integer mass (or coarse mass proxy) used for mass binning.
                 By default uses :data:`_RESIDUE_MASS`.
    :type mass: Dict[str, int]
    :param hbd: token -> H-bond donor count (or bucket).
    :type hbd: Dict[str, int]
    :param kd: token -> hydropathy / KD numeric value (float). By default uses :data:`KD`.
    :type kd: Dict[str, float]
    :param mass_bin: mass bin width; masses are bucketed as m0, m10, m20, …
    :type mass_bin: int
    :param include_identity: if False, downstream labelers can mask token identity.
    :type include_identity: bool
    """

    hydro: Dict[str, str] = None
    mass: Dict[str, float] = None
    hbd: Dict[str, int] = None
    kd: Dict[str, float] = None
    mass_bin: int = 10
    include_identity: bool = True

    def __post_init__(self) -> None:

        if self.hydro is None:
            self.hydro = DEFAULT_HYDRO
        # Use canonical _RESIDUE_MASS as the default mass table (replaces DEFAULT_MASS)
        if self.mass is None:
            self.mass = _RESIDUE_MASS.copy()
        if self.hbd is None:
            self.hbd = {}
        # KD hydropathy added to feature space
        if self.kd is None:
            self.kd = KD.copy()

    def label_token(self, token: str, hide_identity: bool = False) -> str:
        """
        Compose a compact, human-readable label for a token.

        Label includes: identity (optional), charge bucket, hydro bucket, mass bin,
        hydrogen-bond donor count, and KD (hydropathy) rounded to 1 decimal.

        Example result: ``A|neut|polar|m120|hbd0|kd1.8``

        :param token: residue/monomer token (e.g., 'A', 'E', 'Aib').
        :type token: str
        :param hide_identity: override to mask token identity.
        :type hide_identity: bool
        :returns: compact label string
        :rtype: str
        """
        t = token or "X"
        idtok = t if (self.include_identity and not hide_identity) else "X"
        charge = (
            "pos" if t in ("K", "R", "H") else ("neg" if t in ("D", "E") else "neut")
        )
        hydro = self.hydro.get(t, "unk")
        mass = float(self.mass.get(t, 0.0))
        mass_bin = f"m{int((mass // self.mass_bin) * self.mass_bin)}"
        hbd = self.hbd.get(t, 0)
        kd_val = float(self.kd.get(t, 0.0))
        kd_token = f"kd{kd_val:.1f}"
        return f"{idtok}|{charge}|{hydro}|{mass_bin}|hbd{hbd}|{kd_token}"
