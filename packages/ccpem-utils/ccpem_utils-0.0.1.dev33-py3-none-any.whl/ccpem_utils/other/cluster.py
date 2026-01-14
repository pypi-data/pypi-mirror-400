from sklearn import cluster, mixture
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KDTree
from typing import Union, Optional
import numpy as np


def cluster_coord_features(
    array_3Dcoord_features: Union[list, np.ndarray],
    num_clusters: Optional[int] = None,
    dbscan_eps: float = 2.3,
    norm: bool = False,
) -> np.ndarray:
    """
    Cluster spatial features based on
        1) feature density (DBSCAN) or
        2) gaussian mixture model (GMM) when number of clusters is known

    Arguments
    ---------
        array_3Dcoord_features: np.ndarray
            input array (e.g. [[x1,y1,z1,feature11,feature12,...],
                                [x2,y2,z2,feature21,feature22,...]])
        num_clusters: int, optional
            number of clusters expected
        dbscan_eps: float, optional
            maximum distance within same neighborhood (not within a cluster)
            (used only when the number of clusters is not provided)
            Useful eps values for 3D protein coordinate domain level separation:
            all atom: 2.3 (norm - 0.035)
            backbone atoms: 2.8 (norm - 0.04)
            c-alpha: 3.83 [3.7 - 4.0] (norm - 0.07673)
            centre: 5.35 [5.2 - 5.45] (norm - 0.088), geometric centre.

        norm: bool, optional
            Normalize each column (feature) to a similar range
    Returns
    -------
        Array with cluster labels for each input row
    """
    if isinstance(array_3Dcoord_features, list):
        array_3Dcoord_features = np.array(array_3Dcoord_features)
    if norm:
        scaler = MinMaxScaler()
        scaler.fit(array_3Dcoord_features)
        # scale each feature in [0,1], normalising by min and max of each feature
        array_3Dcoord_features_norm = scaler.transform(array_3Dcoord_features)
        if dbscan_eps == 2.3:
            dbscan_eps = 0.035
    else:
        array_3Dcoord_features_norm = array_3Dcoord_features
    if num_clusters is not None:
        model = mixture.GaussianMixture(
            n_components=num_clusters, covariance_type="full"
        )
        model.fit(array_3Dcoord_features_norm)
        return model.predict(array_3Dcoord_features_norm)
    else:
        model = cluster.DBSCAN(eps=dbscan_eps, min_samples=2)
        model.fit_predict(array_3Dcoord_features_norm)
        return model.labels_


def generate_kdtree(
    coords: Union[list, np.ndarray],
    leaf_size: Optional[int] = None,
    metric: str = "euclidean",
) -> KDTree:
    """
    Get a KDtree object from input coordinates

    Arguments
    ---------
        coords: list or np.ndarray
            input array (e.g. [[x1,y1,z1],
                                [x2,y2,z2]])
        leaf_size: int, optional
            size or each segment/leaf of the tree
            tree building is faster with larger leaf size
            querying is usually faster when leaf_size is comparable
                (say between k and 3*k) to the number of neighbors queried
        metric: string, optional
            distance metric, euclidean by default
    Returns
    -------
        sklearn KDTree object
    """
    if leaf_size:
        return KDTree(coords, leaf_size=leaf_size, metric=metric)
    else:
        return KDTree(coords, metric=metric)


def get_neighbors_kdtree(
    coords: Union[list, np.ndarray],
    kdtree: KDTree,
    distance: Optional[float] = None,
    num_neighbors: Optional[int] = None,
):
    if distance:
        return kdtree.query_radius(coords, distance)
    elif num_neighbors:
        return kdtree.query(coords, num_neighbors)


def pairs_kdtree(
    coords: Union[list, np.ndarray], kdtree: KDTree, dist: float
) -> np.ndarray:
    neighbor_index = get_neighbors_kdtree(coords, kdtree, distance=dist)
    pair_indices_array: np.ndarray = np.array([], dtype=int)
    ln = 0
    for neighbors in neighbor_index:
        for n in neighbors:
            pair_index = np.array([[ln, n]])
            if pair_indices_array.size == 0:
                pair_indices_array = pair_index
            else:
                pair_indices_array = np.append(pair_indices_array, pair_index, axis=0)
        ln += 1
    return pair_indices_array
