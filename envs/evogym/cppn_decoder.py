import numpy as np
import torch

from evogym import get_full_connectivity

from neat_cppn import BaseCPPNDecoder, BaseHyperDecoder


class EvogymStructureDecoder(BaseCPPNDecoder):
    def __init__(self, size):
        self.size = size

        x, y = np.meshgrid(np.arange(size[0]), np.arange(size[1]), indexing='ij')
        x = x.flatten()
        y = y.flatten()

        center = (np.array(size) - 1) / 2
        d = np.sqrt(np.square(x - center[0]) + np.square(y - center[1]))

        self.inputs = np.vstack([x, y, d]).T

    def decode(self, genome, config):
        # [empty, rigid, soft, vertical, horizontal] * (robot size)
        output = self.feedforward(self.inputs, genome, config)
        # 各voxelの種類を選択
        material = np.argmax(output, axis=1)

        body = np.reshape(material, self.size)
        connections = get_full_connectivity(body)
        return {'body': body, 'connections': connections}


class EvogymHyperDecoder(BaseHyperDecoder):
    def __init__(self, substrate, use_hidden=False, activation='sigmoid'):

        self.activation = activation

        connections = [('input', 'output')]
        downstream_nodes = ['output']

        substrate.make_substrate()
        if use_hidden:
            substrate.add_hidden('hidden', 1)
            connections.extend([('input', 'hidden'), ('hidden', 'output')])
            downstream_nodes.append('hidden')

        substrate.make_vectors()

        self.set_attr(substrate, connections, downstream_nodes)
