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
from typing import Dict, Type, Any

from radnn.models import ModelHyperparams, ModelInfo
from radnn.errors import *


# ======================================================================================================================
class RadnnModel(type):
  def __new__(mcls, name: str, bases: tuple[type, ...], ns: dict[str, Any]):
    cls = super().__new__(mcls, name, bases, ns)
    # Avoid registering the abstract base itself
    if name != "ModelBuildAdapter":
      key = ns.get("NAME", name)  # optional override via class attribute NAME
      if key in ModelFactory.registry:
        raise KeyError(f"The model '{key}' has been alrady registered ")
      ModelFactory.registry[key] = cls
    return cls


# ======================================================================================================================
class ModelBuildAdapter(metaclass=RadnnModel):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, **kwargs):
    self.builder_kwargs = kwargs
    self.hprm: dict | None = self.builder_kwargs.get("hprm", None)
    self.hyperparams: ModelHyperparams | None = self.builder_kwargs.get("model_hyperparams", None)
    if self.hyperparams is not None:
      self.hprm = self.hyperparams.hprm
    self.model = None
    self.model_info: ModelInfo | None = None
  
  # --------------------------------------------------------------------------------------------------------------------
  def build(self, **kwargs: Any):
    raise NotImplementedError
  # --------------------------------------------------------------------------------------------------------------------


# ======================================================================================================================
class ModelFactory(object):
  registry: Dict[str, Type["ModelBuildAdapter"]] = {}
  
  @classmethod
  def produce(cls, hyperparams: dict, **kwargs: Any) -> ModelBuildAdapter:
    oModelBuilder = None
    oModelHyperparams: ModelHyperparams = ModelHyperparams.from_dict(hyperparams)
    assert oModelHyperparams.input_dims is not None, HPARAMS_DATA_INPUT_DIMS
    assert len(oModelHyperparams.input_dims) > 0, HPARAMS_DATA_INPUT_DIMS
    sModelAdapterKey = oModelHyperparams.base_name + "BuildAdapter"
    if sModelAdapterKey in cls.registry:
      cBuilder = ModelFactory.registry[sModelAdapterKey]
      oModelBuilder = cBuilder(model_hyperparams=oModelHyperparams)
      oModel = oModelBuilder.build(hprm=hyperparams, **kwargs)
      oModelBuilder.model_info = ModelInfo(oModel, oModelHyperparams)
    
    return oModelBuilder
# ======================================================================================================================
