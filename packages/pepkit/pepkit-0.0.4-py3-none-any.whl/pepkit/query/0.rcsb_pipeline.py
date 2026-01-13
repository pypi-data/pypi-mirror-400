import pandas as pd
from rcsbapi.search import search_attributes as attrs
import sys, shutil, os, logging
from pathlib import Path

parent_folder = Path(__file__).resolve().parent.parent
print(parent_folder)
sys.path.insert(0, str(parent_folder))
# sys.path.append("/Users/vitran/Documents/Work/Github/Mod1_data")
from mod1_data.pdb import process_pdbs

# -----------------------------------------------------------------------
# RETRIEVE BY RCSB-API
# -----------------------------------------------------------------------
# base = '/Users/vitran/Documents/Work/Github/Mod1_data'
base = parent_folder
n_jobs = 8
# Peptide related queries
q1 = attrs.rcsb_pubmed_abstract_text.contains_words("peptide")
q2 = attrs.chem_comp.type.in_(
    [
        "L-peptide linking",
        "L-peptide NH3 amino terminus",
        "L-peptide COOH carboxy terminus",
    ]
)
q3 = attrs.pdbx_molecule_features.details.contains_words("peptide")
q4 = attrs.struct_keywords.text.contains_words("peptide")
q5 = attrs.rcsb_entry_info.resolution_combined.less_or_equal(3.0)
# Exclude monomer complexes
q6 = ~attrs.rcsb_struct_symmetry.oligomeric_state.exact_match("Monomer")
# Availability of PDB structure
q7 = attrs.pdbx_database_status.pdb_format_compatible.exact_match("Y")
# Experimental method
q8 = attrs.exptl.method.exact_match("X-RAY DIFFRACTION")
# Exclude DNA | RNA
q9 = ~attrs.rcsb_entry_info.na_polymer_entity_types.in_(
    ["RNA (only)", "DNA (only)", "DNA/RNA (only)", "NA-hybrid (only)"]
)
# Polymer composition (at least has protein)
q10 = attrs.rcsb_entry_info.polymer_composition.in_(
    [
        "heteromeric protein",
        "protein/NA",
        "protein/NA/oligosaccharide",
        "protein/oligosaccharide",
    ]
)
# The number of distinct protein polymer entities.
q11 = attrs.rcsb_entry_info.polymer_entity_count_protein.greater_or_equal(2)
# RELEASE DATE range
print("Query for peptide-related complexes from RCSB")
## train set: before 2023-01-12 (not in AF3 train+test set: https://doi.org/10.1038/s41586-024-07487-w)
batches = ["1.latest", "0.train"]
for batch in batches:
    os.makedirs(f"{base}/raw_data/14.rcsb/{batch}", exist_ok=True)
    if batch == "0.train":
        q = attrs.rcsb_accession_info.initial_release_date.less("2023-01-12")
        # q = attrs.rcsb_accession_info.initial_release_date.range({"from":'2025-04-01',"to":'2025-06-12'})
    else:
        q = attrs.rcsb_accession_info.initial_release_date.range(
            {"from": "2023-01-12", "to": "2025-10-16"}
        )  # (*****)
        # q = attrs.rcsb_accession_info.initial_release_date.range({"from":'2025-06-12',"to":'2025-10-16'})

    query = q & (q1 | q2 | q3 | q4) & q5 & q6 & q7 & q8 & (q9 | q10) & q11
    pep_results = list(query())
    series_pep_results = pd.Series(pep_results)
    # series_pep_results.to_csv(f"{base}/raw_data/14.rcsb/{batch}/pdb_pep_results.txt", index=False, header = False)
    batch_name = batch.split(".")[1]
    print(
        f"Number of all peptide related structures from {batch_name} set: {len(pep_results)}"
    )

    # Query for homo n-mers complexes (2-1000 mers), to remove them from peptide related results
    # N-mer queries
    print(f"Query for Homo n-mers complexes {batch_name} from rcsb")
    nmers = []
    # Peptide related queries
    # for n in range(2,201):                                                                         #(*****)
    #     print(f"Processing Homo {n}-mer")
    #     # Homo n-mer queries
    #     qq = attrs.rcsb_struct_symmetry.oligomeric_state.exact_match(f"Homo {n}-mer")
    #     query = q & qq
    #     results = list(query())
    #     nmers.extend(results)

    series_nmers = pd.Series(nmers)
    # series_nmers.to_csv(f"{base}/raw_data/14.rcsb/{batch}/pdb_nmers_results.txt", index=False, header = False)
    print(f"Number of all homo n-mers from {batch_name} set: {len(nmers)}")

    # Filter on homo n-mers
    # pep_results = pd.read_csv(f"{base}/raw_data/14.rcsb/{batch}/pdb_pep_results.txt", header=None)[0].str.strip()
    # nmers = pd.read_csv(f"{base}/raw_data/14.rcsb/{batch}/pdb_nmers_results.txt", header=None)[0].str.strip()

    remain = list(set(pep_results) - set(nmers))
    print(
        f"Peptide related structures from {batch_name} set:\nQuery:{len(pep_results)}. Homo n-mers:{len(nmers)}. Remain:{len(remain)}"
    )
    # remain.to_csv(f"{base}/raw_data/14.rcsb/{batch}/rcsb_queries.txt", index=False, header=False)

    # -----------------------------------------------------------------------
    # CHECK PROTEIN-PEPTIDE COMPLEXES
    # -----------------------------------------------------------------------
    # rcsb = pd.read_csv(f"{base}/raw_data/14.rcsb/{batch}/rcsb_queries.txt", header=None)[0].str.strip().to_list()
    rcsb = remain
    tmp = f"{base}/raw_data/rcsb"
    # Set up logging
    log_file = f"{base}/raw_data/14.rcsb/{batch}/log_canonical.txt"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Clear any existing handlers and configure logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,  # Force reconfiguration
    )
    print(f"Starting PDB processing pipeline")
    print(f"Processing {len(rcsb)} PDB IDs from {batch}")
    if batch == "0.train":  # (*****)
        df, error = process_pdbs(rcsb, tmp, n_jobs=n_jobs, canonical_check=False)
    else:
        df, error = process_pdbs(rcsb, tmp, n_jobs=n_jobs, canonical_check=True)
    print(f"Final DataFrame of {batch_name}:")
    df.info()

    print(f"\nProcessing summary:")
    print(f"Total structures processed: {len(rcsb)}")
    print(f"Successful: {len(df)}")
    print(f"Failed: {len(error)}")
    df.to_csv(
        f"{base}/raw_data/14.rcsb/{batch}/rcsb_prot_pep_complexes_canonical.csv",
        index=False,
    )

