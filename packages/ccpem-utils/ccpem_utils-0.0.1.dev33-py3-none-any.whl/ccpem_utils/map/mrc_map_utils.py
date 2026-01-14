#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

from ccpem_utils.other.cluster import generate_kdtree
import numpy as np
from ccpem_utils.map.array_utils import (
    crop_array,
    custom_pad_array,
    pad_array,
    tanh_lowpass,
    apply_filter,
    calculate_fft,
    calculate_ifft,
    add_maskarray_softedge,
    apply_real_space_filter,
    apply_mask,
    threshold_array,
    interpolate_to_newgrid,
    downsample_stride,
    blockwise_average,
)
from typing import Sequence, Union, Optional, Tuple
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from ccpem_utils.other.utils import check_gpu


def crop_map_grid(
    input_map: MapObjHandle,
    new_dim: Optional[Sequence[int]] = None,
    crop_dim: Optional[Sequence[int]] = None,
    contour: Optional[float] = None,
    ext: Sequence[int] = (10, 10, 10),
    cubic: bool = False,
    inplace: bool = False,
    input_maskobj: Optional[MapObjHandle] = None,
    mask_thr: Optional[float] = None,
):
    """
    Crop grid based on given dimensions or contour or mask

    Arguments
    ---------
    :input_map: MapObjHandle
        input map object
    :new_dim:
        new dimensions to crop to
    :crop_dim:
        number of slices to crop from either side of each axis
    :contour: float, optional
        map threshold (slices with all values lower than this are cropped)
    :ext: list, optional
        list of number of slices as padding along each axis
    :mask_map: MapObjHandle
        mask to be applied before cropping (slices with all zeros are cropped)
    :cubic: bool
        whether to crop to a cubic box?
    :inplace: bool
        whether to modify existing map object inplace or create new?

    Return
    ------
    cropped map object if not inplace
    """
    mask_array = None
    if input_maskobj:
        mask_array = input_maskobj.data
        if mask_thr:
            mask_array = input_maskobj.data * (input_maskobj.data > mask_thr)
    if crop_dim:
        map_shape = input_map.data.shape
        new_dim = [
            map_shape[2] - 2 * crop_dim[0],
            map_shape[1] - 2 * crop_dim[1],
            map_shape[0] - 2 * crop_dim[2],
        ]
    if input_maskobj:
        cropped_array, start = crop_array(
            arr=input_map.data,
            new_dim=new_dim,
            contour=contour,
            cubic=cubic,
            ext=ext,
            mask_array=mask_array,
        )
    else:
        cropped_array, start = crop_array(
            arr=input_map.data,
            new_dim=new_dim,
            contour=contour,
            cubic=cubic,
            ext=ext,
        )
    ox = input_map.origin[0] + start[0] * input_map.apix[0]
    oy = input_map.origin[1] + start[1] * input_map.apix[1]
    oz = input_map.origin[2] + start[2] * input_map.apix[2]
    nstx = input_map.nstart[0] + start[0]
    nsty = input_map.nstart[1] + start[1]
    nstz = input_map.nstart[2] + start[2]
    if inplace:
        input_map.origin = (ox, oy, oz)
        input_map.data = cropped_array
        input_map.nstart = (nstx, nsty, nstz)
        input_map.update_header_by_data()
    else:
        newmap = input_map.copy()
        newmap.origin = (ox, oy, oz)
        newmap.data = cropped_array
        newmap.nstart = (nstx, nsty, nstz)
        newmap.update_header_by_data()
        return newmap


def pad_map_grid(
    input_map: MapObjHandle,
    ext_dim: Sequence[int],
    fill_padding: Optional[float] = None,
    inplace: bool = False,
):
    """
    Pad grid based on given dimensions

    Arguments
    ---------
    :input_map: MapObjHandle
        input Map object
    :ext_dim:
        extension to add to either sides of each dimension (nx,ny,nz)
    :fill_padding:
        value to fill padding with
    :inplace: bool
        whether to modify existing map object inplace or create new?

    Return
    ------
    New padded map object if not inplace, otherwise padded input_map
    """
    padded_array, start = pad_array(
        arr=input_map.data,
        nx=ext_dim[0],
        ny=ext_dim[1],
        nz=ext_dim[2],
        fill_padding=fill_padding,
    )
    # shift origin
    ox = input_map.origin[0] - start[0] * input_map.apix[0]
    oy = input_map.origin[1] - start[1] * input_map.apix[1]
    oz = input_map.origin[2] - start[2] * input_map.apix[2]
    nstx = input_map.nstart[0] - start[0]
    nsty = input_map.nstart[1] - start[1]
    nstz = input_map.nstart[2] - start[2]
    if inplace:
        input_map.origin = (ox, oy, oz)
        input_map.data = padded_array
        input_map.nstart = (nstx, nsty, nstz)
        input_map.update_header_by_data()
    else:
        newmap = input_map.copy()
        newmap.origin = (ox, oy, oz)
        newmap.data = padded_array
        newmap.nstart = (nstx, nsty, nstz)
        newmap.update_header_by_data()
        return newmap


