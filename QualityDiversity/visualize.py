#Copyright (c) 2007-2011, cesar.gomes and mirrorballu2
#Copyright (c) 2015-2017, CodeReclaimers, LLC
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#following conditions are met:
#
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#disclaimer.
#
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#disclaimer in the documentation and/or other materials provided with the distribution.
#
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
#derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import print_function

import copy
import warnings
import random
import argparse
import os

import matplotlib
matplotlib.use('TkAgg')
import graphviz
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as patches

import numpy as np

import geometry
import agent
import maze_environment as maze

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

def draw_agent_path(maze_env, path_points, genome, filename=None, view=False, show_axes=False, width=400, height=400, fig_height=4):
    """
    The function to draw path of the maze solver agent through the maze.
    Arguments:
        maze_env:       The maze environment configuration.
        path_points:    The list of agent positions during simulation.
        genome:         The genome of solver agent.
        filename:       The name of file to store plot.
        view:           The flag to indicate whether to view plot.
        width:          The width of drawing in pixels
        height:         The height of drawing in pixels
        fig_height:      The plot figure height in inches
    """
    # initialize plotting
    fig, ax = plt.subplots()
    fig.set_dpi(100)
    fig_width = fig_height * (float(width)/float(height )) - 0.2
    print("Plot figure width: %.1f, height: %.1f" % (fig_width, fig_height))
    fig.set_size_inches(fig_width, fig_height)
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)

    ax.set_title('Genome ID: %s, Path Length: %d' % (genome.key, len(path_points)))
    # draw path
    for p in path_points:
        circle = plt.Circle((p.x, p.y), 2.0, facecolor='b')
        ax.add_patch(circle)

    # draw maze
    _draw_maze_(maze_env, ax)

    # turn off axis rendering
    if not show_axes:
        ax.axis('off')

    # Invert Y axis to have coordinates origin at the top left
    ax.invert_yaxis()

    # Save figure to file
    if filename is not None:
        plt.savefig(filename)

    if view:
        plt.show()

    plt.close()

def _draw_maze_(maze_env, ax):
    """
    The function to draw maze environment
    Arguments:
        maze_env:   The maze environment configuration.
        ax:         The figure axis instance
    """
    # draw maze walls
    for wall in maze_env.walls:
        line = plt.Line2D((wall.a.x, wall.b.x), (wall.a.y, wall.b.y), lw=1.5)
        ax.add_line(line)

    # draw start point
    start_circle = plt.Circle((maze_env.agent.location.x, maze_env.agent.location.y),
                                radius=2.5, facecolor=(0.6, 1.0, 0.6), edgecolor='w')
    ax.add_patch(start_circle)

    # draw exit point
    exit_circle = plt.Circle((maze_env.exit_point.x, maze_env.exit_point.y),
                                radius=2.5, facecolor=(1.0, 0.2, 0.0), edgecolor='w')
    ax.add_patch(exit_circle)

if __name__ == '__main__':
    # read command line parameters
    parser = argparse.ArgumentParser(description="The maze experiment visualizer.")
    parser.add_argument('-m', '--maze', default='medium', help='The maze configuration to use.')
    parser.add_argument('-r', '--records', help='The records file.')
    parser.add_argument('-o', '--output', help='The file to store the plot.')
    parser.add_argument('--width', type=int, default=400, help='The width of the subplot')
    parser.add_argument('--height', type=int, default=400, help='The height of the subplot')
    parser.add_argument('--fig_height', type=float, default=7, help='The height of the plot figure')
    parser.add_argument('--show_axes', type=bool, default=False, help='The flag to indicate whether to show plot axes.')
    args = parser.parse_args()

    local_dir = os.path.dirname(__file__)
    if not (args.maze == 'medium' or args.maze == 'hard'):
        print('Unsupported maze configuration: %s' % args.maze)
        exit(1)

    # read maze environment
    maze_env_config = os.path.join(local_dir, '%s_maze.txt' % args.maze)
    maze_env = maze.read_environment(maze_env_config)

    # read agents records
    rs = agent.AgentRecordStore()
    rs.load(args.records)

    # render visualization
    random.seed(42)
    draw_maze_records(maze_env,
                      rs.records,
                      width=args.width,
                      height=args.height,
                      fig_height=args.fig_height,
                      view=True,
                      show_axes=args.show_axes,
                      filename=args.output)


