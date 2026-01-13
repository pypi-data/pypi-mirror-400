"""I/O utilities for combinatorial libraries."""

from __future__ import annotations
import datetime
import hashlib
import json
import os
from typing import Tuple

import pandas as pd


def write_library(
    df: pd.DataFrame, out_dir: str, base_name: str = "pep_lib"
) -> Tuple[str, str]:
    """Write CSV, FASTA (canonical rows only), and SMILES (.smi if present);
    return manifest.

    :param df: DataFrame from `generate_combinatorial_library`.
    :param out_dir: Output directory (created if needed).
    :param base_name: Base filename (without extension).
    :returns: (csv_path, manifest_path)
    """
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(out_dir, f"{base_name}.csv")
    df.to_csv(csv_path, index=False)

    fasta_path = os.path.join(out_dir, f"{base_name}.fasta")
    with open(fasta_path, "w", encoding="utf-8") as fh:
        for i, r in df.iterrows():
            if r.get("is_canonical"):
                fh.write(f">seq_{i}\n{r['sequence_repr']}\n")

    smi_path = os.path.join(out_dir, f"{base_name}.smi")
    with open(smi_path, "w", encoding="utf-8") as fh:
        for _, r in df.iterrows():
            smi = r.get("smiles")
            if isinstance(smi, str) and smi:
                fh.write(smi + "\n")

    with open(csv_path, "rb") as f:
        chk = hashlib.sha256(f.read()).hexdigest()

    mani = {
        "name": base_name,
        "version": "0.1",
        "created": datetime.datetime.utcnow().isoformat() + "Z",
        "rows": int(df.shape[0]),
        "files": [
            {
                "path": os.path.basename(csv_path),
                "sha256": chk,
                "rows": int(df.shape[0]),
            }
        ],
        "generator": {"type": "combinatorial", "params": {}},
    }
    mani_path = os.path.join(out_dir, "manifest.json")
    with open(mani_path, "w", encoding="utf-8") as f:
        json.dump(mani, f, indent=2)

    return csv_path, mani_path