def pad_map_grid_split_distribution(
    mapobj: MapObjHandle,
    ext_dim: tuple,
    inplace: bool = False,
    fill_padding: Optional[float] = None,
    left: bool = True,
):
    """Takes an input map object and pads it with zeros to the specified extent.

    :param mapobj: (MapObjHandle) map object to be padded
    :param ext_dim: (tuple) the extent of the padding in each dimension (X, Y, Z)
    :param inplace: (bool) whether to modify the input map object or return a new one
    :param fill_padding: (float) value to fill the padding with
    :param left: (bool) if there is an odd number of slices to pad, whether to pad
    more on the left or right

    :return: (MapObjHandle) the padded map object
    """

    def even_odd_split(n):
        if n % 2 == 0:
            return n // 2, n // 2
        else:
            return n // 2, n - n // 2

    nx, ny, nz = ext_dim[::-1]
    nx1, nx2 = even_odd_split(nx)
    ny1, ny2 = even_odd_split(ny)
    nz1, nz2 = even_odd_split(nz)

    padded_array = custom_pad_array(
        mapobj.data, nx1, nx2, ny1, ny2, nz1, nz2, fill_padding=fill_padding, left=left
    )

    start = (nx1, ny1, nz1)

    ox = mapobj.origin[0] - start[0] * mapobj.apix[0]
    oy = mapobj.origin[1] - start[1] * mapobj.apix[1]
    oz = mapobj.origin[2] - start[2] * mapobj.apix[2]
    nstx = mapobj.nstart[0] - start[0]
    nsty = mapobj.nstart[1] - start[1]
    nstz = mapobj.nstart[2] - start[2]
    if not inplace:
        newmap = mapobj.copy()
        newmap.origin = (ox, oy, oz)
        newmap.data = padded_array
        newmap.nstart = (nstx, nsty, nstz)
        newmap.update_header_by_data()
        return newmap

    mapobj.origin = (ox, oy, oz)
    mapobj.data = padded_array
    mapobj.nstart = (nstx, nsty, nstz)
    mapobj.update_header_by_data()


def bin_downsample(
    input_map: MapObjHandle,
    new_gridshape: Sequence[int],
    new_spacing: Sequence[float],
    new_origin: Sequence[float],
    method: str = "block_mean",
    reset_nstart=False,
    inplace=False,
):
    o1x, o1y, o1z = (
        float(new_origin[0]),
        float(new_origin[1]),
        float(new_origin[2]),
    )
    arr_shape = input_map.data.shape
    zw, yw, xw = (
        max(2, int(np.ceil(arr_shape[0] / new_gridshape[0]))),
        max(2, int(np.ceil(arr_shape[1] / new_gridshape[1]))),
        max(2, int(np.ceil(arr_shape[2] / new_gridshape[2]))),
    )
    new_spacing = (
        xw * input_map.apix[0],
        yw * input_map.apix[1],
        zw * input_map.apix[2],
    )
    if method == "stride":
        new_array = downsample_stride(input_map.data, stride=(zw, yw, xw))
    else:
        new_array = blockwise_average(input_map.data, block_shape=(zw, yw, xw))
    new_array_shape = new_array.shape
    if inplace:
        input_map.data = new_array
        input_map.update_header_newgrid(
            (o1x, o1y, o1z),
            new_spacing,
            arr_shape,
            new_array_shape,
            reset_nstart=reset_nstart,
        )
    else:
        newmap = input_map.copy()
        newmap.data = new_array
        newmap.update_header_newgrid(
            (o1x, o1y, o1z),
            new_spacing,
            arr_shape,
            new_array_shape,
            reset_nstart=reset_nstart,
        )
        return newmap


