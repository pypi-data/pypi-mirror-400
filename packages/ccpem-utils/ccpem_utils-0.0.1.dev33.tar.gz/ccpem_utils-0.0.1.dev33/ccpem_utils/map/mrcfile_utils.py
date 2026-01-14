from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from ccpem_utils.map.mrc_map_utils import (
    crop_map_grid,
    pad_map_grid,
    downsample_apix,
    softedge_map,
    realspace_filter_mapobj,
    mask_mapobj,
    bin_downsample,
)
from ccpem_utils.map.array_utils import (
    calculate_contour_by_sigma,
    get_contour_mask,
    add_maskarray_softedge,
    map_binary_opening,
)
from ccpem_utils.other.utils import compare_tuple
from ccpem_utils.model.coord_grid import calc_atom_coverage_by_res
import mrcfile
from typing import Sequence, Union, Optional, List, Tuple
import os
import warnings
import shutil


def get_mapobjhandle(map_input: str, datacopy: bool = False) -> MapObjHandle:
    # read
    with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
        wrapped_mapobj = MapObjHandle(mrc, datacopy=datacopy)
        return wrapped_mapobj


def write_newmapobj(mapobj: MapObjHandle, map_output: str, close_mapobj: bool = True):
    with mrcfile.new(map_output, overwrite=True) as mrc:
        mapobj.update_newmap_data_header(mrc)
    if close_mapobj:
        mapobj.close()


def check_origin_zero(map_input: str) -> bool:
    with mrcfile.open(map_input, header_only=True, permissive=True) as mrc:
        if (
            mrc.header.origin.x != 0.0
            or mrc.header.origin.y != 0.0
            or mrc.header.origin.z != 0.0
        ):
            return False
    return True


def get_origin_nstart(map_input: str) -> List[Tuple]:
    with mrcfile.open(map_input, header_only=True, permissive=True) as mrc:
        return [
            mrc.header.origin.item(),
            (
                mrc.header.nxstart.item(),
                mrc.header.nystart.item(),
                mrc.header.nzstart.item(),
            ),
        ]


def check_standard_axis_order(map_input: str) -> bool:
    mapcrs = get_axis_order(map_input)
    return compare_tuple(mapcrs, (1, 2, 3))


def get_axis_order(map_input: str) -> Tuple:
    with mrcfile.open(map_input, header_only=True, permissive=True) as mrc:
        return (mrc.header.mapc, mrc.header.mapr, mrc.header.maps)


def get_voxel_size(map_input: str) -> Tuple:
    with mrcfile.open(map_input, header_only=True, permissive=True) as mrc:
        return mrc.voxel_size.item()


def get_mrcfile_header(map_input: str) -> mrcfile.mrcobject.MrcObject.header:
    with mrcfile.open(map_input, header_only=True, permissive=True) as mrc:
        return mrc.header


def compare_map_dimensions(map1_input: str, map2_input: str) -> bool:
    """Compare map sizes and dimensions (Angstroms)

    :param map1_input: first mrc map file
    :type map1_input: str
    :param map2_input: second mrc map file
    :type map2_input: str
    :return: True if they have same size and dimensions else False
    :rtype: bool
    """
    with mrcfile.open(map1_input, header_only=True, permissive=True) as mrc:
        cella1 = mrc.header.cella.item()
        size1 = (mrc.header.nx, mrc.header.ny, mrc.header.nz)
    with mrcfile.open(map2_input, header_only=True, permissive=True) as mrc:
        cella2 = mrc.header.cella.item()
        size2 = (mrc.header.nx, mrc.header.ny, mrc.header.nz)
    return compare_tuple(cella1, cella2) and compare_tuple(size1, size2)


def edit_input_map_origin_nstart(
    map_input: str,
    new_origin: Optional[Tuple] = None,
    new_nstart: Optional[Tuple] = None,
):
    with mrcfile.mmap(map_input, mode="r+", permissive=True) as mrc:
        if new_origin:
            mrc.header.origin.x = new_origin[0]
            mrc.header.origin.y = new_origin[1]
            mrc.header.origin.z = new_origin[2]
        if new_nstart:
            mrc.header.nxstart = new_nstart[0]
            mrc.header.nystart = new_nstart[1]
            mrc.header.nzstart = new_nstart[2]


