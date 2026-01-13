from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

# -------------------------- canonical tables ---------------------------- #

# Hydrophobicity / hydropathy scale (example values used previously)
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

# ----------------------- General feature buckets ----------------------- #


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
        # Conservative defaults for 20 canonical AAs; everything else -> 'unk' / 0.
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


# -------------------------- Sequence descriptors ------------------------- #

# pKa constants for side chains and termini (same approach as prior code)
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


@dataclass(frozen=True)
class SeqDesc:
    """Frozen container for sequence descriptors.

    :param length: Sequence length.
    :param frac_hydrophobic: Fraction of hydrophobic residues.
    :param kd_mean: Mean KD/hydrophobicity.
    :param net_charge_pH7_4: Net charge at the requested pH (default 7.4).
    :param aromatic_fraction: Fraction of aromatic residues (F, Y, W, H).
    :param basic_fraction: Fraction of basic residues (K, R, H).
    :param acidic_fraction: Fraction of acidic residues (D, E).
    :param composition: Dict of residue counts keyed by 1-letter code.
    :param mol_weight: Approximate molecular weight (Da).
    :param pI: Estimated isoelectric point.
    """

    length: int
    frac_hydrophobic: float
    kd_mean: float
    net_charge_pH7_4: float
    aromatic_fraction: float
    basic_fraction: float
    acidic_fraction: float
    composition: Dict[str, int]
    mol_weight: float
    pI: float


def _hh(pka: float, acid: bool, pH: float) -> float:
    """Henderson–Hasselbalch dependent protonation fraction helper."""
    return 1.0 / (1.0 + 10 ** ((pH - pka) if acid else (pka - pH)))