# interpolate to a new grid
def interpolate_to_grid(
    input_map: MapObjHandle,
    new_gridshape: Tuple[int, int, int],
    new_spacing: Union[float, Sequence[float]],
    new_origin: Sequence[float],
    interp_order: int = 3,
    reset_nstart: bool = False,
    inplace: bool = False,
    prefilter_input: bool = True,
):
    """
    Interpolate to a new map grid given new shape, spacing and origin

    Arguments
    ---------
    :input_map: MapObjHandle
        input map object
    :new_gridshape: tuple
        new dimensions to interpolate to
    :new_spacing: float
        spacing of the new grid
    :new_origin: float
        origin of the new grid
    :reset_nstart: bool
        whether to reset nstart to 0,0,0?


    :inplace: bool
        whether to modify existing map object inplace or create new?

    :interp_order: int
        order of interpolation (0-5)
    :prefilter_input: bool
        whether to prefilter input data?
    Return
    ------
    new map object with new grid properties
    """

    if check_gpu():
        import cupy as cp

        use_cupy = True
        np_ = cp
    else:
        use_cupy = False
        np_ = np

    if isinstance(new_spacing, float):
        new_spacing = (new_spacing, new_spacing, new_spacing)
    origin = np_.asarray(input_map.origin, dtype=np_.float32)
    new_origin = np_.asarray(new_origin, dtype=np_.float32)
    apix = np_.asarray(input_map.apix, dtype=np_.float32)
    scale = (
        float(new_spacing[0]) / input_map.apix[0],
        float(new_spacing[1]) / input_map.apix[1],
        float(new_spacing[2]) / input_map.apix[2],
    )
    offset = new_origin - origin

    inp_shape = input_map.data.shape

    grid_indices = np_.indices(new_gridshape, dtype=np_.uint16)
    z_ind, y_ind, x_ind = (grid_indices[i].ravel() for i in range(3))

    z_ind = (offset[2] / apix[2]) + scale[2] * z_ind
    y_ind = (offset[1] / apix[1]) + scale[1] * y_ind
    x_ind = (offset[0] / apix[0]) + scale[0] * x_ind
    # cubic interpolation by default
    new_array = interpolate_to_newgrid(
        input_map.data,
        np_.array([z_ind, y_ind, x_ind]),
        mode="nearest",
        interp_order=interp_order,
        prefilter_input=prefilter_input,
    )

    if use_cupy:
        new_array = new_array.get()
        grid_indices = grid_indices.get()
        # mypy fix
        if isinstance(new_origin, np_.ndarray):
            new_origin = new_origin.get()
        else:
            new_origin = tuple(new_origin)

    o1x, o1y, o1z = new_origin

    if inplace:
        input_map.data = new_array.reshape(new_gridshape)
        input_map.update_header_newgrid(
            (o1x, o1y, o1z),
            new_spacing,
            inp_shape,
            new_gridshape,
            reset_nstart=reset_nstart,
        )
    else:
        newmap = input_map.copy()
        newmap.data = new_array.reshape(new_gridshape)
        newmap.update_header_newgrid(
            (o1x, o1y, o1z),
            new_spacing,
            inp_shape,
            new_gridshape,
            reset_nstart=reset_nstart,
        )
        return newmap


# interpolate to a new grid with different voxel size
def downsample_apix(
    input_map: MapObjHandle,
    new_spacing: Union[float, Sequence[float]],
    grid_shape: Optional[Union[int, Tuple[int, int, int]]] = None,  # z,y,x
    inplace: bool = False,
    interp_order: int = 3,
    prefilter_input: bool = True,
):
    """
    Downsample map based on voxel size

    Arguments
    ---------
    :input_map: MapObjHandle
        input map object
    :new_spacing: float
        spacing of the new grid
    :inplace: bool
        whether to modify existing map object inplace or create new?

    Return
    ------
    new map object with downsampled grid
    """
    if isinstance(new_spacing, float):
        new_spacing = (new_spacing, new_spacing, new_spacing)
    if not len(new_spacing) == 3:
        raise ValueError("Please provide valid new_spacing for downsampled map")
    apix_ratio = (
        input_map.apix[0] / new_spacing[0],
        input_map.apix[1] / new_spacing[1],
        input_map.apix[2] / new_spacing[2],
    )
    if grid_shape is None:
        grid_shape = (
            int(round(input_map.z_size * apix_ratio[2])),
            int(round(input_map.y_size * apix_ratio[1])),
            int(round(input_map.x_size * apix_ratio[0])),
        )
    if isinstance(grid_shape, int):
        grid_shape = (grid_shape, grid_shape, grid_shape)
    interpolated_mapobj = interpolate_to_grid(
        input_map,
        grid_shape,
        new_spacing,
        input_map.origin,
        inplace=inplace,
        interp_order=interp_order,
        prefilter_input=prefilter_input,
    )
    if not inplace:
        return interpolated_mapobj


