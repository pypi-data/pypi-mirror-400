from torch.optim.lr_scheduler import LRScheduler

class StairCaseLR(LRScheduler):
  def __init__(self, optimizer, setup, last_epoch=-1):
    self.setup = sorted(setup, key=lambda x: x[0])
    self.lrs = [nLR for nEpochIndex, nLR in self.setup]
    self.lrs_count = len(self.lrs)
    super().__init__(optimizer, last_epoch)
  
  def get_lr(self):
    epoch = max(self.last_epoch, 0)
    
    lr = self.setup[0][1]
    for m, candidate_lr in self.setup:
      if epoch >= m:
        lr = candidate_lr
      else:
        break
        
    return [lr for _ in self.optimizer.param_groups]
    
