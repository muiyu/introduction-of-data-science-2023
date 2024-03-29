# -*- coding: utf-8 -*-
# @Filename: iMoLDGNN.py
# @Date: 2023/12/21 15:13
# @Author: LEO XU
# @Email: leoxc1571@163.com
import torch
from torch import nn
import torch.nn.functional as F
from torch_geometric.nn import global_mean_pool
from torch_scatter import scatter_add, scatter_mean
import numpy as np

from GOOD.networks.models.GINs import GINFeatExtractor
from GOOD.networks.models.GINvirtualnode import vGINFeatExtractor

from vector_quantize_pytorch import VectorQuantize
# from .vq_update import VectorQuantize

from torch_geometric.nn import MessagePassing
from torch_geometric.utils import degree
from torch_geometric.nn import global_mean_pool, global_add_pool


class MLP(nn.Module):
    """MLP with linear output"""

    def __init__(self, num_layers, input_dim, hidden_dim, output_dim):
        """MLP layers construction

        Paramters
        ---------
        num_layers: int
            The number of linear layers
        input_dim: int
            The dimensionality of input features
        hidden_dim: int
            The dimensionality of hidden units at ALL layers
        output_dim: int
            The number of classes for prediction

        """
        super(MLP, self).__init__()
        self.linear_or_not = True  # default is linear model
        self.num_layers = num_layers
        self.output_dim = output_dim

        if num_layers < 1:
            raise ValueError("number of layers should be positive!")
        elif num_layers == 1:
            # Linear model
            self.linear = nn.Linear(input_dim, output_dim)
        else:
            # Multi-layer model
            self.linear_or_not = False
            self.linears = torch.nn.ModuleList()
            self.batch_norms = torch.nn.ModuleList()

            self.linears.append(nn.Linear(input_dim, hidden_dim))
            for _ in range(num_layers - 2):
                self.linears.append(nn.Linear(hidden_dim, hidden_dim))
            self.linears.append(nn.Linear(hidden_dim, output_dim))

            for _ in range(num_layers - 1):
                self.batch_norms.append(nn.BatchNorm1d(hidden_dim))

    def forward(self, x):
        if self.linear_or_not:
            # If linear model
            return self.linear(x)
        else:
            # If MLP
            h = x
            for i in range(self.num_layers - 1):
                h = F.relu(self.batch_norms[i](self.linears[i](h)))
            return self.linears[-1](h)


# GIN convolution along the graph structure
class GINConv(MessagePassing):
    def __init__(self, emb_dim):
        '''
            emb_dim (int): node embedding dimensionality
        '''

        super(GINConv, self).__init__(aggr="add")

        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(emb_dim, 2 * emb_dim),
            torch.nn.BatchNorm1d(2 * emb_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(2 * emb_dim, emb_dim)
        )
        self.eps = torch.nn.Parameter(torch.Tensor([0]))
        # if datatype == 'ogb':
        #     self.bond_encoder = BondEncoder(emb_dim=emb_dim)
        # else:
        self.bond_encoder = MLP(num_layers=1, input_dim=10, output_dim=emb_dim, hidden_dim=emb_dim)

    def forward(self, x, edge_index, edge_attr):
        edge_embedding = self.bond_encoder(edge_attr)
        out = self.mlp(
            (1 + self.eps) * x +
            self.propagate(edge_index, x=x, edge_attr=edge_embedding)
        )

        return out

    def message(self, x_j, edge_attr):
        return F.relu(x_j + edge_attr)

    def update(self, aggr_out):
        return aggr_out


# GCN convolution along the graph structure


