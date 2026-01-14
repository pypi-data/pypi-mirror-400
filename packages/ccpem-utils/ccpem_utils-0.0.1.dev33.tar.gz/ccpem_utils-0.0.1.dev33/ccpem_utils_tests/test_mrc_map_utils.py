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
import subprocess
from ccpem_utils.scripts import get_map_parameters
from ccpem_utils.map.mrc_map_utils import (
    crop_map_grid,
    pad_map_grid,
    interpolate_to_grid,
    downsample_apix,
    lowpass_filter,
    normalise_mapobj,
    borders_mapobj,
    data_extent_mapobj,
    pad_map_grid_split_distribution,
)
from ccpem_utils.map.mrcfile_utils import get_mapobjhandle, write_newmapobj
from ccpem_utils.map.array_utils import get_contour_mask, rotate_array
import numpy as np
import mrcfile
from ccpem_utils.other.calc import get_ccc


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

    def test_map_crop(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        wrapped_mapobj = get_mapobjhandle(map_input)
        # process1
        cropped_mapobj = crop_map_grid(wrapped_mapobj, new_dim=(71, 73, 58))
        # write1
        write_newmapobj(cropped_mapobj, "emd_3488_cropped1.mrc")
        # check1
        cropped_mapobj1 = get_mapobjhandle("emd_3488_cropped1.mrc")
        assert cropped_mapobj1.data.shape == (58, 73, 71)
        # process2
        cropped_mapobj2 = crop_map_grid(wrapped_mapobj, contour=0.125, ext=(3, 3, 3))
        # write
        write_newmapobj(cropped_mapobj2, "emd_3488_cropped2.mrc")
        # check
        cropped_mapobj2 = get_mapobjhandle("emd_3488_cropped2.mrc")
        assert cropped_mapobj2.data.shape == (58, 73, 71)
        assert (
            get_ccc(
                cropped_mapobj1.data,
                cropped_mapobj2.data,
            )
            == 1.0
        )
        # process3
        cropped_mapobj3 = crop_map_grid(
            wrapped_mapobj,
            contour=0.125,
            ext=(3, 3, 3),
            cubic=True,
        )
        assert cropped_mapobj3.data.shape == (73, 73, 73)
        maskmap = wrapped_mapobj.copy()
        maskmap.data = wrapped_mapobj.data >= 0.125
        # mask input
        cropped_mapobj4 = crop_map_grid(
            wrapped_mapobj,
            input_maskobj=maskmap,
            ext=(3, 3, 3),
            cubic=True,
        )
        cropped_mapobj3.data = cropped_mapobj3.data * (cropped_mapobj3.data >= 0.125)
        assert (
            get_ccc(
                cropped_mapobj3.data,
                cropped_mapobj4.data,
            )
            == 1
        )
        maskmap = cropped_mapobj4.copy()
        maskmap.data = cropped_mapobj4.data > 0.2
        # convert to label array
        cropped_mapobj4.data[cropped_mapobj4.data > 0.3] = 3
        cropped_mapobj4.data[cropped_mapobj4.data <= 0.1] = 0
        cropped_mapobj4.data[
            np.logical_and(cropped_mapobj4.data > 0.1, cropped_mapobj4.data <= 0.2)
        ] = 1
        cropped_mapobj4.data[
            np.logical_and(cropped_mapobj4.data > 0.2, cropped_mapobj4.data <= 0.3)
        ] = 2

        cropped_mapobj5 = crop_map_grid(
            cropped_mapobj4,
            input_maskobj=maskmap,
            ext=(3, 3, 3),
            cubic=True,
        )
        assert np.amin(cropped_mapobj5.data[cropped_mapobj5.data > 0]) == 2

    def test_map_pad(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        wrapped_mapobj = get_mapobjhandle(map_input)
        # process
        padded_mapobj = pad_map_grid(wrapped_mapobj, ext_dim=(10, 10, 10))
        min_map = wrapped_mapobj.data.min()
        # write
        write_newmapobj(padded_mapobj, "emd_3488_padded.mrc")
        # check1
        padded_mapobj = get_mapobjhandle("emd_3488_padded.mrc")
        assert padded_mapobj.data.shape == (120, 120, 120)
        min_padded_map = padded_mapobj.data.min()
        assert min_map == min_padded_map  # padding filled with min

    def test_map_pad_split(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        wrapped_mapobj = get_mapobjhandle(map_input)
        # process
        padded_mapobj = pad_map_grid_split_distribution(
            wrapped_mapobj, ext_dim=(3, 7, 2)
        )
        min_map = wrapped_mapobj.data.min()
        # write
        write_newmapobj(padded_mapobj, "emd_3488_padded_split.mrc")
        # check1
        padded_mapobj = get_mapobjhandle("emd_3488_padded_split.mrc")
        assert padded_mapobj.data.shape == (103, 107, 102)
        min_padded_map = padded_mapobj.data.min()
        assert min_map == min_padded_map  # padding filled with min

    def test_interpolate_downsample(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
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

    def test_lowpass_filter(self):
        emanmapfile = os.path.join(self.test_data, "1ake_molmap45_tanhlp_eman2.mrc")
        emanmapobj = mrcfile.open(emanmapfile, mode="r")
        map_input = os.path.join(self.test_data, "1ake_molmap45.mrc")
        wrapped_mapobj = get_mapobjhandle(map_input)
        filtered_mapobj = lowpass_filter(
            wrapped_mapobj, resolution=7.5, filter_fall=0.5
        )
        # write1
        write_newmapobj(
            filtered_mapobj, "1ake_molmap45_lowpass.mrc", close_mapobj=False
        )

        self.assertAlmostEqual(
            np.corrcoef(filtered_mapobj.data.ravel(), emanmapobj.data.ravel())[0][1],
            1.0,
            2,
        )
        filtered_mapobj.close()

    def test_run_subprocess_get_map_parameters(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        subprocess.call(
            [
                "python3 "
                + os.path.realpath(get_map_parameters.__file__)
                + " -m "
                + map_input
                + " -odir "
                + self.test_dir,
            ],
            shell=True,
        )
        assert os.path.isfile(
            os.path.join(self.test_dir, "emd_3488_map_parameters.json")
        )
        assert math.isclose(
            os.stat(
                os.path.join(self.test_dir, "emd_3488_map_parameters.json")
            ).st_size,
            275,
            rel_tol=0.05,
        )

    def test_normalse_mapobj(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        wrapped_mapobj = get_mapobjhandle(map_input)
        normalise_mapobj(wrapped_mapobj, inplace=True)
        # write
        write_newmapobj(wrapped_mapobj, "emd_3488_normalised.mrc")
        # check
        wrapped_mapobj = get_mapobjhandle("emd_3488_normalised.mrc")
        assert wrapped_mapobj.data.max() == 1.0
        assert wrapped_mapobj.data.min() == 0.0
        # save the data as a numpy array

    def test_borders_mapobj(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        wrapped_mapobj = get_mapobjhandle(map_input)
        # check borders without a mask
        extent = data_extent_mapobj(wrapped_mapobj)
        shape, (halfx, halfy, halfz) = borders_mapobj(wrapped_mapobj)

        assert extent == (4, 96, 3, 97, 10, 90)
        assert shape == (94, 96, 84)
        assert (halfx, halfy, halfz) == (50, 50, 50)

        # check borders of mask
        contour = 0.125
        mask_bool = get_contour_mask(wrapped_mapobj.data, contour)
        data_zeros = np.zeros(wrapped_mapobj.shape)
        data_zeros[mask_bool] = 1
        wrapped_mapobj.data = data_zeros

        extent = data_extent_mapobj(wrapped_mapobj)
        shape, (halfx, halfy, halfz) = borders_mapobj(wrapped_mapobj)
        assert extent == (19, 81, 18, 82, 25, 74)
        assert shape == (66, 68, 53)
        assert (halfx, halfy, halfz) == (50, 50, 49)

        # write
        wrapped_mapobj.update_header_by_data()
        write_newmapobj(wrapped_mapobj, "emd_3488_mask.mrc")

    def test_rotate_array(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
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
