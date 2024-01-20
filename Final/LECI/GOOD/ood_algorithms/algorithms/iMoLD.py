# -*- coding: utf-8 -*-
# @Filename: iMoLD.py
# @Date: 2023/12/21 15:12
# @Author: LEO XU
# @Email: leoxc1571@163.com
from typing import Tuple

from torch import Tensor
from torch_geometric.data import Batch

from GOOD import register
from GOOD.utils.config_reader import Union, CommonArgs, Munch
from GOOD.utils.initial import reset_random_seed
from GOOD.utils.train import at_stage
from .BaseOOD import BaseOODAlg
from collections import OrderedDict
import torch.nn.functional as F

def set_requires_grad(nets, requires_grad=False):
    """Set requies_grad=Fasle for all the networks to avoid unnecessary computations
    Parameters:
        nets (network list)   -- a list of networks
        requires_grad (bool)  -- whether the networks require gradients or not
    """
    if not isinstance(nets, list):
        nets = [nets]
    for net in nets:
        if net is not None:
            for param in net.parameters():
                param.requires_grad = requires_grad

def simsiam_loss(causal_rep, mix_rep):
    causal_rep = causal_rep.detach()
    causal_rep = F.normalize(causal_rep, dim=1)
    mix_rep = F.normalize(mix_rep, dim=1)
    return -(causal_rep * mix_rep).sum(dim=1).mean()

@register.ood_alg_register
class iMoLD(BaseOODAlg):
    def __init__(self, config: Union[CommonArgs, Munch]):
        super(iMoLD, self).__init__(config)
        self.rep_out = None
        self.causal_out = None
        self.spu_out = None
        self.step = 0

    def stage_control(self, config):
        if config.train.epoch % 4 in range(1):
            # train separator
            set_requires_grad([self.model.separator], requires_grad=True)
            set_requires_grad([self.model.encoder], requires_grad=False)
        else:
            # train classifier
            set_requires_grad([self.model.separator], requires_grad=False)
            set_requires_grad([self.model.encoder], requires_grad=True)

        if self.stage == 0 and at_stage(1, config):
            reset_random_seed(config)
            self.stage = 1

    def output_postprocess(self, model_output: Tensor, **kwargs) -> Tensor:
        r"""
        Process the raw output of model; apply the linear classifier

        Args:
            model_output (Tensor): model raw output

        Returns (Tensor):
            model raw predictions with the linear classifier applied

        """
        self.c_logit, self.c_f, self.s_f, self.cmt_loss, self.reg_loss = model_output
        return self.c_logit

    def loss_calculate(self, raw_pred: Tensor, targets: Tensor, mask: Tensor, node_norm: Tensor,
                       config: Union[CommonArgs, Munch]) -> Tensor:


        loss = config.metric.loss_func(raw_pred, targets, reduction='none') * mask
        return loss

    def loss_postprocess(self, loss: Tensor, data: Batch, mask: Tensor, config: Union[CommonArgs, Munch],
                         **kwargs) -> Tensor:
        self.spec_loss = OrderedDict()
        mix_f = self.model.mix_cs_proj(self.c_f, self.s_f)
        inv_loss = simsiam_loss(self.c_f, mix_f)
        # inv_w: lambda_1
        # reg_w: lambda_2

        self.mean_loss = loss.sum() / mask.sum()
        loss = self.mean_loss + self.cmt_loss + config.ood.extra_param[0] * inv_loss + config.ood.extra_param[1] * self.reg_loss
        return loss