class GCNConv(MessagePassing):
    def __init__(self, emb_dim):
        super(GCNConv, self).__init__(aggr='add')

        self.linear = torch.nn.Linear(emb_dim, emb_dim)
        self.root_emb = torch.nn.Embedding(1, emb_dim)
        # if datatype == 'ogb':
        #     self.bond_encoder = BondEncoder(emb_dim=emb_dim)
        # else:
        self.bond_encoder = MLP(num_layers=1, input_dim=10, output_dim=emb_dim, hidden_dim=emb_dim)

    def forward(self, x, edge_index, edge_attr):
        x = self.linear(x)
        edge_embedding = self.bond_encoder(edge_attr)

        row, col = edge_index

        # edge_weight = torch.ones((edge_index.size(1), ), device=edge_index.device)
        deg = degree(row, x.size(0), dtype=x.dtype) + 1
        deg_inv_sqrt = deg.pow(-0.5)
        deg_inv_sqrt[deg_inv_sqrt == float('inf')] = 0

        norm = deg_inv_sqrt[row] * deg_inv_sqrt[col]

        return self.propagate(
            edge_index, x=x, edge_attr=edge_embedding, norm=norm
        ) + F.relu(x + self.root_emb.weight) * 1. / deg.view(-1, 1)

    def message(self, x_j, edge_attr, norm):
        return norm.view(-1, 1) * F.relu(x_j + edge_attr)

    def update(self, aggr_out):
        return aggr_out


# GNN to generate node embedding
class GNN_node(torch.nn.Module):
    """
    Output:
        node representations
    """

    def __init__(
            self, num_layer, emb_dim, drop_ratio=0.5,
            JK="last", residual=False, gnn_type='gin'
    ):
        '''
            emb_dim (int): node embedding dimensionality
            num_layer (int): number of GNN message passing layers

        '''

        super(GNN_node, self).__init__()
        self.num_layer = num_layer
        self.drop_ratio = drop_ratio
        self.JK = JK
        # add residual connection or not
        self.residual = residual

        # if self.num_layer < 2:
        #     raise ValueError("Number of GNN layers must be greater than 1.")
        # if datatype == 'ogb':
        #     self.atom_encoder = AtomEncoder(emb_dim)
        # else:
        self.atom_encoder = MLP(input_dim=39, hidden_dim=emb_dim, output_dim=emb_dim, num_layers=2)

        # List of GNNs
        self.convs = torch.nn.ModuleList()
        self.batch_norms = torch.nn.ModuleList()

        for layer in range(num_layer):
            if gnn_type == 'gin':
                self.convs.append(GINConv(emb_dim))
            elif gnn_type == 'gcn':
                self.convs.append(GCNConv(emb_dim))
            else:
                raise ValueError(
                    'Undefined GNN type called {}'.format(gnn_type))

            self.batch_norms.append(torch.nn.BatchNorm1d(emb_dim))

    def forward(self, *argv):

        # computing input node embedding
        if len(argv) == 4:
            x, edge_index, edge_attr, batch = argv[0], argv[1], argv[2], argv[3]
        elif len(argv) == 1:
            batched_data = argv[0]
            x, edge_index = batched_data.x, batched_data.edge_index
            edge_attr, batch = batched_data.edge_attr, batched_data.batch
        else:
            raise ValueError("unmatched number of arguments.")

        h_list = [self.atom_encoder(x)]
        for layer in range(self.num_layer):

            h = self.convs[layer](h_list[layer], edge_index, edge_attr)
            h = self.batch_norms[layer](h)

            if layer == self.num_layer - 1:
                # remove relu for the last layer
                h = F.dropout(h, self.drop_ratio, training=self.training)
                # h = h
            else:
                h = F.dropout(
                    F.relu(h), self.drop_ratio, training=self.training
                )

            if self.residual:
                h += h_list[layer]

            h_list.append(h)

        # Different implementations of Jk-concat
        if self.JK == "last":
            node_representation = h_list[-1]
        elif self.JK == "sum":
            node_representation = 0
            for layer in range(self.num_layer + 1):
                node_representation += h_list[layer]

        return node_representation


