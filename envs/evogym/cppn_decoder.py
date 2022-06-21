import numpy as np
import torch

from evogym import get_full_connectivity

from neat_cppn import BaseCPPNDecoder, BaseHyperDecoder


class EvogymStructureDecoder(BaseCPPNDecoder):
    def __init__(self, size):
        self.size = size

        x, y = torch.meshgrid(torch.arange(size[0]), torch.arange(size[1]), indexing='ij')
        x = x.flatten()
        y = y.flatten()

        center = (np.array(size) - 1) / 2
        d = np.sqrt(np.square(x - center[0]) + np.square(y - center[1]))

        self.inputs = {'x': x, 'y': y, 'd': d}
        self.output_keys = ['empty', 'rigid', 'soft', 'hori', 'vert']

    def decode(self, genome, config):
        output = super().decode(genome, config)
        output = np.vstack([output[key] for key in self.output_keys])
        material = np.argmax(output, axis=0)

        robot = np.reshape(material, self.size)
        connectivity = get_full_connectivity(robot)
        return (robot, connectivity)


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
