from __future__ import annotations
from matplotlib.pylab import block
import os, sys, re, requests
import csv, json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from bs4 import BeautifulSoup, NavigableString, Tag
from html.entities import name2codepoint
import xml.etree.ElementTree as ET
import glob
from collections import Counter

# 1. GENERATE A LIST OF INTERESTED IDS -------------------------------------------------
# Filter to only include toxin classified into pharmacological families

# Exact phrases to keep (match as-is; no hyphen/variant normalization)
_ALLOWED = (
    "alpha conotoxin",
    "gamma conotoxin",
    "delta conotoxin",
    "epsilon conotoxin",
    "iota conotoxin",
    "kappa conotoxin",
    "mu conotoxin",
    "rho conotoxin",
    "sigma conotoxin",
    "tau conotoxin",
    "chi conotoxin",
    "omega conotoxin",
)

# Compile once: exact phrase match with word boundaries, case-insensitive
PHRASE_RE = re.compile(r"\b(?:%s)\b" % "|".join(map(re.escape, _ALLOWED)), re.I)

# UniProt-like P + digits (you asked specifically for Pxxxxxx)
PID_RE = re.compile(r"\b(P\d+)\b")


def parse_fasta_ids(fa_path: str) -> List[Dict[str, int]]:
    """
    Parse a FASTA file, keep only entries whose header contains one of the
    EXACT phrases in _ALLOWED, extract Pxxxxxx IDs, and map them to integers.

    :param fa_path: Path to FASTA file
    :return: List of mappings [{'original_id': 'P00001', 'id': 1}, ...]
    """
    mapping: List[Dict[str, int]] = []
    seen: set[str] = set()

    with open(fa_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.startswith(">"):
                continue

            header = line[1:].strip()
            if not PHRASE_RE.search(header):
                continue  # skip if header lacks an exact allowed phrase

            m = PID_RE.search(header)
            if not m:
                continue  # no Pxxxxxx id in this header

            original_id = m.group(1)
            if original_id in seen:
                continue

            seen.add(original_id)
            # Convert 'P00001' -> 1 (strip 'P' and leading zeros safely)
            int_part = original_id[1:]
            int_id = int(int_part.lstrip("0") or "0")
            mapping.append({"original_id": original_id, "id": int_id})

    return mapping


# 2. FROM ID LIST: ------------------------------------------------------------------------------
#   2.1. GENERAL DATA from id + xml:
#       2.1.1. Generate reduced xml:

# minimal sanitization for later parsing
_XML_SAFE = {"amp", "lt", "gt", "quot", "apos"}
_ENTITY_RE = re.compile(r"&([A-Za-z][A-Za-z0-9]+);")
_AMP_FIX_RE = re.compile(r"&(?!(?:#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z][A-Za-z0-9]*;))")
_ILLEGAL_XML10 = re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]")  # allow \t \n \r


def _entry_matches(block: str, id: list) -> bool:
    try:
        _ids = id
    except Exception:
        _ids = []
    TARGET_IDS = {f"P{n:05d}" for n in _ids}  # 1 -> P00001
    # Extract first <id>...</id>, normalize spaces (handles 'P   74'), and compare
    m = _ID_RE.search(block)
    if not m:
        return False
    raw = m.group(1)
    cono_id = re.sub(r"\s+", "", raw)  # 'P   74' -> 'P74'
    # Zero-pad if needed (ConoServer uses Pxxxxx; many files already have padding)
    if cono_id.startswith("P") and cono_id[1:].isdigit():
        # Normalize to the canonical Pxxxxx for matching
        try:
            n = int(cono_id[1:])
            cono_id = f"P{n:05d}"
        except ValueError:
            pass
    return cono_id in TARGET_IDS


def _html_entities_to_unicode(s: str) -> str:
    def repl(m):
        name = m.group(1)
        if name in _XML_SAFE:
            return m.group(0)
        cp = name2codepoint.get(name)
        return chr(cp) if cp else m.group(0)

    return _ENTITY_RE.sub(repl, s)


def _sanitize_block(s: str) -> str:
    # Remove illegal XML chars, convert &alpha;→α, and escape stray '&'
    s = _ILLEGAL_XML10.sub("", s)
    s = _html_entities_to_unicode(s)
    s = _AMP_FIX_RE.sub("&amp;", s)
    return s