def edit_map_origin_nstart(
    map_input: str,
    new_origin: Optional[Tuple] = None,
    new_nstart: Optional[Tuple] = None,
    map_output: str = "",
    inplace=False,
):
    """Edit map origin and nstart records

    :param map_input: input mrc map
    :type map_input: str
    :param new_origin: new origin, defaults to None
    :type new_origin: Optional[Tuple], optional
    :param new_nstart: nstart to set, defaults to None
    :type new_nstart: Optional[Tuple], optional
    :param map_output: output map filename, defaults to ""
    :type map_output: str, optional
    :param inplace: set to True to edit input map, defaults to False
    :type inplace: bool, optional
    """
    if inplace:
        # edit input map
        edit_input_map_origin_nstart(
            map_input=map_input, new_origin=new_origin, new_nstart=new_nstart
        )
    else:
        if not map_output:
            map_output = (
                os.path.splitext(os.path.basename(map_input))[0] + "_shifted.mrc"
            )
        shutil.copyfile(map_input, map_output)
        # edit copied map
        edit_input_map_origin_nstart(
            map_input=map_output, new_origin=new_origin, new_nstart=new_nstart
        )


def crop_mrc_map(
    map_input: str,
    map_output: Optional[str] = None,
    new_dim: Optional[Sequence[int]] = None,
    crop_dim: Optional[Sequence[int]] = None,
    contour: Optional[float] = None,
    ext: Sequence[int] = (10, 10, 10),
    cubic: bool = False,
    inplace: bool = False,
    mask_input: Optional[str] = None,
    mask_thr: Optional[float] = None,
):
    mapobj = get_mapobjhandle(map_input)
    if mask_input:
        mask_mapobj = get_mapobjhandle(mask_input)
    else:
        mask_mapobj = None
    cropped_mapobj = crop_map_grid(
        mapobj,
        new_dim=new_dim,
        crop_dim=crop_dim,
        contour=contour,
        ext=ext,
        cubic=cubic,
        inplace=inplace,
        input_maskobj=mask_mapobj,
        mask_thr=mask_thr,
    )
    # set output as input map if inplace
    if inplace:
        cropped_mapobj = mapobj
    if not map_output:
        map_output = os.path.splitext(map_input)[0] + "_cropped.mrc"
    write_newmapobj(cropped_mapobj, map_output)


def pad_mrc_map(
    map_input: str,
    ext_dim: Sequence[int],
    fill_padding: Optional[float] = None,
    map_output: Optional[str] = None,
    inplace: bool = False,
):
    mapobj = get_mapobjhandle(map_input)
    padded_mapobj = pad_map_grid(
        mapobj,
        ext_dim=ext_dim,
        fill_padding=fill_padding,
        inplace=inplace,
    )
    if not map_output:
        map_output = os.path.splitext(map_input)[0] + "_padded.mrc"
    if inplace:
        padded_mapobj = mapobj
    write_newmapobj(padded_mapobj, map_output)


