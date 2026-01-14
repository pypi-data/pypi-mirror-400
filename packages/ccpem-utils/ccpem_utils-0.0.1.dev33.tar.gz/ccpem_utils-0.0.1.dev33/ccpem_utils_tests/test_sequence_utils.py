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
import tempfile
import shutil
from ccpem_utils_tests import test_data
from ccpem_utils.sequence.sequence_utils import (
    get_seq_identities_exact_match,
    merge_set_unique_id_fasta,
)


class SequenceUtilsTest(unittest.TestCase):
    def setUp(self):
        """
        Setup test data and output directories.
        """
        self.test_data = os.path.dirname(test_data.__file__)
        self.test_dir = tempfile.mkdtemp(prefix="sequence_utils")
        # Change to test directory
        self._orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self._orig_dir)
        # print(self.test_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_seq_identities_exact_match(self):
        sequence_identities = get_seq_identities_exact_match("AEPPVGLLMKPQ", "PPGLMPQ")
        assert sequence_identities == (58.333, 100.0)

    def test_merge_set_unique_id_fasta(self):
        list_fastafiles = [
            os.path.join(self.test_data, "5ni1_entry.fasta"),
            os.path.join(self.test_data, "5ni1_entry.fasta"),
        ]
        dict_fasta = merge_set_unique_id_fasta(list_fastafiles=list_fastafiles)
        assert len(dict_fasta) == 4
        assert len(dict_fasta["5ni1_entry_pdb|5ni1|A C"]) == len(
            dict_fasta["5ni1_entry_pdb|5ni1|A C_1"]
        )
