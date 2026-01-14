#
#     Copyright (C) 2021 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.
#

import unittest
import os
import math
import tempfile
import shutil
from ccpem_utils_tests import test_data
from ccpem_utils.model.gemmi_model_utils import (
    GemmiModelUtils,
    set_bfactor_attributes,
)
from ccpem_utils.scripts import analyse_bfactors
import subprocess


class GemmiModelUtilsTest(unittest.TestCase):
    def setUp(self):
        """
        Setup test data and output directories.
        """
        self.test_data = os.path.dirname(test_data.__file__)
        self.test_dir = tempfile.mkdtemp(prefix="coord_clust")
        # Change to test directory
        self._orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self._orig_dir)
        # print(self.test_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_sequence(self):
        model_input = os.path.join(self.test_data, "5me2.pdb")
        gemmiutils = GemmiModelUtils(model_input)
        dict_seq = gemmiutils.get_sequence_from_atom_records()
        assert len(dict_seq) == 4
        assert len(dict_seq["A"]) == 140
        dict_seq = gemmiutils.get_sequence_resnum_from_atom_records()[0]
        assert len(dict_seq) == 4
        assert len(dict_seq["A"]) == 140

    def test_get_sequence_from_atom_records(self):
        modelfile = os.path.join(self.test_data, "5ni1_updated.cif")
        gemmiutils = GemmiModelUtils(modelfile)
        dict_model_seq = gemmiutils.get_sequence_from_atom_records()
        assert len(dict_model_seq) == 4
        assert len(dict_model_seq["A"]) == 141

    def test_get_best_match_from_fasta(self):
        modelfile = os.path.join(self.test_data, "modelangelo_5ni1.cif")
        fastafile = os.path.join(self.test_data, "5ni1_entry.fasta")
        gemmiutils = GemmiModelUtils(modelfile)
        dict_match = gemmiutils.get_best_match_from_fasta(fastafiles=[fastafile])
        assert dict_match == {
            "Ba": ["pdb|5ni1|B D", 98.63],
            "Aa": ["pdb|5ni1|A C", 97.872],
            "Bb": ["pdb|5ni1|B D", 99.315],
            "Ab": ["pdb|5ni1|A C", 98.582],
        }

    def test_get_chain_matches_to_fasta(self):
        modelfile = os.path.join(self.test_data, "modelangelo_5ni1.cif")
        fastafile = os.path.join(self.test_data, "5ni1_entry.fasta")
        gemmiutils = GemmiModelUtils(modelfile)
        dict_match = gemmiutils.get_chain_matches_to_fasta(fastafiles=[fastafile])
        assert dict_match == {
            "pdb|5ni1|B D": [["Ba", 98.63], ["Bb", 99.315]],
            "pdb|5ni1|A C": [["Aa", 97.872], ["Ab", 98.582]],
        }

    def test_get_bfact_deviation(self):
        model_input = os.path.join(self.test_data, "5me2.pdb")
        gemmiutils = GemmiModelUtils(model_input)
        dict_bfact_dev = gemmiutils.get_avgbfact_deviation()
        assert len(dict_bfact_dev["1"]) == 4
        assert math.isclose(dict_bfact_dev["1"]["A"]["201"][1], 0.0, rel_tol=1e-3)
        for model in dict_bfact_dev:
            dict_attr = {}
            for chain in dict_bfact_dev[model]:
                for res_id in dict_bfact_dev[model][chain]:
                    residue_id = "_".join([model, chain, res_id])
                    dict_attr[residue_id] = dict_bfact_dev[model][chain][res_id][1]
            break
        set_bfactor_attributes(model_input, dict_attr)

    def test_get_atomic_bfact_deviation(self):
        model_input = os.path.join(self.test_data, "5me2.pdb")
        gemmiutils = GemmiModelUtils(model_input)
        dict_bfact = gemmiutils.get_bfact_deviation(calc_dev=False)
        assert len(dict_bfact["1"]) == 4
        assert math.isclose(dict_bfact["1"]["A"]["201"][0], 43.13, rel_tol=1e-3)
        assert math.isclose(dict_bfact["1"]["A"]["201"][1]["NA"], 43.13, rel_tol=1e-3)

    def test_run_subprocess_analyse_bfactors(self):
        model_input = os.path.join(self.test_data, "5me2.pdb")
        subprocess.call(
            [
                "python3 "
                + os.path.realpath(analyse_bfactors.__file__)
                + " -p "
                + model_input
                + " -odir "
                + self.test_dir,
            ],
            shell=True,
        )
        assert os.path.isfile(os.path.join(self.test_dir, "5me2_residue_bfactors.json"))
        assert math.isclose(
            os.stat(os.path.join(self.test_dir, "5me2_residue_bfactors.json")).st_size,
            11661,
            rel_tol=0.05,
        )
        assert os.path.isfile(
            os.path.join(self.test_dir, "5me2_residue_coordinates.json")
        )
        assert math.isclose(
            os.stat(
                os.path.join(self.test_dir, "5me2_residue_coordinates.json")
            ).st_size,
            19383,
            rel_tol=0.05,
        )
