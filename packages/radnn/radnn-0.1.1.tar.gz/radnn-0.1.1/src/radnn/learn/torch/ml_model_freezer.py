class MLModelFreezer(object):
  def __init__(self, model, hyperparams):
    self.model = model
    self.hyperparams = hyperparams
    self.model_name = self.hyperparams["Model.Name"]
    self.variant = self.hyperparams.get("Training.FineTuning.Freeze", None)
    
    if self.model_name == "MobileNet_V3_Large_Weights.IMAGENET1K_V1":
      self.mobilenet_frozen()
    elif self.model_name == "resnet50_Weights.IMAGENET1K_V1":
      self.resnet50_frozen()
    elif self.model_name == "efficientnet_b0_Weights.IMAGENET1K_V1":
      self.efficientnet_frozen()
    elif self.model_name == "convnext_tiny_Weights.IMAGENET1K_V1":
      self.convnext_frozen()
    elif self.model_name == "beitv2_large_patch16_224.in1k_ft_in22k_in1k":
      self.beitv2_frozen_2()
      
  def freeze_batch_norm(self):
    oNamedParams = list(iter(self.model .named_parameters()))
    for nIndex, oTuple in enumerate(oNamedParams):
      name, p = oTuple
      if ".bn" in name:
        p.requires_grad = False
  
  def freeze_layer_norm(self):
    oNamedParams = list(iter(self.model .named_parameters()))
    for nIndex, oTuple in enumerate(oNamedParams):
      name, p = oTuple
      if (".norm" in name) or (".gamma" in name) or (".beta" in name) :
        p.requires_grad = False
    
  def freeze_block(self, module, exclude_normalization=False):
    oParams = list(iter(module.parameters()))
    oNamedParams = list(iter(module.named_parameters()))
    for nIndex, oTuple in enumerate(oNamedParams):
      name, p = oTuple
      p = oParams[nIndex]
      bContinue = True
      if exclude_normalization:
        bContinue = not ".bn" in name
      if bContinue:
        p.requires_grad = False
  
  def mobilenet_frozen(self):
    """
    torchvision.mobilenet_v3_large has:
      model.features: Sequential([...])
      model.classifier: Sequential([...])

    We'll freeze by coarse slices of `features`.
    The exact indices can differ slightly across torchvision versions, but this is stable enough:
      - features[0] is stem
      - features[1:-1] are inverted residual blocks
      - features[-1] is final 1x1 conv block before pooling/classifier
    """
    if self.variant is None:
      return

    if not hasattr(self.model, "features"):
      return

    feats = self.model.features
    n = len(feats)

    # Define slices (roughly early/mid/late)
    # Stem
    if 0 in self.variant:
      self.freeze_block(feats[0])

    # Early inverted residual blocks
    if 1 in self.variant:
      end = max(2, n // 4)
      self.freeze_block(feats[1:end])

    # Mid blocks
    if 2 in self.variant:
      start = max(1, n // 4)
      end = max(start + 1, n // 2)
      self.freeze_block(feats[start:end])

    # Late blocks (excluding last conv)
    if 3 in self.variant:
      start = max(1, n // 2)
      end = max(start + 1, n - 1)
      self.freeze_block(feats[start:end])


      
  
  def resnet50_frozen(self):
    if self.variant is None:
      return
    
    self.freeze_batch_norm()
    
    if 0 in self.variant:
      # Stem
      self.freeze_block(self.model.step_conv)
      self.freeze_block(self.model.bn1)
      
    if 1 in self.variant:
      # First block of multiple conv layers
      self.freeze_block(self.model.block1)

    if 2 in self.variant:
      self.freeze_block(self.model.block2)

    if 3 in self.variant:
      self.freeze_block(self.model.block3)

    if 4 in self.variant:
      # Freezing all layers will train only the classification head
      self.freeze_block(self.model.layer4)


  def efficientnet_frozen(self):
    """
    torchvision.efficientnet_b0 has:
      model.features: Sequential of stem + stages + head conv
      model.classifier

    Commonly len(features) == 9 in torchvision:
      0 stem
      1..7 MBConv/FusedMBConv stages
      8 head conv
    We'll freeze in coarse groups.
    """
    if self.variant is None:
      return

    if not hasattr(self.model, "features"):
      return

    feats = self.model.features
    n = len(feats)

    if n == 0:
      return

    # Stem
    if 0 in self.variant:
      self.freeze_block(feats[0])

    # Early stages
    if 1 in self.variant:
      # typically features[1:3]
      self.freeze_block(feats[1:min(3, n)])

    # Mid stages
    if 2 in self.variant:
      # typically features[3:5]
      self.freeze_block(feats[min(3, n):min(5, n)])

    # Late stages
    if 3 in self.variant:
      # typically features[5:7]
      self.freeze_block(feats[min(5, n):min(7, n)])



  def convnext_frozen(self):
    """
    torchvision.convnext_tiny has:
      model.features: Sequential of 8 modules:
        0 stem
        1 stage1
        2 downsample1
        3 stage2
        4 downsample2
        5 stage3
        6 downsample3
        7 stage4
      model.classifier
    We'll freeze stem/stages (and their downsample ops together).
    """
    if self.variant is None:
      return

    if not hasattr(self.model, "features"):
      return

    feats = self.model.features
    n = len(feats)
    if n < 2:
      return

    # Stem
    if 0 in self.variant:
      self.freeze_block(feats[0])

    # Stage 1 (+ downsample after it if present)
    if 1 in self.variant:
      if n > 1: self.freeze_block(feats[1])
      if n > 2: self.freeze_block(feats[2])

    # Stage 2 (+ downsample)
    if 2 in self.variant:
      if n > 3: self.freeze_block(feats[3])
      if n > 4: self.freeze_block(feats[4])

    # Stage 3 (+ downsample)
    if 3 in self.variant:
      if n > 5: self.freeze_block(feats[5])
      if n > 6: self.freeze_block(feats[6])
  
  
  def beitv2_frozen(self):
    if self.variant is None:
      return
    
    freeze_patch_embed = 0 in self.variant
    # ----------------
    
    if freeze_patch_embed:
      self.freeze_block(self.model.patch_embed)

    blocks = self.model.blocks
    for i, block in enumerate(blocks):
      if i in self.variant:
        self.freeze_block(block)
    
  
  # -------------------------
  # BEiT v2 (timm or HuggingFace)
  # -------------------------
  def beitv2_frozen_2(self):
    """
    Supports:
      - timm-style: model.patch_embed, model.blocks (list/ModuleList), model.norm
      - HF-style:   model.beit.embeddings, model.beit.encoder.layer, model.beit.layernorm

    variant meaning (coarse, stage-like):
      0: freeze patch embedding (+ early norms if present)
      1: freeze first quarter of transformer blocks
      2: freeze first half
      3: freeze first 3/4
      4: freeze all blocks (train head only)

    If you prefer "freeze exact N blocks", you can pass an int in hyperparams instead of a list.
    """
    if self.variant is None:
      return

    # Allow variant to be an int: freeze first N blocks (and patch embed)
    if isinstance(self.variant, int):
      n_blocks_to_freeze = self.variant
      self._beit_freeze_first_n_blocks(n_blocks_to_freeze, freeze_patch_embed=True)
      return

    # Otherwise assume list-like stages
    vset = set(self.variant)

    self.freeze_layer_norm()
    
    # Try timm-style first
    if hasattr(self.model, "blocks"):
      blocks = self.model.blocks
      num_blocks = len(blocks)

      # 0: patch embedding / stem
      if 0 in vset:
        if hasattr(self.model, "patch_embed"):
          self.freeze_block(self.model.patch_embed)
        # some timm models have pos_embed / cls_token as params; those don't need freezing

      # Helper: freeze first k blocks
      def freeze_first_k(k):
        for b in blocks[:max(0, min(k, num_blocks))]:
          self.freeze_block(b)

      # Stage mapping
      if 1 in vset:
        freeze_first_k(max(1, num_blocks // 4))
      if 2 in vset:
        freeze_first_k(max(1, num_blocks // 2))
      if 3 in vset:
        freeze_first_k(max(1, (3 * num_blocks) // 4))
      

    # Fall back to HuggingFace-style
    elif hasattr(self.model, "beit"):
      beit = self.model.beit

      if 0 in vset and hasattr(beit, "embeddings"):
        self.freeze_block(beit.embeddings)

      layers = None
      if hasattr(beit, "encoder") and hasattr(beit.encoder, "layer"):
        layers = beit.encoder.layer

      if layers is not None:
        num_blocks = len(layers)

        def freeze_first_k(k):
          for b in layers[:max(0, min(k, num_blocks))]:
            self.freeze_block(b)

        if 1 in vset:
          freeze_first_k(max(1, num_blocks // 4))
        if 2 in vset:
          freeze_first_k(max(1, num_blocks // 2))
        if 3 in vset:
          freeze_first_k(max(1, (3 * num_blocks) // 4))

    

  def _beit_freeze_first_n_blocks(self, n_blocks_to_freeze: int, freeze_patch_embed: bool = True):
    # timm-style
    if hasattr(self.model, "blocks"):
      if freeze_patch_embed and hasattr(self.model, "patch_embed"):
        self.freeze_block(self.model.patch_embed)
      for b in self.model.blocks[:max(0, n_blocks_to_freeze)]:
        self.freeze_block(b)
      if hasattr(self.model, "norm") and n_blocks_to_freeze >= len(self.model.blocks):
        self.freeze_block(self.model.norm)
      return

    # HF-style
    if hasattr(self.model, "beit"):
      beit = self.model.beit
      if freeze_patch_embed and hasattr(beit, "embeddings"):
        self.freeze_block(beit.embeddings)
      if hasattr(beit, "encoder") and hasattr(beit.encoder, "layer"):
        for b in beit.encoder.layer[:max(0, n_blocks_to_freeze)]:
          self.freeze_block(b)
      if hasattr(beit, "layernorm") and hasattr(beit, "encoder") and hasattr(beit.encoder, "layer"):
        if n_blocks_to_freeze >= len(beit.encoder.layer):
          self.freeze_block(beit.layernorm)
  