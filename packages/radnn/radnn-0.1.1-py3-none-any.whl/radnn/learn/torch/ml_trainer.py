import numpy as np
from radnn import mlsys, FileStore

# -----------------------------
# Standard Libraries
# -----------------------------
import time

# -----------------------------
# PyTorch
# -----------------------------
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler

from radnn.evaluation import EvaluateClassification
from radnn.plots import PlotConfusionMatrix, PlotLearningCurve
from radnn.experiment import MLExperimentLog, experiment_fold_number, experiment_name_with_fold
import matplotlib.pyplot as plt
from radnn.learn.torch import StairCaseLR
from radnn.errors import *

# -----------------------------
# Progress Bar
# -----------------------------
from tqdm import tqdm

# ----------------------------------------------------------------------------------------------------------------------
def seed_everything(seed=42):
  import os
  import random
  os.environ['PYTHONHASHSEED'] = str(seed)
  np.random.seed(seed)
  random.seed(seed)
  torch.manual_seed(seed)
  torch.cuda.manual_seed(seed)
  torch.backends.cudnn.deterministic = True
  torch.backends.cudnn.benchmark = True
# ----------------------------------------------------------------------------------------------------------------------



class MLModelTrainer():
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, hyperparams, dataset, model, device):
    self.hprm = hyperparams
    
    # The python/numpy generators might have been used prior to the start of training.
    # We need to re-seed here to reset to the start of the pseudo-random sequence,
    # plus encapsulating the reproducibility for torch in case mlsys.random_seed_all has not been explicitly called
    seed_everything(self.hprm["Experiment.RandomSeed"])
    
    self.dataset = dataset
    self.model = model
    self.device = device
    self.criterion = None
    self.optimizer = None
    self.scheduler = None
    self.best_model_state = None
    self.best_model_state_file = None
    self.training_logs_file = None
    self.experiment_hyperparams_file = None
    self.get_model_paths()
    self.mlflow_run_id = None
    self.registered_model = None
  
  # --------------------------------------------------------------------------------------------------------------------
  def get_lr(self):
    return self.optimizer.param_groups[0]["lr"]
  
  # --------------------------------------------------------------------------------------------------------------------
  def get_model_paths(self):
    hprm = self.hprm
    sExperimentName = hprm["Experiment.Name"]
    self.best_model_state = f'{hprm["Dataset.Name"]}_{hprm["Model.Name"]}_pipeline{hprm["Data.Pipeline.Type"]}_{sExperimentName}'
    sExperimentWithFoldNumber = experiment_name_with_fold(hprm)
    self.experiment_fs: FileStore = mlsys.filesys.models.subfs(sExperimentWithFoldNumber)
    self.best_model_state_file = self.experiment_fs.file(f'{self.best_model_state}.pth')
    self.best_model_state_onnx_file = self.experiment_fs.file(f'{self.best_model_state}.onnx')
    self.training_logs_file = self.experiment_fs.file(f"training_logs_{sExperimentName}.json")
    self.experiment_hyperparams_file = self.experiment_fs.file(f"hyperparams_{sExperimentWithFoldNumber}.json")
  
  # --------------------------------------------------------------------------------------------------------------------
  def build_optimizer(self):
    hprm = self.hprm
    sExtra = ""
    if hprm["Training.Optimizer"].upper() == "SGD":
      self.optimizer = optim.SGD(self.model.parameters(), lr=hprm["Training.LearningRate"],
                                 momentum=hprm.get("Training.Momentum", 0.0),
                                 nesterov=hprm.get("Training.Momentum.Nesterov", False),
                                 weight_decay=hprm["Training.Regularize.WeightDecay"])
      sExtra = f'momentum={self.optimizer.defaults["momentum"]}'
      if self.optimizer.defaults["nesterov"]:
        sExtra += " (Nesterov)"
    elif hprm["Training.Optimizer"].upper() == "RMSPROP":
      self.optimizer = optim.RMSprop(self.model.parameters(), lr=hprm["Training.LearningRate"],
                                     weight_decay=hprm["Training.Regularize.WeightDecay"],
                                     momentum=hprm.get("Training.Momentum", 0.0),
                                     eps = hprm.get("Training.RMSProp.Epsilon", 1e-8)
                                    )
    elif hprm["Training.Optimizer"].upper() == "ADAM":
      self.optimizer = optim.Adam(self.model.parameters(), lr=hprm["Training.LearningRate"],
                                  weight_decay=hprm["Training.Regularize.WeightDecay"])
    elif hprm["Training.Optimizer"].upper() == "ADAMW":
      self.optimizer = optim.AdamW(self.model.parameters(), lr=hprm["Training.LearningRate"],
                                  weight_decay=hprm["Training.Regularize.WeightDecay"])
  
    print(f'Using {hprm["Training.Optimizer"].upper()} optimizer {sExtra}')
  # --------------------------------------------------------------------------------------------------------------------
  def build_lr_scheduler(self):
    hprm = self.hprm
    sSchedulingType = hprm.get("Training.LearningRateSchedule", "MultiStepDivisor")
    sSchedulingType = sSchedulingType.upper()
    nDefaultSetup = [[0, hprm["Training.LearningRate"]], [hprm["Training.Epochs"], 0.00001]]
    nFinalChangeEpoch, nFinalLR = hprm.get("Training.LearningRateSchedule.Setup", nDefaultSetup)[-1]
    
    self.scheduler = None
    if (sSchedulingType.upper() == "MultiStepDivisor".upper()):
      if "Training.LearningRateSchedule.Epochs" in hprm:
        self.scheduler = lr_scheduler.MultiStepLR(self.optimizer,
                                                  milestones=hprm["Training.LearningRateSchedule.Epochs"],
                                                  gamma=hprm["Training.LearningRateSchedule.StepRatio"])
      else:
        raise Exception(TRAINER_LR_SCHEDULER_INVALID_MILESTONE_SETUP)
    elif (sSchedulingType.upper() == "StairCase".upper()):
      if "Training.LearningRateSchedule.Setup" in hprm:
        oLRSetup = hprm["Training.LearningRateSchedule.Setup"]
        if not isinstance(oLRSetup, list):
          raise Exception(TRAINER_LR_SCHEDULER_INVALID_SETUP)
        self.scheduler = StairCaseLR(self.optimizer, oLRSetup)
      else:
        raise Exception(TRAINER_LR_SCHEDULER_INVALID_SETUP)
    
    elif sSchedulingType.upper() == "CosineAnnealing".upper():
      self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer,
                                                                  T_max=nFinalChangeEpoch,
                                                                  eta_min=nFinalLR)
      
    assert self.scheduler is not None, TRAINER_LR_SCHEDULER_UNSUPPORTED
  # --------------------------------------------------------------------------------------------------------------------
  def prepare(self):
    hprm = self.hprm
    hprm["Model.State.Best"] = self.best_model_state
    sExperimentName = hprm["Experiment.Name"]
    mlsys.filesys.configs.subfs("run_6classes").json.save(hprm, f"{sExperimentName}_hyperparams.json",
                                                           is_sorted_keys=False)

    if "Training.CrossEntropy.UseClassWeights" in hprm:
      class_weights_tensor = torch.tensor(self.dataset.ts.class_weights, dtype=torch.float)
      class_weights_tensor = class_weights_tensor.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
      self.criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    else:
      self.criterion = nn.CrossEntropyLoss()

    self.build_optimizer()
    self.build_lr_scheduler()
  # --------------------------------------------------------------------------------------------------------------------
  def fit(self, device, **kwargs):
    self.model.to(device)
    bIsPreview = kwargs.get("is_preview", False)
    
    hprm = self.hprm
    dInfo = {
              "experiment_name": hprm["Experiment.Name"],
              "experiment_fold_number": experiment_name_with_fold(hprm),
              "model_name": hprm["Model.Name"],
              "model_variants": hprm["Model.Variants"]
            }
    oLog: MLExperimentLog = MLExperimentLog(self.training_logs_file, dInfo)

    best_val_f1_score = 0.0  # Track the best validation accuracy
    patience = 8  # Number of epochs to wait for improvement
    epochs_without_improvement = 0  # Counter for early stopping

    nTSBatchCount = self.dataset.ts.minibatch_count
    nVSBatchCount = self.dataset.vs.minibatch_count
    nEpochCount = hprm["Training.Epochs"]
    bInitialInfoSave = False

    nLR = hprm["Training.LearningRate"]
    self.experiment_fs.json.save(hprm, f'hyperparams_{hprm["Experiment.Name"]}.json')

    oStepLoss = []
    oStepAccuracy = []
    all_labels = None
    all_predictions = None

    nEpochMinibatchCount = 0
    for nEpochIndex in range(nEpochCount):
      print(f"\nEpoch {nEpochIndex + 1}/{nEpochCount}")

      # -------------------- Training --------------------
      self.model.train()
      train_loss, train_correct = 0.0, 0

      nLR = self.scheduler.get_last_lr()[0]
      progress_bar = tqdm(self.dataset.ts.loader, desc=f"Epoch {nEpochIndex + 1}/{nEpochCount} LR={nLR:.5f}", leave=False)
      nStart = time.perf_counter()

      nDebugSteps = 0
      for inputs, labels, ids in progress_bar:
        nDebugSteps += 1
        inputs, labels = inputs.to(self.device), labels.to(self.device)

        self.optimizer.zero_grad()
        outputs = self.model(inputs)
        loss = self.criterion(outputs, labels).double()
        loss.backward()
        self.optimizer.step()

        # Accumulate
        mb_loss = loss.item()
        train_loss += mb_loss
        _, predicted = torch.max(outputs, 1)
        mb_correct = (predicted == labels).sum().item()
        mb_count = len(labels)
        mb_accuracy = mb_correct / mb_count

        oStepLoss.append(mb_loss)
        oStepAccuracy.append(mb_accuracy)

        train_correct += mb_correct
        nEpochMinibatchCount += mb_count
        train_accuracy = train_correct / nEpochMinibatchCount

        progress_bar.set_postfix(loss=f"{mb_loss:.4f}", accuracy=f"{mb_accuracy:.4f}")
        if not bInitialInfoSave:
          bInitialInfoSave = True

        if bIsPreview:
          break

      nElapsedSecs = time.perf_counter() - nStart
      nStart = time.perf_counter()

      train_loss /= nTSBatchCount
      train_accuracy = train_correct / self.dataset.ts.sample_count
      print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_accuracy:.4f}")

      # -------------------- Validation --------------------
      self.model.eval()
      val_loss, val_correct = 0.0, 0

      all_labels= []
      all_predictions = []
      progress_bar = tqdm(self.dataset.vs.loader, desc=f"Validating {nEpochIndex + 1}/{nEpochCount}", leave=False)
      with torch.no_grad():
        for inputs, labels, ids in progress_bar:
          inputs, labels = inputs.to(self.device), labels.to(self.device)
          outputs = self.model(inputs)
          loss = self.criterion(outputs, labels).double()
          
          val_loss += loss.item()
          _, predicted = torch.max(outputs, 1)
          all_labels.extend(labels.cpu().numpy().tolist())
          all_predictions.extend(predicted.cpu().numpy().tolist())
          val_correct += (predicted == labels).sum().item()

          progress_bar.set_postfix(loss=loss.item())

      val_loss /= nVSBatchCount
      val_accuracy = val_correct / self.dataset.vs.sample_count

      if self.scheduler is not None:
        self.scheduler.step()
        nLR = self.scheduler.get_last_lr()[0]
      print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_accuracy:.4f} | LR: {nLR:.5f}")

      # -------------------- Update logs / Evaluation Report --------------------
      oLog.append(epoch=nEpochIndex+1,
                  epoch_time=nElapsedSecs,
                  train_loss = train_loss,
                  train_accuracy = train_accuracy,
                  val_loss = val_loss,
                  val_accuracy = val_accuracy,)
      oLog.assign_series(train_step_loss = oStepLoss, train_step_accuracy = oStepAccuracy)
      oLog.save(self.experiment_fs)
      print(f"📊 Training logs saved to {self.training_logs_file}")

      oEvaluator = self.evaluation_report(all_labels, all_predictions, oLog.logs, is_showing_plots=False)
      
      # -------------------- Checkpoint & Early Stopping --------------------
      val_f1_score = oEvaluator.average_f1score
      if (val_f1_score > best_val_f1_score):
        best_val_f1_score = val_f1_score
        self.best_model_state_file = self.best_model_state_file
        torch.save(self.model.state_dict(), self.best_model_state_file)
        hprm["Model.State.BestEpoch"] = f"Epoch{nEpochIndex + 1}"
        self.experiment_fs.json.save(hprm, f'hyperparams_{hprm["Experiment.Name"]}.json')
        print(f'✅ Best model updated with F1 score: {best_val_f1_score:.4f}')
        self.export_metrics(oEvaluator, nEpochIndex+1)
        
        epochs_without_improvement = 0
      else:
        epochs_without_improvement += 1
      
      if bIsPreview:
        break
      nElapsedSecs = time.perf_counter() - nStart

      #if epochs_without_improvement >= patience:
      #  print(f'⏹ Early stopping after {nEpochIndex + 1} epochs without improvement.')
      #  break

    print("🎉 Training complete!")
  
  # --------------------------------------------------------------------------------------------------------------
  def print_trainable_blocks(self):
    for sName, oParams in self.model.named_parameters():
      bIsTrainable = oParams.requires_grad
      if bIsTrainable:
        print(f" |__ TRAINABLE: {sName}")
  # --------------------------------------------------------------------------------------------------------------
  def export_per_class_metrics(self, evaluator, opened_file, class_names=None):
    if class_names is not None:
      nClassCount = len(evaluator.class_names.keys())
      oClasses = [f"{evaluator.class_names[x]:7}" for x in list(range(nClassCount))]
    else:
      oClasses = sorted(np.unique(evaluator.actual_classes))
      nClassCount = len(oClasses)
      oClasses = [f"{x:^7}" for x in oClasses]
    evaluator.class_count = nClassCount

    sClasses = " |".join(oClasses)
    nRepeat = 28 + (7+2)*evaluator.class_count
    print(f"                            |{sClasses}|", file=opened_file)
    print("-"*nRepeat, file=opened_file)
    print(f"Per Class Recall %          |{evaluator.format_series_as_pc(evaluator.recall[:])}|", file=opened_file)
    print(f"Per Class Precision %       |{evaluator.format_series_as_pc(evaluator.precision[:])}|", file=opened_file)
    print("-" * nRepeat, file=opened_file)
  # --------------------------------------------------------------------------------------------------------------
  def export_overall_metrics(self, evaluator, opened_file):
    print(f"Accuracy %                  :{evaluator.accuracy*100.0       :.3f}", file=opened_file)
    print(f"Average F1 Score %          :{evaluator.average_f1score*100.0:.3f}", file=opened_file)
    print(f"Weighted Average Recall %   :{evaluator.average_recall*100.0:.3f}", file=opened_file)
    print(f"Weighted Average Precision %:{evaluator.average_precision*100.0:.3f}", file=opened_file)
    if (evaluator.class_count == 2) and (evaluator.auc is not None):
      print(f"Area Under the Curve (AUC):{evaluator.auc:.4f}", file=opened_file)
    print("", file=opened_file)
  
  # --------------------------------------------------------------------------------------------------------------
  def export_metrics(self, evaluator, epoch=None):
    hprm = self.hprm
    nFoldNumber = experiment_fold_number(hprm)
    nRepeat = 80
    sMetricsFileName = self.experiment_fs.file(f'metrics_{experiment_name_with_fold(hprm)}.txt')
    with open(sMetricsFileName, "w") as oFile:
      print("="*nRepeat, file=oFile)
      if epoch is None:
        print(f'Experiment [{hprm["Experiment.Name"]}] fold {nFoldNumber} trained.', file=oFile)
      else:
        print(f'Experiment [{hprm["Experiment.Name"]}] fold {nFoldNumber} training in progress, best epoch {epoch}.', file=oFile)
      
      print("="*nRepeat, file=oFile)
      self.export_overall_metrics(evaluator, oFile)
      self.export_per_class_metrics(evaluator, oFile)
  # --------------------------------------------------------------------------------------------------------------
  def inspect_learned_params(self):
    oParams = dict()
    nClipCount = 0
    nTempCount = 0
    for nIndex, (name, tensor) in enumerate(self.model.state_dict().items()):
      if "clip" in name:
        nClipCount += 1
        oParams[f"clip{nClipCount}"] = tensor.detach().cpu().numpy()
      elif "temperature" in name:
        nTempCount += 1
        oParams[f"temp{nTempCount}"] = tensor.detach().cpu().numpy()
        
    print(oParams)
  # --------------------------------------------------------------------------------------------------------------
  def evaluation_report(self, all_labels, all_preds, logs: dict = None,is_showing_plots=False, class_names=None):
    oEvaluator = EvaluateClassification(all_labels, all_preds)
    oEvaluator.print_overall()
    oEvaluator.print_confusion_matrix()
    oEvaluator.class_names = class_names

    oPlot = PlotConfusionMatrix(oEvaluator.confusion_matrix)
    oPlot = oPlot.prepare().save(self.experiment_fs.file("Confusion Matrix.png"))
    if is_showing_plots:
      oPlot.show()

    if logs is not None:
      oTrainingLogPlot = PlotLearningCurve(logs, f'Experiment {self.hprm["Experiment.Name"]}')
      oTrainingLogPlot = oTrainingLogPlot.prepare(metric_key="accuracy").save(self.experiment_fs.file("LearningCurve_Accuracy.png"))
      if is_showing_plots:
        oTrainingLogPlot.show()

      oTrainingLogPlot = PlotLearningCurve(logs, f'Experiment {self.hprm["Experiment.Name"]}')
      oTrainingLogPlot = oTrainingLogPlot.prepare(metric_key="loss").save(self.experiment_fs.file("LearningCurve_Loss.png"))
      if is_showing_plots:
        oTrainingLogPlot.show()
    plt.close()
    self.inspect_learned_params()
    
    return oEvaluator
  
  # --------------------------------------------------------------------------------------------------------------
  def load(self, filename=None):
    if filename is None:
      filename = self.best_model_state_file

    oCheckpoint = torch.load(filename)
    self.model.load_state_dict(oCheckpoint)
    self.model.eval()
  
  # --------------------------------------------------------------------------------------------------------------
  def evaluate(self, class_names: dict=None, filename=None):
    if filename is None:
      filename = self.best_model_state_file


    oCheckpoint = torch.load(filename)
    self.model.load_state_dict(oCheckpoint)
    self.model.eval()

    all_preds, all_labels = [], []
    with torch.no_grad():
      # oDS
      for inputs, labels, ids in tqdm(self.dataset.vs.loader, desc="Final Evaluation"):
        inputs, labels = inputs.to(self.device), labels.to(self.device)
        outputs = self.model(inputs)
        _, preds = torch.max(outputs, 1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
    
    oLog: MLExperimentLog = MLExperimentLog(self.training_logs_file)
    oLog.load(self.experiment_fs)
    
    oEvaluator = self.evaluation_report(all_labels, all_preds, oLog.logs,is_showing_plots=False, class_names=class_names)
    # TODO: Keep epoch number for best
    self.export_metrics(oEvaluator)
  
  # --------------------------------------------------------------------------------------------------------------
  def export_model(self):
    nInputDim = self.hprm["Data.ModelInputSize"]
    cpu_device = torch.device("cpu")
    self.model.to(cpu_device)
    self.model.eval()
    tInput = torch.randn(self.hprm["Training.BatchSize"], 3, nInputDim, nInputDim, requires_grad=True)
    tInput.to(cpu_device)
    #TODO: Test
    torch.onnx.export(self.model, tInput, self.best_model_state_onnx_file,
                      export_params=True, opset_version=12, do_constant_folding=True,
                      input_names=['input'], output_names=[], dynamo=False,
                      dynamic_axes={
                          "input": {0: "batch"},
                          "output": {0: "batch"} }
                      )
    '''
    # [TEMP] Guidance code for exporting the model
    torch.onnx.export(self.model,  # model being run
                      oInput,  # model input (or a tuple for multiple inputs)
                      self.best_model_state_onnx_file,  # where to save the model
                      export_params=True,  # store the trained parameter weights inside the model file
                      opset_version=10,  # the ONNX version to export the model to
                      do_constant_folding=True,  # whether to execute constant folding for optimization
                      input_names=['modelInput'],  # the model's input names
                      output_names=['modelOutput'],  # the model's output names
                      dynamic_axes={'modelInput': {0: 'batch_size'},  # variable length axes
                                    'modelOutput': {0: 'batch_size'}})
    '''
    print('Model has been converted to ONNX')
  # --------------------------------------------------------------------------------------------------------------