# Reuse _RESIDUE_MASS and KD defined above for descriptor computations
@dataclass
class SequenceDescriptor:
    """OOP calculator for peptide sequence descriptors."""

    seq: str
    pH: float = 7.4

    def __post_init__(self) -> None:
        s = (self.seq or "").strip().upper()
        if not s:
            raise ValueError("Empty sequence")
        self.seq = s
        self.length = len(s)
        # lazy caches
        self._composition: Optional[Dict[str, int]] = None
        self._frac_hydrophobic: Optional[float] = None
        self._kd_mean: Optional[float] = None
        self._net_charge: Optional[float] = None
        self._aromatic_fraction: Optional[float] = None
        self._basic_fraction: Optional[float] = None
        self._acidic_fraction: Optional[float] = None
        self._mol_weight: Optional[float] = None
        self._pI: Optional[float] = None

    def compute_composition(self) -> "SequenceDescriptor":
        comp: Dict[str, int] = {}
        for aa in self.seq:
            comp[aa] = comp.get(aa, 0) + 1
        self._composition = comp
        return self

    def compute_frac_hydrophobic(self) -> "SequenceDescriptor":
        hyd = set("AILMFWV")
        count = sum(1 for a in self.seq if a in hyd)
        self._frac_hydrophobic = count / self.length
        return self

    def compute_aromatic_basic_acidic(self) -> "SequenceDescriptor":
        aro = set("FYWH")
        bas = set("KRH")
        acd = set("DE")
        self._aromatic_fraction = sum(1 for a in self.seq if a in aro) / self.length
        self._basic_fraction = sum(1 for a in self.seq if a in bas) / self.length
        self._acidic_fraction = sum(1 for a in self.seq if a in acd) / self.length
        return self

    def compute_kd_mean(self) -> "SequenceDescriptor":
        total = 0.0
        for a in self.seq:
            total += KD.get(a, 0.0)
        self._kd_mean = total / self.length
        return self

    def compute_net_charge(self) -> "SequenceDescriptor":
        net = 0.0
        net += _hh(PKA["N_term"], acid=False, pH=self.pH)
        net -= _hh(PKA["C_term"], acid=True, pH=self.pH)
        for a in self.seq:
            if a in ("K", "R", "H"):
                val = PKA.get(a, None)
                if val is not None:
                    net += _hh(val, acid=False, pH=self.pH)
            if a in ("D", "E", "C", "Y"):
                val = PKA.get(a, None)
                if val is not None:
                    net -= _hh(val, acid=True, pH=self.pH)
        self._net_charge = net
        return self

    def _net_charge_at_pH(self, pH: float) -> float:
        net = 0.0
        net += _hh(PKA["N_term"], acid=False, pH=pH)
        net -= _hh(PKA["C_term"], acid=True, pH=pH)
        for a in self.seq:
            if a in ("K", "R", "H"):
                val = PKA.get(a, None)
                if val is not None:
                    net += _hh(val, acid=False, pH=pH)
            if a in ("D", "E", "C", "Y"):
                val = PKA.get(a, None)
                if val is not None:
                    net -= _hh(val, acid=True, pH=pH)
        return net

    def estimate_pI(
        self, precision: float = 1e-3, max_iter: int = 30
    ) -> "SequenceDescriptor":
        low, high = 0.0, 14.0
        f_low = self._net_charge_at_pH(low)
        f_high = self._net_charge_at_pH(high)
        if f_low == 0.0:
            self._pI = low
            return self
        if f_high == 0.0:
            self._pI = high
            return self
        for _ in range(max_iter):
            mid = 0.5 * (low + high)
            f_mid = self._net_charge_at_pH(mid)
            if abs(f_mid) < 1e-6 or (high - low) / 2.0 < precision:
                self._pI = mid
                return self
            if (f_low < 0 and f_mid > 0) or (f_low > 0 and f_mid < 0):
                high, f_high = mid, f_mid
            else:
                low, f_low = mid, f_mid
        self._pI = 0.5 * (low + high)
        return self

    def estimate_molecular_weight(self) -> "SequenceDescriptor":
        total = 0.0
        for a in self.seq:
            total += _RESIDUE_MASS.get(a, 0.0)
        total += 18.015  # add H2O
        self._mol_weight = total
        return self

    def compute_all(self) -> "SequenceDescriptor":
        return (
            self.compute_composition()
            .compute_frac_hydrophobic()
            .compute_aromatic_basic_acidic()
            .compute_kd_mean()
            .compute_net_charge()
            .estimate_pI()
            .estimate_molecular_weight()
        )

    @property
    def composition(self) -> Dict[str, int]:
        if self._composition is None:
            self.compute_composition()
        return dict(self._composition)

    @property
    def frac_hydrophobic(self) -> float:
        if self._frac_hydrophobic is None:
            self.compute_frac_hydrophobic()
        return float(self._frac_hydrophobic)

    @property
    def kd_mean(self) -> float:
        if self._kd_mean is None:
            self.compute_kd_mean()
        return float(self._kd_mean)

    @property
    def net_charge(self) -> float:
        if self._net_charge is None:
            self.compute_net_charge()
        return float(self._net_charge)

    @property
    def aromatic_fraction(self) -> float:
        if self._aromatic_fraction is None:
            self.compute_aromatic_basic_acidic()
        return float(self._aromatic_fraction)

    @property
    def basic_fraction(self) -> float:
        if self._basic_fraction is None:
            self.compute_aromatic_basic_acidic()
        return float(self._basic_fraction)

    @property
    def acidic_fraction(self) -> float:
        if self._acidic_fraction is None:
            self.compute_aromatic_basic_acidic()
        return float(self._acidic_fraction)

    @property
    def mol_weight(self) -> float:
        if self._mol_weight is None:
            self.estimate_molecular_weight()
        return float(self._mol_weight)

    @property
    def pI(self) -> float:
        if self._pI is None:
            self.estimate_pI()
        return float(self._pI)

    def to_seqdesc(self) -> SeqDesc:
        return SeqDesc(
            length=self.length,
            frac_hydrophobic=self.frac_hydrophobic,
            kd_mean=self.kd_mean,
            net_charge_pH7_4=self.net_charge,
            aromatic_fraction=self.aromatic_fraction,
            basic_fraction=self.basic_fraction,
            acidic_fraction=self.acidic_fraction,
            composition=self.composition,
            mol_weight=self.mol_weight,
            pI=self.pI,
        )


def sequence_descriptors(seq: str, pH: float = 7.4) -> SeqDesc:
    """Convenience wrapper returning a :class:`SeqDesc` for ``seq`` at pH."""
    calc = SequenceDescriptor(seq, pH=pH)
    calc.compute_all()
    return calc.to_seqdesc()
