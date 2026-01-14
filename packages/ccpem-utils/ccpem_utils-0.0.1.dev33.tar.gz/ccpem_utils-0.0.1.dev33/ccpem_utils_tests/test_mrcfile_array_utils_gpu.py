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
import math
import shutil
import numpy as np
from ccpem_utils_tests import test_data
from ccpem_utils.map.mrc_map_utils import (
    interpolate_to_grid,
    downsample_apix,
    normalise_mapobj,
)
from ccpem_utils.map.mrcfile_utils import get_mapobjhandle, write_newmapobj
from ccpem_utils.map.array_utils import rotate_array
from ccpem_utils.other.calc import get_ccc
from ccpem_utils.other.utils import set_gpu


class MapParseTests(unittest.TestCase):
    def setUp(self):
        """
        Setup test data and output directories.
        """
        self.test_data = os.path.dirname(test_data.__file__)
        self.test_dir = tempfile.mkdtemp(prefix="map_parse")
        # Change to test directory
        self._orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self._orig_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @unittest.skipIf(not set_gpu(), "GPU not available")
    def test_interpolate_downsample(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        cpu_downsized_array = os.path.join(self.test_data, "emd_3488_interpolated.npy")
        data_array = np.load(cpu_downsized_array)
        wrapped_mapobj = get_mapobjhandle(map_input)
        # interpolate
        interpolated_mapobj = interpolate_to_grid(
            wrapped_mapobj, (50, 50, 50), (2.1, 2.1, 2.1), (0.0, 0.0, 0.0)
        )
        # write
        write_newmapobj(interpolated_mapobj, "emd_3488_interpolated.mrc")
        # check1
        interpolated_mapobj = get_mapobjhandle("emd_3488_interpolated.mrc")
        assert interpolated_mapobj.data.shape == (50, 50, 50)
        assert interpolated_mapobj.origin == (0.0, 0.0, 0.0)
        assert math.isclose(
            interpolated_mapobj.apix[0],
            2.1,
            rel_tol=0.00001,
        )
        assert np.allclose(interpolated_mapobj.data, data_array, atol=1e-5)
        # downsample
        downsampled_mapobj = downsample_apix(wrapped_mapobj, (2.1, 2.1, 2.1))
        # write
        write_newmapobj(downsampled_mapobj, "emd_3488_downsampled.mrc")
        # check2
        downsampled_mapobj = get_mapobjhandle("emd_3488_downsampled.mrc")
        assert downsampled_mapobj.data.shape == (50, 50, 50)
        assert downsampled_mapobj.origin == (0.0, 0.0, 0.0)
        assert math.isclose(
            downsampled_mapobj.apix[0],
            2.1,
            rel_tol=0.00001,
        )
        assert (
            get_ccc(
                interpolated_mapobj.data,
                downsampled_mapobj.data,
            )
            == 1.0
        )

    @unittest.skipIf(not set_gpu(), "GPU not available")
    def test_normalse_mapobj(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        cpu_normalised_array = os.path.join(self.test_data, "emd_3488_normalised.npy")
        data_array = np.load(cpu_normalised_array)
        wrapped_mapobj = get_mapobjhandle(map_input)
        normalise_mapobj(wrapped_mapobj, inplace=True)
        # write
        write_newmapobj(wrapped_mapobj, "emd_3488_normalised.mrc")
        # check
        wrapped_mapobj = get_mapobjhandle("emd_3488_normalised.mrc")
        assert wrapped_mapobj.data.max() == 1.0
        assert wrapped_mapobj.data.min() == 0.0
        assert np.allclose(wrapped_mapobj.data, data_array, atol=1e-5)

    @unittest.skipIf(not set_gpu(), "GPU not available")
    def test_rotate_array(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        cpu_rotated_array = os.path.join(self.test_data, "emd_3488_rotated.npy")
        data_array = np.load(cpu_rotated_array)
        wrapped_mapobj = get_mapobjhandle(map_input)
        pre_rotated_array = wrapped_mapobj.data.copy()
        rotated_array = rotate_array(
            wrapped_mapobj.data, angle=30, axes=(0, 1), reshape=False
        )
        assert rotated_array.shape == (100, 100, 100)
        # write
        wrapped_mapobj.data = rotated_array
        write_newmapobj(wrapped_mapobj, "emd_3488_rotated.mrc")
        # check
        rotated_mapobj = get_mapobjhandle("emd_3488_rotated.mrc")
        assert not np.array_equal(rotated_mapobj.data, pre_rotated_array)
        assert rotated_mapobj.data.shape == (100, 100, 100)
        assert rotated_mapobj.origin == (0.0, 0.0, 0.0)

        assert np.any(rotated_mapobj.data != pre_rotated_array)

        # The cvals are different so the fill values are different
        # this encompases the majority of the array and assumingly enough to compare
        # the gpu code operates identically to the cpu code
        left = 15
        right = 85
        rotated_map_cpu = rotated_mapobj.data[left:right, left:right, left:right]
        rotated_map_gpu = data_array[left:right, left:right, left:right]

        assert np.sum(rotated_map_cpu != rotated_map_gpu) == 0
        assert np.allclose(rotated_map_cpu, rotated_map_gpu, atol=1e-5)
