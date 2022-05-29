import os
import numpy as np

import matplotlib.pyplot as plt

from .reporting import BaseReporter


class BDDrawer(BaseReporter):
    def __init__(self, save_path, bd1, bd2, no_plot=False):
        self.save_path = save_path
        self.no_plot = no_plot

        self.figure_path = os.path.join(self.save_path, 'bd_map')
        os.makedirs(self.figure_path, exist_ok=True)

        self.fig = None
        self.ax = None
        self._init_figure()

        self.bd1_name = None
        self.bd2_name = None
        self.axis_bd1 = None
        self.axis_bd2 = None
        self._set_bd_to_figure(bd1, bd2)

    def __del__(self):
        plt.clf()
        plt.close('all')

    def _init_figure(self):
        self.fig, self.ax = plt.subplots(figsize=(5*1.2, 5))

        self.ax.set_title('behavioral descriptor 2d map')

    def _set_bd_to_figure(self, bd1, bd2):
        self.bd1_name = bd1.name
        self.bd2_name = bd2.name

        self.axis2, self.axis1 = np.meshgrid(np.array(bd2.bins), np.array(bd1.bins))

        self.ax.set_xlabel(bd1.name)
        self.ax.set_ylabel(bd2.name)

    def start_generation(self, generation):
        self.generation = generation

    def end_generation(self, config, population):

        bd_map = np.full(self.axis1.shape, -np.inf)
        vmin = 0
        vmax = 0
        for _, genome in population.items():
            bd1 = genome.bd[self.bd1_name]
            bd2 = genome.bd[self.bd2_name]
            bd_map[bd1, bd2] = genome.fitness
            vmin = min(vmin, genome.fitness)
            vmax = max(vmax, genome.fitness)
        vmax += (vmax-vmin)*0.05

        cmap = plt.get_cmap('gist_earth')
        pcm = self.ax.pcolormesh(self.axis1, self.axis2, bd_map, cmap=cmap, vmin=vmin, vmax=vmax)
        cb = self.fig.colorbar(pcm, ax=self.ax)

        filename = os.path.join(self.figure_path, f'{self.generation}.jpg')
        self.fig.savefig(filename, bbox_inches='tight')

        if not self.no_plot:
            plt.pause(0.1)

        cb.remove()
        pcm.remove()

    def found_solution(self, config, generation, best):
        plt.clf()
        plt.close('all')
