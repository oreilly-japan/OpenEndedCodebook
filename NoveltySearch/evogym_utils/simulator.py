import os
import csv
import time
import pickle
import numpy as np

import multiprocessing
from multiprocessing import Process

from gym_utils import make_vec_envs

import ns_neat

class Simulator:
    def __init__(self, env_id, structure, load_path, history_file, neat_config):
        self.load_path = load_path
        self.history_file = os.path.join(self.load_path, history_file)
        self.neat_config = neat_config
        self.generation = -1
        self.controller = None
        self.env = make_vec_envs(env_id, structure, 0, 1)

    def update(self):
        if not os.path.exists(self.history_file):
            return

        lines = []
        with open(self.history_file, 'r') as f:
            reader = csv.reader(f)
            lines = list(reader)

        columns = lines[0]
        assert columns[0]=='generation' and columns[1]=='id',\
            'simulator error: history_novelty_file columns is supposed to [generation, id, ...]'

        if len(lines)>1:
            latest = lines[-1]
            if self.generation<int(latest[0]):
                genome_file = os.path.join(self.load_path, 'genome', f'{latest[1]}.pickle')

                with open(genome_file, 'rb') as f:
                    genome = pickle.load(f)

                self.controller = ns_neat.nn.FeedForwardNetwork.create(genome, self.neat_config)
                self.generation = int(latest[0])
                print(f'simulator update controller: generation {latest[0]}  id {latest[1]}')
        else:
            time.sleep(1)

    def simulate(self):
        if self.controller is None:
            return

        done = False
        obs = self.env.reset()
        while not done:
            action = np.array(self.controller.activate(obs[0]))*2 - 1
            obs, _, done, infos = self.env.step([np.array(action)])
            self.env.render()


def run_process(env_id, structure, load_path, history_file, neat_config, generations):
    simulator = Simulator(env_id, structure, load_path, history_file, neat_config)
    count = 0
    while simulator.generation < generations-1:
        try:
            simulator.update()
            count = 0
        except:
            count += 1
            if count>10:
                raise RuntimeError('simulater has something problem.')
        simulator.simulate()


class SimulateProcess:
    def __init__(self, env_id, structure, load_path, history_file, neat_config, generations):
        self.env_id = env_id
        self.structure = structure
        self.load_path = load_path
        self.history_file = history_file
        self.neat_config = neat_config
        self.generations = generations
        self.process = None

    def __del__(self):
        self.process.terminate()

    def init_process(self):
        multiprocessing.set_start_method("spawn", force=True)
        self.process = Process(
            target=run_process,
            args=(self.env_id, self.structure, self.load_path, self.history_file, self.neat_config, self.generations))

    def start(self):
        self.process.start()

    def terminate(self):
        self.process.terminate()
