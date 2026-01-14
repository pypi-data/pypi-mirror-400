# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2018-2026 Pantelis I. Kaplanoglou

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

# .......................................................................................
from radnn import FileStore
from radnn.data.structs import Tree, TreeNode

from torchinfo import ModelStatistics, summary
from torchinfo.layer_info import LayerInfo
from .model_hyperparams import ModelHyperparams


class ModelInfo(object):
  def __init__(self, model=None, hyperparams: ModelHyperparams | dict = None, depth=6):
    self.model = model
    self.hyperparams = hyperparams
    if isinstance(hyperparams, dict):
      self.hyperparams = ModelHyperparams.from_dict(hyperparams)
    self.model_tree: Tree = None
    
    if self.model is not None:
      nInputDims = tuple([1, hyperparams.input_channels] + hyperparams.input_resolution)
      self.summary: ModelStatistics = summary(model, nInputDims, device='cpu', depth=depth)
      self.build_tree()
  
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def filename(self):
    return f'{self.hyperparams.model_name}_{str(self.hyperparams.input_dims).replace(", ", "x")[1:-1]}_cls{str(self.hyperparams.class_count)}'
  
  # --------------------------------------------------------------------------------------------------------------------
  def save(self, fs: str | FileStore):
    if isinstance(fs, str):
      fs = FileStore(fs)
    fs.artifact(self.filename + ".pkl").save(self.summary, is_overwriting=True)
    with open(fs.file(self.filename + ".txt"), "w", encoding="utf-8") as oFile:
      print(self.summary, file=oFile)
    
  # --------------------------------------------------------------------------------------------------------------------
  def load(self, fs: str | FileStore):
    bIsLoaded = False
    if isinstance(fs, str):
      fs = FileStore(fs)
    self.summary = fs.artifact(self.filename + ".pkl").load()
    bIsLoaded = self.summary is not None
    if bIsLoaded:
      self.build_tree()
      '''
      oNodeList = self.model_tree.traverse_depth_first()
      for oNode in oNodeList:
        print(oNode.path)
      '''
    return bIsLoaded
  
  # --------------------------------------------------------------------------------------------------------------------
  def build_tree(self):
    def recurse_build_subtree(source_node: LayerInfo, target_node: TreeNode):
      for nIndex, oSourceChild in enumerate(source_node.children):
        sNodeName = f"{oSourceChild.class_name}: {oSourceChild.depth}-{oSourceChild.depth_index}"
        oTargetChild: TreeNode = target_node.new_child(sNodeName)
        oTargetChild.value = oSourceChild
        recurse_build_subtree(oSourceChild, oTargetChild)
    
    self.model_tree = Tree()
    recurse_build_subtree(self.summary.summary_list[0], self.model_tree.root)
  # --------------------------------------------------------------------------------------------------------------------
