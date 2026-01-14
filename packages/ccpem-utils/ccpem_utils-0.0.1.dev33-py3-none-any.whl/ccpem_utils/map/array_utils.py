import numpy as np
import math
from scipy.ndimage import generic_filter, measurements, gaussian_filter
from typing import Sequence, Optional, Union
from scipy.ndimage import binary_opening, binary_closing
import gc
from ccpem_utils.other.calc import calc_std
from scipy.signal.windows import cosine
from scipy.signal import fftconvolve
import warnings

from scipy.ndimage import map_coordinates as scipy_map_coordinates
from scipy.ndimage import rotate as scipy_rotate
from ccpem_utils.other.utils import check_gpu


try:
    import pyfftw

    pyfftw_flag = True
except ImportError:
    pyfftw_flag = False


def plot_density_histogram(arr, plotfile="density_histogram.png"):
    freq, bins = np.histogram(arr, 100)
    bin_centre = []
    for i in range(len(bins) - 1):
        bin_centre.append((bins[i] + bins[i + 1]) / 2.0)
    assert len(freq) == len(bin_centre)

    try:
        import matplotlib.pyplot as plt
    except (RuntimeError, ImportError) as e:
        if hasattr(e, "message"):
            print("Matplotlib import error {}".format(e.message))
        else:
            print(e)
        plt = None
        return
    import warnings

    warnings.filterwarnings("ignore", category=RuntimeWarning)
    logfreq = []
    for f in freq:
        try:
            logfreq.append(np.log(f))
        except RuntimeWarning:
            logfreq.append(0.0)
    logfreq = np.array(logfreq)
    logfreq[freq == 0] = 0.0
    plt.rcParams.update({"font.size": 15})
    plt.xlabel("Density", fontsize=12)
    plt.ylabel("log(Frequency)", fontsize=12)
    plt.plot(bin_centre, logfreq, linewidth=2.0, color="g")
    #     locs,labs = plt.xticks()
    #     step = (max(locs)-min(locs))/10.
    #     locs = np.arange(min(locs),max(locs)+step,step)
    #     labels = np.round(map_apix/locs[1:],1)
    #     plt.xticks(locs[1:], labels,rotation='vertical')
    plt.savefig(plotfile)
    plt.close()


def get_contour_mask(
    array: np.ndarray,
    threshold_level: float,
    include_threshold_value: bool = False,
) -> np.ndarray:
    if include_threshold_value:
        binary_mask = array >= float(threshold_level)
    else:
        binary_mask = array > float(threshold_level)
    return binary_mask


def threshold_array(
    array: np.ndarray,
    threshold_level: float,
    dtype="float32",
    inplace=False,
) -> np.ndarray:
    binary_mask = get_contour_mask(array, threshold_level)
    return apply_mask(array, binary_mask, dtype=dtype, inplace=inplace)


def calculate_contour_by_sigma(arr: np.ndarray, sigma_factor=2.0):
    background, ave = find_background_peak(arr=arr)
    peak_right_sigma = calc_std(arr[arr >= background], use_mean=background)
    return sigma_factor * peak_right_sigma


def apply_mask(
    arr: np.ndarray,
    mask: np.ndarray,
    ignore_maskedge: bool = False,
    dtype: str = "float32",
    inplace: bool = False,
):
    if not compare_tuple(arr.shape, mask.shape):
        return arr
    if inplace:
        if ignore_maskedge:  # create binary mask
            arr[:] = arr * (mask == 1.0)
        else:
            arr[:] = arr * mask
        return arr
    else:
        if ignore_maskedge:
            return np.array(arr * (mask == 1.0), dtype=dtype)
        else:
            return np.array(arr * mask, dtype=dtype)


def shift_values(arr, offset, inplace=False):
    """
    Shift density given an offset
    """
    if inplace:
        arr[:] = arr + float(offset)
        return arr
    else:
        return arr + float(offset)


def rotate_array(
    arr: np.ndarray,
    angle: float,
    axes: tuple = (1, 0),
    reshape: bool = False,
    interpolate: bool = False,
    interp_order: int = 0,
) -> np.ndarray:
    """Rotate an array and interpolate to new array

    :param arr: input array to be rotated
    :type arr: np.ndarray
    :param angle: rotation angle in degrees
    :type angle: float
    :param axes: The two axes that define the plane of rotation.
        Default is the first two axes.
    :type axes: tuple, optional
    :param reshape: whether to reshape to accomodate rotated array, defaults to False
    :type reshape: bool, optional
    :param interpolate: whether to interpolate after rotation?,
        defaults to False - uses nearest value
    :type interpolate: bool, optional
    :param interp_order: order for interpolation (linear (1),
        cubic (3), ..), defaults to 3
    :type interp_order: int, optional
    :return: rotated array
    :rtype: np.ndarray
    """
    use_cupy = False
    cupy_input = False
    rotate = scipy_rotate
    if check_gpu():
        use_cupy = True
        import cupy as cp
        from cupyx.scipy.ndimage import rotate as cupy_rotate

        if not isinstance(arr, cp.ndarray):
            arr = cp.array(arr)
        else:
            cupy_input = True

        rotate = cupy_rotate

    if interpolate:
        interp_order = 3

    if use_cupy:
        cval = cp.amin(arr) if cp.amin(arr) > 0 else 0.0
    else:
        cval = np.amin(arr)

    rotated_array = rotate(
        arr,
        angle=angle,
        axes=axes,
        reshape=reshape,
        order=interp_order,
        cval=cval,
    )

    if use_cupy and not cupy_input:
        return rotated_array.get()

    return rotated_array