def fastbin_mrc_map(
    map_input: str,
    new_dim: Union[int, Sequence[int], None] = None,
    new_spacing: Union[float, Sequence[float], None] = None,
    map_output: Optional[str] = None,
    inplace: bool = False,
    method: str = "block_mean",
):
    """Downsample a map without interpolation

    :param map_input: input map file
    :type map_input: str
    :param new_dim: New dimensions of binned map, defaults to None
    :type new_dim: Union[int, Sequence[int], None], optional. In x,y,z order
    :param new_spacing: Spacing of binned map (used if new_dim not input),
        defaults to None
    :type new_spacing: Union[float, Sequence[float], None], optional
    :param map_output: output map file, defaults to None
    :type map_output: Optional[str], optional
    :param inplace: modify input map itself, defaults to False
    :type inplace: bool, optional
    :param mode: mode of binning [stride or block_mean]
    :raises ValueError: if both new_dim and new_spacing not provided
    :raises ValueError: if both new_dim and new_spacing are not valid. new_dim should
        be tuple of ints and new_spacing should be tuple of floats.
    """
    if not new_spacing and not new_dim:
        raise ValueError("Please provide either new_dim or new_spacing")
    mapobj = get_mapobjhandle(map_input)
    if isinstance(new_dim, int):
        max_dim = new_dim
        new_spacing = (
            max(
                mapobj.x_size * mapobj.apix[0],
                mapobj.y_size * mapobj.apix[1],
                mapobj.z_size * mapobj.apix[2],
            )
            / max_dim
        )
        new_dim = (new_dim, new_dim, new_dim)
    elif isinstance(new_dim, tuple) and len(new_dim) == 3:
        new_spacing = (
            (mapobj.x_size / new_dim[0]) * mapobj.apix[0],
            (mapobj.y_size / new_dim[1]) * mapobj.apix[1],
            (mapobj.z_size / new_dim[2]) * mapobj.apix[2],
        )
    else:
        if isinstance(new_spacing, float):
            new_spacing = (new_spacing, new_spacing, new_spacing)
        if isinstance(new_spacing, tuple):
            apix_ratio = (
                mapobj.apix[0] / new_spacing[0],
                mapobj.apix[1] / new_spacing[1],
                mapobj.apix[2] / new_spacing[2],
            )
            new_dim = (
                int(round(mapobj.x_size * apix_ratio[0])),
                int(round(mapobj.y_size * apix_ratio[1])),
                int(round(mapobj.z_size * apix_ratio[2])),
            )
        else:
            raise ValueError("Input a valid spacing: float or (float,float,float)")
    if not map_output:
        map_output = os.path.splitext(map_input)[0] + "_binned.mrc"

    if not new_dim or not new_spacing:
        raise ValueError(
            "Input a valid new_dim : int or (int,int,int), or "
            "new_spacing: float or (float,float,float)"
        )
    elif isinstance(new_spacing, tuple):
        binned_mapobj = bin_downsample(
            mapobj,
            new_gridshape=(new_dim[2], new_dim[1], new_dim[0]),  # z,y,x
            new_spacing=(new_spacing[0], new_spacing[1], new_spacing[2]),
            new_origin=mapobj.origin,
            method=method,
            inplace=inplace,
        )

    if not inplace:
        write_newmapobj(binned_mapobj, map_output)
    else:
        write_newmapobj(mapobj, map_output)


