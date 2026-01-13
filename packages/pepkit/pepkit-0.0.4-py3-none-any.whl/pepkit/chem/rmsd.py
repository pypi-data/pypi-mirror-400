import sys

sys.path.append("/Users/vitran/Documents/Work/Github/Insectipep")
import numpy as np
from Bio.Align import PairwiseAligner, substitution_matrices
from insectipep.utils import parse_pdb_chain, alignment_to_gapped_strings


def map_by_sequence(seqA: str, seqB: str, aligner: PairwiseAligner | None = None):
    """
    Align seqA and seqB using Bio.Align.PairwiseAligner and return:
      - mapping dict idxA -> idxB (0-based indices in the original ungapped sequences)
      - gapped alignment strings alnA, alnB (with '-')
    Behavior:
      - By default uses a global aligner tuned to prefer matches; tune the aligner if needed.
    """
    if aligner is None:
        aligner = PairwiseAligner()
        aligner.mode = "global"
        # sensible default scores to prefer matches, allow some gaps
        # aligner.match_score = 1.0
        # aligner.mismatch_score = -1.0 # 0.0 to replicate globalxx
        # aligner.open_gap_score = -0.5
        # aligner.extend_gap_score = -0.1

        # # Uncomment for BLOSSSUM62 matrix
        aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
        aligner.open_gap_score = -10.0
        aligner.extend_gap_score = -0.5

    alignments = aligner.align(seqA, seqB)
    if len(alignments) == 0:
        raise ValueError("No alignment produced between sequences.")

    alignment = alignments[0]  # best alignment
    alnA, alnB = alignment_to_gapped_strings(seqA, seqB, alignment)

    # Build mapping: iterate through aligned strings, count non-gap positions.
    mapAtoB = {}
    iA = iB = 0
    for ca, cb in zip(alnA, alnB):
        if ca != "-" and cb != "-":
            mapAtoB[iA] = iB
        if ca != "-":
            iA += 1
        if cb != "-":
            iB += 1

    return mapAtoB, alnA, alnB


def kabsch_rmsd(P, Q):
    """
    P, Q: numpy arrays shape (N,3) in corresponding order.
    Return RMSD after optimal rotation (Kabsch).
    """
    if P.shape != Q.shape:
        raise ValueError("P and Q must have the same shape")
    N = P.shape[0]
    # center
    Pc = P - P.mean(axis=0)
    Qc = Q - Q.mean(axis=0)
    # covariance
    C = Pc.T @ Qc
    V, S, Wt = np.linalg.svd(C)
    # ensure right-handedness
    d = np.linalg.det(V @ Wt)
    D = np.diag([1.0, 1.0, np.sign(d)])  # sign(d) is +1 or -1
    U = V @ D @ Wt
    P_rot = Pc @ U
    diff = P_rot - Qc
    rmsd = np.sqrt((diff * diff).sum() / N)
    return float(rmsd)


def compute_rmsd(pdb_a, chain_a, pdb_b, chain_b, atomname="CA", min_matches=50):
    """
    High-level function:
      - parses pdb_a and pdb_b for the given chains and atomname
      - aligns sequences built from residues that actually contain that atom
      - maps matched indices, builds coordinate arrays, runs Kabsch RMSD
    Returns:
      {
        "rmsd": float,
        "n_matched": int,
        "coverage_a": float,
        "coverage_b": float,
        "matched_pairs": [(resseq_a, resseq_b), ...]
      }
    Raises ValueError if too few matched residues.
    """
    resseqsA, seqA, coordsA = parse_pdb_chain(pdb_a, chain_a, atomname=atomname)
    resseqsB, seqB, coordsB = parse_pdb_chain(pdb_b, chain_b, atomname=atomname)

    if len(seqA) == 0 or len(seqB) == 0:
        raise ValueError(
            "One chain has no residues with the chosen atom; cannot align/compare."
        )

    mapping, alnA, alnB = map_by_sequence(seqA, seqB)
    P_list = []
    Q_list = []
    matched_pairs = []
    for idxA, idxB in mapping.items():
        # sanity-check indices within coordinate lists
        if idxA < 0 or idxA >= len(coordsA):
            continue
        if idxB < 0 or idxB >= len(coordsB):
            continue
        ca = coordsA[idxA]
        cb = coordsB[idxB]
        # skip if any coordinate is None (shouldn't happen here)
        if ca is None or cb is None:
            continue
        P_list.append(ca)
        Q_list.append(cb)
        matched_pairs.append((resseqsA[idxA], resseqsB[idxB]))

    if len(P_list) < min_matches:
        raise ValueError(
            f"Too few matched residues for meaningful RMSD (found {len(P_list)})."
        )

    P = np.vstack(P_list)
    Q = np.vstack(Q_list)
    rmsd = kabsch_rmsd(P, Q)
    n_matched = P.shape[0]
    coverage_a = n_matched / max(1, len(seqA))
    coverage_b = n_matched / max(1, len(seqB))

    return {
        "rmsd": rmsd,
        "n_matched": n_matched,
        "coverage_a": coverage_a,
        "coverage_b": coverage_b,
        "matched_pairs": matched_pairs,
        "alignment_a": alnA,
        "alignment_b": alnB,
    }


if __name__ == "__main__":
    # pdb_ref = '/Users/vitran/Documents/Work/Github/AF/ColabFold_out/selected/ref/2NXX_H.pdb'
    # pdb_model = '/Users/vitran/Documents/Work/Github/AF/ColabFold_out/selected/A1JUG3_2NXX_H_uniprot + arachnoserver_P11057.pdb'
    # chain_ref = "H"
    # chain_model = "A"

    pdb_ref = "/Users/vitran/Documents/Work/Github/AF/insectipep_offtarget/selected/ref/3SSB_A.pdb"
    pdb_model = "/Users/vitran/Documents/Work/Github/AF/insectipep_offtarget/selected/P82176_3SSB_A_uniprot_P0DPG7.pdb"
    chain_ref = "A"
    chain_model = "A"

    try:
        out = compute_rmsd(pdb_model, chain_model, pdb_ref, chain_ref, atomname="CA")
    except Exception as e:
        print("ERROR:", e)
    else:
        print(f"RMSD (on {out['n_matched']} residues): {out['rmsd']:.3f} Å")
        print(
            f"Coverage model: {out['coverage_a']*100:.1f}%; Coverage ref: {out['coverage_b']*100:.1f}%"
        )

        print("Alignment query:", out["alignment_a"])
        print("Alignment reference:", out["alignment_b"])
