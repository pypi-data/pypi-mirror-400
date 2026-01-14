import torch
import torch.nn as nn

class DualYOLO(nn.Module):
    def __init__(self, ultralytics_model, head1, head2):
        super().__init__()
        # Internal layers and skip-connection indices
        self.model_layers = ultralytics_model.model[:-1]
        self.save = ultralytics_model.save
        self.head1 = head1
        self.head2 = head2
        self.mode = 1
        
        # Required Metadata for Ultralytics Engine
        self.names = ultralytics_model.names
        self.nc = len(self.names)
        self.stride = ultralytics_model.stride
        self.task = 'detect'
        self.yaml = ultralytics_model.yaml
        self.pt = True 

    def forward(self, x, *args, **kwargs):
        y = []  # Feature cache for skip connections
        for m in self.model_layers:
            if m.f != -1:  # Handle connections from other layers (Concat/Skip)
                if isinstance(m.f, int):
                    x = y[m.f]
                else:
                    x = [x if j == -1 else y[j] for j in m.f]
            
            x = m(x)
            y.append(x if m.i in self.save else None)

        # FIX: Detection head expects a list of feature maps from indices like [15, 18, 21]
        target_head = self.head1 if self.mode == 1 else self.head2
        head_inputs = [y[j] for j in target_head.f]
        
        return target_head(head_inputs)

    def fuse(self, *args, **kwargs):
        return self


