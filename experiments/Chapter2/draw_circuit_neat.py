import sys
import os
import csv
import pickle
import numpy as np

import matplotlib.pyplot as plt
import networkx as nx

import multiprocessing as mp


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import neat_cppn
from experiment_utils import load_experiment


from arguments.circuit_neat import get_figure_args


from neat.graphs import feed_forward_layers


def draw_network(genome_key, genome_file, config, figure_file, print_detail=False):

    genome_orig = pickle.load(open(genome_file, 'rb'))

    genome = genome_orig.get_pruned_copy(config)
    nodes = {}
    position = {}

    network_height = 1
    network_width = len(config.input_keys)

    layers = feed_forward_layers(config.input_keys, config.output_keys, genome.connections.keys())
    valid_nodes = config.input_keys + sum(map(list,layers), [])

    for i,key in enumerate(config.input_keys):
        name = f'in{-key-1}'
        nodes[key] = (name, {'color': [0.1,0.1,0.1], 'node_size': 500, 'label': name, 'edgecolor': [0.1,0.1,0.1], 'linewidth': 0})
        pos_x = (i - (len(config.input_keys)-1)/2)
        position[name] = (pos_x, 0)

    if print_detail:
        print('input nodes:  ['+', '.join(map(str, config.input_keys))+']')


    for i,key in enumerate(config.output_keys):
        if key not in valid_nodes:
            continue
        name = f'out{key}'
        node = genome.nodes[key]
        if node.bias>0:
            color = [0.9, 0.5, 0.2]
        else:
            color = [0.2, 0.5, 0.9]
        width = np.log(abs(node.bias)*15+1)
        nodes[key] = (name, {'color': [0.1,0.1,0.1], 'node_size': 500, 'label': name, 'edgecolor': color, 'linewidth': width})
        
        if print_detail:
            print(f'output node {key: 6}:  bias {node.bias: =+.3f}')


    for key,node in genome.nodes.items():
        if key in nodes or key not in valid_nodes:
            continue
        name = f'{key}'
        node = genome.nodes[key]
        if node.bias>0:
            color = [0.9, 0.5, 0.2]
        else:
            color = [0.2, 0.5, 0.9]
        width = np.log(abs(node.bias)*15+1)
        nodes[key] =  (name, {'color': [0.3,0.3,0.3], 'node_size': 150, 'label': '', 'edgecolor': color, 'linewidth': width})

        if print_detail:
            print(f'hidden node {key: =6}:  bias {node.bias: =+.3f}')


    conns = {}
    for (key_i, key_o), conn in genome.connections.items():
        if key_i not in valid_nodes or key_o not in valid_nodes:
            continue
        weight = conn.weight * genome.nodes[key_o].response
        if weight==0:
            continue
        elif weight > 0:
            color = [0.9, 0.5, 0.2]
        else:
            color = [0.2, 0.5, 0.9]
        weight_ = np.log(abs(weight)*15+1)#+0.3
        conns[(key_i, key_o)] = (nodes[key_i][0], nodes[key_o][0],
            {'color': color, 'weight': weight_, 'arrowsize': weight_*4})

        if print_detail:
            print(f'connection {key_i: =6} -> {key_o: =6}:  weight {weight: =+.3f}')


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

    fig,ax = plt.subplots(figsize=(network_width*1.5, network_height))
    ax.set_xlim([-(network_width-1)/2*1.5, (network_width-1)/2*1.5])
    ax.set_ylim([-(network_height-1)-0.2, 0.2])

    nx.draw_networkx_nodes(G, position, ax=ax,
        node_color=[node['color'] for node in G.nodes.values()],
        node_size=[node['node_size'] for node in G.nodes.values()],
        linewidths=[node['linewidth'] for node in G.nodes.values()],
        edgecolors=[node['edgecolor'] for node in G.nodes.values()])
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
    plt.savefig(figure_file, bbox_inches='tight')
    plt.close()

    print(f'genome {genome_key} ... done')


def main():

    args = get_figure_args()

    expt_path = os.path.join(CURR_DIR, 'out', 'circuit_neat', args.name)
    expt_args = load_experiment(expt_path)


    config_file = os.path.join(expt_path, 'circuit_neat.cfg')
    config = neat_cppn.make_config(config_file)


    figure_path = os.path.join(expt_path, 'network')
    os.makedirs(figure_path, exist_ok=True)


    genome_ids = {}

    if args.specified is not None:
        genome_ids = {
            'specified': [args.specified]
        }
    else:
        files = {
            'fitness': 'history_fitness.csv',
        }
        for metric,file in files.items():

            history_file = os.path.join(expt_path, file)
            with open(history_file, 'r') as f:
                reader = csv.reader(f)
                histories = list(reader)[1:]
                ids = sorted(list(set([hist[1] for hist in histories])))
                genome_ids[metric] = ids


    if not args.no_multi and args.specified is None:

        pool = mp.Pool(args.num_cores)
        jobs = []

        for metric,ids in genome_ids.items():
            save_path = os.path.join(figure_path, metric)
            os.makedirs(save_path, exist_ok=True)
            for key in ids:

                figure_file = os.path.join(save_path, f'{key}.jpg')
                genome_file = os.path.join(expt_path, 'genome', f'{key}.pickle')

                if os.path.exists(figure_file) and args.not_overwrite:
                    continue

                func_args = (key, genome_file, config.genome_config, figure_file)
                jobs.append(pool.apply_async(draw_network, args=func_args))

        for job in jobs:
            job.get(timeout=None)


    else:

        for metric,ids in genome_ids.items():
            save_path = os.path.join(figure_path, metric)
            os.makedirs(save_path, exist_ok=True)
            for key in ids:

                figure_file = os.path.join(save_path, f'{key}.jpg')
                genome_file = os.path.join(expt_path, 'genome', f'{key}.pickle')

                if os.path.exists(figure_file) and args.not_overwrite:
                    continue

                func_args = (key, genome_file, config.genome_config, figure_file)
                func_kwargs = {'print_detail': True if args.specified is not None else False}
                draw_network(*func_args, **func_kwargs)

if __name__=='__main__':
    main()
