import types

import numpy  as np
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.cluster.kmeans import kmeans
from pyclustering.utils.metric import distance_metric, type_metric

from measures.periodicMeasure import PeriodicMeasure

# This version of periodic_mean has an error in computation.
# The fix is implemented in the new function below
# def periodic_mean(points, period=360):
#     period_2 = period/2
#     if max(points) - min(points) > period_2:
#         _points = np.array([0 if x > period_2 else 1 for x in points]).reshape(-1,1)
#         n_left =_points.sum()
#         n_right = len(points) - n_left
#         if n_left >0:
#             mean_left = (points * _points).sum()/n_left
#         else:
#             mean_left =0
#         if n_right >0:
#             mean_right = (points * (1-_points)).sum() / n_right
#         else:
#             mean_right = 0
#         _mean = (mean_left*n_left+mean_right*n_right+n_left*period)/(n_left+n_right)
#         return _mean % period
#     else:
#         return points.mean(axis=0)

def periodic_mean(points, period=360):

    points = points.squeeze()

    half_period = period/2
    is_left = np.array([0 if x > half_period else 1 for x in points])
    
    n_left = is_left.sum()
    n_right = len(points) - n_left

    if n_left > 0 and n_right > 0:

        mean_left = (points * is_left).sum() / n_left
        mean_right = (points * (1-is_left)).sum() / n_right

        if mean_right - mean_left <= period/2:
            mean = (n_left*mean_left + n_right*mean_right)/len(points)
        else:
            mean = (n_left*(mean_left + period) + n_right*mean_right)/len(points) % period
    
    else:
        mean = points.sum()/len(points)
    
    return mean


def _periodic_update_centers(self):
    dimension = self._kmeans__pointer_data.shape[1]
    centers = np.zeros((len(self._kmeans__clusters), dimension))

    for index in range(len(self._kmeans__clusters)):
        cluster_points = self._kmeans__pointer_data[self._kmeans__clusters[index], :]
        centers[index] = periodic_mean(cluster_points, self.period)
    return np.array(centers)

def periodic_kmeans(data, initial_centers, metric):

    kmeans_instance =  kmeans(data, initial_centers, metric=metric)
    kmeans_instance._kmeans__update_centers = types.MethodType(_periodic_update_centers,kmeans_instance)
    return kmeans_instance


class PeriodicKMeans(kmeans):

    def __init__(self, data, period, initial_centers = None, no_of_clusters = None):
        self.data = data
        self.period = period
        self.measure = PeriodicMeasure(period)
        self.metric = distance_metric(type_metric.USER_DEFINED, func=self.measure.distance)
        if initial_centers is None:
            _centers = kmeans_plusplus_initializer(data, no_of_clusters).initialize()
        else:
            _centers = initial_centers
        super().__init__(data, _centers, metric=self.metric)
        self._kmeans__update_centers = types.MethodType(_periodic_update_centers, self)

    def clustering(self):
        self.process()
        clusters = self.get_clusters()
        clust_data = []
        for c in range(len(clusters)):
            clust_data.append(np.array(self.data[clusters[c]]))
        return clust_data, self.get_total_wce(), self.get_centers()

    def periodic_shift(self, data):
        return self.measure.periodic_shift(data)





