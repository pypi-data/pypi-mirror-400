#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

import os
import json
from typing import OrderedDict, Union, List, Optional, Sequence, Dict
import pathlib
import gemmi
import numpy as np
import copy
from ccpem_utils.sequence.sequence_utils import (
    find_best_seq_match_identity,
    merge_set_unique_id_fasta,
)


class GemmiStructureExt(object):
    """
    Helper class to extend gemmi Structure class
    """

    def __init__(self, parent_structure: gemmi.Structure):
        self.parent_structure = parent_structure
        for attr in dir(parent_structure):
            try:
                self.__dict__[attr] = copy.deepcopy(self.__getattribute__(attr))
            except TypeError:
                pass

    def __getattribute__(self, name: str):
        try:
            # self.parent_structure call results in recursion error here
            # use superclass method instead
            return getattr(
                super(GemmiStructureExt, self).__getattribute__("parent_structure"),
                name,
            )
        except AttributeError:
            return super(GemmiStructureExt, self).__getattribute__(name)


class GemmiModelUtils(object):
    """
    Operations on gemmi Structure object
    """

    def __init__(self, input_model: Union[str, gemmi.Structure]):
        self.structure = check_structure_inputs(
            input_model
        )  # gemmi.read_structure(modelfile)
        self.resolution = self.structure.resolution
        if isinstance(input_model, str) and os.path.isfile(input_model):
            self.file_ext: Optional[str] = os.path.splitext(input_model)[1].lower()
            self.modelid: Union[str, None] = os.path.splitext(
                os.path.basename(input_model)
            )[0]
        else:
            self.file_ext = None
            self.modelid = None

    def close(self):
        """Detach structure attribute from gemmi structure obj"""
        self.structure = None

    def write_structure_as_mmcif(self, mmcif_name):
        """Write a Gemmi structure out to an mmCIF file."""
        write_structure_as_mmcif(self.structure, mmcif_name)

    def write_structure_as_pdb(self, pdb_name):
        """Write a Gemmi structure out to an PDB file."""
        write_structure_as_pdb(self.structure, pdb_name)

    def shift_coordinates(
        self,
        trans_vector: Union[list, np.ndarray, tuple],
        out_model_path: Optional[Union[pathlib.Path, str]] = None,
        remove_charges: bool = False,
        inplace: bool = False,
    ) -> gemmi.Structure:
        """
        Shift atomic coordinates based on a translation vector (x,y,z)
        """
        if inplace:
            structure = self.structure
        else:
            structure = self.structure.clone()
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        atom.pos = gemmi.Position(
                            round(atom.pos.x + trans_vector[0], 3),
                            round(atom.pos.y + trans_vector[1], 3),
                            round(atom.pos.z + trans_vector[2], 3),
                        )
                        if remove_charges:  # remove negative charges?
                            if atom.charge != 0:
                                atom.charge = 0
        if out_model_path:
            if os.path.splitext(out_model_path)[1].lower() in [
                ".cif",
                ".mmcif",
            ]:
                write_structure_as_mmcif(structure, out_model_path)
            else:
                write_structure_as_pdb(structure, out_model_path)
        return structure

    def remove_atomic_charges(
        self,
        out_model_path: Optional[Union[pathlib.Path, str]] = None,
        inplace: bool = False,
    ) -> gemmi.Structure:
        """
        Remove atomic charges from the model

        Arguments
        ---------
            :out_model_path:
                output atomic model with charges removed
        """
        if inplace:
            structure = self.structure
        else:
            structure = self.structure.clone()
        for model in structure:
            for chain in model:
                # skip non polymers
                # if not polymer: continue
                for residue in chain:
                    for atom in residue:
                        if atom.charge != 0:
                            atom.charge = 0
        if out_model_path:
            if os.path.splitext(out_model_path)[1].lower() in [
                ".cif",
                ".mmcif",
            ]:
                write_structure_as_mmcif(self.structure, out_model_path)
            else:
                write_structure_as_pdb(structure, out_model_path)
        return structure

    def set_residue_attribute(self, attr_name: str, dict_attribute: dict):
        """
        TODO: this is just a placeholder
        Add a new residue attribute to the current gemmi structure instance
        """
        for model in self.structure:
            model_num = str(model.num)
            if model_num not in dict_attribute:
                continue
            for chain in model:
                if chain.name in dict_attribute[model_num]:
                    for residue in chain:
                        pass
                        # try:
                        #     setattr(
                        #         residue,
                        #         attr_name,
                        #         dict_attribute[model_num][chain.name][
                        #             str(residue.seqid.num)
                        #         ],
                        #     )
                        # except KeyError:
                        #     pass

    def set_residue_types(self):
        """
        Set a dictionary to map residue IDs and names
        """
        self.dict_resnames = OrderedDict()
        for model in self.structure:
            model_num = str(model.num)
            self.dict_resnames[model_num] = {}
            for chain in model:
                if chain.name not in self.dict_resnames[model_num]:
                    self.dict_resnames[model_num][chain.name] = {}
                for residue in chain:
                    self.dict_resnames[model_num][chain.name][
                        str(residue.seqid.num)
                    ] = residue.name

    def get_bfact_deviation(
        self,
        calc_dev: bool = True,
        dist_dev: float = 3.0,
        out_json: Optional[str] = None,
        skip_nonpoly: bool = True,
        skip_water: bool = True,
    ) -> Dict[str, Dict[str, Dict[str, List]]]:
        """
        Get average atomic B-factors, and stdev of atomic B-factors
        around each residue in the model

        Returns
        -------
            Dict with B factors and  deviations
            {modelName:{chainName:
            {residueNum_residueName: [avg b-factor, {atom: b-factor}, b-factor dev]}}}
        """
        dict_bfact: Dict[str, Dict[str, Dict[str, List]]] = OrderedDict()
        for model in self.structure:
            if calc_dev:
                subcells = gemmi.NeighborSearch(
                    model, self.structure.cell, dist_dev + 1.0
                )
                subcells.populate(include_h=False)
            model_num = str(model.num)
            dict_bfact[model_num] = {}
            for chain in model:
                polymer = chain.get_polymer()
                # skip non polymers
                if not polymer and skip_nonpoly:
                    continue
                if chain.name not in dict_bfact[model_num]:
                    dict_bfact[model_num][chain.name] = {}
                for residue in chain:
                    # skip waters?
                    if residue.entity_type == gemmi.EntityType.Water and skip_water:
                        continue
                    residue_id = str(residue.seqid.num)  # + "_" + residue.name
                    list_residue_bfact = []
                    dict_residue_bfact = {}
                    list_neigh_bfact = []
                    for atom in residue:
                        list_residue_bfact.append(atom.b_iso)
                        dict_residue_bfact[atom.name] = atom.b_iso
                    avg_bfact = round(
                        sum(list_residue_bfact) / float(len(list_residue_bfact)), 5
                    )
                    if calc_dev:
                        representative_atom = self.get_representative_atom(
                            residue=residue
                        )
                        representative_atom_b = representative_atom.b_iso
                        marks = subcells.find_neighbors(
                            representative_atom, min_dist=0.1, max_dist=dist_dev
                        )
                        for mark in marks:
                            cra = mark.to_cra(model)
                            neigh_atom = cra.atom
                            list_neigh_bfact.append(neigh_atom.b_iso)
                        list_neigh_bfact.append(representative_atom_b)
                    if len(list_neigh_bfact) > 0:
                        dict_bfact[model_num][chain.name][residue_id] = [
                            avg_bfact,
                            dict_residue_bfact,
                            round(np.std(np.array(list_neigh_bfact)), 5),
                        ]
                    else:
                        dict_bfact[model_num][chain.name][residue_id] = [
                            avg_bfact,
                            dict_residue_bfact,
                            0.0,
                        ]
        if out_json is not None:
            with open(out_json, "w") as oj:
                json.dump(dict_bfact, oj)
        return dict_bfact

    def get_avgbfact_deviation(
        self,
        calc_dev: bool = True,
        dist_dev: float = 3.0,
        out_json: Optional[str] = None,
        skip_nonpoly: bool = True,
    ) -> Dict[str, Dict[str, Dict[str, List[float]]]]:
        """
        Get average atomic B-factors, and stdev of atomic B-factors
        around each residue in the model

        Returns
        -------
            Dict with B factors and  deviations
            {modelName:{chainName:
            {residueNum_residueName: [avg b-factor, b-factor dev]}}}
        """
        dict_bfact: Dict[str, Dict[str, Dict[str, List[float]]]] = OrderedDict()
        for model in self.structure:
            if calc_dev:
                subcells = gemmi.NeighborSearch(
                    model, self.structure.cell, dist_dev + 1.0
                )
                subcells.populate(include_h=False)
            model_num = str(model.num)
            dict_bfact[model_num] = {}
            for chain in model:
                polymer = chain.get_polymer()
                # skip non polymers
                if not polymer and skip_nonpoly:
                    continue
                if chain.name not in dict_bfact[model_num]:
                    dict_bfact[model_num][chain.name] = {}
                for residue in chain:
                    if residue.entity_type == gemmi.EntityType.Water:
                        continue
                    residue_id = str(residue.seqid.num)  # + "_" + residue.name
                    list_bfact = []
                    list_neigh_bfact = []
                    for atom in residue:
                        list_bfact.append(atom.b_iso)
                    avg_bfact = round(sum(list_bfact) / float(len(list_bfact)), 5)
                    if calc_dev:
                        representative_atom = self.get_representative_atom(
                            residue=residue
                        )
                        representative_atom_b = representative_atom.b_iso
                        marks = subcells.find_neighbors(
                            representative_atom, min_dist=0.1, max_dist=dist_dev
                        )
                        for mark in marks:
                            cra = mark.to_cra(model)
                            neigh_atom = cra.atom
                            list_neigh_bfact.append(neigh_atom.b_iso)
                        list_neigh_bfact.append(representative_atom_b)
                    if len(list_neigh_bfact) > 0:
                        dict_bfact[model_num][chain.name][residue_id] = [
                            avg_bfact,
                            round(np.std(np.array(list_neigh_bfact)), 5),
                        ]
                    else:
                        dict_bfact[model_num][chain.name][residue_id] = [
                            avg_bfact,
                            0.0,
                        ]

        # if save_obj:  # save gemmi structure object instead of returned dict
        #     self.set_residue_attribute(
        #         attr_name="bfact_avg_dev", dict_attribute=dict_bfact
        #     )
        #     if out_json is not None:
        #         encode_simple_obj_to_json_file(
        #             GemmiStructureExt(self.structure), out_json
        #         )
        #     else:
        #         encode_simple_obj_to_json_file(
        #             GemmiStructureExt(self.structure),
        #             self.modelid + "_gemmistructure.json",
        #         )
        #     print(dir(GemmiStructureExt(self.structure)))
        if out_json is not None:
            with open(out_json, "w") as oj:
                json.dump(dict_bfact, oj)
        return dict_bfact

    def get_coordinates(
        self,
        atom_selection: Union[str, list] = "all",
        skip_non_poly: bool = False,
        return_list: bool = False,
        out_json: Optional[str] = None,
    ):
        """
        Get model atomic coordinates based on user selection

        Arguments
        ---------
            in_model_path: str
                input atomic model
            gemmi_structure_instance: gemmi.Structure, optional
                gemmi structure instance if in_model_path is not input
            atom_selection: Union[str, list], optional
                atom selection for coordinate retrieval
                Input a list of atom names or any of the following keywords:
                    "all": all atoms in the model
                    "backbone": only model backbone atoms, all atoms for non polymers
                    "one_per_residue": representative atoms, e.g. CA for amino acids
                    "centre": geometric centre of the residue
            skip_non_poly: bool, optional
                skip non polymers?
            return_list: bool, optional
                Returns a list of residue IDs and a list of coordinates
            out_json: str, optional
                json file to save the output coordinate dictionary
                (if return_list is False)
        Returns
        -------
            A dictionary of coordinates or list of residue IDs + a list of coordinates
            {modelName:{chainName: {residueNum_residueName: [list atomic coordinates]}}}
        """
        dict_coord: Dict[str, Dict[str, Dict[str, List[Sequence[float]]]]] = (
            OrderedDict()
        )
        list_ids = []
        list_coords = []
        polymertype = None
        # loop through structure
        for model in self.structure:
            model_num = str(model.num)
            if model_num not in dict_coord:
                dict_coord[model_num] = {}
            for chain in model:
                polymer = chain.get_polymer()
                # skip non polymers
                if not polymer and skip_non_poly:
                    continue
                if polymer.check_polymer_type() == gemmi.PolymerType.PeptideL:
                    polymertype = "protein"
                if chain.name not in dict_coord[model_num]:
                    dict_coord[model_num][chain.name] = {}
                for residue in chain:
                    list_residue_coords: List[Sequence[float]] = []
                    if isinstance(atom_selection, list):  # specified atoms only
                        list_residue_coords = self.get_selected_atom_coordinates(
                            residue, atom_selection
                        )
                    elif atom_selection == "all":
                        for atom in residue:
                            atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                            list_residue_coords.append(atom_coord)
                    elif atom_selection == "backbone":  # all backbone
                        list_residue_coords = self.get_backbone_coordinates(
                            residue, polymertype=polymertype
                        )
                    elif atom_selection == "one_per_residue":  # ca or equivalent
                        residue_centre = self.get_representative_coordinate(
                            residue, polymertype=polymertype
                        )
                        list_residue_coords.append(residue_centre)
                    elif atom_selection == "centre":  # central atom
                        residue_centre = self.get_residue_centre_by_coordinates(residue)
                        list_residue_coords.append(residue_centre)
                    if return_list:
                        list_ids.extend(
                            len(list_residue_coords)
                            * [
                                "_".join(
                                    [
                                        model_num,
                                        str(chain.name),
                                        str(residue.seqid.num),
                                        residue.name,
                                    ]
                                )
                            ]
                        )
                        list_coords.extend(list_residue_coords)
                    else:
                        residue_coords = list_residue_coords
                        residue_id = str(residue.seqid.num)  # + "_" + residue.name
                        dict_coord[model_num][str(chain.name)][
                            residue_id
                        ] = residue_coords
        if not return_list:
            if out_json:
                with open(out_json, "w") as j:
                    json.dump(dict_coord, j)
            return dict_coord
        else:
            return list_ids, list_coords

    def get_selected_atom_coordinates(
        self, residue: gemmi.Residue, atom_selection: list
    ) -> List[Sequence[float]]:
        """
        Get coordinates of selected atoms (list of atom names)
        from a given gemmi Residue instance
        """
        list_residue_coords: List[Sequence[float]] = []
        for atom in residue:
            if atom.name in atom_selection:
                atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                list_residue_coords.append(atom_coord)
        return list_residue_coords

    def get_representative_coordinate(
        self, residue: gemmi.Residue, polymertype: Optional[str] = None
    ) -> Sequence[float]:
        """
        Get coordinates of one representative atom per residue
        from a given gemmi Residue instance
        """
        residue_centre: Sequence[float] = ()
        if residue.name in ["A", "T", "C", "G", "U"]:  # nuc acid
            for atom in residue:
                if atom.name in ["P", "C3'", "C1'"]:
                    atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                    residue_centre = atom_coord
        elif not polymertype or polymertype == "protein":  # protein
            for atom in residue:
                # if atom.name == "CB" or (residue.name == "GLY" and atom.name == "CA"):
                if atom.name == "CA":
                    atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                    residue_centre = atom_coord
                    break
        if not residue_centre:  # non nuc acid / prot
            residue_centre = self.get_residue_centre_by_coordinates(residue)
        return residue_centre

    def get_representative_atom(
        self, residue: gemmi.Residue, polymertype: Optional[str] = None
    ) -> gemmi.Atom:
        """
        Get one representative atom per residue
        from a given gemmi Residue instance
        """
        repr_atom = None
        if residue.name in ["A", "T", "C", "G", "U"]:  # nuc acid
            for atom in residue:
                if atom.name in ["P", "C3'", "C1'"]:
                    repr_atom = atom
        elif not polymertype or polymertype == "protein":  # protein
            for atom in residue:
                # if atom.name == "CB" or (residue.name == "GLY" and atom.name == "CA"):
                if atom.name == "CA":
                    repr_atom = atom
                    break
        if not repr_atom:  # non nuc acid / prot
            repr_atom = self.get_central_atom_by_sequence(residue)
        return repr_atom

    def get_backbone_coordinates(
        self, residue: gemmi.Residue, polymertype: Optional[str] = None
    ) -> List[Sequence[float]]:
        """
        Get coordinates of the backbone atoms
        from a given gemmi Residue instance
        """
        list_residue_coords: List[Sequence[float]] = []
        if residue.name in ["A", "T", "C", "G", "U"]:  # nuc acid
            for atom in residue:
                # TODO : fix the backbone atom list
                if atom.name in ["P", "C3'", "C1'"]:
                    atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                    list_residue_coords.append(atom_coord)
        elif residue.het_flag == "H":  # all het atoms
            for atom in residue:
                atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                list_residue_coords.append(atom_coord)
        elif not polymertype or polymertype == "protein":  # protein
            for atom in residue:
                if atom.name in ["N", "CA", "C", "O"]:
                    atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                    list_residue_coords.append(atom_coord)
        if len(list_residue_coords) == 0:  # all
            for atom in residue:
                atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                list_residue_coords.append(atom_coord)
        return list_residue_coords

    def get_residue_centre_by_coordinates(
        self, gemmi_residue_instance: gemmi.Residue
    ) -> Sequence[float]:
        """
        Get coordinates of one central atom (sequence centre) per residue
        from a given gemmi Residue instance
        """
        list_coords = []
        for atom in gemmi_residue_instance:
            atom_coord = [atom.pos.x, atom.pos.y, atom.pos.z]
            list_coords.append(atom_coord)
        return list(np.mean(np.array(list_coords), axis=0))

    def get_residue_centre_by_sequence(self, gemmi_residue_instance: gemmi.Residue):
        """
        Get coordinates of one central atom (sequence centre) per residue
        from a given gemmi Residue instance
        """
        try:
            center_index = int(len(gemmi_residue_instance) / 2)
            atom = gemmi_residue_instance[center_index]
            atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
            residue_centre = atom_coord
        except IndexError:
            for atom in gemmi_residue_instance:
                atom_coord = (atom.pos.x, atom.pos.y, atom.pos.z)
                residue_centre = atom_coord
                break  # first atom
        return residue_centre

    def get_central_atom_by_sequence(
        self, gemmi_residue_instance: gemmi.Residue
    ) -> gemmi.Atom:
        """
        Get one central atom (sequence centre) per residue
        from a given gemmi Residue instance
        """
        try:
            center_index = int(len(gemmi_residue_instance) / 2)
            atom = gemmi_residue_instance[center_index]
            central_atom = atom
        except IndexError:
            for atom in gemmi_residue_instance:
                central_atom = atom
                break  # first atom
        return central_atom

    def get_sequence_from_entity_records(self):
        """
        Get polymer sequence from atom records
        """
        dict_seq = {}
        self.structure.add_entity_types(overwrite=True)
        self.structure.assign_subchains()  # assigns subchains in each chain
        self.structure.ensure_entities()  # each subchain linked to one Entity object
        for entity in self.structure.entities:
            if entity.entity_type == gemmi.EntityType.Polymer:
                seq_res_list = entity.full_sequence
                seq_res_list = [gemmi.Entity.first_mon(item) for item in seq_res_list]
                sequence = "".join(
                    [
                        gemmi.find_tabulated_residue(resname).one_letter_code
                        for resname in seq_res_list
                    ]
                )
                dict_seq[entity.name] = sequence
        return dict_seq

    def get_sequence_from_atom_records(self, keep_gaps=True, keep_unknowns=True):
        """
        Get sequence from polymer atom records
        """
        self.structure.setup_entities()
        self.structure.assign_label_seq_id()
        dict_seq = {}
        for model in self.structure:
            for ch in model:
                polymer = ch.get_polymer()
                # skip non polymers
                if not polymer:
                    continue
                chainid = ch.name
                # use this if subchain ID is set
                # if self.file_ext in [".pdb", ".ent"]:
                #     chainid = ch.name
                # else:
                #     subchain = ch.subchains()[0]
                #     chainid = subchain.subchain_id()
                polymer_seq = polymer.make_one_letter_sequence()
                if not keep_gaps:
                    polymer_seq = polymer_seq.replace("-", "")
                if not keep_unknowns:
                    polymer_seq = polymer_seq.replace("X", "")
                dict_seq[chainid] = polymer_seq
        return dict_seq

    def get_sequence_resnum_from_atom_records(self):
        """
        Get polymer sequence and list of residue number from model atom records

        Returns
        -------
            Dict of sequences of each chain
            Dict of residue numbers of each chain {'A': ['G 74', 'L 75', 'A 76', ....]}
        """
        dict_seq = {}
        dict_residues = {}
        for model in self.structure:
            for chain in model:
                polymer = chain.get_polymer()
                # skip non polymers
                if not polymer:
                    continue
                list_seq = []
                list_resnum = []
                for residue in chain:
                    rescode = gemmi.find_tabulated_residue(residue.name).one_letter_code
                    if rescode != " ":
                        list_seq.append(rescode)
                        list_resnum.append(rescode + " " + str(residue.seqid.num))
                sequence = "".join(list_seq)
                dict_seq[chain.name] = sequence
                dict_residues[chain.name] = list_resnum
        return dict_seq, dict_residues

    def get_best_match_from_fasta(
        self, fastafiles: List[str], keep_gaps: bool = False, keep_unknowns: bool = True
    ) -> Dict[str, List]:
        """From input fasta, get the best matching sequence to each model chain

        Args:
            fastafiles (List[str]): List of fasta files to search against

        Returns:
            Dict[str, List]:
                Dictionary {[chain_id] =[fasta_seq_id, percent identity],...}
        """
        dict_fasta_seq = merge_set_unique_id_fasta(list_fastafiles=fastafiles)
        dict_model_seq = self.get_sequence_from_atom_records(
            keep_gaps=keep_gaps, keep_unknowns=keep_unknowns
        )
        dict_best_match: Dict[str, List] = {}
        for c in dict_model_seq:
            search_id, search_identity = find_best_seq_match_identity(
                target_seq=dict_model_seq[c], search_dict_seq=dict_fasta_seq
            )
            # shorten search id
            if len(search_id) > 30:
                search_id = search_id[:15] + search_id[-15:]
            dict_best_match[c] = [search_id, search_identity]
        return dict_best_match

    def get_chain_matches_to_fasta(
        self, fastafiles: List[str], keep_gaps: bool = False, keep_unknowns: bool = True
    ) -> Dict[str, List]:
        """For each sequence in input fasta(s), get the best matching model chains

        Args:
            fastafiles (List[str]): List of fasta files to search against

        Returns:
            Dict[str, List]: Dictionary {[fasta_seq_id] =
            [[chain_id1, percent identity],[chain_id2, percent_identity],..]}
        """
        dict_fasta_seq = merge_set_unique_id_fasta(list_fastafiles=fastafiles)
        dict_model_seq = self.get_sequence_from_atom_records(
            keep_gaps=keep_gaps, keep_unknowns=keep_unknowns
        )
        dict_best_match: Dict[str, List] = {}
        for c in dict_model_seq:
            search_id, search_identity = find_best_seq_match_identity(
                target_seq=dict_model_seq[c], search_dict_seq=dict_fasta_seq
            )
            # shorten search id
            if len(search_id) > 30:
                search_id = search_id[:15] + search_id[-15:]
            try:
                dict_best_match[search_id].append([c, search_identity])
            except KeyError:
                dict_best_match[search_id] = [[c, search_identity]]
        return dict_best_match


