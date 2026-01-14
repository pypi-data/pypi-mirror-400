def experiment_fold_number(hyperparams: dict):
  return hyperparams.get("Experiment.FoldNumber", hyperparams.get("Dataset.FoldNumber", 0))
  
def experiment_name_with_fold(hyperparams: dict):
  nFoldNumber = hyperparams.get("Experiment.FoldNumber", hyperparams.get("Dataset.FoldNumber", 0))
  sExperimentName = hyperparams.get("Experiment.Name", "noname")
  return f"{sExperimentName}.{nFoldNumber}"