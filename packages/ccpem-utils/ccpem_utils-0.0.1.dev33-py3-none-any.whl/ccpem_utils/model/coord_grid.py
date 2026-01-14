#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

from ccpem_utils.map.mrc_map_utils import mrcmap_kdtree
import numpy as np
from typing import Union, Optional
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from ccpem_utils.model.gemmi_model_utils import GemmiModelUtils


def calc_atom_coverage_by_res(
    res_map: float = 3.0,
    sim_sigma_coeff: float = 0.225,
    sigma_thr: float = 2.5,
    min_apix: bool = True,
    apix: Optional[Union[float, tuple]] = None,
) -> float:
    """
    Calculates distance based on a single gaussian representation scaled by resolution.

    Arguments:
        :res_map:
            Map resolution
        :sim_sigma_coeff:
        From https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/midas/molmap.html
            Together with the resolution, the sigma factor f determines the width
            of the Gaussian distribution used to describe each atom:

            σ = f(resolution)
            By default, f = 1/(π * 2½) ≈ 0.225 which makes the Fourier transform (FT)
            of the distribution fall to 1/e of its maximum value at
                wavenumber 1/resolution.
            Other plausible choices:

            1/(π * (2/log2)½) ≈ 0.187 makes the FT fall to half maximum
                at wavenumber 1/resolution
            1/(2 * 2½) ≈ 0.356 makes the Gaussian width at 1/e maximum height
                equal the resolution
            1/(2 * (2log2)½) ≈ 0.425 makes the Gaussian width at half maximum height
                equal the resolution
        :sigma_thr:
            Threshold for gaussian sigma
    """
    gauss_distance = sigma_thr * sim_sigma_coeff * res_map
    if min_apix and apix:
        if isinstance(apix, tuple):
            return max(max(apix), gauss_distance)
        else:
            return max(apix, gauss_distance)
    return gauss_distance


def mapGridPositions(
    map_instance: MapObjHandle,
    atom_coord: Union[list, tuple, np.ndarray],
    gauss: bool = True,
    res_map: float = 3.0,
    sim_sigma_coeff: float = 0.225,
    sigma_thr: float = 2.5,
    dist_search: float = 0.0,
) -> list:
    """
    Returns the indices of the nearest pixels to an atom as a list.

    Arguments:
        :map_instance:
            MrcFile or MapObjHandle Map instance.
        :atom_coord:
            3D Coordinate.
        :res_map:
            Map resolution
        :gauss:
            Whether to use resolution dependent gaussian blur to determine search space
        :sim_sigma_coeff:
        From https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/midas/molmap.html
            Together with the resolution, the sigma factor f determines the width
            of the Gaussian distribution used to describe each atom:

            σ = f(resolution)
            By default, f = 1/(π * 2½) ≈ 0.225 which makes the Fourier transform (FT)
            of the distribution fall to 1/e of its maximum value at
                wavenumber 1/resolution.
            Other plausible choices:

            1/(π * (2/log2)½) ≈ 0.187 makes the FT fall to half maximum
                at wavenumber 1/resolution
            1/(2 * 2½) ≈ 0.356 makes the Gaussian width at 1/e maximum height
                equal the resolution
            1/(2 * (2log2)½) ≈ 0.425 makes the Gaussian width at half maximum height
                equal the resolution
        :sigma_thr:
            Threshold for gaussian sigma
        :dist_search:
            Additional distance to search when gauss is False
            Nearest voxel is returned when dist_search=0.0
    """
    origin = map_instance.origin
    apix = map_instance.apix
    atom_x, atom_y, atom_z = atom_coord

    x_pos = int(round((atom_x - origin[0]) / apix[0], 0))
    y_pos = int(round((atom_y - origin[1]) / apix[1], 0))
    z_pos = int(round((atom_z - origin[2]) / apix[2], 0))
    if (
        (map_instance.x_size >= x_pos >= 0)
        and (map_instance.y_size >= y_pos >= 0)
        and (map_instance.z_size >= z_pos >= 0)
    ):
        gridtree = mrcmap_kdtree(map_instance)[0]
        if gauss:
            # search all points withing 2.0sigma
            list_points = gridtree.query_radius(
                [
                    [
                        atom_x,
                        atom_y,
                        atom_z,
                    ]
                ],
                calc_atom_coverage_by_res(
                    res_map=res_map,
                    sigma_thr=sigma_thr,
                    sim_sigma_coeff=sim_sigma_coeff,
                    apix=apix,
                ),
            )[0]
        elif dist_search != 0:
            # search withing the given radius
            list_points = gridtree.query_radius(
                [
                    [
                        atom_x,
                        atom_y,
                        atom_z,
                    ]
                ],
                max(
                    [
                        dist_search,
                        min(apix),
                    ]
                ),
            )[0]
        else:
            list_points = gridtree.query(
                [
                    [
                        atom_x,
                        atom_y,
                        atom_z,
                    ]
                ],
                k=1,
            )[1]
        return list_points
    else:
        print("Warning, atom out of map box")
        return []


