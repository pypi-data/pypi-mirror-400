import math
from typing import List, Tuple, Union, Sequence
import torch
import torch.nn as nn
from torch import Tensor
from mmengine.model import BaseModule
from mmdet.utils import OptMultiConfig
from mmdet.models.utils import multi_apply
from mmyolo.models.utils import make_divisible
from mmengine.registry import MODELS
from ..layers.yolo_bricks import Proto, Conv, DWConv

@MODELS.register_module()
class YOLO11InsHeadModule(BaseModule):
    def __init__(self,
                 num_classes: int,
                 in_channels: Union[int, Sequence],
                 widen_factor: float = 1.0,
                 num_base_priors: int = 1,
                 mask_channels: int = 32,
                 proto_channels: int = 256,
                 featmap_strides: Sequence[int] = (8, 16, 32),
                 init_cfg: OptMultiConfig = None):
        super().__init__(init_cfg=init_cfg)
        self.num_classes = num_classes
        self.widen_factor = widen_factor
        self.mask_channels = mask_channels
        # self.num_out_attrib_with_proto = 5 + num_classes + mask_channels
        self.proto_channels = make_divisible(proto_channels, widen_factor)
        self.featmap_strides = featmap_strides
        self.num_out_attrib = 5 + self.num_classes
        self.num_levels = len(self.featmap_strides)
        self.num_base_priors = num_base_priors

        if isinstance(in_channels, int):
            self.in_channels = [make_divisible(in_channels, widen_factor)
                                ] * self.num_levels
        else:
            self.in_channels = [
                make_divisible(i, widen_factor) for i in in_channels
            ]

        self._init_layers()


    def _init_layers(self):
        """initialize conv layers in YOLOv5 Ins head."""
        reg_out_channels = max(16, self.in_channels[0] // 4)
        cls_out_channels = max(self.in_channels[0], self.num_classes)
        c4 = max(self.in_channels[0] // 4, self.num_classes)
        self.cv2 = nn.ModuleList()
        self.cv3 = nn.ModuleList()
        self.cv4 = nn.ModuleList()
        self.proto = Proto(
            self.in_channels[0],
            self.proto_channels,
            self.mask_channels)
        for i in range(self.num_levels):
            self.cv2.append(
                nn.Sequential(
                    Conv(self.in_channels[i], reg_out_channels, 3),
                    Conv(reg_out_channels, reg_out_channels, 3),
                    nn.Conv2d(reg_out_channels, 4 * self.num_base_priors, 1))
            )  # box
            self.cv3.append(
                    nn.Sequential(
                        nn.Sequential(DWConv(self.in_channels[i], self.in_channels[i], 3), Conv(self.in_channels[i], cls_out_channels, 1)),
                        nn.Sequential(DWConv(cls_out_channels, cls_out_channels, 3), Conv(cls_out_channels, cls_out_channels, 1)),
                        nn.Conv2d(cls_out_channels, self.num_classes * self.num_base_priors, 1),
                    )
                )  # cls
            self.cv4.append(nn.Sequential(Conv(self.in_channels[i], c4, 3), Conv(c4, c4, 3), nn.Conv2d(c4, self.mask_channels * self.num_base_priors, 1)))

    def init_weights(self):
        """Initialize the bias of YOLOv5 head."""
        super().init_weights()
        for c2, c3, c4, s in zip(self.cv2, self.cv3, self.cv4, self.featmap_strides):  # from

            c2[-1].bias.data[:] = 1.0 # box
            c3[-1].bias.data[:self.num_classes] = math.log(
                5 / self.num_classes / (640 / s)**2)
            c4[-1].bias.data[:] = 1.0 # mask


    def forward(self, x: Tuple[Tensor]) -> Tuple[List]:
        """Forward features from the upstream network.

        Args:
            x (Tuple[Tensor]): Features from the upstream network, each is
                a 4D-tensor.
        Returns:
            Tuple[List]: A tuple of multi-level classification scores, bbox
            predictions, objectnesses, and mask predictions.
        """
        mask_protos = self.proto(x[0])  # mask protos (b, n, 160, 160)
        cls_scores, bbox_preds, objectnesses, coeff_preds = multi_apply(
            self.forward_single, x, self.cv2, self.cv3, self.cv4)
        
        return cls_scores, bbox_preds, objectnesses, coeff_preds, mask_protos

    def forward_single(
            self, x: Tensor,
            cv2: nn.Module, cv3: nn.Module, cv4: nn.Module) -> Tuple[Tensor, Tensor, Tensor, Tensor]:

        """Forward feature of a single scale level."""

        bs, _, ny, nx = x.shape
        cls_score = cv3(x).view(bs, -1, ny, nx)  # (b, 3*c, ny, nx)
        c = cls_score.shape[1] // self.num_base_priors
        bbox_pred = cv2(x).view(bs, -1, ny, nx)  # (b, 12, ny, nx)
        objectness = [cls_score[:, i*c: (i+1)*c].max(dim=1, keepdim=True).values for i in range(self.num_base_priors)]
        objectness = torch.concat(objectness, dim=1) # (b, 3, ny, nx)
        coeff_pred = cv4(x).view(bs, -1, ny, nx)  # (b, _, ny, nx)

        return cls_score, bbox_pred, objectness, coeff_pred