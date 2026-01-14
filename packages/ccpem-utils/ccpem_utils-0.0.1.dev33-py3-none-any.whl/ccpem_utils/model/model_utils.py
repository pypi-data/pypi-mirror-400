import re
import os
from Bio.PDB import PDBParser, Selection
from Bio import SeqIO, pairwise2
import types
from collections import OrderedDict

dictaa_3letters = {
    "P": "PRO",
    "S": "SER",
    "G": "GLY",
    "L": "LEU",
    "T": "THR",
    "V": "VAL",
    "I": "ILE",
    "M": "MET",
    "C": "CYS",
    "F": "PHE",
    "Y": "TYR",
    "W": "TRP",
    "A": "ALA",
    "K": "LYS",
    "R": "ARG",
    "D": "ASP",
    "E": "GLU",
    "N": "ASN",
    "Q": "GLN",
    "H": "HIS",
}

dictaa_1letter = {
    "VAL": "V",
    "ILE": "I",
    "LEU": "L",
    "GLU": "E",
    "GLN": "Q",
    "ASP": "D",
    "ASN": "N",
    "HIS": "H",
    "TRP": "W",
    "PHE": "F",
    "TYR": "Y",
    "ARG": "R",
    "LYS": "K",
    "SER": "S",
    "THR": "T",
    "MET": "M",
    "ALA": "A",
    "GLY": "G",
    "PRO": "P",
    "CYS": "C",
}

dssp_sse_desc = {
    "H": "helix",
    "E": "strand",
    "T": "turn",
    "B": "beta bridge",
    "G": "helix-3",
    "I": "helix-5",
    "S": "bend",
}
# the mutation results in loss of polar atoms in the side-chain
# and interactions involving them
list_residues_polar = ["T", "S", "H", "N", "Q", "D", "E", "K", "R", "Y", "W"]
# the mutation results in loss of aromatic side-chain and interactions
# involving the aromatic ring
list_aromatic_residues = ["F", "Y", "W"]
# the mutation results in hydrophobic to polar side-chain properties
list_residues_hydrophobic = ["G", "A", "L", "V", "I", "P", "M", "F", "C"]
list_residues_backbone_unique = ["P", "G"]
# In the selected structure, the polar side-chain atom is involved in interactions
dict_atoms_acceptor = {
    "T": ["OG1"],
    "S": ["OG"],
    "Y": ["OH"],
    "N": ["OD1"],
    "Q": ["OE1"],
    "D": ["OD1", "OD2"],
    "E": ["OE1", "OE2"],
    "H": ["ND1", "NE2"],
}
dict_atoms_donor = {
    "T": ["OG1"],
    "S": ["OG"],
    "Y": ["OH"],
    "N": ["ND2"],
    "Q": ["NE2"],
    "H": ["ND1", "NE2"],
    "R": ["NE", "NH1", "NH2"],
    "K": ["NZ"],
    "W": ["NE1"],
}
list_branched_sidechains = ["S", "T", "I", "V", "L"]
list_flexible_sidechains = ["M", "K"]
dict_sidechain_accessible_surface = {
    "A": 67,
    "R": 196,
    "N": 113,
    "D": 106,
    "C": 104,
    "Q": 144,
    "E": 138,
    "G": 1,
    "H": 151,
    "I": 140,
    "L": 137,
    "K": 167,
    "M": 160,
    "F": 175,
    "P": 105,
    "S": 80,
    "T": 102,
    "W": 217,
    "Y": 187,
    "V": 117,
}
dict_pI_aa = {
    "ARG": 10.76,
    "LYS": 9.74,
    "HIS": 7.59,
    "GLY": 5.97,
    "ALA": 6.00,
    "VAL": 5.96,
    "LEU": 5.98,
    "ILE": 6.02,
    "PRO": 6.30,
    "MET": 5.74,
    "SER": 5.68,
    "THR": 5.60,
    "ASN": 5.41,
    "GLN": 5.65,
    "ASP": 2.77,
    "GLU": 3.22,
    "PHE": 5.48,
    "TYR": 5.66,
    "TRP": 5.89,
    "CYS": 5.07,
}
# Rose et al. 1985
dict_maxacc = {
    "A": 118.1,
    "R": 256.0,
    "N": 165.5,
    "D": 158.7,
    "C": 146.1,
    "E": 186.2,
    "Q": 193.2,
    "G": 88.1,
    "H": 202.5,
    "I": 181.0,
    "L": 193.1,
    "K": 225.8,
    "M": 203.4,
    "F": 222.8,
    "P": 146.8,
    "S": 129.8,
    "T": 152.5,
    "W": 266.3,
    "Y": 236.8,
    "V": 164.5,
}


