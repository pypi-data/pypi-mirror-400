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
from ccpem_utils.other.utils import get_unique_id


class UtilsTests(unittest.TestCase):
    def setUp(self):
        """
        Setup test data and output directories.
        """
        self.test_data = os.path.dirname(test_data.__file__)
        self.test_dir = tempfile.mkdtemp(prefix="utils")
        # Change to test directory
        self._orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self._orig_dir)
        print(self.test_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_unique_id(self):
        list_ids = ["chain A", "chain A_B", "chain B", "chain A_1", "chain A_B_1"]
        assert get_unique_id("chain A", list_ids=list_ids) == "chain A_2"
        assert get_unique_id("chain A_B", list_ids=list_ids) == "chain A_B_2"
        assert get_unique_id("chain B", list_ids=list_ids) == "chain B_1"
        assert get_unique_id("chain C", list_ids=list_ids) == "chain C"
        assert get_unique_id("chain A_1", list_ids=list_ids) == "chain A_1_1"
