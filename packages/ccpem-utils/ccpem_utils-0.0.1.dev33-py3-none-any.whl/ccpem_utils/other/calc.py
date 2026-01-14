import numpy as np
from typing import Union, Type, Sequence, List, Optional

try:
    from scipy.spatial import cKDTree as kdt
except ImportError:
    from scipy.spatial import KDTree as kdt
from scipy.signal import argrelextrema
import math
import re
from scipy.stats import skew


def calc_z(
    list_vals: Union[list, np.ndarray],
    val: Optional[float] = None,
) -> Union[float, list]:
    # remove selected value before calculating z
    if val is not None:
        if isinstance(val, list):
            list_vals.remove(val)  # remove val from list
        elif isinstance(val, np.ndarray):
            list_vals = list_vals[list_vals != val]
        else:
            pass
    sum_mapval = np.sum(list_vals)
    mean_mapval = sum_mapval / len(list_vals)
    # median_mapval = np.median(list_vals)
    std_mapval = np.std(list_vals)
    if val is None:
        if std_mapval == 0.0:
            z: Union[float, List[float]] = [0.0] * len(list_vals)
        else:
            z = np.round((np.array(list_vals) - mean_mapval) / std_mapval, 2)
    else:
        if std_mapval == 0.0:
            z = 0.0
        else:
            z = (val - mean_mapval) / std_mapval
    return z


def calc_z_median(
    list_vals: Union[list, np.ndarray],
    val: Optional[float] = None,
) -> Union[float, list]:
    # remove selected value before calculating z
    if val is not None:
        if isinstance(val, list):
            list_vals.remove(val)  # remove val from list
        elif isinstance(val, np.ndarray):
            list_vals = list_vals[list_vals != val]
        else:
            pass

    # sum_smoc = np.sum(list_vals)
    median_smoc = np.median(list_vals)
    mad_smoc = np.median(np.absolute(np.array(list_vals) - median_smoc))
    if val is None:
        if mad_smoc == 0.0:
            z: Union[float, List[float]] = [0.0] * len(list_vals)
        else:
            z = np.around((np.array(list_vals) - median_smoc) / mad_smoc, 2)
    else:
        if mad_smoc == 0.0:
            z = 0.0
        else:
            z = round(((val - median_smoc) / mad_smoc), 2)
    return z


def calc_std(arr: Union[np.ndarray, list], use_mean: Optional[float] = None) -> float:
    if not use_mean:
        use_mean = np.mean(arr)
    return np.sqrt(np.sum(np.square(np.array(arr) - use_mean)) / np.array(arr).size)


def get_indices_sphere(
    gridtree: Type[kdt],
    coord: Union[list, np.ndarray],
    dist: float = 5.0,
) -> list:
    list_points = gridtree.query_ball_point([coord[0], coord[1], coord[2]], dist)
    return list_points


def check_list_overlap(
    list1: List,
    list2: List,
    diff_limit: float = 0.2,
):
    n_diff = 0
    for n in range(len(list1)):
        if list1[n] not in list2:
            n_diff += 1
    if float(n_diff) / len(list1) > diff_limit:
        return False
    return True


# utility functions to compare dict/list/str/num including a tolerance
# for any numeric comparisons within
def compare_dict_almost_equal(dict1: dict, dict2: dict, num_rel_tol: float):
    for k in dict1:
        if isinstance(dict1[k], dict):
            assert isinstance(dict2[k], dict)
            compare_dict_almost_equal(dict1[k], dict2[k], num_rel_tol)
        elif type(dict1[k]) in [list, tuple]:
            assert len(dict1[k]) == len(dict2[k])
            compare_list_almost_equal(dict1[k], dict2[k], num_rel_tol)
        else:
            compare_values_almost_equal(dict1[k], dict2[k], num_rel_tol)


def compare_list_almost_equal(list1, list2, num_rel_tol):
    assert len(list1) == len(list2)
    for n in range(len(list1)):
        if isinstance(list1[n], dict):
            assert isinstance(list2[n], dict)
            compare_dict_almost_equal(list1[n], list2[n], num_rel_tol)
        if type(list1[n]) in [list, tuple]:
            assert len(list1[n]) == len(list2[n])
            compare_list_almost_equal(list1[n], list2[n], num_rel_tol)
        else:
            compare_values_almost_equal(list1[n], list2[n], num_rel_tol)


def compare_values_almost_equal(value1, value2, num_rel_tol):
    if isinstance(value1, str):
        l1 = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", value1)
        l2 = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", value2)
        assert len(l1) == len(l2)
        if len(l1) == 1:
            assert math.isclose(float(l1[0]), float(l2[0]), rel_tol=num_rel_tol)
        else:
            assert l1 == l2
    else:
        try:
            assert math.isclose(float(l1), float(l2), rel_tol=num_rel_tol)
        except ValueError:
            assert l1 == l2


def get_moc(array1: np.ndarray, array2: np.ndarray) -> float:
    num = np.sum(array1 * array2)
    den = np.sqrt(np.sum(np.square(array1)) * np.sum(np.square(array2)))
    if den == 0.0:
        if num == 0.0:
            return 1.0
        return -1.0
    return num / den


def get_ccc(array1: np.ndarray, array2: np.ndarray) -> float:
    num = np.sum((array1 - np.mean(array1)) * (array2 - np.mean(array2)))
    den = np.sqrt(
        np.sum(np.square(array1 - np.mean(array1)))
        * np.sum(np.square(array2 - np.mean(array2)))
    )
    if den == 0.0:
        if num == 0.0:
            return 1.0
        return -1.0
    return num / den


def get_histogram_peaks(data: Sequence[Union[int, float]], bins=10):
    """Get local peaks from a distribution

    :param data: sequence of numbers
    :param bins: number of bins to divide the data
    :type data: Sequence[Union[int,float]]
    """
    bin_freq, bin_val = np.histogram(data, min(len(data), bins))
    # check for local peaks
    local_peaks = argrelextrema(bin_freq, np.greater, order=3)

    list_peaks = []
    max_peak_frac = float(np.amax(bin_freq)) / np.sum(bin_freq)
    for peak in local_peaks[0]:
        if max_peak_frac < 0.95 and peak > 10:
            list_peaks.append(peak)
    return list_peaks, max_peak_frac


def get_skewness(dist: Union[List[Union[float, int]], np.ndarray]):
    """Get skewness of a distribution

    :param dist: input distribution
    :type dist: Union[List[float, int], np.ndarray]
    :return: skewness
    :rtype: float
    """
    unique_values = np.unique(np.array(dist))
    if len(unique_values) == 1:  # identical
        return math.nan
    else:
        skewness = skew(dist, nan_policy="omit")
        if math.isnan(skewness):  # TODO: sometimes skew returns nan?
            return 0.0
        return skewness
