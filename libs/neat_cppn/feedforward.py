from neat.graphs import feed_forward_layers
from neat.nn import FeedForwardNetwork
from neat.activations import sigmoid_activation
from neat.aggregations import sum_aggregation

class FeedForwardNetwork(FeedForwardNetwork):

    # modified argument "config" to indice "genome_config"
    @staticmethod
    def create(genome, config):
        """ Receives a genome and returns its phenotype (a FeedForwardNetwork). """

        # Gather expressed connections.
        connections = [cg.key for cg in genome.connections.values() if cg.enabled]

        layers = feed_forward_layers(config.input_keys, config.output_keys, connections)
        node_evals = []
        for layer in layers:
            for node in layer:
                inputs = []
                node_expr = [] # currently unused
                for conn_key in connections:
                    inode, onode = conn_key
                    if onode == node:
                        cg = genome.connections[conn_key]
                        inputs.append((inode, cg.weight))
                        node_expr.append("v[{}] * {:.7e}".format(inode, cg.weight))

                ng = genome.nodes[node]
                aggregation_function = config.aggregation_function_defs.get(ng.aggregation)
                activation_function = config.activation_defs.get(ng.activation)
                node_evals.append((node, activation_function, aggregation_function, ng.bias, ng.response, inputs))

        return FeedForwardNetwork(config.input_keys, config.output_keys, node_evals)


    @staticmethod
    def create_from_weights(config, input_keys, output_keys, biases, weights, weight_thr=0.05, default_aggregation='sum', default_activation='sigmoid'):
        connections = [key for key,weight in weights.items() if abs(weight)>weight_thr]

        layers = feed_forward_layers(input_keys, output_keys, connections)
        node_evals = []
        for layer in layers:
            for node in layer:
                inputs = []
                node_expr = [] # currently unused
                for conn_key in connections:
                    inode, onode = conn_key
                    if onode == node:
                        weight = weights[conn_key]
                        inputs.append((inode, weight))
                        node_expr.append("v[{}] * {:.7e}".format(inode, weight))

                bias = biases[node]
                aggregation_function = config.aggregation_function_defs.get(default_aggregation)
                activation_function = config.activation_defs.get(default_activation)
                node_evals.append((node, activation_function, aggregation_function, bias, 1, inputs))

        return FeedForwardNetwork(input_keys, output_keys, node_evals)
