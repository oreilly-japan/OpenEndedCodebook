import sys
import os
from copy import deepcopy
import numpy as np

import matplotlib.pyplot as plt


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import me_neat


class StructureDecoder:
    def __init__(self, size):
        self.size = size

        x, y = np.meshgrid(np.arange(size[0]), np.arange(size[1]), indexing='ij')
        x = x.flatten()
        y = y.flatten()

        center = (np.array(size) - 1) / 2
        d = np.sqrt(np.square(x - center[0]) + np.square(y - center[1]))

        # inputs: [x, y, d] * (robot size)
        self.inputs = np.vstack([x, y, d]).T
        self.types = ['empty', 'rigid', 'soft', 'horizontal', 'vertical']

    def decode(self, genome, config):
        cppn = me_neat.FeedForwardNetwork.create(genome, config)

        print('( x,  y) :   empty   rigid   soft    hori    vert ')
        print('            ======  ======  ======  ======  ======')
        states = {}
        for inp in self.inputs:
            state = cppn.activate(inp)
            pos_x = int(inp[0])
            pos_y = int(inp[1])

            m = np.argmax(state)
            voxel_type = self.types[m]
            print(f'({pos_x: =2}, {pos_y: =2}) :  ' +
                '  '.join(('*' if i==m else ' ') + f'{v: =+.2f}' for i,v in enumerate(state)) +
                f'  ->  {voxel_type.rjust(10)}'
            )
            states[(int(inp[0]), int(inp[1]))] = voxel_type
        print()

        return states

class RobotDrawer:
    def __init__(self, size):
        self.size = size
        fig, self.ax = plt.subplots(figsize=size)
        self.colors = {
            'empty': [1, 1, 1],
            'rigid': [0.15, 0.15, 0.15],
            'soft': [0.75, 0.75, 0.75],
            'horizontal': [0.93, 0.58, 0.31],
            'vertical': [0.49, 0.68, 0.83]
        }

    def draw(self, state):
        self.ax.cla()
        for (x,y), voxel in state.items():
            color = self.colors[voxel]
            self.ax.fill_between([x, x+1], [y]*2, [y+1]*2, color=color)
        self.ax.grid()
        self.ax.set_xlim([0, self.size[0]])
        self.ax.set_ylim([0, self.size[1]])
        self.ax.invert_yaxis()

        plt.pause(0.01)

    

def reset_genome(config):
    genome = config.genome_type(1)
    genome.configure_new(config.genome_config)
    return genome

def mutate_genome(genome, config):
    new_genome = deepcopy(genome)
    new_genome.key = genome.key + 1
    new_genome.mutate(config.genome_config)
    return new_genome

def main():
    robot_size = (5, 5)
    
    decoder = StructureDecoder(robot_size)
    drawer = RobotDrawer(robot_size)

    config_file = os.path.join(CURR_DIR, 'config', 'evogym_me_cppn.cfg')
    config = me_neat.make_config(config_file)

    genome = reset_genome(config)
    states = decoder.decode(genome, config.genome_config)
    drawer.draw(states)

    while True:
        print('put the operation (m: mutate, r: reset genome, else: finish): ', end='')
        operation = input()
        if operation == 'm':
            genome = mutate_genome(genome, config)
        elif operation == 'r':
            genome = reset_genome(config)
        else:
            break

        states = decoder.decode(genome, config.genome_config)
        drawer.draw(states)
        





if __name__=='__main__':
    main()