class ProgressDrawer():
    def __init__(self, maze_env, width=400, height=400, fig_height=6, show_axes=False, save_interval=0):
        self.maze_env = maze_env
        self.width = width
        self.height = height
        self.fig_height = fig_height
        self.fig_width = fig_height * (float(width)/float(height)) - 0.2
        self.show_axes = show_axes
        self.save_interval = save_interval
        self.fig_stat = None
        self.ax_stat = None
        self.fig_map = None
        self.ax_map = None
        self.best_fitness = -1
        self.best_path = None
        self.best_genome = None
        self.update_in_generation = False

    def initialize_figure(self,save_dir):
        self.save_dir = save_dir

        self.fig_stat,self.ax_stat = plt.subplots()
        self.fig_stat.set_dpi(100)
        self.fig_stat.set_size_inches(self.fig_width,self.fig_height)

        self.ax_stat.set_xlim(0, self.width)
        self.ax_stat.set_ylim(0, self.height)

        self.ax_stat.invert_yaxis()

        self.fig_map,self.ax_map = plt.subplots()
        self.fig_map.set_dpi(100)
        self.fig_map.set_size_inches(self.fig_height*1.1,self.fig_height)

        self.ax_map.set_title('behavioral descriptor 2d map')
        self.ax_map.invert_yaxis()

    def set_bd(self, bd1_item, bd2_item):
        self.bd1_key,bd1 = bd1_item
        self.bd2_key,bd2 = bd2_item
        self.axis2,self.axis1 = np.meshgrid(np.array(bd2.bins),np.array(bd1.bins))
        self.bd_map_2d = np.full(self.axis1.shape,-np.inf)

        self.ax_map.set_xlabel(bd1.name)
        self.ax_map.set_ylabel(bd2.name)

    def update_best(self,genome,fitness):
        if self.best_genome is None or fitness>self.best_fitness:
            self.best_fitness = fitness
            self.best_genome = genome
            self.update_in_generation = True

    def set_path(self,path):
        self.best_path = path

    def update_bd_map(self, population):
        for _,genome in population:
            bd1 = genome.bd[self.bd1_key]
            bd2 = genome.bd[self.bd2_key]
            if  genome.fitness > self.bd_map_2d[bd1,bd2]:
                self.bd_map_2d[bd1,bd2] = genome.fitness

    def draw(self, generation, population):
        self.ax_stat.set_title('Generation : %d , best Genome ID: %s' % (generation,self.best_genome.key))

        current_x,current_y = [],[]
        for _,genome in population:
            x,y = genome.data
            circle = plt.Circle((x,y), 0.8, facecolor='y',alpha=0.7)
            current_x.append(x)
            current_y.append(y)
            self.ax_stat.add_patch(circle)

        for p in self.best_path:
            circle = plt.Circle((p.x, p.y), 1.0, facecolor='b',alpha=1.0)
            self.ax_stat.add_patch(circle)


        _draw_maze_(self.maze_env,self.ax_stat)
        if not self.show_axes:
            self.ax_stat.axis('off')

        pcm = self.ax_map.pcolormesh(self.axis1, self.axis2, self.bd_map_2d)
        cb = self.fig_map.colorbar(pcm, ax=self.ax_map)

        if self.save_interval>0 and generation%self.save_interval==0:
            filename = os.path.join(self.save_dir,'progress_maze%d.png'%generation)
            self.fig_stat.savefig(filename)

            filename = os.path.join(self.save_dir,'progress_map%d.png'%generation)
            self.fig_map.savefig(filename)

        plt.pause(0.1)

        self.ax_stat.patches = []
        self.ax_stat.scatter(current_x,current_y,s=1.0,facecolor='gray',alpha=0.7)

        cb.remove()
        pcm.remove()

        self.update_in_generation = False

    def close(self):
        plt.clf()
        plt.close('all')
