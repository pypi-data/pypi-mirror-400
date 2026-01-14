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
import math
from ccpem_utils_tests import test_data
import subprocess
from ccpem_utils.scripts import get_map_parameters
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from ccpem_utils.model.coord_grid import mapGridPositions
from ccpem_utils.map.mrcfile_utils import get_origin_nstart
import mrcfile


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

    def test_map_parse(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # process
        wrapped_mapobj.shift_origin((1.0, 1.0, 1.0))
        with mrcfile.new("emd_3488_shifted.mrc", overwrite=True) as mrc:
            wrapped_mapobj.update_newmap_data_header(mrc)
        wrapped_mapobj.close()
        # write
        with mrcfile.open("emd_3488_shifted.mrc", mode="r") as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
            assert wrapped_mapobj.origin == (1.0, 1.0, 1.0)
        assert get_origin_nstart("emd_3488_shifted.mrc")[0] == (1.0, 1.0, 1.0)

    def test_map_fix_origin(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # process
        wrapped_mapobj.shift_nstart((1, 1, 1))
        wrapped_mapobj.fix_origin()
        assert tuple([round(o, 5) for o in wrapped_mapobj.origin]) == (
            1.05,
            1.05,
            1.05,
        )

    def test_map_check_origin(self):
        # read
        map_input = os.path.join(self.test_data, "emd_21457_seg_orig0.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # process
        assert wrapped_mapobj.check_nstart_zero()
        assert wrapped_mapobj.check_origin_zero()
        wrapped_mapobj.close()
        map_input = os.path.join(self.test_data, "emd_21457_seg.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # process
        assert wrapped_mapobj.check_nstart_zero()
        assert not wrapped_mapobj.check_origin_zero()
        wrapped_mapobj.close()

    def test_map_coordinate_search(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
            list_grid_points = mapGridPositions(
                wrapped_mapobj, atom_coord=(61.197, 39.327, 61.266), res_map=3.2
            )
            assert len(list_grid_points) == 22
            list_grid_points = mapGridPositions(
                wrapped_mapobj,
                atom_coord=(61.197, 39.327, 61.266),
                res_map=3.2,
                gauss=False,
            )
            assert len(list_grid_points) == 1

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
