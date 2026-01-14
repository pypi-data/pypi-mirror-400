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
from ccpem_utils_tests import test_data
from ccpem_utils.map.mrcfile_utils import (
    crop_mrc_map,
    pad_mrc_map,
    calc_mrc_sigma_contour,
    save_contour_mask,
    realspace_filter_map,
    add_softedge,
    bin_mrc_map,
    check_standard_axis_order,
    get_mapobjhandle,
    check_origin_zero,
    get_origin_nstart,
    compare_map_dimensions,
    edit_map_origin_nstart,
    write_newmapobj,
    get_axis_order,
)
import mrcfile
import numpy as np


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

    def test_compare_map_dimensions(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        mask_input = map_input = os.path.join(
            self.test_data, "emd_3488_contour_mask.mrc"
        )
        assert compare_map_dimensions(map1_input=map_input, map2_input=mask_input)

    def test_axis_order(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        assert check_standard_axis_order(map_input)
        mapobj = get_mapobjhandle(map_input)
        mapobj.mapc = 2
        mapobj.mapr = 1
        mapobj.maps = 3
        write_newmapobj(mapobj=mapobj, map_output="emd_order_swapped.mrc")
        assert get_axis_order("emd_order_swapped.mrc")[0].item() == 2
        assert not check_standard_axis_order("emd_order_swapped.mrc")

    def test_edit_map_origin(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        edit_map_origin_nstart(map_input=map_input, new_nstart=(1, 1, 1))
        assert os.path.isfile("emd_3488_shifted.mrc")
        assert get_origin_nstart(map_input="emd_3488_shifted.mrc")[1] == (
            1,
            1,
            1,
        )
        edit_map_origin_nstart(
            map_input="emd_3488_shifted.mrc",
            new_origin=(1.05, 1.05, 1.05),
            inplace=True,
        )
        assert tuple(
            [
                round(o, 5)
                for o in get_origin_nstart(map_input="emd_3488_shifted.mrc")[0]
            ]
        ) == (
            1.05,
            1.05,
            1.05,
        )

    def test_map_crop(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        crop_mrc_map(
            map_input, new_dim=(71, 73, 58), map_output="emd_3488_cropped1.mrc"
        )
        assert not check_origin_zero("emd_3488_cropped1.mrc")
        # check1
        wrapped_mapobj1 = get_mapobjhandle("emd_3488_cropped1.mrc")
        assert wrapped_mapobj1.data.shape == (58, 73, 71)
        # check2
        crop_mrc_map(
            map_input, crop_dim=(10, 10, 10), map_output="emd_3488_cropped2.mrc"
        )
        wrapped_mapobj2 = get_mapobjhandle("emd_3488_cropped2.mrc")
        assert wrapped_mapobj2.data.shape == (80, 80, 80)

    def test_map_pad(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        pad_mrc_map(map_input, ext_dim=(5, 5, 5), map_output="emd_3488_padded.mrc")
        # check1
        wrapped_mapobj = get_mapobjhandle("emd_3488_padded.mrc")
        assert wrapped_mapobj.data.shape == (110, 110, 110)

    def test_downsample(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        bin_mrc_map(map_input, new_dim=50, map_output="emd_3488_downsampled_dim.mrc")
        # check
        downsampled_mapobj = get_mapobjhandle("emd_3488_downsampled_dim.mrc")
        assert downsampled_mapobj.data.shape == (50, 50, 50)
        assert downsampled_mapobj.origin == (0.0, 0.0, 0.0)
        assert check_origin_zero("emd_3488_downsampled_dim.mrc")
        assert get_origin_nstart("emd_3488_downsampled_dim.mrc")[0] == (
            0.0,
            0.0,
            0.0,
        )
        assert math.isclose(
            downsampled_mapobj.apix[0],
            2.1,
            rel_tol=0.00001,
        )
        bin_mrc_map(
            map_input,
            new_spacing=(2.1, 2.1, 2.1),
            map_output="emd_3488_downsampled.mrc",
        )
        # check
        downsampled_mapobj = get_mapobjhandle("emd_3488_downsampled.mrc")
        assert downsampled_mapobj.data.shape == (50, 50, 50)
        assert downsampled_mapobj.origin == (0.0, 0.0, 0.0)
        assert math.isclose(
            downsampled_mapobj.apix[0],
            2.1,
            rel_tol=0.00001,
        )
        assert not compare_map_dimensions(map_input, "emd_3488_downsampled.mrc")

    def test_sigma_contour(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        sigma_contour = calc_mrc_sigma_contour(map_input, sigma_factor=2.0)
        # sigma_contour = 0.068012
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            assert math.isclose(sigma_contour, 2.0 * np.std(mrc.data), rel_tol=0.09)
            mrc_array = mrc.data
        save_contour_mask(map_input, sigma_factor=2.0)
        map_output = os.path.splitext(map_input)[0] + "_contour_mask.mrc"
        assert os.path.isfile(map_output)
        with mrcfile.open(map_output, mode="r", permissive=True) as mrc:
            assert np.sum(mrc_array > sigma_contour) == np.sum(mrc.data)

    def test_real_space_filters(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        # generate two filtered maps and compare
        realspace_filter_map(map_input, filter_type="gaussian")
        realspace_filter_map(map_input, filter_type="tanh")
        assert math.isclose(
            os.stat(
                os.path.join(self.test_dir, "emd_3488_gaussian_filtered.mrc")
            ).st_size,
            os.stat(os.path.join(self.test_dir, "emd_3488_tanh_filtered.mrc")).st_size,
            rel_tol=0.05,
        )

    def test_smooth_maskedge(self):
        map_input = os.path.join(self.test_data, "emd_3488_contour_mask.mrc")
        add_softedge(map_input, edgetype="cosine", edge=3)
        add_softedge(map_input, edgetype="tanh", edge=3)
        assert math.isclose(
            os.stat(
                os.path.join(self.test_dir, "emd_3488_contour_mask_cosine_softmask.mrc")
            ).st_size,
            os.stat(
                os.path.join(self.test_dir, "emd_3488_contour_mask_tanh_softmask.mrc")
            ).st_size,
            rel_tol=0.05,
        )
