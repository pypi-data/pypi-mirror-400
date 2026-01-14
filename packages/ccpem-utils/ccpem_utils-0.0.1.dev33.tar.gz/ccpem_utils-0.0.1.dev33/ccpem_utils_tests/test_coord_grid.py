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
import shutil
import tempfile
import numpy as np
from ccpem_utils_tests import test_data
from ccpem_utils.model.coord_grid import (
    set_map_grid,
    set_cubic_map_grid,
    mapGridPositions,
)
from ccpem_utils.model.gemmi_model_utils import GemmiModelUtils
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from ccpem_utils.scripts import (
    shift_model_refmap_origin,
)
from ccpem_utils.map.mrc_map_utils import crop_map_grid
from ccpem_utils.map.mrcfile_utils import (
    write_newmapobj,
    get_mapobjhandle,
    edit_map_origin_nstart,
)
from ccpem_utils.other.calc import check_list_overlap
import mrcfile
import subprocess


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
        print(self.test_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_model_grid(self):
        # read
        model_input = os.path.join(self.test_data, "5me2.pdb")
        origin, dim = set_map_grid(model_input, apix=(1.0, 1.0, 1.0))
        with mrcfile.new("5me2.mrc") as mrc:
            mrc.header.origin.x = origin[0]
            mrc.header.origin.y = origin[1]
            mrc.header.origin.z = origin[2]
            # dimensions
            mrc.header.cella.x = dim[0]
            mrc.header.cella.y = dim[1]
            mrc.header.cella.z = dim[2]
            # voxel_size
            mrc.voxel_size = (1.0, 1.0, 1.0)
            mrc.set_data(np.zeros((dim[2], dim[1], dim[0]), dtype="float32"))
        assert dim == (108, 110, 96)
        origin, dim = set_cubic_map_grid(model_input, apix=(1.0, 1.0, 1.0))
        assert dim == (110, 110, 110)

    def test_run_subprocess_shift_map_model_zero(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # crop
        cropped_mapobj = crop_map_grid(wrapped_mapobj, new_dim=(71, 73, 58))
        # write
        write_newmapobj(cropped_mapobj, "emd_3488_cropped.mrc", close_mapobj=False)
        list_grid_points = mapGridPositions(
            cropped_mapobj, atom_coord=(61.197, 39.327, 61.266), res_map=3.2
        )[:]
        assert len(list_grid_points) == 22
        ox, oy, oz = cropped_mapobj.origin
        cropped_mapobj.close()
        model_input = os.path.join(self.test_data, "5me2.pdb")
        subprocess.call(
            [
                "python3 "
                + os.path.realpath(shift_model_refmap_origin.__file__)
                + " -refm "
                + "emd_3488_cropped.mrc"
                + " -p "
                + model_input
            ],
            shell=True,
        )
        shifted_map = (
            os.path.splitext(os.path.basename("emd_3488_cropped.mrc"))[0]
            + "_shifted_zero.mrc"
        )
        edit_map_origin_nstart(
            map_input="emd_3488_cropped.mrc",
            new_origin=(0, 0, 0),
            map_output=shifted_map,
        )
        wrapped_mapobj = get_mapobjhandle(shifted_map)
        list_grid_points_shifted = mapGridPositions(
            wrapped_mapobj,
            atom_coord=(61.197 - ox, 39.327 - oy, 61.266 - oz),
            res_map=3.2,
        )
        shifted_model = (
            os.path.splitext(os.path.basename(model_input))[0]
            + "_shifted"
            + os.path.splitext(model_input)[1]
        )
        assert os.path.isfile(shifted_map)
        assert os.path.isfile(shifted_model)
        assert np.array_equal(list_grid_points, list_grid_points_shifted)

    def test_run_subprocess_shift_model_back_nonzero(self):
        map_input = os.path.join(self.test_data, "emd_21457_seg.mrc")
        wrapped_mapobj = get_mapobjhandle(map_input)
        list_grid_points = mapGridPositions(
            wrapped_mapobj, atom_coord=(183.125, 247.995, 249.119), res_map=3.2
        )[:]
        assert len(list_grid_points) == 21
        wrapped_mapobj.close()
        model_input = os.path.join(self.test_data, "6vyb_Ndom_shifted.pdb")
        subprocess.call(
            [
                "python3 "
                + os.path.realpath(shift_model_refmap_origin.__file__)
                + " -refm "
                + map_input
                + " -p "
                + model_input
                + " --fitted_zero "
            ],
            shell=True,
        )
        shifted_model = (
            os.path.splitext(os.path.basename(model_input))[0]
            + "_shifted"
            + os.path.splitext(model_input)[1]
        )
        gemmiutils = GemmiModelUtils(shifted_model)
        dict_coord = gemmiutils.get_coordinates(atom_selection="one_per_residue")
        E132_coord = dict_coord["1"]["A"]["132"][0]
        assert os.path.isfile(shifted_model)
        list_grid_points_shifted = mapGridPositions(
            wrapped_mapobj,
            atom_coord=E132_coord,
            res_map=3.2,
        )
        # check if the map grid positions overlap
        assert check_list_overlap(
            list(list_grid_points),
            list(list_grid_points_shifted),
            diff_limit=0.1,
        )
