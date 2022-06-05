import os
import sys
import time
import numpy as np

import matplotlib.pyplot as plt
import networkx as nx

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import neat_cppn
from neat.graphs import feed_forward_layers, creates_cycle


def draw_network(genome_orig, config, fig, ax):
    fig.set_figwidth(1)
    fig.set_figheight(1)
    ax.cla()

    genome = genome_orig.get_pruned_copy(config)
    nodes = {}
    position = {}

    network_height = 1
    network_width = len(config.input_keys)

    layers = feed_forward_layers(config.input_keys, config.output_keys, genome.connections.keys())
    valid_nodes = config.input_keys + sum(map(list,layers), [])

    for i,key in enumerate(config.input_keys):
        name = f'{key}'
        nodes[key] = (name, {'color': [0.1,0.1,0.1], 'node_size': 500, 'label': name})
        pos_x = (i - (len(config.input_keys)-1)/2)
        position[name] = (pos_x, 0)

    for i,key in enumerate(config.output_keys):
        if key not in valid_nodes:
            continue
        name = f'{key}'
        nodes[key] = (name, {'color': [0.1,0.1,0.1], 'node_size': 500, 'label': name})

    for key,node in genome.nodes.items():
        if key in nodes or key not in valid_nodes:
            continue
        name = f'{key}'
        nodes[key] =  (name, {'color': [0.4,0.4,0.4], 'node_size': 300, 'label': name})


    conns = {}
    for (key_i, key_o), conn in genome.connections.items():
        if key_i not in valid_nodes or key_o not in valid_nodes:
            continue
        weight = conn.weight * genome.nodes[key_o].response
        if weight > 0:
            color = [0.9, 0.3, 0.1]
        else:
            color = [0.1, 0.4, 0.9]
        weight = np.log(abs(weight)*10+1)+0.3
        conns[(key_i, key_o)] = (nodes[key_i][0], nodes[key_o][0],
            {'color': color, 'weight': weight, 'arrowsize': weight*4})


    for h_i,layer in enumerate(layers):
        layer_size = len(layer)
        for w_i,node in enumerate(layer):
            pos_x = (w_i - (layer_size-1)/2)
            position[nodes[node][0]] = (pos_x, -h_i-1)

        network_width = max(network_width, layer_size)
        network_height += 1


    G = nx.DiGraph()
    G.add_nodes_from(nodes.values())
    G.add_edges_from(conns.values())

    fig.set_figwidth(network_width*1.5)
    fig.set_figheight(network_height*0.8)
    ax.set_xlim([-(network_width-1)/2-0.5, (network_width-1)/2+0.5])
    ax.set_ylim([-(network_height-1)-0.3, 0.3])

    nx.draw_networkx_nodes(G, position, ax=ax,
        node_color=[node['color'] for node in G.nodes.values()],
        node_size=[node['node_size'] for node in G.nodes.values()])
    nx.draw_networkx_labels(G, position, ax=ax,
        labels={node[0]: node[1]['label'] for node in nodes.values()},
        font_size=8,
        font_color=[1.0,1.0,1.0])
    nx.draw_networkx_edges(G, position, ax=ax,
        width=[edge['weight'] for edge in G.edges.values()],
        edge_color=[edge['color'] for edge in G.edges.values()],
        arrowsize=[edge['arrowsize'] for edge in G.edges.values()],
        connectionstyle='arc3,rad=0.2',
        alpha=0.6)

    ax.axis("off")

def plot_function(NN, fig, ax):
    ax.cla()
    inputs = np.linspace(-5,5,101)
    outputs = [NN.activate([inp])[0] for inp in inputs]

    ax.set_xlabel('input')
    ax.set_ylabel('output')

    ax.plot(inputs, outputs)



def add_node(genome, config, between):
    node_key = config.get_new_node_key(genome.nodes)
    node_gene = genome.create_node(config, node_key)
    node_gene.bias = 0
    node_gene.response = 1
    genome.nodes[node_key] = node_gene
    print(f'OPERATOR: add node {node_key}.')

    add_connection(genome, config, between[0], node_key)
    add_connection(genome, config, node_key, between[1])

def add_connection(genome, config, input_key, output_key):
    connection_key = (input_key, output_key)
    if connection_key in genome.connections:
        print(f'OPERATOR: connection between {input_key} and {output_key} is already exists.')

    if creates_cycle(list(genome.connections), connection_key):
        print('OPERATOR: it is loop connection, so this operation can not be done.')
        return

    connection_gene = genome.create_connection(config, input_key, output_key)
    connection_gene.weight = 1
    genome.connections[connection_key] = connection_gene
    print(f'OPERATOR: add connection between {input_key} and {output_key}.')

