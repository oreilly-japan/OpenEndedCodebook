import os
import numpy as np

import matplotlib.pyplot as plt

import neat_cppn

class DrawReporter(neat_cppn.BaseReporter):
    def __init__(self, env, timesteps, save_dir, no_plot=False):

        self.env = env
        self.timesteps = timesteps
        self.save_dir = save_dir
        self.no_plot = no_plot

        self.fig = None
        self.ax = None
        self._init_figure()

        self.best_reward = float('-inf')
        self.best_path = None
        self.generation = -1

        os.makedirs(save_dir, exist_ok=True)

    def _init_figure(self):
        walls = self.env.walls

        width = np.max(walls[:,:,0])-np.min(walls[:,:,0])
        height = np.max(walls[:,:,1])-np.min(walls[:,:,1])

        self.fig, self.ax = plt.subplots(figsize=(width/25,height/25))

        for w_i in range(walls.shape[0]):
            self.ax.plot(walls[w_i,:,0], walls[w_i,:,1], c='k', linewidth=3)

        start_point = self.env.init_location
        exit_point = self.env.exit_point
        self.ax.scatter(start_point[0], start_point[1], color=[0.0,0.6,0.3], s=96, marker='s')
        self.ax.scatter(exit_point[0], exit_point[1], color=[0.9,0.2,0.0], s=128, marker='*')

        self.ax.axis('off')

    def start_generation(self, generation):
        self.generation = generation

    def _update_path(self, genomes, config):
        genome_reward = max(genomes.values(), key=lambda z: z.fitness)
        if genome_reward.fitness > self.best_reward:
            self.best_reward = genome_reward.fitness
            self.best_path = self._get_path(genome_reward, config)

    def _get_path(self, genome, config):
        controller = neat_cppn.nn.FeedForwardNetwork.create(genome, config)
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
        scatter_data = self.ax.scatter(current_data[:,0], current_data[:,1], s=2.0, color='y', alpha=0.5)

        line_best = self.ax.plot(self.best_path[:,0], self.best_path[:,1], linewidth=3, c='b', alpha=0.7)

        filename = os.path.join(self.save_dir,f'{self.generation}.jpg')
        plt.savefig(filename, bbox_inches='tight')

        if not self.no_plot:
            plt.pause(0.01)

        line_best.pop(0).remove()
        scatter_data.remove()

        self.ax.scatter(current_data[:,0], current_data[:,1], s=1.0, facecolor='gray', alpha=0.7)

    def found_solution(self, config, generation, best):
        plt.clf()
        plt.close('all')
