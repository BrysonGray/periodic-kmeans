import numpy as np

class PeriodicMeasure:
    def __init__(self, period):
        self.period = period

    def distance(self, a, b):
        d = abs (a-b)
        return min (d, self.period - d)

    def periodic_mean(self,points):
        if max(points) - min(points) > self.period/2:
            _points = np.array([0 if x > self.period/2 else self.period for x in points]).reshape(-1, 1)
            _points = points + _points
            _mean = _points.mean(axis=0)
        else:
            _mean = points.mean(axis=0)
        if _mean > self.period:
            return _mean - self.period
        else:
            return _mean