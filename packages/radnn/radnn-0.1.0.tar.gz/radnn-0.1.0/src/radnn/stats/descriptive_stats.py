import numpy as np

class DescriptiveStats(object):
  INNER_FENCE_RATIO = 1.5
  OUTER_FENCE_RATIO = 3.0

  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, data):
    if (data.ndim == 2) and (np.prod(data.shape) == np.max(data.shape)):
      data = data.reshape(-1)

    self.min = np.min(data)
    self.max = np.max(data)

    self.mean = np.mean(data)
    self.std = np.std(data)

    self.q1 = np.percentile(data, q=25)
    self.median = np.median(data)
    self.q2 = self.median
    self.q3 = np.percentile(data, q=75)
    self.iq_range = self.q3 - self.q1

    self.inner_fence_low = self.q1 - type(self).INNER_FENCE_RATIO * self.iq_range
    self.inner_fence_high = self.q3 + type(self).INNER_FENCE_RATIO * self.iq_range

    self.outer_fence_low = self.q1 - type(self).OUTER_FENCE_RATIO * self.iq_range
    self.outer_fence_high = self.q3 + type(self).OUTER_FENCE_RATIO * self.iq_range

  # --------------------------------------------------------------------------------------------------------------------
  def outliers(self, data, is_using_outer_fence=False, dtype=np.float32):
    if is_using_outer_fence:
      nResult = np.asarray([x for x in data if x < self.outer_fence_low or x > self.outer_fence_high], dtype=dtype)
    else:
      nResult = np.asarray([x for x in data if x < self.inner_fence_low or x > self.inner_fence_high], dtype=dtype)
    return nResult
  # --------------------------------------------------------------------------------------------------------------------
  def __str__(self):
    sResult = "range=[%.6f,%.6f] mean=%6f std=%.6f iqrange=%.6f Q1=%.6f median (Q2)=%.6f Q3=%.6f max (Q4)=%.6f" % (self.min, self.max,
                                                                                                self.mean, self.std,
                                                                                                self.iq_range,
                                                                                                self.q1, self.median,
                                                                                                self.q3, self.max)
    return sResult
  # --------------------------------------------------------------------------------------------------------------------