def convert_pdb_to_mmcif(pdb_path, mmcif_path=None):
    """Convert coordinate file from PDB format to mmCIF/PDBx format"""
    structure = gemmi.read_structure(pdb_path)
    if mmcif_path is None:
        mmcif_path = os.path.splitext(pdb_path)[0] + ".cif"
    write_structure_as_mmcif(structure, mmcif_path)
    return mmcif_path


def write_structure_as_mmcif(structure, mmcif_name):
    """Write a Gemmi structure out to an mmCIF file."""
    # Refmac crashes for long _entry.id
    st_new = structure.clone()
    st_new.name = st_new.name[:78]  # in case of pdb this will be _entry.id
    if "_entry.id" in st_new.info:
        st_new.info["_entry.id"] = st_new.info["_entry.id"][:78]
    st_new.make_mmcif_document().write_file(mmcif_name)


def write_structure_as_pdb(structure, pdb_name):
    """Write a Gemmi structure out to a PDB file."""
    st_new = structure.clone()
    st_new.shorten_chain_names()
    st_new.write_pdb(pdb_name, use_linkr=True)


def convert_mmcif_to_pdb(mmcif_path, pdb_path=None):
    """Convert coordinate file from mmCIF/PDBx format to PDB format"""
    structure = gemmi.read_structure(mmcif_path)
    if pdb_path is None:
        pdb_path = os.path.splitext(pdb_path)[0] + ".pdb"
    write_structure_as_pdb(structure, pdb_path)
    return pdb_path