# stream entry blocks and filter by <id>
_START_RE = re.compile(r"<entry\b", re.I)
_END_RE = re.compile(r"</entry>", re.I)
_ID_RE = re.compile(r"<id>\s*([^<]+?)\s*</id>", re.I | re.S)


def filter_entries(in_path: str, out_path: str, id: list) -> None:
    kept = 0
    with (
        open(in_path, "r", encoding="utf-8", errors="replace") as fin,
        open(out_path, "w", encoding="utf-8") as fout,
    ):

        # write a tiny root so the filtered file is well-formed XML
        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n<conoserver>\n')

        buf = []
        depth = 0

        for raw in fin:

            starts = len(_START_RE.findall(raw))
            ends = len(_END_RE.findall(raw))

            if depth == 0 and starts:
                depth = starts - ends
                buf = [raw]
                if depth == 0:
                    block = "".join(buf)
                    if _entry_matches(block, id=id):
                        fout.write(_sanitize_block(block))
                        kept += 1
                continue

            if depth > 0:
                buf.append(raw)
                depth += starts - ends
                if depth == 0:
                    block = "".join(buf)
                    if _entry_matches(block, id=id):
                        fout.write(_sanitize_block(block))
                        kept += 1
                    buf = []

        fout.write("\n</conoserver>\n")

    print(f"Kept {kept} entries → {out_path}")


#       2.1.2. Extract GENERAL DATA from reduced xml to csv:
_ID_SPACES = re.compile(r"\s+")


def _normalize_cono_id(raw: str):
    """
    Normalize things like 'P   74' -> ('P00074', 74).
    Returns (cono_id_str, int_id_or_empty_str).
    """
    if not raw:
        return "", ""
    s = _ID_SPACES.sub("", raw.strip())  # remove interior spaces
    if s.startswith("P"):
        num = s[1:]
        if num.isdigit():
            n = int(num)
            return f"P{n:05d}", n
    return s, ""  # fallback


def filtered_to_csv(
    xml_filtered_path: str, out_csv: str = "conoserver_subset.csv"
) -> int:
    """
    Parse the filtered ConoServer XML and dump a CSV with:
    id (int), cono_id (Pxxxxx), name, sequence, pharmacologicalFamily.
    Returns the number of rows written (excluding header).
    """
    rows = 0
    with open(out_csv, "w", newline="", encoding="utf-8") as fout:
        w = csv.writer(fout)
        w.writerow(["id", "cono_id", "name", "sequence", "pharmacologicalFamily"])

        for event, elem in ET.iterparse(xml_filtered_path, events=("end",)):
            if elem.tag != "entry":
                continue

            raw_id = elem.findtext("id") or ""
            cono_id, int_id = _normalize_cono_id(raw_id)

            name = (elem.findtext("name") or "").strip()
            seq = (elem.findtext("sequence") or "").strip()
            pharm = (elem.findtext("pharmacologicalFamily") or "").strip()

            w.writerow([int_id, cono_id, name, seq, pharm])
            rows += 1
            elem.clear()  # free memory
    return rows


# 2.2. Scrape ACTIVITY DATA from conoserver card for ACTIVITY (target, targeting organism)
#   2.2.1. Scrape ACTIVITY DATA and save to a folder (csv+json) per peptide
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ConoScraper/1.0; +https://example.local/)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

DEFAULT_CARD_URL = (
    "https://www.conoserver.org/index.php?page=card&table=protein&id={id}"
)


def _safe_label(s: str) -> str:
    return re.sub(r"[^\w\d\-_.]+", "_", s).strip("_")[:120] or "label"


