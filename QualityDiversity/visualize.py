from __future__ import print_function

import copy
import warnings
import random
import os

import matplotlib
matplotlib.use('TkAgg')
import graphviz
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as patches

import numpy as np

def plot_stats(statistics, ylog=False, view=False, filename='avg_fitness.svg'):
    """ Plots the population's average and best fitness. """
    if plt is None:
        warnings.warn("This display is not available due to a missing optional dependency (matplotlib)")
        return

    generation = range(len(statistics.most_fit_genomes))
    best_fitness = [c.fitness for c in statistics.most_fit_genomes]
    avg_fitness = np.array(statistics.get_fitness_mean())
    stdev_fitness = np.array(statistics.get_fitness_stdev())

    plt.plot(generation, avg_fitness, 'b-', label="average")
    plt.plot(generation, avg_fitness - stdev_fitness, 'g-.', label="-1 sd")
    plt.plot(generation, avg_fitness + stdev_fitness, 'g-.', label="+1 sd")
    plt.plot(generation, best_fitness, 'r-', label="best")

    plt.title("Population's average and best fitness")
    plt.xlabel("Generations")
    plt.ylabel("Fitness")
    plt.grid()
    plt.legend(loc="best")
    if ylog:
        plt.gca().set_yscale('symlog')

    plt.savefig(filename)
    if view:
        plt.show()

    plt.close()


def draw_net(config, genome, view=False, filename=None, directory=None, node_names=None, show_disabled=True, prune_unused=False,
             node_colors=None, fmt='svg'):
    """ Receives a genome and draws a neural network with arbitrary topology. """
    # Attributes for network nodes.
    if graphviz is None:
        warnings.warn("This display is not available due to a missing optional dependency (graphviz)")
        return

    if node_names is None:
        node_names = {}

    assert type(node_names) is dict

    if node_colors is None:
        node_colors = {}

    assert type(node_colors) is dict

    node_attrs = {
        'shape': 'circle',
        'fontsize': '9',
        'height': '0.2',
        'width': '0.2'}

    dot = graphviz.Digraph(format=fmt, node_attr=node_attrs)

    inputs = set()
    for k in config.genome_config.input_keys:
        inputs.add(k)
        name = node_names.get(k, str(k))
        input_attrs = {'style': 'filled', 'shape': 'box', 'fillcolor': node_colors.get(k, 'lightgray')}
        dot.node(name, _attributes=input_attrs)

    outputs = set()
    for k in config.genome_config.output_keys:
        outputs.add(k)
        name = node_names.get(k, str(k))
        node_attrs = {'style': 'filled', 'fillcolor': node_colors.get(k, 'lightblue')}

        dot.node(name, _attributes=node_attrs)

    if prune_unused:
        connections = set()
        for cg in genome.connections.values():
            if cg.enabled or show_disabled:
                connections.add((cg.in_node_id, cg.out_node_id))

        used_nodes = copy.copy(outputs)
        pending = copy.copy(outputs)
        while pending:
            new_pending = set()
            for a, b in connections:
                if b in pending and a not in used_nodes:
                    new_pending.add(a)
                    used_nodes.add(a)
            pending = new_pending
    else:
        used_nodes = set(genome.nodes.keys())

    for n in used_nodes:
        if n in inputs or n in outputs:
            continue

        attrs = {'style': 'filled',
                 'fillcolor': node_colors.get(n, 'white')}
        dot.node(str(n), _attributes=attrs)

    for cg in genome.connections.values():
        if cg.enabled or show_disabled:
            #if cg.input not in used_nodes or cg.output not in used_nodes:
            #    continue
            input, output = cg.key
            a = node_names.get(input, str(input))
            b = node_names.get(output, str(output))
            style = 'solid' if cg.enabled else 'dotted'
            color = 'green' if cg.weight > 0 else 'red'
            width = str(0.1 + abs(cg.weight / 5.0))
            dot.edge(a, b, _attributes={'style': style, 'color': color, 'penwidth': width})

    dot.render(filename, directory, view=view)

    return dot


class ProgressDrawer:

    def __init__(self, width=400, height=400, fig_height=6, show_axes=False, no_plot=False):
        self.width = width
        self.height = height
        self.fig_height = fig_height
        self.fig_width = fig_height * (float(width) / float(height)) - 0.2
        self.show_axes = show_axes
        self.no_plot = no_plot
        self.fig_map = None
        self.ax_map = None

    def initialize_figure(self, save_dir):
        self.save_dir = save_dir

        self.fig_map, self.ax_map = plt.subplots()
        self.fig_map.set_dpi(100)
        self.fig_map.set_size_inches(self.fig_height * 1.1, self.fig_height)

        self.ax_map.set_title('behavioral descriptor 2d map')

    def set_bd(self, bd1_item, bd2_item):
        self.bd1_key, bd1 = bd1_item
        self.bd2_key, bd2 = bd2_item

        self.axis2, self.axis1 = np.meshgrid(np.array(bd2.bins), np.array(bd1.bins))
        self.bd_map_2d = np.full(self.axis1.shape, -np.inf)

        self.ax_map.set_xlabel(bd1.name)
        self.ax_map.set_ylabel(bd2.name)

    def update_bd_map(self, population):
        for _, genome in population:
            bd1 = genome.bd[self.bd1_key]
            bd2 = genome.bd[self.bd2_key]
            if genome.fitness > self.bd_map_2d[(bd1, bd2)]:
                self.bd_map_2d[(bd1, bd2)] = genome.fitness

    def draw(self, generation):

        pcm = self.ax_map.pcolormesh(self.axis1, self.axis2, self.bd_map_2d)
        cb = self.fig_map.colorbar(pcm, ax=(self.ax_map))

        filename = os.path.join(self.save_dir, 'progress_map%d.png' % generation)
        self.fig_map.savefig(filename)

        if not self.no_plot:
            plt.pause(0.1)

        cb.remove()
        pcm.remove()

    def close(self):
        plt.clf()
        plt.close('all')
