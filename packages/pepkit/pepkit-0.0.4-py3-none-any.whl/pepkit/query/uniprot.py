from __future__ import annotations
import io, re, time, os, json, requests
import pandas as pd
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from insectipep.models import PeptideRaw


# 1. PEPTIDE QUERY
UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb/search"
ENTRY_JSON = "https://rest.uniprot.org/uniprotkb/{acc}.json"

DEFAULT_QUERY = "cc_function:(insecti*) AND length:[2 TO 51]"
FIELDS = ",".join(
    [
        "accession",
        "id",
        "protein_name",
        "sequence",
        "length",
        "keyword",
        "xref_pdb",
        "xref_alphafolddb",
        "go_f",
        "cc_function",
        "cc_miscellaneous",
        "organism_name",
    ]
)


# Query -> TSV -> DataFrame
def uniprot_query(
    query: str = DEFAULT_QUERY, field: str = FIELDS, size: int = 500
) -> pd.DataFrame:
    """
    Function to query request from uniprot and return single TSV based on query
    normalize column names
    """
    params = {
        "query": query,
        "fields": field,
        "format": "tsv",
        "size": size,
    }
    base = "https://rest.uniprot.org/uniprotkb/search"

    r = requests.get(base, params=params)
    # r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), sep="\t")
    # Normalize column names to keys
    col_map = {
        "Entry": "accession",
        "Entry Name": "id",
        "Protein names": "protein_name",
        "Sequence": "sequence",
        "Length": "length",
        "Keywords": "keyword",
        "Cross-reference (PDB)": "xref_pdb",
        "Cross-reference (AlphaFoldDB)": "xref_alphafolddb",
        "Gene Ontology (molecular function)": "go_f",
        "Function [CC]": "cc_function",
        "Miscellaneous [CC]": "cc_miscellaneous",
        "Organism": "organism_name",
        "Organism (ID)": "organism_id",
    }
    present = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=present)
    return df


# 2. From QUERY results, get JSON and enrich with additional fields (FUNCTION, MISC/TOXIC DOSE, PMIDs)
# Fetch JSON
def fetch_json(acc: str, max_retries: int = 4, backoff: float = 0.8) -> Optional[dict]:
    """
    Fetch a json file based on accession number {acc}
    url = https://rest.uniprot.org/uniprotkb/{acc}.json
    """
    for i in range(max_retries):
        try:
            r = requests.get(
                ENTRY_JSON.format(acc=acc),
                headers={"Accept": "application/json"},
                timeout=40,
            )
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(backoff * (2**i))
                continue
            return None
        except requests.RequestException:
            time.sleep(backoff * (2**i))
    return None


# Parse JSON fields
def parse_json_fields(
    j: Optional[dict],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Function to parse a json file.
    Return (pmids, function_texts, mf_keywords, org_texts, negative_notes)
      - function_texts: values if 'commentType'=='FUNCTION'
      - mf_keywords:    name if 'category'=='Molecular function'
      - org_texts:      MISC/TOXIC DOSE values NOT starting with 'Negative results:'
      - negative_notes: MISC/TOXIC DOSE values starting with 'Negative results:' (prefix removed)
      - pmids:          FUNCTION-only (EVIDENCES ONLY)
    """
    if not j:
        return ([], [], [], [], [])

    pmids: set[str] = set()
    function_texts: list[str] = []
    mf_keywords: list[str] = []
    org_texts: list[str] = []
    negative_notes: list[str] = []

    # Parse "comment" -> "commentType" > FUNCTION (for targets + pmids), MISC/TOXIC DOSE (for org/negatives)
    for c in j.get("comments") or []:
        ctype = c.get("commentType")

        if ctype == "FUNCTION":
            for t in c.get("texts") or []:
                val = t.get("value")
                if isinstance(val, str) and val:
                    function_texts.append(val)

                # FUNCTION evidences ONLY
                for ev in t.get("evidences") or []:
                    if (
                        isinstance(ev, dict)
                        and ev.get("source") == "PubMed"
                        and ev.get("id")
                    ):
                        pmids.add(f"PMID:{ev['id']}")

        elif ctype in {"MISCELLANEOUS", "TOXIC DOSE"}:
            for t in c.get("texts") or []:
                val = t.get("value")
                if not isinstance(val, str) or not val:
                    continue
                if val.startswith("Negative results:"):
                    cleaned = re.sub(r"^Negative results:\s*", "", val).strip()
                    if cleaned:
                        negative_notes.append(cleaned)
                else:
                    org_texts.append(val)

    # Keywords → add to inference pool
    for k in j.get("keywords") or []:
        if k.get("category") == "Molecular function":
            name = k.get("name")
            if isinstance(name, str) and name:
                mf_keywords.append(name)

    return pmids, function_texts, mf_keywords, org_texts, negative_notes


# Enrich with additional fields:
#   - Dump to uniprot/uniprot_query/JSON files
#   - Return to a DataFrame
#   - Return enriched class PeptideRaw


def enrich(
    df: pd.DataFrame, max_workers: int = 8, outdir="data/uniprot/uniprot_raw.csv"
) -> pd.DataFrame:
    if "accession" not in df.columns:
        return df
    if df.empty:
        df = df.assign(
            pmids=pd.Series(dtype=str),
            sequence=pd.Series(dtype=str),
            function_texts=pd.Series(dtype=object),
            mf_keywords=pd.Series(dtype=object),
            org_texts=pd.Series(dtype=object),
            negative_notes=pd.Series(dtype=object),
        )
        return df

    accs = df["accession"].tolist()
    results = {}
    peptides = []
    df_out = pd.DataFrame()
    os.makedirs(outdir, exist_ok=True)

    with ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(accs)))) as ex:
        futs = {ex.submit(fetch_json, acc): acc for acc in accs}
        for fut in as_completed(futs):
            acc = futs[fut]
            j = fut.result()
            pmids, function_texts, mf_keywords, org_texts, negative_notes = (
                parse_json_fields(j)
            )
            seq = j.get("sequence", {}).get("value") if j else None
            sequence = seq if isinstance(seq, str) else None
            peptide = PeptideRaw(
                acc=acc,
                pmids=list(pmids),
                sequence=sequence,
                function_texts=function_texts,
                mf_keywords=mf_keywords,
                org_texts=org_texts,
                negative_notes=negative_notes,
            )
            results[acc] = peptide
            peptides.append(peptide)
            filepath = os.path.join(outdir, f"{acc}.json")
            with open(filepath, "w") as f:
                json.dump(asdict(peptide), f, indent=2)
    df_out = df_out.assign(
        acc=[results[acc].acc for acc in accs],
        pmids=[results[acc].pmids for acc in accs],
        sequence=[results[acc].sequence for acc in accs],
        function_texts=[results[acc].function_texts for acc in accs],
        mf_keywords=[results[acc].mf_keywords for acc in accs],
        org_texts=[results[acc].org_texts for acc in accs],
        negative_notes=[results[acc].negative_notes for acc in accs],
    )

    return peptides, df_out


def uniprot_enrich(
    query: str, field: str, path: str = "data/uniprot/uniprot_raw.csv"
) -> list[PeptideRaw]:
    """
    Wrapping function from query to enrichment.
    Retrieve JSON files for all query results and save enriched DataFrame.
    """
    uniprot_q = uniprot_query(query=query, field=field)
    peptidesraw, json_df = enrich(df=uniprot_q, outdir="data/uniprot/uniprot_query")
    json_df.to_csv(path, index=False)
    print(f"Uniprot query results saved to: {path}")

    return peptidesraw