def check_structure_inputs(
    input_structure: Union[str, gemmi.Structure],
) -> gemmi.Structure:
    """
    Check if the given input is a model file path or a gemmi Structure instance

    Returns
    -------
    gemmi Structure instance
    """
    if isinstance(input_structure, gemmi.Structure):
        structure = input_structure
    elif input_structure is not None and os.path.isfile(input_structure):
        structure = gemmi.read_structure(input_structure)
    else:
        raise IOError("Input either a valid model file or a gemmi structure instance")
    return structure


def get_residue_attribute(list_ids: List[str], list_attr: List[Union[float, int]]):
    """
    Get residue attributes as average of atom attributes

    Arguments
    ---------
        :list_ids:
            list of residue or atom IDs of the format:
            residue_id = "_".join(
                    [
                        model name,
                        chain name,
                        str(residue number),
                        residue name,
                    ]
                )
            atom_id = "_".join([residue_id, atom name])
        :list_attr:
            list of atom attributes (same length as list_ids)

    Returns:
        Lists of residue IDs and average attributes
    """
    list_res_ids = []
    list_res_attr = []
    dict_current_res: dict = {}
    # model.num_chain.name_residue.seqid.num_residue.name
    atom_number = 0
    previous_res_id = None
    for atom_id in list_ids:
        atom_id_split = atom_id.split("_")
        if len(atom_id_split) > 4:  # has atom identifier
            res_id = "_".join(atom_id_split[:4])
        else:
            res_id = atom_id
        try:
            dict_current_res[res_id].append(list_attr[atom_number])
        except KeyError:
            if previous_res_id:
                list_res_ids.append(previous_res_id)
                if len(dict_current_res[previous_res_id]) == 1:
                    list_res_attr.append(dict_current_res[previous_res_id][0])
                elif len(dict_current_res[previous_res_id]) > 1:
                    list_res_attr.append(
                        round(
                            np.sum(dict_current_res[previous_res_id])
                            / len(dict_current_res[previous_res_id]),
                            5,
                        )
                    )
            dict_current_res = {}  # reinitialize
            dict_current_res[res_id] = [list_attr[atom_number]]
        previous_res_id = res_id
        atom_number += 1
    if previous_res_id:
        list_res_ids.append(previous_res_id)
        if len(dict_current_res[previous_res_id]) == 1:
            list_res_attr.append(dict_current_res[previous_res_id][0])
        elif len(dict_current_res[previous_res_id]) > 1:
            list_res_attr.append(
                round(
                    np.sum(dict_current_res[previous_res_id])
                    / len(dict_current_res[previous_res_id]),
                    5,
                )
            )
    return list_res_ids, list_res_attr


