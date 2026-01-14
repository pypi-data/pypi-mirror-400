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
import math
from ccpem_utils.other.calc import get_skewness


class CoordClustTests(unittest.TestCase):
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
        print(self.test_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_skewness(self):
        assert get_skewness([0, 1, 2, 3, 4, 5]) == 0.0
        assert math.isclose(
            get_skewness([0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 4, 5]), 1.265, rel_tol=0.001
        )
        assert math.isnan(get_skewness([1, 1, 1, 1, 1, 1, 1, 1, 1]))
