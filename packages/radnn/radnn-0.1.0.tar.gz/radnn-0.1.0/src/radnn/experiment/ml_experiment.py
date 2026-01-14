# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2019-2025 Pantelis I. Kaplanoglou

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ......................................................................................
import os
import numpy as np
from datetime import datetime

from radnn.core import RequiredLibs
oReqs = RequiredLibs()
if oReqs.is_tensorflow_installed:
  from tensorflow import keras
  
from radnn import MLSystem, FileSystem, FileStore, Errors
from radnn.data import DataSetBase
from radnn.learn.keras import KLearningAlgorithm

from radnn.plots import PlotLearningCurve
from radnn.evaluation import EvaluateClassification

from .ml_experiment_env import MLExperimentEnv
from .ml_experiment_config import MLExperimentConfig, model_code_mllib
from .ml_experiment_store import MLExperimentStore


# --------------------------------------------------------------------------------------------------------------------
# Define a custom sorting function
def _sort_by_last_path_element(folder):
  # Split the path into its components
  components = folder.split(os.pathsep)
  # Extract the last path element
  last_element = components[-1]
  # Extract the numeric part of the last element
  numeric_part = ''.join(filter(str.isdigit, last_element))
  # Convert the numeric part to an integer
  try:
    return int(numeric_part)
  except ValueError:
    # If the numeric part is not convertible to an integer, return a large number
    return float('inf')
# --------------------------------------------------------------------------------------------------------------------






