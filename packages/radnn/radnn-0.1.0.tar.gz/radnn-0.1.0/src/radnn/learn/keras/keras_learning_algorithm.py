from radnn.learn.keras.keras_optimization_combo import KOptimizationCombo

class KLearningAlgorithm(object):
  # -----------------------------------------------------------------------------------
  def __init__(self, config, is_verbose=True):
    self.config = config
    self.is_verbose = is_verbose
    self._implementation = None

    self.prepare()
  # -----------------------------------------------------------------------------------
  @property
  def optimizer(self):
    oResult = None
    if self._implementation is not None:
      if isinstance(self._implementation, KOptimizationCombo):
        oResult = self._implementation.optimizer
    return oResult
  # -----------------------------------------------------------------------------------
  @property
  def callbacks(self):
    oResult = None
    if self._implementation is not None:
      if isinstance(self._implementation, KOptimizationCombo):
        oResult = self._implementation.callbacks
    return oResult
  # -----------------------------------------------------------------------------------
  def prepare(self):
    if mlsys.is_tensorflow_installed:
      self._implementation = KOptimizationCombo(self.config, self.is_verbose)
    return self
  # -----------------------------------------------------------------------------------