def lowpass_filter(
    input_map: MapObjHandle,
    resolution: float,
    filter_fall: float = 0.3,
    new_spacing: Optional[Sequence[float]] = None,
    inplace: bool = False,
):
    """Lowpass filter a given map (MapObjHandle instance)

    :param input_map: input map instance to lowpass filter
    :type input_map: MapObjHandle
    :param resolution: resolution for lowpass cutoff
    :type resolution: float
    :param filter_fall: smoothness of falloff [0-> tophat,1.0-> gaussian],
        defaults to 0.3
    :type filter_fall: float
    :param new_spacing: filtered map spacing, defaults to None (current spacing)
    :type new_spacing: Sequence[float], optional
    :param inplace: to overwrite map array inplace?, defaults to True
    :type inplace: bool, optional
    """
    ftmap = calculate_fft(input_map.data, keep_shape=False)
    cutoff = min(0.5, max(input_map.apix) / resolution)
    tanh_filter = tanh_lowpass(
        input_map.data.shape,
        cutoff=cutoff,
        fall=filter_fall,
        keep_shape=False,
    )
    ftmap[:] = np.fft.fftshift(ftmap, axes=(0, 1))
    filt_ftmap = apply_filter(ftmap, tanh_filter)
    filt_ftmap[:] = np.fft.ifftshift(filt_ftmap, axes=(0, 1))
    filt_map = calculate_ifft(filt_ftmap, output_shape=input_map.data.shape)

    if inplace:
        input_map.data = filt_map
        if new_spacing:
            downsample_apix(input_map, new_spacing, inplace=True)
    else:
        filtered_map = input_map.copy()
        filtered_map.data = filt_map
        if new_spacing:
            downsample_apix(filtered_map, new_spacing, inplace=True)
        return filtered_map


def softedge_map(
    mapobj: MapObjHandle,
    filter_type: str = "cosine",
    edge: int = 6,
    inplace: bool = False,
):
    blurred_array = add_maskarray_softedge(
        mapobj.data, edge=edge, filter_type=filter_type
    )
    if inplace:
        mapobj.data = blurred_array
        mapobj.update_header_by_data()
    else:
        new_mapobj = mapobj.copy(deep=False)
        new_mapobj.data = blurred_array
        new_mapobj.update_header_by_data()
        return new_mapobj


def realspace_filter_mapobj(
    mapobj: MapObjHandle,
    filter_type: str = "gaussian",
    kernel_size: int = 5,
    sigma: float = 1,
    truncate: int = 3,
    iter: int = 1,
    inplace: bool = False,
    edgeonly: bool = False,
    minzero: bool = False,
    normzero_one: bool = False,  # normalise between 0 and 1
    maxone: bool = False,  # for masks with edgeonly
):
    blurred_array = apply_real_space_filter(
        mapobj.data,
        filter_type=filter_type,
        inplace=inplace,
        kernel_size=kernel_size,
        sigma=sigma,
        truncate=truncate,
        iter=iter,
        edgeonly=edgeonly,
        minzero=minzero,
        normzero_one=normzero_one,
        maxone=maxone,
    )
    if inplace:
        mapobj.data[:] = blurred_array
        mapobj.update_header_by_data()
    else:
        new_mapobj = mapobj.copy()
        new_mapobj.data = blurred_array
        new_mapobj.update_header_by_data()
        return new_mapobj


def mrcmap_kdtree(map_instance):
    """
    Returns the KDTree of coordinates from a mrc map grid.

    Arguments:
        *map_instance*
            MrcFile or MapObjHandle Map instance.
    """
    if map_instance.__class__.__name__ == "MrcFile":
        origin = map_instance.header.origin.item()
        apix = map_instance.voxel_size.item()
        nz, ny, nx = map_instance.data.shape
    else:
        origin = map_instance.origin
        apix = map_instance.apix
        nz, ny, nx = map_instance.data.shape

    # convert to real coordinates
    zg, yg, xg = np.mgrid[0:nz, 0:ny, 0:nx]
    # to get indices in real coordinates
    zg = zg * apix[2] + origin[2] + apix[2] / 2.0
    yg = yg * apix[1] + origin[1] + apix[1] / 2.0
    xg = xg * apix[0] + origin[0] + apix[0] / 2.0
    indi = list(zip(xg.ravel(), yg.ravel(), zg.ravel()))
    gridtree = generate_kdtree(indi, leaf_size=42)
    return gridtree, indi