# ======================================================================================================================
class MLExperiment:
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, setup, model=None, learning_algorithm=None, cost_function=None, metrics=[], is_retraining=False):
    # ...........................................................................
    self.model = model
    self.learning_algorithm: LearningAlgorithm = learning_algorithm
    self.cost_function = cost_function
    self.metrics = metrics
    self.is_retraining = is_retraining
    self.is_showing_step_progress = False
    self.environment = None
    self.config = None
    self.model_name = None
    self.model_fs = None

    self.generator = None
    self._dataset: DataSetBase = None
    self._ts_feed = None
    self._vs_feed = None

    self.process_log = None
    self.learning_history = None
    self._evaluation = None

    self._is_graph_built = False
    self._has_loaded_state = False

    self._start_train_time = None
    self._end_train_time = None

    self._currentModelFolder = None
    self._currentModelStateFolder = None
    self._currentModelLogFileStore = None
    # ...........................................................................

    if isinstance(setup, MLExperimentEnv):
      self.environment = setup
      self.config = self.environment.config
      self.model_fs = self.environment.model_fs
    elif isinstance(setup, MLExperimentConfig):
      self.config = setup
    elif isinstance(setup, dict):
      self.config = MLExperimentConfig().assign(setup)
    elif hasattr(setup, "config"):
      self.config = setup.config
    else:
      raise Exception("Incompatible machine learning experiment setup object")

    self.model_name = model_code_mllib(self.config)

    #if self.environment is None:
    #  raise Exception("Not supported yet: Creating a machine learning experiment environment from a config or dictionary object")

    if self.model_fs is None:
      if MLSystem.Instance().filesys is None:
        raise Exception(Errors.MLSYS_NO_FILESYS)
      oFileSys: FileSystem = MLSystem.Instance().filesys
      self.model_fs = MLExperimentStore(oFileSys.models.folder(self.model_name))

    assert isinstance(self.model_fs, MLExperimentStore), f"Unsupported model store object of class {self.model_fs.__class__}"
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def evaluation(self):
    if self._evaluation is None:
      raise Exception("Must run evaluation for the metrics object to become available")
    return self._evaluation
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def model_state_folder(self):
    return self.model_fs.state_fs.base_folder
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def checkpoint_paths(self):
    oCheckpointFS = self.model_fs.checkpoint_fs
    if self._currentModelFolder is not None:
      if self._currentModelFolder != self.model_fs.base_folder:
        oCheckpointFS = FileStore(self._currentModelFolder).subfs("checkpoints")

    sCheckPointPaths = oCheckpointFS.Files("*.index", True, p_tSortFilenamesAs=int)
    sCheckPointPaths = sorted(sCheckPointPaths, key=_sort_by_last_path_element)
    return sCheckPointPaths
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def is_pretrained(self):
    return self.model_fs.state_fs.exists("saved_model.pb")
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def restore(cls, model_name, model=None):
    oConfig = {"ModelName": model_name}
    oExperiment = MLExperiment(oConfig, model)
    return oExperiment.load()
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def dataset(self):
    return self._dataset
  # ......................................
  @dataset.setter
  def dataset(self, value):
    self._dataset = value
    if isinstance(self._dataset, DataSetBase):
      if self._ts_feed is None:
        self._ts_feed = self._dataset.ts.feed
      if self._vs_feed is None:
        self._vs_feed = self._dataset.vs.feed
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def training_set(self):
    return self._ts_feed
  # ......................................
  @training_set.setter
  def training_set(self, value):
    self._ts_feed = value
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def validation_set(self):
    return self._vs_feed
  # ......................................
  @validation_set.setter
  def validation_set(self, value):
    self._vs_feed = value

  # --------------------------------------------------------------------------------------------------------------------
  def print_info(self):
    if not self._is_graph_built:
      for oSamples, oTarget in self._ts_feed.take(1):
        # We recall one batch/sample to create the graph and initialize the model parameters
        y = self.model(oSamples)
        break

      self._is_graph_built = True

    self.model.summary()
  # --------------------------------------------------------------------------------------------------------------------
  def _timing_info(self):
    # Timings
    nEpochs = self.config["Training.MaxEpoch"]
    dDiff = self._end_train_time - self._start_train_time
    nElapsedHours = dDiff.total_seconds() / 3600
    nSecondsPerEpoch = dDiff.total_seconds() / nEpochs
    dTiming = {"StartTime": self._start_train_time, "EndTime": self._end_train_time,
               "ElapsedHours": nElapsedHours, "SecondsPerEpoch": nSecondsPerEpoch}
    return dTiming
  # --------------------------------------------------------------------------------------------------------------------
  def save(self):

    self.model.save(self.model_fs.state_fs.base_folder)
    if self.learning_history is not None:
      self.model_fs.log_fs.obj.save(self.learning_history, "keras_learning_history.pkl")
      dTiming = self._timing_info()
      self.model_fs.log_fs.obj.save(dTiming, "timing_info.pkl")
      dTiming["StartTime"] = dTiming["StartTime"].strftime('%Y-%m-%dT%H:%M:%S')
      dTiming["EndTime"] = dTiming["EndTime"].strftime('%Y-%m-%dT%H:%M:%S')
      self.model_fs.log_fs.json.save(dTiming, f"timing_info_{self._end_train_time.strftime('%Y-%m-%dT%H%M%S')}.json",
                             is_sorted_keys=False)

    # //TODO: Keep cost function names and other learning parameters for evaluation
  # --------------------------------------------------------------------------------------------------------------------
  def load(self, use_last_checkpoint=False, model_root_folder=None):
    self._currentModelFolder = self.model_fs.base_folder
    self._currentModelStateFolder = self.model_fs.state_fs.base_folder
    self._currentModelLogFileStore = self.model_fs.log_fs
    if model_root_folder is not None:
      self._currentModelFolder = model_root_folder
      self._currentModelStateFolder = os.path.join(model_root_folder, "state")
      self._currentModelLogFileStore = FileStore(model_root_folder).subfs("logs")

    print("Loading saved state from ", self._currentModelStateFolder)
    self.model = keras.models.load_model(self._currentModelStateFolder)
    self.learning_history = (self._currentModelLogFileStore.obj.load("keras_learning_history.pkl"))
    self._has_loaded_state = True

    if use_last_checkpoint:
      self.load_model_params(use_last_checkpoint=True)

    return self.model
  # --------------------------------------------------------------------------------------------------------------------
  def unload_model(self):
    del self.model
    self.model = None
  # --------------------------------------------------------------------------------------------------------------------
  def save_model_params(self):
    if self.model is not None:
      self.model.save_weights(self.model_fs.param_fs.folder("model_params"))
  # --------------------------------------------------------------------------------------------------------------------
  def load_model_params(self, checkpoint_path=None, use_last_checkpoint=False, is_ignoring_not_found=False):
    sTargetPath = None
    sCheckPointPaths = self.checkpoint_paths
    if checkpoint_path is not None:
      if checkpoint_path in sCheckPointPaths:
        sTargetPath = checkpoint_path
      else:
        raise Exception(f"Model params not found in checkpoint path {checkpoint_path}")
    elif use_last_checkpoint:
      if len(sCheckPointPaths) > 0:
        sTargetPath = sCheckPointPaths[-1]
      else:
        raise Exception(f"No checkpoints are saved in {self.model_fs.checkpoint_fs.base_folder}")
    else:
      if self.model_fs.param_fs.is_empty:
        raise Exception(f"Model params not found in {self.model_fs.param_fs.base_folder}")
      else:
        sTargetPath = self.model_fs.param_fs.subpath("model_params")

    if sTargetPath is not None:
      if is_ignoring_not_found:
        self.model.load_weights(sTargetPath)
        '''
        nLogLevel = tf.get_logger().getEffectiveLevel()
        try:
          tf.get_logger().setLevel(logging.CRITICAL) #This does not suppress warning during loading of models

        finally:
          tf.get_logger().setLevel(nLogLevel)
        '''
      else:
        self.model.load_weights(sTargetPath)
      print("Loaded weights from %s" % sTargetPath)
      self._has_loaded_state = True
  # --------------------------------------------------------------------------------------------------------------------
  def transfer_model_params_to(self, new_model, input_shape, metircs=[]):
    self.save_model_params()
    del self.model
    self.model = new_model
    self.model.build(input_shape=input_shape)
    self.load_model_params()
    self.model.compile(metrics=metircs)  # , run_eagerly = True)
    return self.model
  # --------------------------------------------------------------------------------------------------------------------
  def train(self):
    # //TODO: Decouple from Keras training

    if (not self.is_pretrained) or self.is_retraining:
      oOptimizer = self.learning_algorithm.optimizer
      self._start_train_time = datetime.now()
      self.model.compile(loss=self.cost_function, optimizer=oOptimizer, metrics=self.metrics)
      if MLSystem.Instance().switches["IsDebuggable"]:
        self.model.run_eagerly = True

      if self.is_showing_step_progress:
        nVerbose = 1
      else:
        nVerbose = 2

      nEpochs = self.config["Training.MaxEpoch"]

      if self.generator is not None:
        self.process_log = self.model.fit_generator(generator=self.generator,
                                                    epochs=nEpochs,
                                                    callbacks=self.learning_algorithm.callbacks,
                                                    validation_data=self._vs_feed,
                                                    verbose=nVerbose)
      else:
        if "Training.StepsPerEpoch" in self.config:
          self.process_log = self.model.fit(self._ts_feed
                                            , batch_size=self.config["Training.BatchSize"]
                                            , epochs=nEpochs
                                            , validation_data=self._vs_feed
                                            , callbacks=self.learning_algorithm.callbacks
                                            , steps_per_epoch=self.config["Training.StepsPerEpoch"]
                                            , verbose=nVerbose)
        else:
          self.process_log = self.model.fit(self._ts_feed
                                            , batch_size=self.config["Training.BatchSize"]
                                            , epochs=nEpochs
                                            , validation_data=self._vs_feed
                                            , callbacks=self.learning_algorithm.callbacks
                                            , verbose=nVerbose)
      self._end_train_time = datetime.now()
      self.learning_history = self.process_log.history
      self.save()
      self._is_graph_built = True
    else:
      self.load()

    return self.model
  # --------------------------------------------------------------------------------------------------------------------


  # // Evaluation \\
  # --------------------------------------------------------------------------------------------------------------------
  def plot_learning_curve(self):
    oTrainingLogPlot = PlotLearningCurve(self.learning_history, self.model_name)
    oTrainingLogPlot.prepare(metric_key=self.metrics[0]).show()
    oTrainingLogPlot.prepare_cost(self.cost_function).show()
  # --------------------------------------------------------------------------------------------------------------------
  def _evaluation_metrics(self, true_class_labels, predicted_class_labels):
    true_class_labels = true_class_labels.reshape(-1)
    predicted_class_labels = predicted_class_labels.reshape(-1)
    self._evaluation = EvaluateClassification(true_class_labels, predicted_class_labels)

    return self._evaluation
  # --------------------------------------------------------------------------------------------------------------------
  def _evaluation_report(self, true_class_labels, predicted_class_labels, p_nID=None):
    true_class_labels = true_class_labels.reshape(-1)
    predicted_class_labels = predicted_class_labels.reshape(-1)

    self._evaluation = EvaluateClassification(true_class_labels, predicted_class_labels)
    self._evaluation.print_confusion_matrix()
    self._evaluation.print_overall()
    self._evaluation.print_per_class()

    if p_nID is not None:
      bMissclassifiedFlags = (true_class_labels != predicted_class_labels)
      print(f"Missclassified Samples: {np.sum(bMissclassifiedFlags)}/{true_class_labels.shape[0]}")

      nMissTrue = true_class_labels[bMissclassifiedFlags]
      nMissPredicted = predicted_class_labels[bMissclassifiedFlags]
      nMissIDs = p_nID[bMissclassifiedFlags]
      for i, nID in enumerate(nMissIDs):
        print(f"  |__ Sample#{int(nID):07d} True:{int(nMissTrue[i])} != {int(nMissPredicted[i])}")

    return self._evaluation
  # --------------------------------------------------------------------------------------------------------------------
  def evaluate_classifier(self, true_class_labels=None, sample_feed=None, is_evaluating_using_keras=False, is_printing=True):
    if sample_feed is None:
      sample_feed = self._vs_feed

    nLoss, nAccuracy = (None, None)
    if is_evaluating_using_keras:
      oTestResults = self.model.evaluate(sample_feed, verbose=1)
      nLoss, nAccuracy = oTestResults
      print("Evaluation: Loss:%.6f - Accuracy:%.6f" % (nLoss, nAccuracy))

    # ... // Evaluate \\ ...
    nVerbose = 0
    if is_printing:
      nVerbose = 1

    nPrediction = self.model.predict(sample_feed, verbose=nVerbose)
    if isinstance(nPrediction, tuple):
      nPredictedClassProbabilities, nPredictedClassLabels, nIDs = nPrediction
    else:
      nPredictedClassProbabilities = nPrediction
      nPredictedClassLabels = np.argmax(nPredictedClassProbabilities, axis=1)
      nIDs = None

    if true_class_labels is None:
      true_class_labels = self._dataset.vs_labels

    if is_printing:
      return self._evaluation_report(true_class_labels, nPredictedClassLabels, nIDs), nLoss, nAccuracy
    else:
      return self._evaluation_metrics(true_class_labels, nPredictedClassLabels), nLoss, nAccuracy
  # --------------------------------------------------------------------------------------------------------------------