# Virtual GNN to generate node embedding
class GNN_node_Virtualnode(torch.nn.Module):
    """
    Output:
        node representations
    """

    def __init__(
            self, num_layer, emb_dim, drop_ratio=0.5,
            JK="last", residual=False, gnn_type='gin'
    ):
        '''
            emb_dim (int): node embedding dimensionality
        '''

        super(GNN_node_Virtualnode, self).__init__()
        self.num_layer = num_layer
        self.drop_ratio = drop_ratio
        self.JK = JK
        # add residual connection or not
        self.residual = residual

        if self.num_layer < 2:
            raise ValueError("Number of GNN layers must be greater than 1.")

        # self.atom_encoder = AtomEncoder(emb_dim)
        # if datatype == 'ogb':
        #     self.atom_encoder = AtomEncoder(emb_dim)
        # else:
        self.atom_encoder = MLP(input_dim=39, hidden_dim=emb_dim, output_dim=emb_dim, num_layers=2)


        # set the initial virtual node embedding to 0.
        self.virtualnode_embedding = torch.nn.Embedding(1, emb_dim)
        torch.nn.init.constant_(self.virtualnode_embedding.weight.data, 0)

        # List of GNNs
        self.convs = torch.nn.ModuleList()
        # batch norms applied to node embeddings
        self.batch_norms = torch.nn.ModuleList()

        # List of MLPs to transform virtual node at every layer
        self.mlp_virtualnode_list = torch.nn.ModuleList()

        for layer in range(num_layer):
            if gnn_type == 'gin':
                self.convs.append(GINConv(emb_dim))
            elif gnn_type == 'gcn':
                self.convs.append(GCNConv(emb_dim))
            else:
                raise ValueError(f'Undefined GNN type called {gnn_type}')

            self.batch_norms.append(torch.nn.BatchNorm1d(emb_dim))

        for layer in range(num_layer - 1):
            self.mlp_virtualnode_list.append(torch.nn.Sequential(
                torch.nn.Linear(emb_dim, 2 * emb_dim),
                torch.nn.BatchNorm1d(2 * emb_dim),
                torch.nn.ReLU(),
                torch.nn.Linear(2 * emb_dim, emb_dim),
                torch.nn.BatchNorm1d(emb_dim),
                torch.nn.ReLU()
            ))

    def forward(self, batched_data):

        x, edge_index = batched_data.x, batched_data.edge_index
        edge_attr, batch = batched_data.edge_attr, batched_data.batch
        # virtual node embeddings for graphs
        virtualnode_embedding = self.virtualnode_embedding(torch.zeros(
            batch[-1].item() + 1).to(edge_index.dtype).to(edge_index.device))

        h_list = [self.atom_encoder(x)]
        for layer in range(self.num_layer):
            # add message from virtual nodes to graph nodes
            h_list[layer] = h_list[layer] + virtualnode_embedding[batch]

            # Message passing among graph nodes
            h = self.convs[layer](h_list[layer], edge_index, edge_attr)

            h = self.batch_norms[layer](h)
            if layer == self.num_layer - 1:
                # remove relu for the last layer
                h = F.dropout(h, self.drop_ratio, training=self.training)
            else:
                h = F.dropout(
                    F.relu(h), self.drop_ratio, training=self.training
                )

            if self.residual:
                h = h + h_list[layer]

            h_list.append(h)

            # update the virtual nodes
            if layer < self.num_layer - 1:
                # add message from graph nodes to virtual nodes
                virtualnode_embedding_temp = global_add_pool(
                    h_list[layer], batch) + virtualnode_embedding
                # transform virtual nodes using MLP

                if self.residual:
                    virtualnode_embedding = virtualnode_embedding + F.dropout(
                        self.mlp_virtualnode_list[layer](
                            virtualnode_embedding_temp
                        ), self.drop_ratio, training=self.training
                    )
                else:
                    virtualnode_embedding = F.dropout(
                        self.mlp_virtualnode_list[layer](
                            virtualnode_embedding_temp
                        ), self.drop_ratio, training=self.training
                    )

        # Different implementations of Jk-concat
        if self.JK == "last":
            node_representation = h_list[-1]
        elif self.JK == "sum":
            node_representation = 0
            for layer in range(self.num_layer + 1):
                node_representation += h_list[layer]

        return node_representation

