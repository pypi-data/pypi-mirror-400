import torch
import torch.nn as nn
import torch.nn.functional as F
from ultralytics.nn.modules.conv import Conv
from ultralytics.nn.modules.block import C2f, Bottleneck, SPPF

class DualConv(nn.Module):
    def __init__(self, original_conv: Conv):
        super().__init__()
        self.conv = original_conv 
        self.weight2 = nn.Parameter(self.conv.conv.weight.clone())
        
        # Copy Ultralytics metadata required for the forward loop
        self.i = getattr(original_conv, 'i', 0)
        self.f = getattr(original_conv, 'f', -1)
        
        if self.conv.conv.bias is not None:
            self.bias2 = nn.Parameter(self.conv.conv.bias.clone())
        else:
            self.register_parameter('bias2', None)
        
        self.active = 1 

    def forward(self, x):
        if self.active == 1:
            return self.conv(x)
        
        # Manually apply CatDog weights through original BN and Act
        y2 = F.conv2d(
            x, self.weight2, self.bias2,
            self.conv.conv.stride, self.conv.conv.padding,
            self.conv.conv.dilation, self.conv.conv.groups
        )
        return self.conv.act(self.conv.bn(y2))

# --- BACKBONE CONVERSION ---

SKIP_PARENTS = (C2f, Bottleneck, SPPF)

def farida_convert_backbone_to_dual(human_model_internal, cat_model_internal):
    for (name, h_mod), (_, c_mod) in zip(human_model_internal.named_modules(), cat_model_internal.named_modules()):
        if isinstance(h_mod, Conv) and isinstance(c_mod, Conv):
            parent = human_model_internal
            skip = False
            parts = name.split(".")
            for p in parts[:-1]:
                parent = getattr(parent, p)
                if isinstance(parent, SKIP_PARENTS):
                    skip = True
                    break
            
            if skip or h_mod.conv.weight.shape != c_mod.conv.weight.shape:
                continue

            dual = DualConv(h_mod)
            dual.weight2.data.copy_(c_mod.conv.weight.data)
            
            target = human_model_internal
            for p in parts[:-1]:
                target = getattr(target, p)
            setattr(target, parts[-1], dual)
    return human_model_internal

def farida_activate_weight_set(model, mode):
    for m in model.modules():
        if isinstance(m, DualConv):

            m.active = mode

def run_dual_inference(dual_yolo , mode, names_dict, image_path, conf=0.25):
    """
    Switch weights and run prediction with correct metadata.
    """
    
    # 2. Update Model metadata
    dual_yolo.model.names = names_dict
    dual_yolo.model.nc = len(names_dict)
    
    try:
        # 3. Predict
        results = dual_yolo.predict(image_path, conf=conf)
        
        # 4. Sync Predictor (Fixes the CMD/Terminal printout)
        if hasattr(dual_yolo, 'predictor') and dual_yolo.predictor:
            dual_yolo.predictor.model.names = names_dict
            
        # 5. Sync Results (Fixes the labels on the pop-up window)
        if results:
            results[0].names = names_dict                
        return results
    except Exception as e:
        print(f"❌ Error in Mode {mode}: {e}")
        return None