def bin_mrc_map(
    map_input: str,
    new_dim: Union[int, Sequence[int], None] = None,
    new_spacing: Union[float, Sequence[float], None] = None,
    map_output: Optional[str] = None,
    inplace: bool = False,
    interp_order: int = 1,
    prefilter_input: bool = False,
    mode: str = "fast",
    method: str = "interpolate",
    optimise_largemaps: bool = True,
):
    """Downsample a map

    :param map_input: input map file
    :type map_input: str
    :param new_dim: New dimensions of binned map, defaults to None. In x,y,z order
    :type new_dim: Union[int, Sequence[int], None], optional
    :param new_spacing: Spacing of binned map (used if new_dim not input),
        defaults to None
    :type new_spacing: Union[float, Sequence[float], None], optional
    :param map_output: output map file, defaults to None
    :type map_output: Optional[str], optional
    :param inplace: modify input map itself, defaults to False
    :type inplace: bool, optional
    :param interp_order: defaults to tri-linear (order 1), defaults to 1
    :type interp_order: int, optional
    :param prefilter_input: Determines if the input array is prefiltered
        with spline_filter before interpolation. The default is True,
        which will create a temporary float64 array of filtered values
        if order > 1. If setting this to False, the output will be slightly blurred
        if order > 1, unless the input is prefiltered, defaults to False
    :type prefilter_input: bool, optional
    :param mode: use 'slow' for cubic interpolation (more accurate),
        defaults to 'fast' - linear interpolation
    :type mode: str, optional
    :param method: 'interpolate' is more accurate but slower than 'stride',
        defaults to 'interpolate'
    :type method: str, optional
    :param optimise_largemaps: use False for using 'interpolate' method for large maps,
        defaults to True which switches method to 'stride' for maps of dimensions > 500
        along all axes.
    :type mode: bool, optional
    :raises ValueError: if both new_dim and new_spacing not provided
    :raises ValueError: if both new_dim and new_spacing are not valid. new_dim should
        be tuple of ints and new_spacing should be tuple of floats.
    """
    if not new_spacing and not new_dim:
        raise ValueError("Please provide either new_dim or new_spacing")
    mapobj = get_mapobjhandle(map_input, datacopy=False)
    if isinstance(new_dim, int):
        max_dim = new_dim
        new_spacing = (
            max(
                mapobj.x_size * mapobj.apix[0],
                mapobj.y_size * mapobj.apix[1],
                mapobj.z_size * mapobj.apix[2],
            )
            / max_dim
        )
        new_dim = (new_dim, new_dim, new_dim)
    elif new_dim:
        new_spacing = (
            (mapobj.x_size / new_dim[0]) * mapobj.apix[0],
            (mapobj.y_size / new_dim[1]) * mapobj.apix[1],
            (mapobj.z_size / new_dim[2]) * mapobj.apix[2],
        )
    else:
        if isinstance(new_spacing, float):
            new_spacing = (new_spacing, new_spacing, new_spacing)
        if isinstance(new_spacing, tuple):
            apix_ratio = (
                mapobj.apix[0] / new_spacing[0],
                mapobj.apix[1] / new_spacing[1],
                mapobj.apix[2] / new_spacing[2],
            )
            new_dim = (
                int(round(mapobj.x_size * apix_ratio[0])),
                int(round(mapobj.y_size * apix_ratio[1])),
                int(round(mapobj.z_size * apix_ratio[2])),
            )
        else:
            raise ValueError("Input a valid spacing: float or (float,float,float)")
    if not map_output:
        map_output = os.path.splitext(map_input)[0] + "_binned.mrc"
    if not new_spacing:
        raise ValueError("Please provide valid new_dim or new_spacing")
    if optimise_largemaps and min(mapobj.data.shape) >= 500:
        method = "stride"
        warnings.warn(
            "Input map has dimensions > 500, using stride method instead. "
            "Set optimise_largemaps to False to disable this."
        )
    if method == "interpolate":
        if mode == "slow":
            interp_order = 3
            prefilter_input = True
        downsampled_mapobj = downsample_apix(
            mapobj,
            new_spacing=new_spacing,
            grid_shape=(new_dim[2], new_dim[1], new_dim[0]),  # z,y,x
            inplace=inplace,
            interp_order=interp_order,
            prefilter_input=prefilter_input,
        )
    elif isinstance(new_spacing, tuple):
        downsampled_mapobj = bin_downsample(
            mapobj,
            new_gridshape=(new_dim[2], new_dim[1], new_dim[0]),  # z,y,x
            new_spacing=(new_spacing[0], new_spacing[1], new_spacing[2]),
            new_origin=mapobj.origin,
            method=method,
            inplace=inplace,
        )
    if not inplace:
        write_newmapobj(downsampled_mapobj, map_output)
    else:
        write_newmapobj(mapobj, map_output)


def calc_mrc_sigma_contour(
    map_input: str,
    sigma_factor: float = 1.5,
):
    with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
        return calculate_contour_by_sigma(arr=mrc.data, sigma_factor=sigma_factor)


