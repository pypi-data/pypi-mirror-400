# Copyright (c) . All rights reserved.

from cycler import K
from mmyolo.models.backbones import YOLOv8CSPDarknet
from mmyolo.models.utils import make_divisible, make_round
from mmengine.registry import MODELS

from ..layers.yolo_bricks import C3K2, C2PSA, Conv, SPPF



@MODELS.register_module()
class YOLOv11CSPDarknet(YOLOv8CSPDarknet):
    """
    在YOLOv8 backbone基础上, 将csp layer换为C3K2, 最后再加上一个C2PSA
    """
    arch_settings = {
        'P5': [[64, 128, 2, 0.25, False, False], [128, 256, 2, 0.25, False, False],
               [256, 512, 2, 0.5, True, False], [512, 1024, 2, 0.5, True, True]],
    } # blocks different with v8

    def build_stem_layer(self):
         return Conv(
            self.input_channels,
            make_divisible(self.arch_setting[0][0], self.widen_factor),
            k=3,
            s=2)

    def build_stage_layer(self, stage_idx: int, setting: list) -> list:
        """Build a stage layer.

        Args:
            stage_idx (int): The index of a stage layer.
            setting (list): The architecture setting of a stage layer.
        """
        in_channels, out_channels, num_blocks, expand_ratio, c3k, use_spp = setting
        if self.widen_factor > 0.5: # foe xlm model size
            c3k = True
        in_channels = make_divisible(in_channels, self.widen_factor)
        out_channels = make_divisible(out_channels, self.widen_factor)
        num_blocks = make_round(num_blocks, self.deepen_factor)
        c3k_in_channels = out_channels
        if stage_idx <2:
            c3k_out_channels= out_channels*2
        else:
            c3k_out_channels= out_channels
        if stage_idx == 1 or stage_idx == 2:
            in_channels = out_channels
        stage = []
        conv_layer = Conv(
            in_channels,
            out_channels,
            k=3,
            s=2)
        stage.append(conv_layer)
        csp_layer = C3K2(
            c3k_in_channels,
            c3k_out_channels,
            num_blocks=num_blocks,
            expand_ratio=expand_ratio,
            c3k=c3k)
        stage.append(csp_layer)
        if use_spp: # last stage
            spp = SPPF(
                out_channels,
                out_channels,
                k=5,)
            stage.append(spp)
            c2psa = C2PSA(out_channels, out_channels, n=num_blocks)  
            stage.append(c2psa)
        return stage