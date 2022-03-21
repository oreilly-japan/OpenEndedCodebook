import random
import os

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from neat import BaseReporter
from neat.nn import FeedForwardNetwork

from visualize import _draw_maze_

class DrawReporter(BaseReporter):
    def __init__(
            self,
            env,
            timesteps,
            save_dir,
            width=200,height=200,fig_height=6,
            show_axes=False,
            no_plot=False):

        self.env = env
        self.timesteps = timesteps
        self.save_dir = save_dir
        self.width = width
        self.height = height
        self.fig_height = fig_height
        self.fig_width = fig_height
        self.show_axes = show_axes
        self.no_plot = no_plot
        self.fig = None
        self.ax = None
        self.best_reward = float('-inf')
        self.best_path = None
        self.generation = -1
        self.update_in_generation = False

        self.fig,self.ax = plt.subplots()
        self.fig.set_dpi(100)
        self.fig.set_size_inches(self.fig_width,self.fig_height)

        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.invert_yaxis()

        os.makedirs(save_dir, exist_ok=True)

    def start_generation(self, generation):
        self.generation = generation

    def _update_path(self, genomes, config):
        genome_reward = max(genomes.values(), key=lambda z: z.reward)
        if genome_reward.reward > self.best_reward:
            self.best_reward = genome_reward.reward
            self.best_path = self._get_path(genome_reward, config)
            self.update_in_generation = True

        genome_novelty = max(genomes.values(), key=lambda z: z.fitness)
        self.novelty_path = self._get_path(genome_novelty, config)

    def _get_path(self, genome, config):
        controller = FeedForwardNetwork.create(genome, config)
        self.env.reset()

        path = []
        for i in range(self.timesteps):
            obs = self.env.create_net_inputs()
            action = controller.activate(obs)
            done = self.env.update(action)

            path.append((self.env.agent.location.x, self.env.agent.location.y))

            if done:
                break
        return path

    def post_evaluate(self, config, population, species, best_genome):
        self._update_path(population, config)
        self.ax.set_title(f'Generation : {self.generation}')

        current_x,current_y = [],[]
        for _, genome in population.items():
            x,y = genome.data
            circle = plt.Circle((x,y), 0.8, facecolor='y', alpha=0.5)
            current_x.append(x)
            current_y.append(y)
            self.ax.add_patch(circle)

        for x,y in self.best_path:
            circle = plt.Circle((x, y), 1.0, facecolor='b', alpha=0.7)
            self.ax.add_patch(circle)

        for x,y in self.novelty_path:
            circle = plt.Circle((x, y), 1.0, facecolor='orange', alpha=0.7)
            self.ax.add_patch(circle)

        _draw_maze_(self.env,self.ax)

        if not self.show_axes:
            self.ax.axis('off')

        filename = os.path.join(self.save_dir,f'{self.generation}.png')
        plt.savefig(filename)

        if not self.no_plot:
            plt.pause(0.1)

        for _ in range(len(self.ax.patches)):
            self.ax.patches.pop()
        self.ax.scatter(current_x, current_y, s=1.0, facecolor='gray', alpha=0.7)

        self.update_in_generation = False

    def close(self):
        plt.clf()
        plt.close('all')