def convert_dict_attributes_to_list(dict_attr):
    list_ids = []
    list_attr = []
    for model in dict_attr:
        for chain in dict_attr[model]:
            for residue in dict_attr[model][chain]:
                if isinstance(dict_attr[model][chain][residue], dict):
                    for atom in dict_attr[model][chain][residue]:
                        atom_id = "_".join([model, str(chain), str(residue), str(atom)])
                        list_ids.extend(
                            len(dict_attr[model][chain][residue][atom]) * [atom_id]
                        )
                        list_attr.extend(dict_attr[model][chain][residue][atom])

                else:
                    res_id = "_".join([model, str(chain), str(residue)])
                    list_ids.extend(len(dict_attr[model][chain][residue]) * [res_id])
                    list_attr.extend(dict_attr[model][chain][residue])
    return list_ids, list_attr


def set_bfactor_attributes(
    in_model_path: str,
    dict_attr: dict,
    skip_non_poly: bool = True,
    attr_name: str = "",
    out_dir: Optional[str] = None,
):
    """
    Replace atomic B-factors with the given attributes
    Use this for visualisation purpose (colr by b-factors) only

    Arguments
    ---------
        in_model_path:
            input atomic model path
        dict_attr:
            Dictionary of residue or atom attributes
            Dict keys are residue or atom IDs of the format:
            residue_id = "_".join(
                    [
                        model name,
                        chain name,
                        str(residue number),
                        residue name,
                    ]
                )
            atom_id = "_".join([residue_id, atom name])
        skip_non_poly: bool, optional
            skip non polymers?
    Returns
    -------
        A dictionary of coordinates or list of residue IDs + a list of coordinates

    """
    structure = gemmi.read_structure(in_model_path)
    # setup entities in case that nothing were set when reading the file
    structure.setup_entities()
    structure.assign_label_seq_id()
    count_atom = 0
    for model in structure:
        for chain in model:
            polymer = chain.get_polymer()
            # skip non polymers
            if not polymer and skip_non_poly:
                continue
            for residue in chain:
                residue_id = "_".join(
                    [
                        str(model.num),
                        str(chain.name),
                        str(residue.seqid.num),
                        residue.name,
                    ]
                )
                for atom in residue:
                    atom_id = "_".join([residue_id, atom.name])
                    if atom_id in dict_attr:
                        atom.b_iso = dict_attr[atom_id]
                    elif residue_id in dict_attr:
                        atom.b_iso = dict_attr[residue_id]
                    else:
                        atom.b_iso = 0.0
                    count_atom += 1
    if out_dir:
        structure.write_pdb(
            os.path.join(
                out_dir,
                os.path.splitext(os.path.basename(in_model_path))[0]
                + "_"
                + attr_name
                + "_attr.pdb",
            )
        )
    else:
        structure.write_pdb(
            os.path.splitext(os.path.basename(in_model_path))[0]
            + "_"
            + attr_name
            + "_attr.pdb"
        )