def remove_node(genome, config, node_key):
    print()
    del genome.nodes[node_key]
    print(f'OPERATOR: remove node {node_key}.')

    for connection_key in list(genome.connections.keys()):
        if node_key==connection_key[0] or node_key==connection_key[1]:
            del genome.connections[connection_key]
            print(f'OPERATOR: remove connection between {connection_key[0]} and {connection_key[1]}.')
    print()

def remove_connection(genome, config, input_key, output_key):
    connection_key = (input_key, output_key)
    if connection_key not in genome.connections:
        print(f'OPERATOR: connection between {input_key} and {output_key} is not exists.')
        return

    del genome.connections[connection_key]
    print(f'OPERATOR: remove connection between {input_key} and {output_key}.')

    for node_key in list(genome.nodes.keys()):

        valid = False
        for connection_key in genome.connections.keys():
            if node_key==connection_key[0] or node_key==connection_key[1]:
                valid = True
                break

        if not valid:
            del genome.nodes[node_key]
            print(f'OPERATOR: remove node {node_key}.')

def set_node_bias(genome, config, node_key, bias):
    if node_key not in genome.nodes:
        print(f'OPERATOR: node {node_key} is not exists.')
    genome.nodes[node_key].bias = bias
    print(f'OPERATOR: set bias {bias} to node {node_key}.')

def set_connection_weight(genome, config, input_key, output_key, weight):
    connection_key = (input_key, output_key)
    if connection_key not in genome.connections:
        print(f'OPERATOR: connection between {input_key} and {output_key} is not exists.')
        return
    genome.connections[connection_key].weight = weight
    print(f'OPERATOR: set weight {weight} to connection between {input_key} and {output_key}.')


def activate_detail(NN, inputs):
    print(f'OPERATOR: input {inputs[0]} to neural network.')
    print('----------NODES STATE----------')

    values = {}
    for node_key, value in zip(NN.input_nodes, inputs):
        values[node_key] = value
        print(f'Input  Node {node_key: =2}: {value}')

    for node_key, act_func, agg_func, bias, response, links in NN.node_evals[:-1]:
        print(f'Hidden Node {node_key: =2}: ', end='')
        node_inputs = []
        for i, w in links:
            node_inputs.append(values[i] * w)
        s = agg_func(node_inputs)
        values[node_key] = act_func(bias + response * s)
        print(f'{values[node_key]: =.3f} <- ', end='')
        print('sigmoid( ' + ' + '.join([f'node[{input_key}]*{weight: =.2f}' for input_key,weight in links]) + f' + {bias: =.2f} )')

    node_key, act_func, agg_func, bias, response, links = NN.node_evals[-1]
    print(f'Output Node {node_key: =2}: ', end='')
    node_inputs = []
    for i, w in links:
        node_inputs.append(values[i] * w)
    s = agg_func(node_inputs)
    values[node_key] = act_func(bias + response * s)
    print(f'{values[node_key]: =.3f} <- ', end='')
    print('sigmoid( ' + ' + '.join([f'node[{input_key}]*{weight: =.2f}' for input_key,weight in links]) + f' + {bias: =.2f} )')


def get_valid_input(question, options):
    while True:
        answer = input(question)
        if answer in options:
            break
        print(f'\tINVALID: "{answer}" is not valid, choose from {options}')
    return answer


def get_value(question, options):
    while True:
        answer = input(question)
        try:
            _ = float(answer)
            break
        except:
            if answer in options:
                break
        print(f'\tINVALID: "{answer}" is not numeral, or choose from {options}')
    return answer