# -----------------------------------------------------------------------
# REMOVE REDUNDANCY & OVERLAPPING
# -----------------------------------------------------------------------
import subprocess
from mod1_data.fasta import get_chain_fasta, parallel_fetch_fastas

# Prepare fasta and run mmseqs2
batches = ["1.latest", "0.train"]  # (*****)
# batches = ['1.latest_','0.train_']

for batch in batches:
    # output file paths
    fa_train = f"{base}/raw_data/14.rcsb/{batch}/receptors.fasta"
    error_train = f"{base}/raw_data/14.rcsb/{batch}/error_pdbs.txt"
    # input file paths
    complex_list = (
        f"{base}/raw_data/14.rcsb/{batch}/rcsb_prot_pep_complexes_canonical.csv"
    )
    data = pd.read_csv(complex_list)
    pdb_ids = data["pdb_id"].tolist()
    pep_chains = data["pep_chain"].tolist()
    receptor_chains = data["receptor_chain"].tolist()

    batch_name = batch.split(".")[1]
    # Run MMseqs2 clustering on the fetched FASTA file
    mmseq2_root = f"{base}/mmseqs2"
    mmseqs_path = f"{base}/mmseqs/bin/mmseqs"
    file_path = f"{base}/raw_data/14.rcsb/{batch}/receptors.fasta"

    cmd = [
        mmseqs_path,
        "easy-cluster",
        file_path,
        f"{mmseq2_root}/{batch_name}_out",
        f"{mmseq2_root}/{batch_name}_tmp",
        "--min-seq-id",
        "0.5",
        "-c",
        "0.8",
        "--cov-mode",
        "0",
    ]

    if batch == "1.latest":  # (*****)
        with open(fa_train, "w") as f:
            pass

        results = parallel_fetch_fastas(
            pdb_ids,
            pep_chains,
            receptor_chains,
            fa_train=fa_train,
            error_train=error_train,
            get_chain_fasta=get_chain_fasta,
            n_jobs=n_jobs,
            verbose=4,
        )

        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"Error occurred while processing {file_path}: {e}")
        continue

    else:
        fa = f"{base}/mmseqs2/latest_out_rep_seq.fasta"  # (*****)
        with open(fa, "r") as f:
            lines = f.readlines()
        with open(fa_train, "w") as f:
            f.writelines(lines)

        results = parallel_fetch_fastas(
            pdb_ids,
            pep_chains,
            receptor_chains,
            fa_train=fa_train,
            error_train=error_train,
            get_chain_fasta=get_chain_fasta,
            n_jobs=n_jobs,
            verbose=4,
        )
        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"Error occurred while processing {file_path}: {e}")

latest = pd.read_csv(
    f"{base}/mmseqs2/latest_out_cluster.tsv", sep="\t", header=None
)  # (*****)
train = pd.read_csv(
    f"{base}/mmseqs2/train_out_cluster.tsv", sep="\t", header=None
)  # (*****)

# Get all representatives from latest dataset
latest_cluster = set(latest.iloc[:, 0].to_list())

# Get all representatives from latest-train dataset - keep only entries that appear exactly once
value_counts = train.iloc[:, 0].value_counts()
unique_only = value_counts[value_counts == 1].index.to_list()
train_cluster = unique_only