def threshold_mapobj(
    mapobj: MapObjHandle,
    threshold: float,
    inplace: bool = False,
):
    masked_array = threshold_array(mapobj.data, threshold, inplace=inplace)
    if not inplace:
        new_mapobj = mapobj.copy(deep=False)
        new_mapobj.data = masked_array
        new_mapobj.update_header_by_data()
        return new_mapobj


def mask_mapobj(
    mapobj: MapObjHandle,
    maskobj: MapObjHandle,
    ignore_maskedge: bool = False,
    inplace: bool = False,
):
    masked_array = apply_mask(
        mapobj.data,
        maskobj.data,
        ignore_maskedge=ignore_maskedge,
        inplace=inplace,
    )
    if not inplace:
        new_mapobj = mapobj.copy()
        new_mapobj.data = masked_array
        new_mapobj.update_header_by_data()
        return new_mapobj


def normalise_mapobj(mapobj: MapObjHandle, inplace: bool = False):
    """
    Normalise map values between 0 and 1
    """
    use_cupy = False
    if check_gpu():
        import cupy as cp

        use_cupy = True

    if inplace:
        if use_cupy:
            data_to_normalize = cp.asarray(mapobj.data)
        else:
            data_to_normalize = np.array(mapobj.data)

    else:
        if use_cupy:
            data_to_normalize = cp.array(mapobj.data)
        else:
            data_to_normalize = np.array(mapobj.data, copy=True)

    data_to_normalize[data_to_normalize < 0] = 0
    min_val = data_to_normalize.min()
    max_val = data_to_normalize.max()

    if max_val != min_val:
        data_to_normalize = (data_to_normalize - min_val) / (max_val - min_val)
    else:
        data_to_normalize.fill(0)

    if use_cupy:
        data_to_normalize = data_to_normalize.get()
    if not inplace:
        new_mapobj = mapobj.copy(deep=False)

        new_mapobj.data = data_to_normalize
        new_mapobj.update_header_by_data()
        return new_mapobj
    else:
        mapobj.data = data_to_normalize
        mapobj.update_header_by_data()


def grid_to_real_mapobj(mapobj: MapObjHandle):
    #  TODO: Ask Jola/ Agnel about what the intial grid coordinates x,y,z represent
    #  I'm guessing mask points in the grid

    raise NotImplementedError("mapobj_grid_to_real is not implemented yet")


def borders_mapobj(mapobj: MapObjHandle, margin=5, cshape=None):
    # TODO: check if needed as this is a helper function for the crop but that seems to
    # do a good job of cropping the map around the centre
    """
    Returns the borders of a map object

    Arguments:
        *mapobj*
            MapObjHandle instance
    """
    extent = data_extent_mapobj(mapobj)  # find data extent in each direction
    # find a margin that prevents padding small maps beyond their original shape
    shape = (
        extent[1]
        - extent[0]
        + 2
        * int(
            min(
                margin / 2,
                (extent[0] + 1) / 2,
                (mapobj.x_size - extent[1] - 1) / 2,
            )
        ),
        extent[3]
        - extent[2]
        + 2
        * int(
            min(
                margin / 2,
                (extent[2] + 1) / 2,
                (mapobj.y_size - extent[3] - 1) / 2,
            )
        ),
        extent[5]
        - extent[4]
        + 2
        * int(
            min(
                margin / 2,
                (extent[4] + 1) / 2,
                (mapobj.z_size - extent[5] - 1) / 2,
            )
        ),
    )  # x,y,z
    # keep minimum of cshape or size of the map
    if cshape:
        shape = (
            min(mapobj.x_size, shape[0]),
            min(mapobj.y_size, shape[1]),
            min(mapobj.z_size, shape[2]),
        )  # x,y,z
    halfx = extent[0] + ((extent[1] - extent[0]) // 2)
    halfy = extent[2] + ((extent[3] - extent[2]) // 2)
    halfz = extent[4] + ((extent[5] - extent[4]) // 2)  # x,y,z
    return shape, (halfx, halfy, halfz)


def data_extent_mapobj(mapobj: MapObjHandle):
    """
    Returns the data extent of a mask object (min, max) in x, y, z

    Arguments:
        *mapobj*
            MapObjHandle instance

    Returns:
        tuple
            (minx, maxx, miny, maxy, minz, maxz)
    """
    x_mask = np.nonzero(mapobj.data.sum((0, 1)))[0]
    y_mask = np.nonzero(mapobj.data.sum((0, 2)))[0]
    z_mask = np.nonzero(mapobj.data.sum((1, 2)))[0]

    return (
        x_mask.min(),
        x_mask.max(),
        y_mask.min(),
        y_mask.max(),
        z_mask.min(),
        z_mask.max(),
    )
