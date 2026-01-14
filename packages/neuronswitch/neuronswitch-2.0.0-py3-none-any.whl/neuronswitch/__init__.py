import torch
import torch.nn as nn
import torch.nn.functional as F
from ultralytics.nn.modules.conv import Conv
from ultralytics.nn.modules.block import C2f, Bottleneck, SPPF
from farida_DualYOLO import DualYOLO
from farida_DualConv import convert_backbone_to_dual_farida,activate_weight_set_farida
