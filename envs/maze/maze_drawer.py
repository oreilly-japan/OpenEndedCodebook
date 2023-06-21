import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors

from neat_cppn import BaseReporter as BaseReporterNEAT
from ns_neat import BaseReporter as BaseReporterNS


class MazeReporterNEAT(BaseReporterNEAT):
    def __init__(self, env, timesteps, save_path, decode_function, generations, no_plot=False):

        self.env = env
        self.timesteps = timesteps
        self.save_path = save_path
        self.decode_function = decode_function
        self.generations = generations
        self.no_plot = no_plot

        self.fig = None
        self.ax = None
        self._init_figure()

        self.best_fitness = float('-inf')
        self.best_path = None
        self.generation = -1

        os.makedirs(save_path, exist_ok=True)

    def __del__(self):
        plt.clf()
        plt.close('all')

    def _init_figure(self):
        walls = self.env.walls

        width = np.max(walls[:,:,0])-np.min(walls[:,:,0])
        height = np.max(walls[:,:,1])-np.min(walls[:,:,1])

        self.fig, self.ax = plt.subplots(figsize=(width/25,height/25))

        for w_i in range(walls.shape[0]):
            self.ax.plot(walls[w_i,:,0], walls[w_i,:,1], c='k', linewidth=3)

        self.start_point = self.env.init_location
        self.exit_point = self.env.exit_point

        self.ax.axis('off')

    def start_generation(self, generation):
        self.generation = generation

    def _update_path(self, genomes, config):
        genome_best = max(genomes.values(), key=lambda z: z.fitness)
        if genome_best.fitness > self.best_fitness:
            self.best_fitness = genome_best.fitness
            self.best_path = self._get_path(genome_best, config)

    def _get_path(self, genome, config):
        controller = self.decode_function(genome, config.genome_config)
        self.env.reset()

        path = []
        for i in range(self.timesteps):
            obs = self.env.get_observation()
            action = controller.activate(obs)
            done = self.env.update(action)

            path.append(self.env.get_agent_location())

            if done:
                break
        return np.vstack(path)

    def post_evaluate(self, config, population, species, best_genome):
        self._update_path(population, config)
        self.ax.set_title(f'Generation : {self.generation}')

        current_data = np.vstack([genome.data for genome in population.values()])
        current_points = self.ax.scatter(current_data[:,0], current_data[:,1], s=3.0, color=[1.0,0.4,0.2], alpha=0.9)

        start_point = self.ax.scatter(self.start_point[0], self.start_point[1], color=[0.0,0.6,0.3], s=96, marker='s')
        goal_point = self.ax.scatter(self.exit_point[0], self.exit_point[1], color=[0.9,0.2,0.0], s=128, marker='*')

        line_best = self.ax.plot(self.best_path[:,0], self.best_path[:,1], linewidth=3, c='b', alpha=0.7)

        filename = os.path.join(self.save_path, f'{self.generation}.jpg')
        plt.savefig(filename, bbox_inches='tight')

        if not self.no_plot:
            plt.pause(0.01)

        line_best.pop(0).remove()
        current_points.remove()
        start_point.remove()
        goal_point.remove()

        cmap = plt.get_cmap('terrain')
        color = cmap(int(self.generation/self.generations*255))
        hsv = colors.rgb_to_hsv(color[:3])
        hsv[1] = 0.25
        color = colors.hsv_to_rgb(hsv)
        self.ax.scatter(current_data[:,0], current_data[:,1], s=1.0, facecolor=color, alpha=0.2)

    def found_solution(self, config, generation, best):
        plt.clf()
        plt.close('all')


class MazeReporterNS(BaseReporterNS):
    def __init__(self, env, timesteps, save_path, decode_function, generations, no_plot=False):

        self.env = env
        self.timesteps = timesteps
        self.save_path = save_path
        self.decode_function = decode_function
        self.generations = generations
        self.no_plot = no_plot

        self.fig = None
        self.ax = None
        self._init_figure()

        self.best_score = float('-inf')
        self.best_path = None
        self.novelty_path = None
        self.generation = -1

        os.makedirs(save_path, exist_ok=True)

    def __del__(self):
        plt.clf()
        plt.close('all')

    def _init_figure(self):
        walls = self.env.walls

        width = np.max(walls[:,:,0])-np.min(walls[:,:,0])
        height = np.max(walls[:,:,1])-np.min(walls[:,:,1])

        self.fig, self.ax = plt.subplots(figsize=(width/25,height/25))

        for w_i in range(walls.shape[0]):
            self.ax.plot(walls[w_i,:,0], walls[w_i,:,1], c='k', linewidth=3)

        self.start_point = self.env.init_location
        self.exit_point = self.env.exit_point

        self.ax.axis('off')

    def start_generation(self, generation):
        self.generation = generation

    def _update_path(self, genomes, config):
        genome_best = max(genomes.values(), key=lambda z: z.score)
        if genome_best.score > self.best_score:
            self.best_score = genome_best.score
            self.best_path = self._get_path(genome_best, config)

        genome_novelty = max(genomes.values(), key=lambda z: z.fitness)
        self.novelty_path = self._get_path(genome_novelty, config)

    def _get_path(self, genome, config):
        controller = self.decode_function(genome, config.genome_config)
        self.env.reset()

        path = []
        for i in range(self.timesteps):
            obs = self.env.get_observation()
            action = controller.activate(obs)
            done = self.env.update(action)

            path.append(self.env.get_agent_location())

            if done:
                break
        return np.vstack(path)

    def post_evaluate(self, config, population, species, best_genome):
        self._update_path(population, config)
        self.ax.set_title(f'Generation : {self.generation}')

        current_data = np.vstack([genome.data for genome in population.values()])
        current_points = self.ax.scatter(current_data[:,0], current_data[:,1], s=3.0, color=[1.0,0.4,0.2], alpha=0.9)

        start_point = self.ax.scatter(self.start_point[0], self.start_point[1], color=[0.0,0.6,0.3], s=96, marker='s')
        goal_point = self.ax.scatter(self.exit_point[0], self.exit_point[1], color=[0.9,0.2,0.0], s=128, marker='*')

        line_best = self.ax.plot(self.best_path[:,0], self.best_path[:,1], linewidth=3, c='b', alpha=0.7, label='best')
        line_novelty = self.ax.plot(self.novelty_path[:,0], self.novelty_path[:,1], linewidth=3, c='orange', alpha=0.7, label='novelty')

        legend = plt.legend(bbox_to_anchor=(0.95, 0.97), loc='lower right', borderaxespad=0, fontsize=10)

        filename = os.path.join(self.save_path,f'{self.generation}.jpg')
        plt.savefig(filename, bbox_inches='tight')

        if not self.no_plot:
            plt.pause(0.01)

        line_best.pop(0).remove()
        line_novelty.pop(0).remove()
        current_points.remove()
        start_point.remove()
        goal_point.remove()
        legend.remove()

        cmap = plt.get_cmap('terrain')
        color = cmap(int(self.generation/self.generations*255))
        hsv = colors.rgb_to_hsv(color[:3])
        hsv[1] = 0.25
        color = colors.hsv_to_rgb(hsv)
        self.ax.scatter(current_data[:,0], current_data[:,1], s=1.0, facecolor=color, alpha=0.3)

    def found_solution(self, config, generation, best):
        plt.clf()
        plt.close('all')
