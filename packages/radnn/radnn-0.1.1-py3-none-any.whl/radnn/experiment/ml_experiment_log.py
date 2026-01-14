from radnn.system.filesystem import FileStore
class MLExperimentLog:
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, filename: str, experiment_info: dict | None = None):
    self.filename = filename
    if experiment_info is None:
      experiment_info = {}
    self.experiment_info = experiment_info
    self.logs = { "experiment": experiment_info,
                  "epoch": [],
                  "epoch_time": [],
                  "train_step_loss": [],
                  "train_step_accuracy": [],
                  "train_loss": [],
                  "train_accuracy": [],
                  "val_loss": [],
                  "val_accuracy": [],
            }
  # --------------------------------------------------------------------------------------------------------------------
  def assign_series(self, is_autoinit=False, **kwargs):
    if is_autoinit:
      for key, value in kwargs.items():
        if key not in self.logs:
          self.logs[key] = []
      
    for key, value in kwargs.items():
      self.logs[key] = value
  # --------------------------------------------------------------------------------------------------------------------
  def append(self, is_autoinit=False, **kwargs):
    if is_autoinit:
      for key, value in kwargs.items():
        if key not in self.logs:
          self.logs[key] = []

    for key, value in kwargs.items():
      self.logs[key].append(value)
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def load(self, experiment_fs: FileStore):
    self.logs = experiment_fs.json.load(self.filename)
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def save(self, experiment_fs: FileStore):
    experiment_fs.json.save(self.logs, self.filename)
    return self
  # --------------------------------------------------------------------------------------------------------------------
    