class ConoServerCard:
    """
    OOP wrapper for fetching + extracting ConoServer protein card pages.
    """

    def __init__(self, url: Optional[str] = None, html: Optional[str] = None) -> None:
        """
        Provide either url or html (raw page). If url provided and html not provided,
        the object will fetch the page when `fetch()` or `extract_all()` is called.
        """
        if url is None and html is None:
            raise ValueError("Either 'url' or 'html' must be provided.")
        self.url = url
        self.html = html
        self.soup = None
        self.id = self._extract_id_from_url() if url else None
        self.result: Dict = {}

    # -------------
    # fetching / soup
    # -------------
    def fetch(self, timeout: int = 20) -> str:
        if self.html is not None:
            return self.html
        if not self.url:
            raise RuntimeError("No URL available to fetch.")
        resp = requests.get(self.url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        self.html = resp.text
        return self.html

    def _get_soup(self):
        if self.soup is not None:
            return self.soup
        html = self.fetch()
        # prefer lxml but fallback to built-in parser
        try:
            self.soup = BeautifulSoup(html, "lxml")
        except Exception:
            self.soup = BeautifulSoup(html, "html.parser")
        return self.soup

    # -------------------
    # helpers / id parsing
    # -------------------
    def _extract_id_from_url(self) -> Optional[str]:
        if not self.url:
            return None
        m = re.search(r"[?&]id=(\d+)\b", self.url)
        if m:
            return m.group(1)
        # try to find common alternative patterns (e.g. id=405 at end)
        m2 = re.search(r"\b/(\d+)(?:/|$)", self.url)
        if m2:
            return m2.group(1)
        return None

    def ensure_id(self):
        # if id still unknown, try to find from HTML (e.g., title or link)
        if self.id:
            return self.id
        soup = self._get_soup()
        # try h1 href anchor like <h1><a href='?page=card&table=protein&id=405'>EpI</a>...
        a = soup.find("h1")
        if a:
            href = a.find("a")
            if href and href.has_attr("href"):
                m = re.search(r"[?&]id=(\d+)\b", href["href"])
                if m:
                    self.id = m.group(1)
                    return self.id
        # fallback: timestamp-based id
        self.id = datetime.utcnow().strftime("noid_%Y%m%d%H%M%S")
        return self.id

    # -------------------
    # parsing: fields
    # -------------------
    def _parse_card_tables(self) -> Dict[str, str]:
        soup = self._get_soup()
        out: Dict[str, str] = {}
        # ConoServer uses table.cardtable for many panels
        for table in soup.find_all("table", class_=lambda c: c and "cardtable" in c):
            for tr in table.find_all("tr"):
                cols = tr.find_all("td")
                if len(cols) >= 2:
                    left = cols[0].get_text(" ", strip=True).rstrip(":")
                    right = " ".join(c.get_text(" ", strip=True) for c in cols[1:])
                    if left:
                        out[left] = right
        # fallback to any th/td pairs if nothing found
        if not out:
            for table in soup.find_all("table"):
                for tr in table.find_all("tr"):
                    th = tr.find("th")
                    tds = tr.find_all("td")
                    if th and tds:
                        key = th.get_text(" ", strip=True)
                        val = " ".join(td.get_text(" ", strip=True) for td in tds)
                        out[key] = val
        return out

    def _extract_sequence(self) -> Optional[str]:
        soup = self._get_soup()
        seq_div = soup.find("div", class_=lambda c: c and "seq" in c)
        if seq_div:
            return seq_div.get_text(" ", strip=True)
        cardseq = soup.find("td", class_=lambda c: c and "cardsequence" in c)
        if cardseq:
            return cardseq.get_text(" ", strip=True)
        return None

    # -------------------
    # parsing: activity
    # -------------------
    def _parse_table_to_records(self, tbl: Tag) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        all_trs = tbl.find_all("tr")
        if not all_trs:
            return rows
        header_cells: List[str] = []
        header_row_index: Optional[int] = None
        for i, tr in enumerate(all_trs[:3]):
            ths = tr.find_all("th")
            if ths:
                header_cells = [
                    th.get_text(" ", strip=True) or f"col{i}"
                    for i, th in enumerate(ths)
                ]
                header_row_index = i
                break
        if not header_cells:
            first_cells = all_trs[0].find_all(["td", "th"])
            header_cells = [
                c.get_text(" ", strip=True) or f"col{i}"
                for i, c in enumerate(first_cells)
            ]
            header_row_index = 0
        for tr in all_trs[header_row_index + 1 :]:
            cols = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
            if len(cols) < len(header_cells):
                cols += [""] * (len(header_cells) - len(cols))
            elif len(cols) > len(header_cells):
                cols = cols[: len(header_cells)]
            record = dict(zip(header_cells, cols))
            rows.append(record)
        return rows

    def _find_activity_fieldset(self) -> Optional[Tag]:
        soup = self._get_soup()
        legend = soup.find("legend", string=re.compile(r"\bActivity\b", re.I))
        if legend:
            return legend.find_parent("fieldset")
        node = soup.find(
            lambda t: getattr(t, "name", "") in ("h1", "h2", "h3", "h4")
            and re.search(r"\bActivity\b", t.get_text(), re.I)
        )
        if node:
            p = node
            while p and p.name != "fieldset":
                p = p.parent
            return p
        return None

    def _extract_activity(self) -> Dict[str, List[Dict[str, str]]]:
        out: Dict[str, List[Dict[str, str]]] = {}
        fs = self._find_activity_fieldset()
        if not fs:
            # fallback: collect tables with class activitytable
            soup = self._get_soup()
            for tbl in soup.find_all(
                "table", class_=lambda c: c and "activitytable" in c
            ):
                recs = self._parse_table_to_records(tbl)
                out.setdefault("Activity_misc", []).extend(recs)
            return out

        current_label = "Activity"
        for child in fs.find_all(recursive=False):
            if isinstance(child, NavigableString):
                continue
            if child.name in ("h1", "h2", "h3", "h4", "h5"):
                current_label = child.get_text(" ", strip=True)
                continue
            if child.name == "table":
                recs = self._parse_table_to_records(child)
                if recs:
                    out.setdefault(current_label, []).extend(recs)
                continue
            inner_tables = child.find_all("table")
            for tbl in inner_tables:
                recs = self._parse_table_to_records(tbl)
                if recs:
                    out.setdefault(current_label, []).extend(recs)
        return out

    # -------------------
    # public extraction
    # -------------------
    def extract_all(self) -> Dict:
        """
        Perform full extraction and return the result dict; also store in self.result.
        """
        soup = self._get_soup()
        result: Dict = {}
        result["source_url"] = self.url or ""
        fields = self._parse_card_tables()
        seq = self._extract_sequence()
        if seq:
            fields.setdefault("Sequence", seq)
        result["fields"] = fields
        result["activity"] = self._extract_activity()
        # snippet for debugging
        fs = self._find_activity_fieldset()
        result["activity_snippet"] = str(fs)[:8000] if fs else None
        self.result = result
        # ensure id available
        self.ensure_id()
        return result

    # -------------------
    # saving
    # -------------------
    def save(self, outdir: str, prefix: Optional[str] = None) -> Path:
        """
        Save extraction result to a folder: outdir/<id>/
        Returns the folder Path.
        """
        if not self.result:
            raise RuntimeError("No extracted result to save. Call extract_all() first.")

        id_str = self.ensure_id()
        folder = Path(outdir) / str(id_str)
        folder.mkdir(parents=True, exist_ok=True)

        # filenames
        prefix = prefix or f"protein_{id_str}"
        json_path = folder / f"{prefix}.json"
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(self.result, fh, indent=2, ensure_ascii=False)

        # fields CSV (one row)
        fields = self.result.get("fields", {}) or {}
        fields_csv = folder / f"{prefix}_fields.csv"
        try:
            if pd is not None:
                pd.DataFrame([fields]).to_csv(str(fields_csv), index=False)
            else:
                with open(fields_csv, "w", encoding="utf-8", newline="") as fh:
                    writer = csv.writer(fh)
                    writer.writerow(["field", "value"])
                    for k, v in fields.items():
                        writer.writerow([k or "", v or ""])
        except Exception as e:
            print("Warning: failed to write fields CSV:", e, file=sys.stderr)

        # activity JSON
        activity_json = folder / f"{prefix}_activity.json"
        with open(activity_json, "w", encoding="utf-8") as fh:
            json.dump(self.result.get("activity", {}), fh, indent=2, ensure_ascii=False)

        # write per-activity CSVs
        for label, records in (self.result.get("activity") or {}).items():
            safe = _safe_label(label)
            csv_path = folder / f"{prefix}_activity_{safe}.csv"
            try:
                if pd is not None and records:
                    pd.DataFrame(records).to_csv(str(csv_path), index=False)
                else:
                    # jsonlines fallback
                    with open(str(csv_path) + ".jsonl", "w", encoding="utf-8") as fh:
                        for rec in records:
                            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            except Exception as e:
                print(
                    f"Warning: failed to write activity file for {label}: {e}",
                    file=sys.stderr,
                )

        return folder


# 3. ENRICH GENERAL DATA WITH ACTIVITY DATA ---------------------------------------------------------
def _find_case_insensitive(fieldnames, target_name):
    t = target_name.lower()
    for f in fieldnames or []:
        if f.lower() == t:
            return f
    return None


def _iter_pairs_from_file(csv_path):
    """
    Yield (Target, Organism) pairs from one activity CSV.
    Keeps ONLY rows where BOTH are non-empty after strip(),
    and Organism is NOT 'unknown' or 'unidentified' (case-insensitive).
    """
    with open(csv_path, "r", encoding="utf-8", errors="replace", newline="") as f:
        rdr = csv.DictReader(f)
        if not rdr.fieldnames:
            return
        tcol = _find_case_insensitive(rdr.fieldnames, "Target")
        ocol = _find_case_insensitive(rdr.fieldnames, "Organism")
        if not tcol or not ocol:
            return
        for row in rdr:
            t = (row.get(tcol) or "").strip()
            o = (row.get(ocol) or "").strip()
            if not (t and o):
                continue
            if o.lower().strip() in {"unknown", "unidentified"}:
                continue
            yield (t, o)


def _pairs_for_id(outputs_dir: Path, id_val: str):
    """Collect unique (Target, Organism) pairs for one id across all matching files."""
    folder = outputs_dir / id_val
    if not folder.is_dir():
        return []
    pattern = str(folder / f"protein_{id_val}_activity*.csv")
    pairs, seen = [], set()
    for fp in sorted(glob.glob(pattern)):
        for pair in _iter_pairs_from_file(fp):
            if pair not in seen:
                seen.add(pair)
                pairs.append(pair)
    return pairs


def augment_conoserver_with_targets_only_valid(
    conoserver_csv: str = "conoserver.csv",
    outputs_dir: str = "outputs",
    out_csv: str = "conoserver_with_targets.csv",
) -> int:
    """
    Read conoserver.csv (must have column 'id'), collect Target/Organism pairs from
    outputs/<id>/protein_<id>_activity*.csv, and write ONLY rows where BOTH Target and
    Organism are present and Organism is not 'unknown'/'unidentified'.
    Rows/IDs with no valid pair are dropped.
    Returns number of rows written (excluding header).
    """
    outputs_dir = Path(outputs_dir)
    rows_out = 0

    with open(
        conoserver_csv, "r", encoding="utf-8", errors="replace", newline=""
    ) as fin:
        rdr = csv.DictReader(fin)
        base_fields = list(rdr.fieldnames or [])
        for col in ("Target", "Organism"):
            if col not in base_fields:
                base_fields.append(col)

        with open(out_csv, "w", encoding="utf-8", newline="") as fout:
            w = csv.DictWriter(fout, fieldnames=base_fields)
            w.writeheader()

            for row in rdr:
                id_raw = (row.get("id") or "").strip()
                if not id_raw:
                    continue
                try:
                    id_norm = str(int(id_raw))  # folders named 1,2,3...
                except ValueError:
                    id_norm = id_raw

                pairs = _pairs_for_id(outputs_dir, id_norm)

                for t, o in pairs:
                    out_row = dict(row)
                    out_row["Target"] = t
                    out_row["Organism"] = o
                    w.writerow(out_row)
                    rows_out += 1

    return rows_out


# 4. INSPECT ORGANISMS FOR INSECTA ----------------------------------------------------------------
def inspect_organisms(csv_file: str = "conoserver.csv"):
    df = pd.read_csv(csv_file)
    orgs = df["Organism"].dropna().astype(str).str.strip()
    orgs = orgs[orgs.ne("")]
    counts = orgs.value_counts()
    for name, n in counts.items():
        print(f"{name}: {n}")


# 5. INSPECT UNIQUE IDs:
def _norm_id(x: str) -> str:
    """Normalize ids so '00123' and '123' compare equal."""
    x = (x or "").strip()
    try:
        return str(int(x))
    except Exception:
        return x


def check_id_uniqueness(
    original_csv="conoserver.csv", augmented_csv="conoserver_with_targets.csv"
):
    # load ids
    with open(original_csv, encoding="utf-8", newline="") as f:
        orig_ids = [_norm_id(r.get("id", "")) for r in csv.DictReader(f)]
    with open(augmented_csv, encoding="utf-8", newline="") as f:
        aug_rows = list(csv.DictReader(f))
        aug_ids = [_norm_id(r.get("id", "")) for r in aug_rows]

    # quick stats
    orig_set, aug_set = set(orig_ids), set(aug_ids)
    dup_counts = Counter(aug_ids)
    dup_counts = {k: c for k, c in dup_counts.items() if c > 1}

    print(f"Unique peptides with pharmacological families:  {len(orig_set):,}")
    print(f"Unique peptides with target & targeting_organism: {len(aug_set):,}")
    bad = [
        r
        for r in aug_rows
        if not (r.get("Target", "").strip() and r.get("Organism", "").strip())
    ]
    print(f"Entry missing target or targeting_organism in {augmented_csv}: {bad} ")