class pdb2seq:
    """
    Functions to parse pdbfile and extract sequences
    """

    def __init__(self, pdbfile):
        self.pdbfile = pdbfile

    def get_pdbatomseq(self):
        """
        get seq based on atom records
        """
        dict_seq = {}
        dict_resdet = {}
        pdbname = os.path.split(self.pdbfile)[1].split(".")[0]
        pdbobj = PDBParser(QUIET=True)
        structure_instance = pdbobj.get_structure(pdbname, self.pdbfile)
        for model in structure_instance:
            for chain in model:
                chid = chain.get_id()
                if chid in ["", " "]:
                    chid_fix = " "
                else:
                    chid_fix = chid
                residues = Selection.unfold_entities(chain, "R")
                seq = ""
                list_resdet = []
                for res in residues:
                    hetatm_flag, resnum, icode = res.get_id()
                    resname = res.get_resname()
                    if resname not in dictaa_1letter:
                        continue
                    seq += dictaa_1letter[resname]
                    list_resdet.append(str(resnum) + " " + dictaa_1letter[resname])

                dict_seq[pdbname + "_" + chid_fix] = seq
                dict_resdet[pdbname + "_" + chid_fix] = list_resdet[:]
        return dict_seq, dict_resdet

    def get_pdbseqres(self, outfile=None, chain_id=None, flagout=False, warnings=False):
        """
        get seq based on seqres if available
        return '' otherwise
        """
        dict_seq = {}
        pdbname = os.path.split(self.pdbfile)[1].split(".")[0]
        list_records = SeqIO.parse(self.pdbfile, "pdb-seqres")
        if list_records is None or not isinstance(list_records, types.GeneratorType):
            print("Warning: seqres record not found")
            return dict_seq
        for record in list_records:
            # chain ID?
            if chain_id is not None:
                if record.annotations["chain"] != chain_id:
                    continue
            else:
                chain_id = record.annotations["chain"]
            if flagout:
                outfile = os.path.splitext(self.pdbfile)[0] + "_" + chain_id + ".fasta"
                ou = open(os.path.abspath(outfile), "w")
                ou.write(">" + pdbname + "_" + chain_id + "\n")
            str_seq = ""
            if re.search("X", str(record.seq)) is not None:
                for s in str(record.seq):
                    if s != "X":
                        str_seq += s
            else:
                str_seq = str(record.seq)
            if warnings:
                if len(str_seq) > 800:
                    print("Sequence too long for Jpred: {}".format(chain_id))
                    continue
                elif len(str_seq) < 30:
                    print("Sequence too short for Jpred: {}".format(chain_id))
                    continue
            if flagout:
                ou.write(str_seq + "\n")
                ou.close()
            dict_seq[pdbname + "_" + record.annotations["chain"]] = str_seq
        return dict_seq

    def match_atom_seqres(self, dict_atomseq, dict_seqres):
        dict_atomseq_aln = {}
        dict_seqres_aln = {}
        for pdbch in dict_atomseq:
            if pdbch not in dict_seqres:
                continue
            aligned_seq1, aligned_seq2 = alignseq(
                dict_atomseq[pdbch], dict_seqres[pdbch]
            )
            # skip non similar sequences
            if float(aligned_seq1.count("-")) / len(aligned_seq1) < 0.5:
                continue
            if float(aligned_seq2.count("-")) / len(aligned_seq2) < 0.5:
                continue
            dict_atomseq_aln[pdbch] = aligned_seq1[:]
            dict_seqres_aln[pdbch] = aligned_seq2[:]

        return dict_atomseq_aln, dict_seqres_aln


