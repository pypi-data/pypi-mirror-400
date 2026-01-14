from __future__ import annotations
import numpy as np
import copy
from typing import Union, Optional, Sequence
import mrcfile


class MapObjHandle(object):
    """This class wraps MrcFile or TEMPy Map objects and sets new attributes and methods
        Note that TEMPy map objects are being replaced by MrcFile objects from TEMPy v2
    :mapobject: Can be a MrcFile, TEMPy Map object or a MapObjHandle instance
    """

    def __init__(self, mapobject, datacopy: Optional[bool] = False):
        super(MapObjHandle, self).__init__()
        if type(mapobject) is MapObjHandle:
            for k, v in mapobject.__dict__.items():
                try:
                    if not datacopy and k == "data":
                        self.__dict__[k] = None
                    else:
                        self.__dict__[k] = copy.deepcopy(v)
                except TypeError:  # skip file object pickle failures
                    pass
            self.mrc = None
        else:
            # map data and header details
            # add other attributes?
            self.class_name = mapobject.__class__.__name__
            self.initialize(mapobject, datacopy=datacopy)
            self.mrc = mapobject

    @classmethod
    def from_file(cls, map_input):
        return get_mapobjhandle(map_input)

    @property
    def shape(self):
        return self.data.shape

    @property
    def min(self):
        return np.amin(self.data)

    @property
    def max(self):
        return np.amax(self.data)

    @property
    def std(self):
        return np.std(self.data)

    @property
    def x_size(self):
        """
        size of the map array in x direction.
        """
        return self.data.shape[2]

    @property
    def y_size(self):
        """
        size of the map array in y direction.
        """
        return self.data.shape[1]

    @property
    def z_size(self):
        """
        size of the map array in z direction.
        """
        return self.data.shape[0]

    def copy(self, deep=False):
        """
        Copy contents to a new object
        """
        # create a new mapobj
        copymap = MapObjHandle(self, datacopy=deep)
        if not deep:
            copymap.data = None
        return copymap

    def data_copy(self, mapobject):
        """
        Copy data from mapobj (not to modify inplace)
        """
        if self.class_name == "MrcFile":
            self.data = mapobject.data.copy()
        elif self.class_name == "Map":
            self.data = mapobject.fullMap.copy()

    def reinitialize_data(self, mapobject, datacopy=False):
        """
        Initialize or re-initialize data
        """
        if not datacopy:
            if self.class_name == "MrcFile":
                self.data = mapobject.data
            elif self.class_name == "Map":
                self.data = mapobject.fullMap
        else:
            self.data_copy(mapobject)

    def reinitialize_header(self, mapobject):
        """
        Initialize or re-initialize header
        """

        if self.class_name == "MrcFile":
            self.origin = mapobject.header.origin.item()
            self.apix = mapobject.voxel_size.item()
            self.dim = mapobject.header.cella.item()
            self.nstart = (
                mapobject.header.nxstart,
                mapobject.header.nystart,
                mapobject.header.nzstart,
            )

            self.mapc = mapobject.header.mapc
            self.mapr = mapobject.header.mapr
            self.maps = mapobject.header.maps

        elif self.class_name == "Map":
            self.origin = tuple(mapobject.origin)
            self.apix = (
                round(mapobject.header[10] / mapobject.header[7], 2),
                round(mapobject.header[11] / mapobject.header[8], 2),
                round(mapobject.header[12] / mapobject.header[9], 2),
            )
            self.dim = (
                self.x_size * self.apix[0],
                self.y_size * self.apix[1],
                self.z_size * self.apix[2],
            )
            self.nstart = mapobject.header[4:7]
        else:
            raise TypeError("Only MrcFile and TEMPY Map objects currently supported")

    def initialize(self, mapobject, datacopy=False):
        """
        Initialize/re-initialize data/header
        """
        self.reinitialize_data(mapobject, datacopy=datacopy)
        self.reinitialize_header(mapobject)

    @staticmethod
    def compare_tuple(tuple1, tuple2):
        for val1, val2 in zip(tuple1, tuple2):
            if type(val2) is float:
                if round(val1, 2) != round(val2, 2):
                    return False
            else:
                if val1 != val2:
                    return False
        return True

    # update map header records
    def update_newmap_header(self, mrcobj):
        """
        Copy current values to a newmap (mrcfile/ TEMPy Map obj)
        """
        if mrcobj.__class__.__name__ == "MrcFile":
            # origin
            mrcobj.header.origin.x = self.origin[0]
            mrcobj.header.origin.y = self.origin[1]
            mrcobj.header.origin.z = self.origin[2]
            # dimensions
            mrcobj.header.cella.x = self.dim[0]
            mrcobj.header.cella.y = self.dim[1]
            mrcobj.header.cella.z = self.dim[2]
            # voxel_size
            mrcobj.voxel_size = self.apix
            mrcobj.header.nxstart = self.nstart[0]
            mrcobj.header.nystart = self.nstart[1]
            mrcobj.header.nzstart = self.nstart[2]
            mrcobj.header.mapc = self.mapc
            mrcobj.header.mapr = self.mapr
            mrcobj.header.maps = self.maps

        elif mrcobj.__class__.__name__ == "Map":
            # origin
            mrcobj.origin[0] = self.origin[0]
            mrcobj.origin[1] = self.origin[1]
            mrcobj.origin[2] = self.origin[2]
            # voxel_size
            mrcobj.apix = self.apix[0]
            mrcobj.header[4] = self.nstart[0]
            mrcobj.header[5] = self.nstart[1]
            mrcobj.header[6] = self.nstart[2]
            # TODO: Update the mapc, mapr, maps values

    # update map array data
    def update_newmap_data(self, mrcobj):
        """
        Update new map (mrcfile/TEMPy) data array with current
        """
        if mrcobj.__class__.__name__ == "MrcFile":
            if not str(self.data.dtype) == "float32":
                try:
                    mrcobj.set_data(self.data.astype("float32", copy=False))
                except (TypeError, ValueError):
                    raise TypeError("Could not set data of type 'float32'")
            else:
                mrcobj.set_data(self.data)
        elif mrcobj.__class__.__name__ == "Map":
            mrcobj.fullMap[:] = self.data

    def update_newmap_data_header(self, mrcobj):
        """
        Update data and header of mrcfile map obj with current values
        """
        self.update_newmap_data(mrcobj)
        self.update_newmap_header(mrcobj)

    def update_header_by_data(self):
        self.dim = (
            self.x_size * self.apix[0],
            self.y_size * self.apix[1],
            self.z_size * self.apix[2],
        )

    def update_header_newgrid(
        self,
        new_origin: Sequence[float],
        new_spacing: Sequence[float],
        gridshape: Sequence[int],
        new_gridshape: Sequence[int],
        reset_nstart: bool = False,
    ):
        """update header for new grid

        :param new_origin: new grid origin
        :type new_origin: Sequence[float]
        :param new_spacing: new spacing
        :type new_spacing: Sequence[float]
        :param gridshape: current/old grid shape [z,y,x]
        :type gridshape: Sequence[int]
        :param new_gridshape: new grid shape [z,y,x]
        :type new_gridshape: Sequence[int]
        :param reset_nstart: _description_, defaults to False
        :type reset_nstart: bool, optional
        """
        self.origin = new_origin
        if reset_nstart:
            self.reset_nstart_apix(new_spacing)
        else:
            self.set_nstart_shape(gridshape, new_gridshape)
        self.set_dim_apix(new_spacing)
        # self.update_header_by_data()

    def set_attributes_tempy(self):
        """
        Set class attributes to use with TEMPy functions
        """
        self.fullMap = self.data
        self.nxstart = self.nstart[0]
        self.nystart = self.nstart[1]
        self.nzstart = self.nstart[2]

    def set_dim_apix(self, apix):
        """
        Set dimensions (Angstroms) given voxel size
        """
        self.apix = apix
        self.dim = (
            self.x_size * self.apix[0],
            self.y_size * self.apix[1],
            self.z_size * self.apix[2],
        )

    def set_apix_dim(self, dim):
        """
        Set voxel size given dimensions (Angstroms) of Grid
        """
        self.dim = dim
        self.apix = (
            np.around(self.dim[0] / self.x_size, decimals=3),
            np.around(self.dim[1] / self.y_size, decimals=3),
            np.around(self.dim[2] / self.z_size, decimals=3),
        )

    def set_nstart_shape(self, gridshape: Sequence[int], new_shape: Sequence[int]):
        """
        Set nstart given new shape of Grid
        """
        size_scale = (
            new_shape[2] / gridshape[2],
            new_shape[1] / gridshape[1],
            new_shape[0] / gridshape[0],
        )
        self.nstart = (
            int(round(self.nstart[0] * size_scale[0])),
            int(round(self.nstart[1] * size_scale[1])),
            int(round(self.nstart[2] * size_scale[2])),
        )

    def reset_nstart_apix(self, new_apix):
        """
        Reset nstart given new spacing of Grid
        """
        self.nstart = (
            int(round(self.origin[0] / new_apix[0])),
            int(round(self.origin[1] / new_apix[1])),
            int(round(self.origin[2] / new_apix[2])),
        )

    def set_apix_tempy(self, inplace=True):
        """
        Set apix to single float value for using TEMPy functions
        """
        if isinstance(self.apix, tuple):
            if self.apix[0] == self.apix[1] == self.apix[2]:
                self.apix = self.apix[0]
            else:
                self.downsample_apix(max(self.apix), inplace=inplace)
                self.apix = self.apix[0]

    def check_origin_zero(self):
        """
        Check map origin is (0,0,0)
        """
        return self.compare_tuple(tuple(self.origin), (0.0, 0.0, 0.0))

    def check_nstart_zero(self):
        """
        Check map nstart is (0,0,0)
        """
        return self.compare_tuple(tuple(self.nstart), (0, 0, 0))

    def shift_origin(self, new_origin: Union[list, tuple, np.ndarray]):
        """
        Shift map to given origin
        """
        assert len(new_origin) == 3
        self.origin = tuple(new_origin)

    def shift_nstart(self, new_nstart: Union[list, tuple, np.ndarray]):
        """
        Update nstart record to given nstart
        """
        assert len(new_nstart) == 3
        self.nstart = tuple(new_nstart)

    def fix_origin(self):
        """
        Set origin record based on nstart if non-zero
        """
        if self.origin[0] == 0.0 and self.origin[1] == 0.0 and self.origin[2] == 0.0:
            if self.nstart[0] != 0 or self.nstart[1] != 0 or self.nstart[2] != 0:
                self.set_apix_as_tuple()
                # origin
                self.origin = (
                    self.nstart[0] * self.apix[0],
                    self.nstart[1] * self.apix[1],
                    self.nstart[2] * self.apix[2],
                )

    def set_apix_as_tuple(self):
        if isinstance(self.apix, (int, float)):
            self.apix = (self.apix, self.apix, self.apix)

    def detach_data(self):
        self.data = None

    def close(self):
        self.detach_data
        if self.mrc:
            if self.class_name == "MrcFile":
                self.mrc.close()
            self.mrc = None

    def to_file(self, map_output, close=True):
        write_mrc_file(map_output, self, close=close)


def get_mapobjhandle(map_input):
    # read
    with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
        wrapped_mapobj = MapObjHandle(mrc)
        return wrapped_mapobj


def write_mrc_file(map_output, wrapped_mapobj, close=True):
    # write
    with mrcfile.new(map_output, overwrite=True) as mrc:
        wrapped_mapobj.update_newmap_data_header(mrc)
    if close:
        wrapped_mapobj.close()