# Get clean representatives (rep in latest) + (rep in latest-train without any cluster members)
clean_reps = list((set(latest_cluster) & set(train_cluster)))
print(f"Total cluster representatives (receptors) in latest: {len(latest_cluster)}")

# -----------------------------------------------------------------------
# CLEAN_REPS TO CSV
# -----------------------------------------------------------------------
from collections import defaultdict
from mod1_data.fasta import parse_fasta

# Create all.fasta
batch = "1.latest"  # (*****)
complex_list = f"{base}/raw_data/14.rcsb/{batch}/rcsb_prot_pep_complexes_canonical.csv"
fa_all = f"{base}/raw_data/14.rcsb/{batch}/all.fasta"
error_all = f"{base}/raw_data/14.rcsb/{batch}/error_pdbs.txt"
with open(fa_all, "w") as f:
    pass

data = pd.read_csv(complex_list)
pdb_ids = data["pdb_id"].tolist()
pep_chains = data["pep_chain"].tolist()
receptor_chains = data["receptor_chain"].tolist()

results = parallel_fetch_fastas(
    pdb_ids,
    pep_chains,
    receptor_chains,
    fa_train=fa_all,
    error_train=error_all,
    get_chain_fasta=get_chain_fasta,
    n_jobs=n_jobs,
    verbose=4,
    use_both_chains=True,  # fetch both peptide and receptor chains (all.fasta)
)

# Parse the FASTA file
clean_pdb_ids = list(set(rep.split(".")[0] for rep in clean_reps))
all_fasta = f"{base}/raw_data/14.rcsb/{batch}/all.fasta"
sequences = parse_fasta(all_fasta)

# Group sequences by PDB ID
pdb_sequences = defaultdict(list)
for header in sequences.keys():
    # Extract PDB ID (before first dot)
    pdb_id = header.split(".")[0]
    if pdb_id in clean_pdb_ids:
        # Extract chain ID (after dot, keep 'auth' prefix if present)
        if ".auth" in header:
            chain = "auth" + header.split(".auth")[1]
        else:
            chain = header.split(".")[1]
        pdb_sequences[pdb_id].append((chain, header, sequences[header]))

# Create the dataframe
data = []
for pdb_id in clean_pdb_ids:
    if pdb_id in pdb_sequences:
        chains_data = pdb_sequences[pdb_id]

        # First chain is peptide, rest are protein chains
        if chains_data:
            # Sort by the order they appear in the FASTA file (maintain original order)
            peptide_chain, peptide_header, peptide_seq = chains_data[0]

            if len(chains_data) > 1:
                protein_chains = []
                protein_sequences = []

                for chain, header, seq in chains_data[1:]:
                    protein_chains.append(chain)
                    protein_sequences.append(seq)

                protein_chain_str = "".join(protein_chains)
                protein_seq_str = ":".join(protein_sequences)
            else:
                protein_chain_str = ""
                protein_seq_str = ""

            data.append(
                {
                    "pdb_id": pdb_id,
                    "peptide_chain": peptide_chain,
                    "peptide_sequence": peptide_seq,
                    "protein_chain": protein_chain_str,
                    "protein_sequence": protein_seq_str,
                }
            )
        else:
            print(f"Warning: No sequences found for PDB ID {pdb_id}")

# Create DataFrame
df = pd.DataFrame(data)
print(f"Created DataFrame with {len(df)} entries")

df["peptide_length"] = df["peptide_sequence"].str.len()
df["protein_length"] = df["protein_sequence"].str.len()
df = df[df["peptide_length"] <= 50]
df.info()
df.head()
df.to_csv(
    f"{base}/raw_data/14.rcsb/non_redundant_non_overlapping.csv", index=False
)  # (*****)

# move mmseq2 output to corresponding batch folders
batches = ["1.latest", "0.train"]  # (*****)
for batch in batches:
    batch_name = batch.split(".")[1]
    if not os.path.exists(f"{base}/raw_data/14.rcsb/{batch}/mmseqs2_output"):
        os.makedirs(f"{base}/raw_data/14.rcsb/{batch}/mmseqs2_output")
        shutil.move(
            f"{base}/mmseqs2/{batch_name}_out_cluster.tsv",
            f"{base}/raw_data/14.rcsb/{batch}/mmseqs2_output/{batch_name}_out_cluster.tsv",
        )
        shutil.move(
            f"{base}/mmseqs2/{batch_name}_out_rep_seq.fasta",
            f"{base}/raw_data/14.rcsb/{batch}/mmseqs2_output/{batch_name}_out_rep_seq.fasta",
        )
        shutil.move(
            f"{base}/mmseqs2/{batch_name}_out_all_seqs.fasta",
            f"{base}/raw_data/14.rcsb/{batch}/mmseqs2_output/{batch_name}_out_all_seqs.fasta",
        )
print("Pipeline completed successfully.")