def save_contour_mask(
    map_input: str,
    filter_type: str = "cosine",
    contour: float = -100,
    map_output: str = "",
    add_softedge: bool = True,
    remove_dust: bool = False,
    remove_dust_iterations: int = 1,
    edge: int = 6,
    sigma_factor: float = 1.5,
    include_threshold_value: bool = False,
    inplace: bool = False,
):
    mapobj = get_mapobjhandle(map_input)
    if contour == -100:
        contour = calculate_contour_by_sigma(arr=mapobj.data, sigma_factor=sigma_factor)
    if remove_dust:
        contour_mask = map_binary_opening(
            arr=mapobj.data, contour=contour, it=remove_dust_iterations
        )
    else:
        contour_mask = get_contour_mask(
            array=mapobj.data,
            threshold_level=contour,
            include_threshold_value=include_threshold_value,
        )
    if add_softedge:
        softedged_mask = add_maskarray_softedge(
            contour_mask, edge=edge, filter_type=filter_type
        )
    else:
        softedged_mask = contour_mask
    if not map_output:
        map_output = (
            os.path.splitext(os.path.basename(map_input))[0] + "_contour_mask.mrc"
        )
    if inplace:
        mapobj.data = softedged_mask
        write_newmapobj(mapobj, map_output)
    else:
        newmap = mapobj.copy()
        newmap.data = softedged_mask
        write_newmapobj(newmap, map_output)


def calc_atom_gaussian_coverage(
    map_input: str,
    res_map: float = 3.0,
    sim_sigma_coeff: float = 0.225,
    sigma_thr: float = 2.5,
):
    with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
        apix = mrc.voxel_size.item()
        return calc_atom_coverage_by_res(
            res_map=res_map,
            sim_sigma_coeff=sim_sigma_coeff,
            sigma_thr=sigma_thr,
            apix=apix,
        )


def add_softedge(
    map_input: str,
    edgetype: str = "cosine",
    edge: int = 6,
    map_output: Optional[str] = None,
    inplace: bool = False,
):
    mapobj = get_mapobjhandle(map_input)
    softedged_mapobj = softedge_map(
        mapobj=mapobj, filter_type=edgetype, edge=edge, inplace=inplace
    )
    if not map_output:
        map_output = (
            os.path.basename(os.path.splitext(map_input)[0])
            + "_"
            + edgetype
            + "_softmask.mrc"
        )
    if inplace:
        softedged_mapobj = mapobj
    write_newmapobj(softedged_mapobj, map_output)


def realspace_filter_map(
    map_input: str,
    filter_type: str = "gaussian",
    map_output: Optional[str] = None,
    kernel_size: int = 5,
    sigma: float = 1,
    truncate: int = 3,
    iter: int = 1,
    edgeonly: bool = False,
    minzero: bool = False,
    normzero_one: bool = False,  # normalise between 0 and 1
    maxone: bool = False,  # for masks with edgeonly
    inplace: bool = False,
):
    mapobj = get_mapobjhandle(map_input)
    filtered_mapobj = realspace_filter_mapobj(
        mapobj,
        filter_type=filter_type,
        kernel_size=kernel_size,
        sigma=sigma,
        inplace=inplace,
        truncate=truncate,
        iter=iter,
        edgeonly=edgeonly,
        minzero=minzero,
        normzero_one=normzero_one,
        maxone=maxone,
    )
    if not map_output:
        map_output = (
            os.path.basename(os.path.splitext(map_input)[0])
            + "_"
            + filter_type
            + "_filtered.mrc"
        )
    if inplace:
        filtered_mapobj = mapobj
    write_newmapobj(filtered_mapobj, map_output)


def mask_map(
    map_input: str,
    mask_input: str,
    ignore_maskedge: bool = False,
    map_output: Optional[str] = None,
    inplace: bool = False,
):
    mapobj = get_mapobjhandle(map_input)
    maskobj = get_mapobjhandle(mask_input)
    masked_mapobj = mask_mapobj(
        mapobj=mapobj,
        maskobj=maskobj,
        ignore_maskedge=ignore_maskedge,
        inplace=inplace,
    )
    if not map_output:
        map_output = os.path.basename(os.path.splitext(map_input)[0]) + "_masked.mrc"
    if inplace:
        masked_mapobj = mapobj
    write_newmapobj(masked_mapobj, map_output)