class Separator(nn.Module):
    def __init__(self,config):
        super(Separator, self).__init__()
        if config.model.gnn_type == 'GIN':
            self.r_gnn = GINFeatExtractor(config, without_readout=True)
        else:
            self.r_gnn = vGINFeatExtractor(config, without_readout=True)
        emb_d = config.model.dim_hidden

        self.separator = nn.Sequential(nn.Linear(emb_d, emb_d * 2),
                                       nn.BatchNorm1d(emb_d * 2),
                                       nn.ReLU(),
                                       nn.Linear(emb_d * 2, emb_d),
                                       nn.Sigmoid())

    def forward(self, data):
        inkwargs = {'data': data}
        node_feat = self.r_gnn(**inkwargs)
        score = self.separator(node_feat)  # [n, d]

        # reg on score

        pos_score_on_node = score.mean(1)  # [n]
        pos_score_on_batch = scatter_add(pos_score_on_node, data.batch, dim=0)  # [B]
        neg_score_on_batch = scatter_add((1 - pos_score_on_node), data.batch, dim=0)  # [B]
        return score, pos_score_on_batch + 1e-8, neg_score_on_batch + 1e-8


class DiscreteEncoder(nn.Module):
    def __init__(self,config):
        super(DiscreteEncoder, self).__init__()
        self.config = config
        emb_dim = config.model.dim_hidden
        if config.model.gnn_type == 'GIN':
            self.gnn = GINFeatExtractor(config, without_readout=True)
        else:
            self.gnn = vGINFeatExtractor(config, without_readout=True)
        self.classifier = nn.Sequential(*(
            [nn.Linear(emb_dim, config.dataset.num_classes)]
        ))

        self.pool = global_mean_pool

        self.vq = VectorQuantize(dim=emb_dim,
                                 codebook_size=config.ood.num_e,
                                 commitment_weight=config.ood.commitment_weight,
                                 decay=0.9)

        self.mix_proj = nn.Sequential(nn.Linear(emb_dim * 2, emb_dim),
                                      nn.BatchNorm1d(emb_dim),
                                      nn.ReLU(),
                                      nn.Dropout(),
                                      nn.Linear(emb_dim, emb_dim))

        self.simsiam_proj = nn.Sequential(nn.Linear(emb_dim, emb_dim * 2),
                                          nn.BatchNorm1d(emb_dim * 2),
                                          nn.ReLU(),
                                          nn.Linear(emb_dim * 2, emb_dim))

    def vector_quantize(self, f, vq_model):
        v_f, indices, v_loss = vq_model(f)

        return v_f, v_loss

    def forward(self, data, score):
        inkwars = {'data': data}
        node_feat = self.gnn(**inkwars)

        node_v_feat, cmt_loss = self.vector_quantize(node_feat.unsqueeze(0), self.vq)
        node_v_feat = node_v_feat.squeeze(0)
        node_res_feat = node_feat + node_v_feat
        c_node_feat = node_res_feat * score
        s_node_feat = node_res_feat * (1 - score)

        c_graph_feat = self.pool(c_node_feat, data.batch)
        s_graph_feat = self.pool(s_node_feat, data.batch)

        c_logit = self.classifier(c_graph_feat)

        return c_logit, c_graph_feat, s_graph_feat, cmt_loss



from GOOD import register
from GOOD.utils.config_reader import Union, CommonArgs, Munch
@register.model_register
class iMoLDGNN(nn.Module):
    def __init__(self, config):
        super(iMoLDGNN, self).__init__()
        self.config = config
        self.gamma = config.ood.gamma
        self.separator = Separator(config)
        self.encoder = DiscreteEncoder(config)

    def forward(self, *args, **kwargs):
        data = kwargs.get('data')
        score, pos_score, neg_score = self.separator(data)
        c_logit, c_graph_feat, s_graph_feat, cmt_loss = self.encoder(data, score)
        # reg on score
        loss_reg = torch.abs(pos_score / (pos_score + neg_score) - self.gamma * torch.ones_like(pos_score)).mean()
        return c_logit, c_graph_feat, s_graph_feat, cmt_loss, loss_reg

    def mix_cs_proj(self, c_f: torch.Tensor, s_f: torch.Tensor):
        n = c_f.size(0)
        perm = np.random.permutation(n)
        mix_f = torch.cat([c_f, s_f[perm]], dim=-1)
        proj_mix_f = self.encoder.mix_proj(mix_f)
        return proj_mix_f

