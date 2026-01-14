import gemmi
import os
from typing import Tuple, Dict, List
from ccpem_utils.other.utils import get_unique_id


def set_alignmentstrategy(mode: str = "default"):
    """Set a sequence alignment strategy

    Args:
        mode (str): alignment strategy, defaults to "default".
            Use "no_mismatch" to align with minimum/no substitutions

    Returns:
        gemmi.AlignmentScoring: gemmi AlignmentScoring object with specified strategy
    """
    scoring = gemmi.AlignmentScoring()
    if mode == "no_mismatch":  # best exact match
        scoring.mismatch = -5
        scoring.gape = 0  # no penalty for gap extension
    elif mode != "default":
        raise ValueError(
            "Currently only the 'default' and 'no_mismatch' modes are supported"
        )
    return scoring


def get_seq_identities_exact_match(seq1: str, seq2: str) -> Tuple[float, float]:
    """Align two sequences to maximise match and get identities

    Args:
        seq1 (str): First sequence string
        seq2 (str): Second sequence string

    Returns:
        Tuple[float,float] : Sequence identities w.r.t first and second inputs
    """
    scoring = set_alignmentstrategy(mode="no_mismatch")
    alignment_result = gemmi.align_string_sequences(
        list(seq1), list(seq2), [], scoring=scoring
    )
    return (
        round(alignment_result.calculate_identity(1), 3),
        round(alignment_result.calculate_identity(2), 3),
    )


def find_best_seq_match_identity(
    target_seq: str, search_dict_seq: Dict[str, str]
) -> Tuple[str, float]:
    """Search sequence dictionary for best match against input target sequence

    Args:
        target_seq (str): Sequence to match
        search_dict_seq (Dict[str,str]): dict of sequences

    Returns:
        Tuple[str, float]: matched sequence id and percent identity
    """
    max_identity = 0.0
    best_matchid_search = ""
    for seqid in search_dict_seq:
        identity_search = get_seq_identities_exact_match(
            target_seq, search_dict_seq[seqid]
        )[1]
        if identity_search > max_identity:
            max_identity = identity_search
            best_matchid_search = seqid
    return best_matchid_search, max_identity


def get_input_seq_dict(fastafile: str) -> Dict[str, str]:
    """Get dictionary of sequence from fasta file

    Args:
        fastafile (str): input fasta file

    Returns:
        Dict[str,str]
    """
    k = ""
    with open(fastafile, "r") as s:
        dict_seq: Dict[str, str] = {}
        for line in s:
            lstrip = line.strip()
            if lstrip and k and lstrip[0] != ">":
                try:
                    dict_seq[k] += lstrip
                except KeyError:
                    dict_seq[k] = lstrip
            elif lstrip and lstrip[0] == ">":
                k = lstrip[1:]
    return dict_seq


def merge_set_unique_id_fasta(list_fastafiles: List[str]) -> Dict[str, str]:
    """Merge multiple fasta files and set unique ids"""
    list_seqids: List[str] = []
    dict_seq_all: Dict[str, str] = {}
    for fastafile in list_fastafiles:
        if not os.path.isfile(fastafile):
            raise IOError(f"Input fasta file not found: {fastafile}")
        dict_seq = get_input_seq_dict(fastafile=fastafile)
        file_basename = os.path.splitext(os.path.basename(fastafile))[0]
        for seqid in dict_seq.keys():
            new_seqid = seqid
            if len(list_fastafiles) > 1:
                new_seqid = file_basename + "_" + seqid  # add file name to id
            if new_seqid in list_seqids:
                new_seqid = get_unique_id(new_seqid, list_seqids)
            dict_seq_all[new_seqid] = dict_seq[seqid]
            list_seqids.append(new_seqid)
    return dict_seq_all