def main():

    config_file = os.path.join(CURR_DIR, 'config', 'tutorial.cfg')
    custom_config = [
        ('DefaultGenome', 'num_inputs', 1),
        ('DefaultGenome', 'num_hidden', 0),
        ('DefaultGenome', 'num_outputs', 1),
        # ('DefaultGenome', 'activation_default', 'identity'),
        # ('DefaultGenome', 'activation_options', 'identity'),
        ('DefaultGenome', 'initial_connection', 'full_direct'),
    ]
    config = neat_cppn.make_config(config_file, custom_config=custom_config)

    genome = config.genome_type(1)
    genome.configure_new(config.genome_config)

    InputKey = config.genome_config.input_keys[0]
    OutputKey = config.genome_config.output_keys[0]

    genome.nodes[OutputKey].bias = 0
    genome.nodes[OutputKey].response = 1
    genome.connections[(InputKey, OutputKey)].weight = 1

    fig_network, ax_network = plt.subplots(num='neural network')
    fig_function, ax_function = plt.subplots(num='function plot', figsize=(4,4))

    operation_options = ['add', 'remove', 'set', 'input']
    gene_type_options = ['node', 'connection', 'conn']
    attribute_options = ['bias', 'weight']
    other_operations = ['exit', 'back']

    while True:
        NN = neat_cppn.FeedForwardNetwork.create(genome, config.genome_config)
        draw_network(genome, config.genome_config, fig_network, ax_network)
        plot_function(NN, fig_function, ax_function)
        plt.pause(0.01)

        valid_nodes = [str(node_key) for node_key in genome.nodes.keys() if node_key!=OutputKey]
        upstream_nodes = [str(InputKey)] + valid_nodes
        downstream_nodes = [str(OutputKey)] + valid_nodes
        valid_inputs = list(set([str(input_key) for input_key,_ in genome.connections.keys()]))
        valid_outputs = list(set([str(output_key) for _,output_key in genome.connections.keys()]))

        operation = get_valid_input(
            question='|Input| operation (options: add, remove, set, input):  ',
            options=operation_options+other_operations
        )
        if operation=='add':
            gene_type = get_valid_input(
                question='|Input| gene type (options: node, connection):  ',
                options=gene_type_options+other_operations
            )
            if gene_type=='node':
                input_key = get_valid_input(
                    question='|Input| upstream   node:  ',
                    options=upstream_nodes+other_operations
                )
                if input_key=='back':
                    continue
                elif input_key=='exit':
                    break

                output_key = get_valid_input(
                    question='|Input| downstream node:  ',
                    options=downstream_nodes+other_operations
                )
                if output_key=='back':
                    continue
                elif output_key=='exit':
                    break

                print()
                add_node(genome, config.genome_config, (int(input_key), int(output_key)))

            elif gene_type=='connection' or gene_type=='conn':
                input_key = get_valid_input(
                    question='|Input| input  node:  ',
                    options=upstream_nodes+other_operations
                )
                if input_key=='back':
                    continue
                elif input_key=='exit':
                    break

                output_key = get_valid_input(
                    question='|Input| output node:  ',
                    options=downstream_nodes+other_operations
                )
                if output_key=='back':
                    continue
                elif output_key=='exit':
                    break

                print()
                add_connection(genome, config.genome_config, int(input_key), int(output_key))

            elif gene_type=='back':
                continue
            elif gene_type=='exit':
                break

        elif operation=='remove':
            gene_type = get_valid_input(
                question='|Input| gene type (options: node, connection):  ',
                options=gene_type_options+other_operations
            )
            if gene_type=='node':
                node_key = get_valid_input(
                    question='|Input| node:  ',
                    options=valid_nodes+other_operations
                )
                if input_key=='back':
                    continue
                elif input_key=='exit':
                    break

                print()
                remove_node(genome, config.genome_config, int(node_key))

            elif gene_type=='connection' or gene_type=='conn':
                input_key = get_valid_input(
                    question='|Input| input  node:  ',
                    options=valid_inputs+other_operations
                )
                if input_key=='back':
                    continue
                elif input_key=='exit':
                    break

                output_key = get_valid_input(
                    question='|Input| output node:  ',
                    options=valid_outputs+other_operations
                )
                if output_key=='back':
                    continue
                elif output_key=='exit':
                    break

                print()
                remove_connection(genome, config.genome_config, int(input_key), int(output_key))

            elif gene_type=='back':
                continue
            elif gene_type=='exit':
                break

        elif operation=='set':
            gene_type = get_valid_input(
                question='|Input| attribute type (options: bias, weight):  ',
                options=attribute_options+other_operations
            )
            if gene_type=='bias':
                node_key = get_valid_input(
                    question='|Input| node:  ',
                    options=downstream_nodes+other_operations
                )
                if node_key=='back':
                    continue
                elif node_key=='exit':
                    break

                bias = get_value(
                    question='|Input| bias:  ',
                    options=other_operations
                )
                if bias=='back':
                    continue
                elif bias=='exit':
                    break

                print()
                set_node_bias(genome, config.genome_config, int(node_key), float(bias))

            elif gene_type=='weight':
                input_key = get_valid_input(
                    question='|Input| input  node:  ',
                    options=valid_inputs+other_operations
                )
                if input_key=='back':
                    continue
                elif input_key=='exit':
                    break

                output_key = get_valid_input(
                    question='|Input| output node:  ',
                    options=valid_outputs+other_operations
                )
                if output_key=='back':
                    continue
                elif output_key=='exit':
                    break

                weight = get_value(
                    question='|Input| weight:  ',
                    options=other_operations
                )
                if weight=='back':
                    continue
                elif weight=='exit':
                    break

                print()
                set_connection_weight(genome, config.genome_config, int(input_key), int(output_key), float(weight))

            elif gene_type=='back':
                continue
            elif gene_type=='exit':
                break

        elif operation=='input':
            value = get_value(
                question='|Input| value:  ',
                options=other_operations
            )
            if value=='back':
                continue
            elif value=='exit':
                break

            print()
            activate_detail(NN, [float(value)])

        elif operation=='back':
            continue
        elif operation=='exit':
            break

        print()

    print('quit process')



if __name__=='__main__':
    main()
