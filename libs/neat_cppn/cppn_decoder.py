
import numpy as np

from .feedforward import FeedForwardNetwork
from .pytorch_neat.cppn import create_cppn


class BaseCPPNDecoder:
    def __init__(self):
        self.inputs = None
        self.output_keys = None

    def decode(self, genome, config):
        nodes = create_cppn(
            genome, config,
            leaf_names=self.inputs.keys(),
            node_names=self.output_keys)

        outputs = {}
        for key, node in zip(self.output_keys, nodes):
            outputs[key] = node(**self.inputs).numpy()

        return outputs

class BaseHyperDecoder:
    def __init__(self, substrate, activation='sin'):

        connections = None
        downstream_nodes = None
        self.activation = activation
        
        self.set_attr(substrate, connections, downstream_nodes)

    def set_attr(self, substrate, connections, downstream_nodes):

        self.edge_labels, self.edge_inputs = substrate.get_connection_inputs(connections)
        self.node_labels, self.node_inputs = substrate.get_node_inputs(downstream_nodes)
        self.input_nodes = substrate.get_nodes('input')
        self.output_nodes = substrate.get_nodes('output')
        self.input_dims = substrate.get_dim_size()
        self.output_dims = 1

    def decode(self, genome, config):
        output_activation = genome.nodes[config.output_keys[0]].activation

        nodes = create_cppn(
            genome, config,
            leaf_names=self.edge_inputs.keys(),
            node_names=['value'])


        biases = nodes[0](**self.node_inputs).numpy()
        biases = self.scale_outputs(biases, output_activation)

        biases = {node: bias for node,bias in zip(self.node_labels, biases)}

        weights = nodes[0](**self.edge_inputs).numpy()
        weights = self.scale_outputs(weights, output_activation)

        connections = {edge: weight for edge,weight in zip(self.edge_labels, weights)}

        return FeedForwardNetwork.create_from_weights(
            config=config,
            input_keys=self.input_nodes,
            output_keys=self.output_nodes,
            biases=biases,
            weights=connections,
            weight_thr=0.5,
            default_activation=self.activation)

    @staticmethod
    def scale_outputs(outputs, activation):
        if activation in ['sigmoid', 'gauss', 'hat']:
            return (outputs - 0.5) * 10
        elif activation in ['tanh', 'sin', 'clamped']:
            return outputs * 5
        else:
            return outputs
