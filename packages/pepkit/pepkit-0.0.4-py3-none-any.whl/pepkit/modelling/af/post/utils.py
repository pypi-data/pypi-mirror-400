import os
import re
import shutil
import zipfile
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Union, Optional


class Utils:
    # Helper functions
    @staticmethod
    def _parse_atom(line):
        """Extract (chain, resSeq, coords, plddt) from an ATOM/HETATM line."""
        return (
            line[21].strip(),  # chain ID
            int(line[22:26]),  # resSeq
            (float(line[30:38]), float(line[38:46]), float(line[46:54])),  # X  # Y  # Z
            float(line[60:66]),  # pLDDT in B-factor
        )

    @staticmethod
    def _avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    @staticmethod
    def _round(val, round_digits):
        return None if val is None else round(val, round_digits)

    @staticmethod
    def _check_type(pdb_lines):
        chains = set()
        for line in pdb_lines:
            if line.startswith(("ATOM  ", "HETATM")):
                if len(line) <= 21:
                    continue
                chain = line[21].strip()
                chains.add(chain)
        if len(chains) == 1:
            return "apo"
        else:
            return "complex"

    @staticmethod
    def _extract_pep_chain(
        pdb: Union[str, Path, list], max_diff: int = 10
    ) -> Optional[str]:
        """
        Return a peptide chain ID from a PDB file or list of PDB lines.

        Accepts either a file path (str/Path) or a list of lines.
        """
        counts = defaultdict(set)  # chain -> set of (resseq_str, iCode)

        # Determine input type
        if isinstance(pdb, (str, Path)):
            fh = open(pdb, "r", encoding="latin-1")
            close_fh = True
        elif isinstance(pdb, list):
            fh = pdb
            close_fh = False
        else:
            raise TypeError("pdb must be a file path or list of lines")

        try:
            for line in fh:
                if not line.startswith("ATOM  "):
                    continue
                if len(line) < 27:
                    continue
                chain = line[21]
                if chain == " ":
                    continue
                resseq_raw = line[22:26].strip()
                icode = line[26].strip()
                counts[chain].add((resseq_raw, icode))
        finally:
            if close_fh:
                fh.close()

        # valid chains: more than 2 unique residues
        valid = {ch: len(s) for ch, s in counts.items() if len(s) > 2}
        if not valid:
            return None

        shortest_len = min(valid.values())
        candidates = {
            ch: ln for ch, ln in valid.items() if ln <= (shortest_len + max_diff)
        }

        if not candidates:
            return sorted(valid.items(), key=lambda x: (x[1], x[0]))[0][0]

        if len(candidates) == 1:
            return next(iter(candidates.keys()))

        selected = sorted(candidates.items(), key=lambda x: (-x[1], x[0]))[0][0]
        return selected

    @staticmethod
    def processing_time(log_path):
        log_path = Path(log_path)
        with open(log_path) as f:
            lines = f.readlines()
        # Find all timestamps in the log
        timestamps = [
            re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", line)
            for line in lines
        ]
        timestamps = [m.group(1) for m in timestamps if m]
        if len(timestamps) < 2:
            return None
        fmt = "%Y-%m-%d %H:%M:%S,%f"
        start = datetime.strptime(timestamps[0], fmt)
        end = datetime.strptime(timestamps[-1], fmt)
        return int(round((end - start).total_seconds(), ndigits=0))

    @staticmethod
    def get_length(entry_dir):
        json_matches = sorted(entry_dir.glob("*_scores_*.json"))
        if not json_matches:
            print(f"Warning: No JSON score files found in {entry_dir.name}")
            return {}
        with open(json_matches[0], "r") as f:
            rec = json.load(f)
            length = len(rec.get("plddt", []))
        return length

    @staticmethod
    def unzip_colabfold(folder: str):
        """
        Unzip all .zip files in the specified folder, moving contents up one level.
        """
        for fname in os.listdir(folder):
            if fname.endswith(".zip"):
                zip_path = os.path.join(folder, fname)
                extract_dir = os.path.join(folder, "outputdir")

                # unzip into 'outputdir'
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(extract_dir)

                # expect inner = outputdir/outputdir/*
                inner_lv1 = os.path.join(extract_dir, "outputdir")
                if os.path.isdir(inner_lv1):
                    inner_items = os.listdir(inner_lv1)
                    if len(inner_items) == 1:
                        inner_src = os.path.join(inner_lv1, inner_items[0])
                        dst = os.path.join(folder, inner_items[0])

                        # overwrite if needed
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.move(inner_src, dst)

                # clean up both layers
                shutil.rmtree(extract_dir)

    @staticmethod
    def process_pdb(pdb_path):
        with open(pdb_path, "r", encoding="latin-1") as f:
            pdb_lines = f.readlines()
        return pdb_lines

    @staticmethod
    def process_json(json_path):
        import json

        with open(json_path, "r") as f:
            record = json.load(f)
        return record

    @staticmethod
    def args():
        parser = argparse.ArgumentParser(
            description="Utility functions for feature extraction."
        )
        parser.add_argument(
            "--log",
            type=str,
            help="Path to the log file for processing time calculation.",
        )
        parser.add_argument(
            "--unzip",
            type=str,
            help="Folder containing output from ColabFold.",
        )
        return parser


if __name__ == "__main__":
    parser = Utils.args()
    args = parser.parse_args()

    if args.log:
        time_taken = Utils.processing_time(args.log)
        if time_taken is not None:
            print(f"Processing time: {time_taken} seconds")
        else:
            print("Could not determine processing time from log.")

    if args.unzip:
        Utils.unzip_colabfold(args.unzip)

    # Example usage:
    # python -m pepq.featoop.utils --log data/features/raw/7QWV_A_7QWV_B_log.txt
    # python -m pepq.featoop.utils --unzip data/features/raw/zip