def crop_array(
    arr: np.ndarray,
    new_dim: Optional[Sequence[int]] = None,
    contour: Optional[float] = None,
    ext: Sequence[int] = (10, 10, 10),
    cubic: bool = False,
    inplace: bool = False,
    mask_array: Optional[np.ndarray] = None,
    nd: int = 3,
):
    """
    Crop an array based on
        1) an array value threshold or mask
            (plus optional
                padding (ext) applied as number of pixels/voxels)
        2) new array dimensions

    Arguments
    ---------
        :arr: np.ndarray
            input array (indexed as arr[z][y][x])
        :new_dim:
            new dimensions to crop to
        :contour: float, optional
            map threshold (slices with all values lower than this are cropped)
        :ext: int, optional
            number of pixels/voxels as padding
        :mask_array: np.ndarray
            mask to be applied before cropping (slices with all zeros are cropped)
        :cubic: bool
            whether to crop to a cubic box?

    Returns
    -------
        Cropped array
    """
    # check input array dimension
    if len(arr.shape) != 3:
        raise ValueError("Input array must be 3D")
    xs = 0
    ys = 0
    zs = 0
    # crop based on given dimensions
    if new_dim is not None:
        crop_x = int(arr.shape[2] - new_dim[0])
        xs = max(0, int(np.ceil(float(crop_x) / 2)))
        xe = min(
            arr.shape[2],
            arr.shape[2] - int(np.floor(float(crop_x) / 2)),
        )

        crop_y = int(arr.shape[1] - new_dim[1])
        ys = max(0, int(np.ceil(float(crop_y) / 2)))
        ye = min(
            arr.shape[1],
            arr.shape[1] - int(np.floor(float(crop_y) / 2)),
        )

        crop_z = int(arr.shape[0] - new_dim[2])
        zs = max(0, int(np.ceil(float(crop_z) / 2)))
        ze = min(
            arr.shape[0],
            arr.shape[0] - int(np.floor(float(crop_z) / 2)),
        )
    # crop based on the give n contour and factor_sigma
    elif contour or mask_array is not None:
        if contour:
            minval = float(contour)
        elif mask_array is not None:
            assert mask_array.shape == arr.shape
            arr = arr * mask_array  # apply mask
            minval = np.amin(arr[arr > 0])
        map_data = arr
        list_indices = []
        for i in range(nd):
            ct1 = 0
            try:
                while np.nanmax(map_data[ct1]) < minval:
                    ct1 += 1
            except IndexError:
                pass

            ct2 = 0
            try:
                while np.nanmax(map_data[-1 - ct2]) < minval:
                    ct2 += 1
            except IndexError:
                pass
            # transpose
            map_data = np.transpose(map_data, (2, 0, 1))
            # TODO, substracting 1 is not necessary?
            list_indices.append([ct1 - 1, ct2 - 1])

        # indices for cropping
        # z axis
        zs, ze = (
            max(0, list_indices[0][0] - ext[2]),
            min(arr.shape[0] - list_indices[0][1] + ext[2], arr.shape[0]),
        )
        # y axis
        ys, ye = (
            max(0, list_indices[2][0] - ext[1]),
            min(arr.shape[1] - list_indices[2][1] + ext[1], arr.shape[1]),
        )
        # x axis
        xs, xe = (
            max(0, list_indices[1][0] - ext[0]),
            min(arr.shape[2] - list_indices[1][1] + ext[0], arr.shape[2]),
        )

        # make cubic dimensions
        if cubic:
            s_min = min([zs, ys, xs])
            e_max = max([ze, ye, xe])
            zs = s_min
            xs = s_min
            ys = s_min

            ze = e_max
            ye = e_max
            xe = e_max

        # cropped data, save a copy to get a contiguous memory block
        # delete the reference
        del map_data
    if inplace:
        return arr[zs:ze, ys:ye, xs:xe], (xs, ys, zs)
    else:
        return np.copy(arr[zs:ze, ys:ye, xs:xe]), (xs, ys, zs)


def pad_array(arr, nx, ny, nz, fill_padding=None):
    """

    Pad an array with specified increments along each dimension.
    Arguments:
        *nx,ny,nz*
           Number of slices to add to either sides of each dimension.
    Return:
        array
    """

    gridshape = (
        arr.shape[0] + 2 * nz,
        arr.shape[1] + 2 * ny,
        arr.shape[2] + 2 * nx,
    )
    input_dtype = str(arr.dtype)
    new_array = np.zeros(gridshape, dtype=input_dtype)
    # fill padding
    if not fill_padding:
        fill_padding = arr.min()
    new_array.fill(fill_padding)
    # find indices of old array
    oldshape = arr.shape
    indz, indy, indx = (
        int(round((gridshape[0] - oldshape[0]) / 2.0)),
        int(round((gridshape[1] - oldshape[1]) / 2.0)),
        int(round((gridshape[2] - oldshape[2]) / 2.0)),
    )
    # copy the data
    new_array[
        indz : indz + oldshape[0],
        indy : indy + oldshape[1],
        indx : indx + oldshape[2],
    ][:] = arr
    return new_array, (indx, indy, indz)


def custom_pad_array(
    arr: np.ndarray,
    nx1: int,
    nx2: int,
    ny1: int,
    ny2: int,
    nz1: int,
    nz2: int,
    fill_padding: Optional[Union[int, float]] = None,
    left: bool = True,
):
    """

    Pad an array with specified increments for each side of each dimension.
    Arguments:
        *nx1, nx2, ny1, ny2, nz1, nz2*
           Number of slices to add to each side of each dimension.
    Return:
        array
    """
    if not left:
        nx1, nx2 = nx2, nx1
        ny1, ny2 = ny2, ny1
        nz1, nz2 = nz2, nz1

    if fill_padding is None:
        fill_padding = arr.min()

    return np.pad(
        arr,
        ((nz1, nz2), (ny1, ny2), (nx1, nx2)),
        mode="constant",
        constant_values=fill_padding,
    )


# footprint array corresponding to 6 neighboring faces of a voxel
def grid_footprint():
    """
    Generate a footprint array for local neighborhood (6 faces)
    """
    a = np.zeros((3, 3, 3))
    a[1, 1, 1] = 1
    a[0, 1, 1] = 1
    a[1, 0, 1] = 1
    a[1, 1, 0] = 1
    a[2, 1, 1] = 1
    a[1, 2, 1] = 1
    a[1, 1, 2] = 1

    return a


