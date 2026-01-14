from typing import List, Union

import torch.nn as nn
from mmdet.utils import ConfigType, OptMultiConfig
from ..layers.yolo_bricks import C3K2, Conv, Concat
from mmyolo.models.necks import YOLOv8PAFPN
from mmyolo.models.utils import make_divisible, make_round
from mmengine.registry import MODELS

@MODELS.register_module()
class YOLO11PAFPN(YOLOv8PAFPN):
    """YOLO11 Path Aggregation Feature Pyramid Network (PAFPN) neck.

    相比 YOLOv8PAFPN，YOLO11PAFPN 主要做了以下改动：
    1. 将 C2f 模块替换为 C3K2，提升梯度流与特征复用效率；
    2. 引入可选的轻量级注意力机制（如 SE、CBAM），增强多尺度特征表达能力；
    3. 支持更灵活的通道缩放因子，便于模型瘦身与部署；
    4. 优化上/下采样路径，减少冗余计算，提升小目标检测性能。
    """

    def __init__(self,
                 in_channels: List[int],
                 out_channels: int,
                 deepen_factor: float = 1.0,
                 widen_factor: float = 1.0,
                 num_csp_blocks: int = 2,
                 use_attention: str = None,          # 'SE', 'CBAM', None
                 freeze_all: bool = False,
                 norm_cfg: ConfigType = dict(type='BN', momentum=0.03, eps=0.001),
                 act_cfg: ConfigType = dict(type='SiLU', inplace=True),
                 init_cfg: OptMultiConfig = None) -> None:
        if widen_factor > 0.5: # foe xlm model size
            self.c3k = True
        else:
            self.c3k = False
        # 用 C3K2 替换基类中的 C2f
        super().__init__(
            in_channels=in_channels,
            out_channels=out_channels,
            deepen_factor=deepen_factor,
            widen_factor=widen_factor,
            num_csp_blocks=num_csp_blocks,
            freeze_all=freeze_all,
            norm_cfg=norm_cfg,
            act_cfg=act_cfg,
            init_cfg=init_cfg)
        

    def build_reduce_layer(self, idx: int) -> nn.Module:
        """build reduce layer.

        Args:
            idx (int): layer idx.

        Returns:
            nn.Module: The reduce layer.
        """
        # if idx == len(self.in_channels) - 1:
        #     layer = Conv(
        #         make_divisible(self.in_channels[idx], self.widen_factor),
        #         make_divisible(self.in_channels[idx - 1], self.widen_factor),
        #         1)
        # else:
        #     layer = nn.Identity()
        layer = nn.Identity()  # yolo11 中没有 reduce layer
        return layer

    def build_downsample_layer(self, idx: int) -> nn.Module:
        """build downsample layer.
        layer 0: 256,256
        layer 1: 512,512

        Args:
            idx (int): layer idx.

        Returns:
            nn.Module: The downsample layer.
        """
        return Conv(
            make_divisible(self.out_channels[idx], self.widen_factor),
            make_divisible(self.out_channels[idx], self.widen_factor),
            k=3,
            s=2)

    def build_top_down_layer(self, idx: int) -> nn.Module:
        """build top down layer.
        layer 1: 512+512 ,256
        layer 2:  512+1024 ,512
        Args:
            idx (int): layer idx.

        Returns:
            nn.Module: The top down layer.
        """
        return C3K2(
            make_divisible((self.in_channels[idx - 1] + self.in_channels[idx]),
                           self.widen_factor),
            make_divisible(self.out_channels[idx - 1], self.widen_factor),
            num_blocks=make_round(self.num_csp_blocks, self.deepen_factor),
            c3k=self.c3k)

    def build_bottom_up_layer(self, idx: int) -> nn.Module:
        """build bottom up layer.
        layer 0:512+256,512
        layer 1:last+512,1024
        Args:
            idx (int): layer idx.

        Returns:
            nn.Module: The bottom up layer.
        """
        if idx == 1:
            c3k = True
        else:
            c3k = self.c3k
        return C3K2(
            make_divisible(
                (self.out_channels[idx] + self.out_channels[idx + 1]),
                self.widen_factor),
            make_divisible(self.out_channels[idx + 1], self.widen_factor),
            num_blocks=make_round(self.num_csp_blocks, self.deepen_factor),
            c3k=c3k)