def alignseq(seq1, seq2):
    if isinstance(seq1, list):
        seq1_str = "".join(seq1)
    elif isinstance(seq1, str):
        seq1_str = seq1
    else:
        print("Could not align sequences:")
        print(seq1)
        print(seq2)
        return None, None
    if isinstance(seq2, list):
        seq2_str = "".join(seq2)
    elif isinstance(seq2, str):
        seq2_str = seq2
    else:
        print("Could not align sequences:")
        print(seq1)
        print(seq2)
        return None, None
    aligned = pairwise2.align.globalms(seq1_str, seq2_str, 1, -1, -0.5, -0.1)[0]
    aligned_seq1, aligned_seq2 = list(aligned[0]), list(aligned[1])
    return aligned_seq1, aligned_seq2


def match_lists_add(list1, list2):
    if isinstance(list1, str):
        list1 = [e for e in list1]
    if isinstance(list2, str):
        list2 = [e for e in list2]
    # add gaps to list1 based on list2
    indices = [i for i, x in enumerate(list2) if x == "-"]
    ct = 0
    for i in indices:
        list1.insert(i, "-")
        ct += 1
    return list1


def match_lists_del(list1, list2):
    if isinstance(list1, str):
        list1 = [e for e in list1]
    if isinstance(list2, str):
        list2 = [e for e in list2]
    # remove indices in list1 corresponding to gaps in list2
    indices = [i for i, x in enumerate(list2) if x == "-"]
    ct = 0
    for i in indices:
        list1.pop(i - ct)
        ct += 1
    return list1


def parse_dssp_file(dsspfile, modelid):
    out_fh = open(dsspfile, "r")
    residue_scores_start = False
    dict_sses = {}
    for line in out_fh:
        if residue_scores_start:
            if modelid not in dict_sses:
                dict_sses[modelid] = {}
            parse_dssp_line(line[:-1], modelid, dict_sses)
        if "#" in line and "RESIDUE" in line:
            residue_scores_start = True
    return dict_sses


def parse_dssp_line(line, modelid, dict_sses):
    line_split = line.split()
    # residue number
    resnum = line_split[1]
    # residue name
    try:
        resname = dictaa_3letters[line_split[3]]
    except KeyError:
        resname = line_split[3]
    # chain ID
    chainID = line_split[2]
    # secondary structure
    dssp_sse = line[16]
    # secondary structure description
    try:
        sse_desc = dssp_sse_desc[dssp_sse]
    except KeyError:
        sse_desc = " "
    # calculate relative solvant accessibility
    try:
        dssp_acc = float(line[35:38])
        residue_1l = line_split[3]
        if len(residue_1l) == 1 and residue_1l.islower():
            residue_1l = "C"  # disulfide bridge
        dssp_acc = dssp_acc / dict_maxacc[residue_1l]
    except KeyError:
        # print sse_desc,dssp_sse,dssp_acc,resname,line_split[3]
        dssp_acc = -1.0
    # Ca coordinates
    try:
        x, y, z = ["{:.4f}".format(float(coord)) for coord in line_split[-5:-2]]
    except IndexError:
        x = y = z = ""
    # save details
    try:
        dict_sses[modelid][chainID][resnum] = [
            sse_desc,
            dssp_sse,
            dssp_acc,
            resname,
            x,
            y,
            z,
        ]
    except KeyError:
        dict_sses[modelid][chainID] = OrderedDict()
        dict_sses[modelid][chainID][resnum] = [
            sse_desc,
            dssp_sse,
            dssp_acc,
            resname,
            x,
            y,
            z,
        ]


def rgb(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b = int(max(0, 255 * (1 - ratio)))
    r = int(max(0, 255 * (ratio - 1)))
    g = 255 - b - r
    return r, g, b