# SMOOTHING/DUSTING
# useful when a 'safe' contour level is chosen
# for high resolution maps with fine features on the surface,
# this might erode part of useful density
def map_binary_opening(arr, contour, it=1, inplace=False):
    """
    Remove isolated densities by erosion
    """
    fp = grid_footprint()
    # current position can be updated based on neighbors only
    fp[1, 1, 1] = 0
    if inplace:
        arr[:] = arr * binary_opening(arr > float(contour), structure=fp, iterations=it)
        return arr
    else:
        return arr * binary_opening(arr > float(contour), structure=fp, iterations=it)


def map_binary_closing(arr, contour, it=1, inplace=False):
    """
    Close/Fill 'empty' (zero) voxels with filled (non-zero) neighbors
    """
    fp = grid_footprint()
    # current position can be updated based on neighbors only
    fp[1, 1, 1] = 0
    # threshold can be 1*std() to be safe?
    if inplace:
        arr[:] = arr * binary_closing(arr > float(contour), structure=fp, iterations=it)
        return arr
    else:
        return arr * binary_closing(arr > float(contour), structure=fp, iterations=it)


def apply_filter(ftmap, ftfilter, inplace=False):
    # fftshifted ftmap
    if inplace:
        ftmap[:] = ftmap * ftfilter
        return ftmap
    else:
        return ftmap * ftfilter


def find_level(arr, vol, apix):
    """
    Get the threshold corresponding to volume.
    """

    # initiate with reasonable values
    c1 = arr.min()
    vol_calc = float(vol) * 2
    # loop until calc vol and exp vol matches
    it = 0
    flage = 0
    while (vol_calc - float(vol)) / (apix[0] * apix[1] * apix[2]) > 10 and flage == 0:
        # mask only values >= previous sel
        mask_array = arr >= c1
        # compute histogram wt 1000 bins
        dens_freq, dens_bin = np.histogram(arr[mask_array], 1000)
        # loop over bins to select a min level from the bins
        sum_freq = 0.0
        for i in range(len(dens_freq)):
            sum_freq += dens_freq[-(i + 1)]
            dens_level = dens_bin[-(i + 2)]
            vol_calc = sum_freq * (apix[0] * apix[1] * apix[2])
            # break when vol exceeds exp vol to select the bin level
            if vol_calc > float(vol):
                sel_level = dens_level
                it += 1
                if sel_level <= c1:
                    flage = 1
                # print it, sel_level, c1, sum_freq, vol_calc, vol, flage
                c1 = sel_level
                if it == 3:
                    flage = 1
                break
    return sel_level


def interpolate_to_newgrid(
    arr: np.ndarray,
    flat_indices: np.ndarray,
    mode: str = "nearest",
    interp_order: int = 3,
    prefilter_input: bool = True,
):
    use_cupy = False
    cupy_input = False
    map_coordinates = scipy_map_coordinates
    if check_gpu():
        use_cupy = True
        import cupy
        from cupyx.scipy.ndimage import map_coordinates as cupy_map_coordinates

        if not isinstance(arr, cupy.ndarray):
            arr = cupy.array(arr)
            cupy_input = True

        if not isinstance(flat_indices, cupy.ndarray):
            flat_indices = cupy.array(flat_indices)
        map_coordinates = cupy_map_coordinates

    coords = map_coordinates(
        arr,
        flat_indices,
        mode=mode,
        order=interp_order,
        prefilter=prefilter_input,
    )
    if use_cupy and not cupy_input:
        return coords.get()
    return coords


def downsample_stride(
    arr: np.ndarray,
    stride: Union[int, Sequence[int]],
):
    warnings.warn("Output array shape might be different from the one requested")
    if isinstance(stride, tuple) and len(stride) == 3:  # x, y and z strides
        return arr[:: stride[2], :: stride[1], :: stride[0]]
    elif isinstance(stride, int):
        return arr[::stride, ::stride, ::stride]
    else:
        raise ValueError(
            "Input a valid stride: (stride_x,stride_y,stride_z) or "
            "single stride value along all axes"
        )