def set_map_grid(
    modelfile: str,
    apix: Union[tuple, list, np.ndarray],
    edge: Union[int, float] = 20.0,
):
    """
    Find grid parameters to fit the model

    Arguments:

    :modelfile: input model file
    :apix: voxel size of the output grid
    :edge: padding to the model extremities in Angstroms

    Return:
    Map grid origin and dimensions (number of voxels)
    """
    gemmiutils = GemmiModelUtils(modelfile)
    list_coords = gemmiutils.get_coordinates(return_list=True)[1]
    coords_array = np.array(list_coords)
    del list_coords
    list_x, list_y, list_z = np.transpose(coords_array)
    min_x = min(list_x) - edge
    max_x = max(list_x) + edge
    min_y = min(list_y) - edge
    max_y = max(list_y) + edge
    min_z = min(list_z) - edge
    max_z = max(list_z) + edge
    dim_x, dim_y, dim_z = max_x - min_x, max_y - min_y, max_z - min_z
    # adjust dimensions to number of voxels
    rem_x, rem_y, rem_z = dim_x % apix[0], dim_y % apix[1], dim_z % apix[2]
    dim_x, dim_y, dim_z = (
        dim_x + apix[0] - rem_x,
        dim_y + apix[1] - rem_y,
        dim_z + apix[2] - rem_z,
    )
    if int(dim_z / apix[2]) % 2 != 0:
        dim_z = dim_z + apix[2]  # z not even?
    if int(dim_x / apix[0]) % 2 != 0:
        dim_x = dim_x + apix[0]  # x not even?
    origin = (
        min_x - apix[0] + rem_x,
        min_y - apix[1] + rem_y,
        min_z - apix[2] + rem_z,
    )
    return origin, (
        int(dim_x / apix[0]),
        int(dim_y / apix[1]),
        int(dim_z / apix[2]),
    )


def set_cubic_map_grid(
    modelfile: str,
    apix: Union[tuple, list, np.ndarray],
    edge: Union[int, float] = 20.0,
):
    """
    Find CUBIC grid parameters to fit the model

    Arguments:

    :modelfile: input model file
    :apix: voxel size of the output grid
    :edge: padding to the model extremities in Angstroms

    Return:
    Map grid origin and dimensions (number of voxels)
    """
    gemmiutils = GemmiModelUtils(modelfile)
    list_coords = gemmiutils.get_coordinates(return_list=True)[1]
    coords_array = np.array(list_coords)
    del list_coords
    list_x, list_y, list_z = np.transpose(coords_array)
    min_x = min(list_x) - edge
    max_x = max(list_x) + edge
    min_y = min(list_y) - edge
    max_y = max(list_y) + edge
    min_z = min(list_z) - edge
    max_z = max(list_z) + edge
    dim_x, dim_y, dim_z = max_x - min_x, max_y - min_y, max_z - min_z
    dim = [dim_x, dim_y, dim_z]
    max_dim = max(dim)
    # set cubic dimensions
    if max_dim - dim_x != 0.0:
        min_x = min_x - (max_dim - dim_x) / 2.0
        max_x = max_x + (max_dim - dim_x) / 2.0
    if max_dim - dim_y != 0.0:
        min_y = min_y - (max_dim - dim_y) / 2.0
        max_y = max_y + (max_dim - dim_y) / 2.0
    if max_dim - dim_z != 0.0:
        min_z = min_z - (max_dim - dim_z) / 2.0
        max_z = max_z + (max_dim - dim_z) / 2.0
    dim_x, dim_y, dim_z = max_x - min_x, max_y - min_y, max_z - min_z
    # adjust dimensions to number of voxels
    rem_x, rem_y, rem_z = dim_x % apix[0], dim_y % apix[1], dim_z % apix[2]
    dim_x, dim_y, dim_z = (
        dim_x + apix[0] - rem_x,
        dim_y + apix[1] - rem_y,
        dim_z + apix[2] - rem_z,
    )
    origin = (
        min_x - apix[0] + rem_x,
        min_y - apix[1] + rem_y,
        min_z - apix[2] + rem_z,
    )
    return origin, (
        int(dim_x / apix[0]),
        int(dim_y / apix[1]),
        int(dim_z / apix[2]),
    )
