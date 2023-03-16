
import numpy as np

from .feedforward import FeedForwardNetwork


class BaseCPPNDecoder:
    def feedforward(self, inputs, genome, config):
        cppn = FeedForwardNetwork.create(genome, config)

        states = []
        for inp in inputs:
            state = cppn.activate(inp)
            states.append(state)

        return np.vstack(states)

class BaseHyperDecoder:
    def __init__(self, substrate, activation='sin'):

        connections = None
        downstream_nodes = None
        self.activation = activation
        
        self.set_attr(substrate, connections, downstream_nodes)

    def set_attr(self, substrate, connections, downstream_nodes):
        self.egde_inputs = substrate.get_connection_inputs(connections)
        self.node_inputs = substrate.get_node_inputs(downstream_nodes)
        self.input_nodes = substrate.get_nodes('input')
        self.output_nodes = substrate.get_nodes('output')
        self.input_dims = substrate.get_dim_size()
        self.output_dims = 1

    def decode(self, genome, config):
        output_activation = genome.nodes[config.output_keys[0]].activation

        cppn = FeedForwardNetwork.create(genome, config)

        biases = {}
        for node,inp in self.node_inputs.items():
            bias = cppn.activate(inp)[0]
            bias = self.scale_outputs(bias, output_activation)
            biases[node] = bias

        connections = {}
        for edge,inp in self.egde_inputs.items():
            weight = cppn.activate(inp)[0]
            weight = self.scale_outputs(weight, output_activation)
            connections[edge] = weight

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