def blockwise_average(arr: np.ndarray, block_shape: Union[int, Sequence[int]]):
    warnings.warn("Output array shape might be different from the one requested")
    arr_shape = arr.shape
    # check array dimension
    if len(arr_shape) != 3:
        raise ValueError("Input array must be 3D")
    if isinstance(block_shape, int):
        block_shape = (block_shape, block_shape, block_shape)
    zw, yw, xw = block_shape
    if arr_shape[0] % zw == 0 and arr_shape[1] % yw == 0 and arr_shape[2] % xw == 0:
        new_shape = (arr_shape[0] // zw, arr_shape[1] // yw, arr_shape[2] // xw)
        warnings.warn("Output will be of the shape {}".format(new_shape))
        return arr.reshape(new_shape[0], zw, new_shape[1], yw, new_shape[2], xw).mean(
            (1, 3, 5)
        )
    else:
        warnings.warn(
            "Using the stride mode instead of block average. "
            "Output will only have one value from every stride along each axis"
        )
        return downsample_stride(arr, stride=(zw, yw, xw))


# sizes of all patches
def size_patches(arr, contour):
    """
    Get sizes or size distribution of isolated densities
        Arguments:
            *contour*
                density threshold
        Return:
            array of sizes
    """
    fp = grid_footprint()
    binmap = arr > float(contour)
    label_array, labels = measurements.label(arr * binmap, structure=fp)
    sizes = measurements.sum(binmap, label_array, range(labels + 1))
    return sizes


def get_sigma_map(arr, window=5):
    footprint_sph = make_spherical_footprint(window)
    sigma_array = generic_filter(
        arr, np.std, footprint=footprint_sph, mode="constant", cval=0.0
    )
    return sigma_array


def get_fsc(map1_array, map2_array, map_apix=1.0, maxRes=None, keep_shape=False):
    dist1 = make_fourier_shell(
        map1_array.shape, keep_shape=keep_shape, fftshift=False, normalise=False
    )
    dist1 = dist1.astype(np.int)
    # dist2 = make_fourier_shell(map2_array.shape,keep_shape=keep_shape,
    #                           fftshift=False,normalise=False)
    # dist2 = dist2.astype(np.int)
    ftarray1 = calculate_fft(map1_array, keep_shape=keep_shape)
    ftarray2 = calculate_fft(map2_array, keep_shape=keep_shape)

    ftarray1 = np.fft.fftshift(ftarray1, axes=(0, 1))
    ftarray2 = np.fft.fftshift(ftarray2, axes=(0, 1))

    listfreq, listfsc, listnsf = calculate_fsc(
        ftarray1, ftarray2, dist1, map_apix=map_apix
    )

    return calculate_fscavg(listfreq, listfsc, listnsf, maxRes=maxRes)


def get_fsc_curve(map1_array, map2_array, map_apix=1.0, keep_shape=False):
    dist1 = make_fourier_shell(
        map1_array.shape, keep_shape=keep_shape, fftshift=False, normalise=False
    )
    dist1 = dist1.astype(np.int)
    # dist2 = make_fourier_shell(map2_array.shape,keep_shape=keep_shape,
    #                           fftshift=False,normalise=False)
    # dist2 = dist2.astype(np.int)
    ftarray1 = calculate_fft(map1_array, keep_shape=keep_shape)
    ftarray2 = calculate_fft(map2_array, keep_shape=keep_shape)

    ftarray1 = np.fft.fftshift(ftarray1, axes=(0, 1))
    ftarray2 = np.fft.fftshift(ftarray2, axes=(0, 1))

    listfreq, listfsc, listnsf = calculate_fsc(
        ftarray1, ftarray2, dist1, map_apix=map_apix
    )

    return listfreq, listfsc


def get_raps(arr, keep_shape=False, plotfile="ps.png", map_apix=1.0):
    # make frequency shells
    dist = make_fourier_shell(
        arr.shape, keep_shape=keep_shape, fftshift=False, normalise=False
    )
    dist = dist.astype(np.int)
    ftarray = calculate_fft(arr, keep_shape=keep_shape)
    list_freq = []
    list_intensities = []
    for r in np.unique(dist)[0 : int(np.ceil(arr.shape[0] / 2))]:
        shell_indices = dist == r
        shell_amplitude = np.absolute(ftarray[shell_indices])
        avg_shell_intensity = np.log10(np.mean(np.square(shell_amplitude)))
        list_freq.append(float(r) / arr.shape[0])
        list_intensities.append(avg_shell_intensity)
    try:
        import matplotlib.pyplot as plt
    except (RuntimeError, ImportError) as e:
        if hasattr(e, "message"):
            print("Matplotlib import error {}".format(e.message))
        else:
            print(e)
        plt = None
        return list_freq, list_intensities

    plt.rcParams.update({"font.size": 12})
    plt.xlabel("Resolution", fontsize=12)
    plt.ylabel("log(Intensity)", fontsize=12)
    plt.plot(list_freq, list_intensities, linewidth=2.0, color="g")
    locs, labs = plt.xticks()
    step = (max(locs) - min(locs)) / 10.0
    locs = np.arange(min(locs), max(locs) + step, step)
    labels = np.round(map_apix / locs[1:], 1)
    plt.xticks(locs[1:], labels, rotation="vertical")
    plt.savefig(plotfile)
    plt.close()
    return list_freq, list_intensities


def calculate_fscavg(
    listfreq, listfsc, listnsf, maxRes=None, minRes=None, list_weights=None
):
    if maxRes is None:
        maxfreq_index = len(listfreq)
    else:
        maxfreq = 1.0 / maxRes
        # print maxfreq
        maxfreq_index = np.searchsorted(listfreq, maxfreq, side="right")
    if minRes is None:
        minfreq_index = 0
    else:
        minfreq = 1.0 / minRes
        minfreq_index = np.searchsorted(listfreq, minfreq)
    maxfreq_index = min(maxfreq_index, len(listfreq))

    weighted_fsc_sum = 0.0
    sum_nsf = 0.0
    for ind in range(minfreq_index, maxfreq_index):
        weighted_fsc_sum += listfsc[ind] * listnsf[ind]
        sum_nsf += listnsf[ind]
    FSCavg = weighted_fsc_sum / sum_nsf
    return FSCavg


def find_background_peak(arr, iter=2):
    lbin = np.amin(arr)
    rbin = np.amax(arr)
    ave = np.mean(arr)
    sigma = np.std(arr)
    for it in range(iter):
        if it == 0:
            data = arr
        else:
            data = arr[(arr >= lbin) & (arr <= rbin)]

        freq, bins = np.histogram(data, 100)
        ind = np.nonzero(freq == np.amax(freq))[0]
        peak = None
        for i in ind:
            val = (bins[i] + bins[i + 1]) / 2.0
            if val < float(ave) + float(sigma):
                peak = val
                lbin = bins[i]
                rbin = bins[i + 1]
        if peak is None:
            break
    return peak, ave


def plan_fft(arr, keep_shape=False, new_inparray=False):
    input_dtype = str(arr.dtype)
    if input_dtype not in ["float32", "float64", "longdouble"]:
        input_dtype = "float32"
        arr = arr.astype("float32")
    if not keep_shape:
        output_dtype = "complex64"
        if input_dtype == "float64":
            output_dtype = "complex128"
        elif input_dtype == "longdouble":
            output_dtype = "clongdouble"
        # for r2c transforms:
        output_array_shape = arr.shape[: len(arr.shape) - 1] + (arr.shape[-1] // 2 + 1,)
    else:
        output_dtype = "complex64"
        output_array_shape = arr.shape

    fftoutput = pyfftw.empty_aligned(output_array_shape, n=16, dtype=output_dtype)
    # check if array is byte aligned
    # TODO: can we read the map file as byte aligned?
    if new_inparray or not pyfftw.is_byte_aligned(arr):
        inputarray = pyfftw.empty_aligned(arr.shape, n=16, dtype=input_dtype)
        fft = pyfftw.FFTW(
            inputarray,
            fftoutput,
            direction="FFTW_FORWARD",
            axes=(0, 1, 2),
            flags=["FFTW_ESTIMATE"],
        )
    elif pyfftw.is_byte_aligned(arr):
        fft = pyfftw.FFTW(
            arr,
            fftoutput,
            direction="FFTW_FORWARD",
            axes=(0, 1, 2),
            flags=["FFTW_ESTIMATE"],
        )
        inputarray = np.copy(arr)

    return fft, fftoutput, inputarray


def calculate_fft(arr, keep_shape=False, new_inparray=False):
    if pyfftw_flag:
        fft, fftoutput, inputarray = plan_fft(
            arr, keep_shape=keep_shape, new_inparray=new_inparray
        )
        inputarray[:, :, :] = arr
        fft()
    else:
        # TODO: warning raises error in tasks
        # warnings.warn("PyFFTw not found!, using numpy fft")
        if not keep_shape:
            fftoutput = np.fft.rfftn(arr)
        else:
            fftoutput = np.fft.fftn(arr)
    return fftoutput


def plan_ifft(arr, output_shape=None, output_array_dtype=None, new_inparray=False):
    input_dtype = str(arr.dtype)
    #         #for c2r transforms:
    #             if output_shape is None: output_shape = \
    #                                     arr.shape[:len(arr.shape)-1]+\
    #                                     ((arr.shape[-1] - 1)*2,)
    if output_array_dtype is None:
        output_array_dtype = "float32"
    if output_shape is None:
        output_shape = arr.shape[: len(arr.shape) - 1] + ((arr.shape[-1] - 1) * 2,)
        if input_dtype not in ["complex64", "complex128", "clongdouble"]:
            input_dtype = "complex64"
        elif input_dtype == "complex128":
            output_array_dtype = "float64"
        elif input_dtype == "clongdouble":
            output_array_dtype = "longdouble"
    elif output_shape[-1] // 2 + 1 == arr.shape[-1]:
        if input_dtype not in ["complex64", "complex128", "clongdouble"]:
            input_dtype = "complex64"
        elif input_dtype == "complex128":
            output_array_dtype = "float64"
        elif input_dtype == "clongdouble":
            output_array_dtype = "longdouble"
    else:
        output_shape = arr.shape
        output_array_dtype = "complex64"

    output_array = pyfftw.empty_aligned(output_shape, n=16, dtype=output_array_dtype)
    # check if array is byte aligned
    if new_inparray or not pyfftw.is_byte_aligned(arr):
        inputarray = pyfftw.n_byte_align_empty(arr.shape, n=16, dtype=input_dtype)
        ifft = pyfftw.FFTW(
            inputarray,
            output_array,
            direction="FFTW_BACKWARD",
            axes=(0, 1, 2),
            flags=["FFTW_ESTIMATE"],
        )  # planning_timelimit=0.5)
        inputarray[:, :, :] = arr
    else:
        ifft = pyfftw.FFTW(
            arr,
            output_array,
            direction="FFTW_BACKWARD",
            axes=(0, 1, 2),
            flags=["FFTW_ESTIMATE"],
        )  # planning_timelimit=0.5)
        inputarray = arr

    return ifft, output_array, inputarray


def calculate_ifft(arr, output_shape=None, inplace=False, new_inparray=False):
    """
    Calculate inverse fourier transform
    """
    if pyfftw_flag:
        ifft, output_array, inputarray = plan_ifft(
            arr, output_shape=output_shape, new_inparray=new_inparray
        )
        # r2c fft
        ifft()
    else:
        # TODO: warnings raises error in tasks
        # warnings.warn("PyFFTw not found!, using numpy fft")
        if output_shape is None or output_shape[-1] // 2 + 1 == arr.shape[-1]:
            # if s is specified, axes must be specified too
            output_array = np.fft.irfftn(arr, s=output_shape, axes=(0, 1, 2))
        else:
            output_array = np.real(np.fft.ifftn(arr))
        # np.fft.fftpack._fft_cache.clear()
    del arr
    return output_array.real.astype(np.float32, copy=False)


def make_fourier_shell(map_shape, keep_shape=False, normalise=True, fftshift=True):
    """
    For a given grid, make a grid with sampling
    frequencies in the range (0:0.5)
    Return:
        grid with sampling frequencies
    """
    z, y, x = map_shape
    # numpy fftfreq : odd-> 0 to (n-1)/2 & -1 to -(n-1)/2 and
    # even-> 0 to n/2-1 & -1 to -n/2 to check with eman
    # set frequencies in the range -0.5 to 0.5
    if keep_shape:
        rad_z, rad_y, rad_x = np.mgrid[
            -np.floor(z / 2.0) : np.ceil(z / 2.0),
            -np.floor(y / 2.0) : np.ceil(y / 2.0),
            -np.floor(x / 2.0) : np.ceil(x / 2.0),
        ]
        if not fftshift:
            rad_x = np.fft.ifftshift(rad_x)
    # r2c arrays from fftw/numpy rfft
    else:
        rad_z, rad_y, rad_x = np.mgrid[
            -np.floor(z / 2.0) : np.ceil(z / 2.0),
            -np.floor(y / 2.0) : np.ceil(y / 2.0),
            0 : np.floor(x / 2.0) + 1,
        ]
    if not fftshift:
        rad_z = np.fft.ifftshift(rad_z)
        rad_y = np.fft.ifftshift(rad_y)
    if normalise:
        rad_z = rad_z / float(np.floor(z))
        rad_y = rad_y / float(np.floor(y))
        rad_x = rad_x / float(np.floor(x))
    rad_x = rad_x**2
    rad_y = rad_y**2
    rad_z = rad_z**2
    dist = np.sqrt(rad_z + rad_y + rad_x)
    return dist


def tanh_lowpass(map_shape, cutoff, fall=0.3, keep_shape=False):
    """
    Lowpass filter with a hyperbolic tangent function

    cutoff: high frequency cutoff [0:0.5]
    fall: smoothness of falloff [0-> tophat,1.0-> gaussian]
    Return:
        tanh lowpass filter to apply on fourier map
    """
    # e.g cutoff = apix/reso is the stop band
    if fall == 0.0:
        fall = 0.01
    drop = math.pi / (2 * float(cutoff) * float(fall))
    cutoff = min(float(cutoff), 0.5)
    # fall determines smoothness of falloff, 0-> tophat, 1.0-> gaussian
    # make frequency shells
    dist = make_fourier_shell(map_shape, keep_shape=keep_shape, fftshift=True)
    # filter
    dist1 = dist + cutoff
    dist1[:] = drop * dist1
    dist1[:] = np.tanh(dist1)
    dist[:] = dist - cutoff
    dist[:] = drop * dist
    dist[:] = np.tanh(dist)
    dist[:] = dist1 - dist
    dist = 0.5 * dist
    del dist1

    #     list_freq = []
    #     list_intensities = []
    #     rprev = 0.0
    #     for r in np.arange(0.02,0.5,0.02):
    #         shell_indices = (dist_ini < r) & (dist_ini <= rprev)
    #         avg_shell_intensity = np.mean(dist[shell_indices])
    #         list_freq.append(r)
    #         list_intensities.append(avg_shell_intensity)
    #         rprev = r
    #     print list_freq
    #     print list_intensities
    #
    return dist


def tanh_bandpass(
    map_shape,
    low_cutoff=0.0,
    high_cutoff=0.5,
    low_fall=0.1,
    high_fall=0.1,
    keep_shape=False,
):
    """
    Bandpass filter with a hyperbolic tangent function
    low_cutoff: low frequency cutoff [0:0.5]
    high-cutoff : high frequency cutoff [0:0.5]
    fall: determines smoothness of falloff [0-> tophat,1.0-> gaussian]
    Return:
        tanh lowpass filter to apply on fourier map
    """
    low_drop = math.pi / (2 * float(high_cutoff - low_cutoff) * float(low_fall))
    high_drop = math.pi / (2 * float(high_cutoff - low_cutoff) * float(high_fall))

    dist = make_fourier_shell(map_shape, keep_shape=keep_shape, fftshift=True)
    return 0.5 * (
        np.tanh(high_drop * (dist + high_cutoff))
        - np.tanh(high_drop * (dist - high_cutoff))
        - np.tanh(low_drop * (dist + low_cutoff))
        + np.tanh(low_drop * (dist - low_cutoff))
    )


def butterworth_lowpass(map_shape, pass_freq, keep_shape=False):
    """
    Lowpass filter with a gaussian function
    pass_freq : low-pass cutoff frequency [0:0.5]
    """
    eps = 0.882
    a = 10.624
    high_cutoff = (
        0.15 * math.log10(1.0 / pass_freq) + pass_freq
    )  # stop band frequency (used to determine the fall off)

    fall = 2.0 * (
        math.log10(eps / math.sqrt(a**2 - 1))
        / math.log10(pass_freq / float(high_cutoff))
    )

    cutoff_freq = float(pass_freq) / math.pow(eps, 2 / fall)

    dist = make_fourier_shell(map_shape, keep_shape=keep_shape, fftshift=True)
    # filter
    dist = dist / cutoff_freq
    return np.sqrt(1.0 / (1.0 + np.power(dist, fall)))


def gauss_bandpass(map_shape, sigma, center=0.0, keep_shape=False):
    """
    Bandpass filter with a gaussian function
    sigma : cutoff frequency [0:0.5]
    """
    # sigma = sigma/1.414
    # get frequency shells
    dist = make_fourier_shell(map_shape, keep_shape=keep_shape, fftshift=True)
    # filter
    return np.exp(-((dist - center) ** 2) / (2 * sigma * sigma))


def gauss_lowpass(map_shape, sigma, keep_shape=False):
    """
    Bandpass filter with a gaussian function
    sigma : cutoff frequency [0:0.5]
    """
    # sigma = sigma/1.414
    # get frequency shells
    dist = make_fourier_shell(map_shape, keep_shape=keep_shape, fftshift=True)
    # filter
    return np.exp(-(dist**2) / (2 * sigma * sigma))


def make_3D_from_1D(vec_x, vec_y, vec_z):
    vec_x = vec_x**2
    vec_y = vec_y**2
    vec_z = vec_z**2
    dist = np.sqrt(vec_z[:, None, None] + vec_y[:, None] + vec_x)
    return dist


def get_radial_distance_map(radius):
    """
    Get radial distance box
    """
    rad_z = np.arange(radius * -1, radius + 1)
    rad_y = np.arange(radius * -1, radius + 1)
    rad_x = np.arange(radius * -1, radius + 1)
    return make_3D_from_1D(rad_x, rad_y, rad_z)


def make_spherical_footprint(radius):
    """
    Get spherical footprint of a given diameter
    """
    dist = get_radial_distance_map(radius)
    # set_printoptions(threshold='nan')
    return (dist <= radius) * 1


def apply_real_space_filter(
    arr: np.ndarray,
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
    if edgeonly:
        bin_arr = arr > 0.0
    filtered_array = arr
    for i in range(iter):
        if filter_type == "gaussian":
            filtered_array = apply_gaussian_filter(
                filtered_array, sigma=sigma, truncate=truncate, inplace=inplace
            )
        elif filter_type == "mean":
            filtered_array = apply_mean_filter(
                filtered_array, kernel_size=kernel_size, inplace=inplace
            )
        elif filter_type == "tanh":
            filtered_array = apply_tanh_filter(
                filtered_array, kernel_size=kernel_size, inplace=inplace
            )
        else:
            raise ValueError(
                "filter type not recognised, choose from [gaussian, mean, tanh]"
            )
        if inplace:  # if filtered_array is returned as None
            filtered_array = arr
    if normzero_one:
        filtered_array = (filtered_array - np.amin(filtered_array)) / (
            np.amax(filtered_array) - np.amin(filtered_array)
        )
    elif maxone:
        filtered_array /= np.amax(filtered_array)
    if minzero:
        filtered_array[filtered_array < 0.0] = 0.0
    if edgeonly:
        filtered_array[bin_arr] = arr[bin_arr]
    return filtered_array


def apply_mean_filter(arr: np.ndarray, kernel_size: int = 5, inplace=False):
    footprint_sph = make_spherical_footprint(np.ceil(float(kernel_size) / 2))
    if inplace:
        arr[:] = generic_filter(
            arr, np.mean, footprint=footprint_sph, mode="constant", cval=0.0
        )
    else:
        newarray = np.copy(arr)
        newarray[:] = generic_filter(
            arr, np.mean, footprint=footprint_sph, mode="constant", cval=0.0
        )
        return newarray


def apply_gaussian_filter(
    arr: np.ndarray, sigma: float = 1, truncate: int = 3, inplace=False
):
    if inplace:
        arr[:] = gaussian_filter(
            arr, sigma=sigma, truncate=truncate, mode="constant", cval=0.0
        )
    else:
        newarray = np.copy(arr)
        newarray[:] = gaussian_filter(
            newarray, sigma=sigma, truncate=truncate, mode="constant", cval=0.0
        )
        return newarray


def apply_tanh_filter(arr: np.ndarray, kernel_size: int = 5, inplace: bool = False):
    footprint_sph = make_spherical_footprint(np.ceil(float(kernel_size) / 2))
    arr_max = np.amax(arr)
    if inplace:
        arr *= 5.0 / arr_max  # set maximum to 5.0 (tanh = 0.99)
        arr[:] = generic_filter(
            arr,
            tanh_convolve,
            footprint=footprint_sph,
            mode="constant",
            cval=0.0,
        )
        arr *= arr_max / np.amax(arr)  # reset max to previous max (TODO: improve this)
    else:
        newarray = np.copy(arr)
        newarray *= 5.0 / arr_max  # set maximum to 5.0 (tanh = 0.99)
        newarray[:] = generic_filter(
            arr,
            tanh_convolve,
            footprint=footprint_sph,
            mode="constant",
            cval=0.0,
        )
        newarray *= arr_max / np.amax(arr)
        return newarray


def tanh_convolve(x):
    return np.sum(np.tanh(x))


def smooth_radially(
    arr: np.ndarray,
    filter_type: str = "cosine",
    inplace: bool = False,
):
    # check array dimension
    if len(arr.shape) != 3:
        raise ValueError("Input array must be 3D")
    z, y, x = arr.shape
    if not z == x or not x == y:
        raise ValueError("Input array should be cubic")
    radial_filter = get_radialfilter_kernel(kernel_size=z, filter_type=filter_type)
    if inplace:
        arr[:] = arr * radial_filter
    else:
        return arr * radial_filter


def get_radialfilter_kernel(kernel_size: int = 6, filter_type: str = "cosine"):
    if filter_type == "cosine":
        oneD_window = cosine(kernel_size)
    elif filter_type == "tanh":
        oneD_window = np.linspace(
            -5,
            5,
            int(np.floor(kernel_size / 2.0)),
            endpoint=True if kernel_size % 2.0 == 0 else False,
        )
        oneD_window = np.append(
            oneD_window,
            np.linspace(5, -5, int(np.ceil(kernel_size / 2.0)), endpoint=True),
        )
        oneD_window = np.tanh(oneD_window)
        oneD_window += 1.0  # 0 - 2
        oneD_window /= 2.0  # 0 - 1
    radial_filter = make_3D_from_1D(oneD_window, oneD_window, oneD_window)
    radial_filter = radial_filter / np.amax(radial_filter)
    return radial_filter


def add_maskarray_softedge(arr: np.ndarray, filter_type: str = "cosine", edge: int = 6):
    bin_arr = arr > 0
    filter_kernel = get_radialfilter_kernel(
        kernel_size=2 * edge, filter_type=filter_type
    )
    filtered_array = fftconvolve(arr, filter_kernel, mode="same")
    filtered_array[np.isnan(filtered_array)] = 0.0
    filtered_array /= np.amax(filtered_array)
    filtered_array[bin_arr] = arr[bin_arr]
    filtered_array[filtered_array < 0.0] = 0.0
    return filtered_array


def calculate_shell_correlation(shell1, shell2):
    cov_ps1_ps2 = shell1 * np.conjugate(shell2)
    sig_ps1 = shell1 * np.conjugate(shell1)
    sig_ps2 = shell2 * np.conjugate(shell2)
    cov_ps1_ps2 = np.sum(np.real(cov_ps1_ps2))
    var_ps1 = np.sum(np.real(sig_ps1))
    var_ps2 = np.sum(np.real(sig_ps2))
    # skip shells with no variance
    if np.round(var_ps1, 15) == 0.0 or np.round(var_ps2, 15) == 0.0:
        fsc = 0.0
    else:
        fsc = cov_ps1_ps2 / (np.sqrt(var_ps1 * var_ps2))
    return fsc


def calculate_fsc(
    ftarr1,
    ftarr2,
    dist1,
    dist2=None,
    step=None,
    maxlevel=None,
    map_apix=None,
    reso=None,
    plot=False,
):
    list_freq = []
    list_fsc = []
    list_nsf = []
    x = 0.0
    # for grids of different dimensions
    if dist2 is None:
        dist2 = dist1
    # Assume maxlevel is N/2 if maxlevel is None
    if step is None:
        assert compare_tuple(ftarr1.shape, ftarr2.shape)
        maxlevel = ftarr1.shape[0] // 2
    # Assume step=1 and dist is in range 0-N/2, if step is None
    if step is None:
        assert compare_tuple(ftarr1.shape, ftarr2.shape)
        step = 1.0
    highlevel = x + step

    while x < maxlevel:
        fshell_indices = (dist1 < min(maxlevel, highlevel)) & (dist1 >= x)
        fsc = calculate_shell_correlation(
            ftarr1[fshell_indices], ftarr2[fshell_indices]
        )
        # print highlevel, fsc
        list_freq.append(highlevel)
        list_fsc.append(fsc)
        num_nonzero_avg = min(
            np.count_nonzero(ftarr1[fshell_indices]),
            np.count_nonzero(ftarr2[fshell_indices]),
        )
        list_nsf.append(num_nonzero_avg)
        x = highlevel
        highlevel = x + step
    if step == 1.0 and map_apix is not None:
        list_freq = np.array(list_freq) / (ftarr1.shape[0] * map_apix)

    listfreq, listfsc, listnsf = zip(*sorted(zip(list_freq, list_fsc, list_nsf)))
    return listfreq, listfsc, listnsf


def scale_amplitudes(
    ftarr1,
    ftarr2,
    dist1,
    dist2=None,
    maxlevel=None,
    step=None,
    ref=False,
    plot=False,
):
    """
    Scale amplitudes in each resolution shell:
        to avg (by default)
        to a reference (ref=True)
    dist1,dist2 : frequency shells (fftshifted) [0-0.5 or 0-N/2 or
                                                0-1/(nyquist resolution)]
    For grids of same dimensions, dist2 = dist1 (dist2=None)
    step: shell width (values in agreement with dist1,dist2)
            e.g. 1/N if dist in [0-0.5]
                1/(N*apix) if dist in [0-1/nyq.res]
                1 if dist in [0-N/2]
    maxlevel : nyquist (values in agreement with dist1,dist2)
    """
    # SCALING
    # storing for plots
    ft1_avg = []
    ft2_avg = []
    ft1_avg_new = []
    lfreq = []
    nc = 0
    x = 0.0
    highlevel = x + step
    # for grids of different dimensions
    if dist2 is None:
        dist2 = dist1
    # Assume step=1 and dist is in range 0-N/2, if step is None
    if step is None:
        assert compare_tuple(ftarr1.shape, ftarr2.shape)
        step = 1
    # Assume maxlevel is N/2 if maxlevel is None
    if maxlevel is None:
        assert compare_tuple(ftarr1.shape, ftarr2.shape)
        maxlevel = ftarr1.shape[0] // 2
    while x < maxlevel:
        # indices between upper and lower shell bound
        fshells1 = (dist1 < min(maxlevel, highlevel)) & (dist1 >= x)
        # radial average
        shellvec1 = ftarr1[fshells1]
        # indices between upper and lower shell bound
        fshells2 = (dist2 < min(maxlevel, highlevel)) & (dist2 >= x)
        # radial average
        shellvec2 = ftarr2[fshells2]

        abs1 = abs(shellvec1)
        abs2 = abs(shellvec2)
        # check non zero amplitudes in a shell
        ns1 = len(np.nonzero(abs1)[0])  # or count_nonzero
        ns2 = len(np.nonzero(abs2)[0])  # or count_nonzero
        # only few fourier terms in a shell: merge two shells
        if (ns1 < 5 or ns2 < 5) and nc < 3:
            nc += 1
            highlevel = min(maxlevel, x + (nc + 1) * step)
            if highlevel < maxlevel:
                continue
        else:
            nc = 0
        # scale intensities
        mft1 = np.mean(np.square(abs1))
        mft2 = np.mean(np.square(abs2))
        if mft1 == 0.0 and mft2 == 0.0:
            x = highlevel
            highlevel = x + step
            if highlevel < maxlevel:
                continue
        if plot:
            # sq of radial avg amplitude
            ft1_avg.append(np.log10(mft1))
            ft2_avg.append(np.log10(mft2))
        # scale to amplitudes of the ref map
        if ref:
            if mft1 == 0.0:
                continue
            ftarr1[fshells1] = shellvec1 * np.sqrt(mft2 / mft1)
        else:
            # replace with avg amplitudes for the two maps
            ftarr1[fshells1] = shellvec1 * np.sqrt((mft2 + mft1) / (2.0 * mft1))
            ftarr2[fshells2] = shellvec2 * np.sqrt((mft2 + mft1) / (2.0 * mft2))

        if plot:
            # new radial average (to check)
            mft1 = np.mean(
                np.square(abs(ftarr1[fshells1]))
            )  # numsum(absolute(ft1.fullMap[fshells1]))/len(shellvec1)
            ft1_avg_new.append(np.log10(mft1))
            lfreq.append(x + (highlevel - x) / 2.0)

        del fshells1, fshells2, shellvec1, shellvec2
        x = highlevel
        highlevel = x + step
        gc.collect()

    dict_plot = {}
    if plot:
        dict_plot["map1"] = [lfreq, ft1_avg]
        dict_plot["map2"] = [lfreq, ft2_avg]
        dict_plot["scaled"] = [lfreq, ft1_avg_new]
        return dict_plot


def get_median_deviation(array: np.ndarray) -> float:
    return np.median(np.absolute(array - np.median(array)))


def scale_median(arr1, arr2):
    """Scale one list/array of scores with respect to another based on
    distribution around median.

    Arguments:
        arr1, arr2: Array/list of scores

    Returns:
        Scaled arr1, based on the values in arr2
    """
    nparr1 = np.array(arr1)
    nparr2 = np.array(arr2)
    # median deviation
    med_dev_1 = get_median_deviation(nparr1)
    med_dev_2 = get_median_deviation(nparr2)
    if med_dev_1 == 0.0:
        scale_factor = 1.0
    else:
        scale_factor = med_dev_2 / med_dev_1
    shift_factor = np.median(nparr2) - (scale_factor * np.median(nparr1))

    # TODO: find a better way to avoid outliers in general
    if (max(nparr1) - min(nparr1)) > 0.1:
        scaled_arr = ((scale_factor * nparr1 + shift_factor) + nparr2) / 2.0
    else:
        scaled_arr = nparr1
    return scaled_arr


def calculate_array_overlap(
    array1,
    array2,
    arrays_masked=False,
    array1_threshold=None,
    array2_threshold=None,
):
    """
    Calculate fraction of overlap between two arrays (non-zero values)

    return:
    fraction of overlap with respect to the first array, with respect to
    second and with respect to the total (union)
    """
    if not arrays_masked and not (array1_threshold or array2_threshold):
        raise ValueError("Please provide masked maps or contour thresholds")
    elif arrays_masked:
        binmap1 = array1
        binmap2 = array2
    else:
        binmap1 = array1 > float(array1_threshold)
        binmap2 = array2 > float(array2_threshold)
    mask_array = (binmap1 * binmap2) > 0

    size1 = np.sum(binmap1)
    size2 = np.sum(binmap2)
    return (
        float(np.sum(mask_array)) / size1,
        float(np.sum(mask_array)) / size2,
        float(np.sum(mask_array)) / (size1 + size2),
    )


def compare_tuple(tuple1, tuple2):
    for val1, val2 in zip(tuple1, tuple2):
        if isinstance(val2, float):
            if round(val1, 2) != round(val2, 2):
                return False
        else:
            if val1 != val2:
                return False
    return True
