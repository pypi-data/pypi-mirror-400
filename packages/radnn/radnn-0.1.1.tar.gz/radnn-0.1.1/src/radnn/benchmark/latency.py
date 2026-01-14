import numpy as np
import time
import functools


class LatencyBenchmark(dict):
  def __init__(self):
    self.enabled = False
  
  def stats(self, key):
    nSeries = np.asarray(self.get(key, [0.0]), np.float32)
    nMean = np.mean(nSeries)
    nStd = np.std(nSeries)
    nMax = np.max(nSeries)
    nMin = np.min(nSeries)
    return nMin, nMax, nMean, nStd

    

mlbench = LatencyBenchmark()


def timed_method(name: str | None = None):
  """
  Decorator to measure elapsed time using a high-resolution timer.

  Usage:
      @timeit()
      def f(...):

      @timeit("custom_name")
      def g(...):
  """
  
  def decorator(func):
    label = name or func.__qualname__
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      if not mlbench.enabled:
        return func(*args, **kwargs)
      else:
        start = time.perf_counter()
        try:
          return func(*args, **kwargs)
        finally:
          end = time.perf_counter()
          elapsed = end - start
          if not label in mlbench:
            mlbench[label] = []
          mlbench[label].append(elapsed * 1e3)
    
    return wrapper
  
  return decorator