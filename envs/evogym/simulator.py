import os
import csv
import time
import pickle
import numpy as np

import multiprocessing
from multiprocessing import Process
from pyrsistent import s

from stable_baselines3 import PPO

from gym_utils import make_vec_envs


class EvogymControllerSimulator():
    def __init__(self, env_id, structure, decode_function, load_path, history_file, genome_config):
        self.env_id = env_id
        self.structure = structure
        self.decode_function = decode_function
        self.load_path = load_path
        self.history_file = os.path.join(load_path, history_file)
        self.genome_config = genome_config
        self.generation = None
        self.env = None
        self.controller = None

    def initialize(self):
        self.generation = -1
        self.env = make_vec_envs(self.env_id, self.structure, 0, 1)

    def update(self):
        if not os.path.exists(self.history_file):
            time.sleep(0.1)
            return

        lines = []
        with open(self.history_file, 'r') as f:
            reader = csv.reader(f)
            lines = list(reader)

        columns = lines[0]
        assert columns[0]=='generation' and columns[1]=='id',\
            f'simulator error: {self.history_file} columns is supposed to [generation, id, ...]'

        if len(lines)>1:
            latest = lines[-1]
            if self.generation<int(latest[0]):
                genome_file = os.path.join(self.load_path, 'genome', f'{latest[1]}.pickle')

                with open(genome_file, 'rb') as f:
                    genome = pickle.load(f)

                self.controller = self.decode_function(genome, self.genome_config)
                self.generation = int(latest[0])
                print(f'simulator update controller: generation {latest[0]}  id {latest[1]}')
        else:
            time.sleep(0.1)

    def simulate(self):
        if self.controller is None:
            return

        done = False
        obs = self.env.reset()
        while not done:
            action = np.array(self.controller.activate(obs[0]))*2 - 1
            obs, _, done, infos = self.env.step([np.array(action)])
            self.env.render()

class EvogymControllerSimulatorPPO():
    def __init__(self, env_id, structure, load_path, deterministic=False):
        self.env_id = env_id
        self.structure = structure
        self.load_path = load_path
        self.deterministic = deterministic
        self.iter = -1
        self.generation = self.iter
        self.env = None
        self.controller = None

    def initialize(self):
        self.generation = -1
        self.env = make_vec_envs(self.env_id, self.structure, 0, 1, vecnormalize=True)
        self.env.training = False

    def update(self):

        iter = self.iter + 1
        controller_file = os.path.join(self.load_path, f'{iter}.zip')
        while os.path.exists(controller_file):
            iter += 1
            controller_file = os.path.join(self.load_path, f'{iter}.zip')

        if self.iter==iter-1:
            time.sleep(0.1)
            return

        if self.iter < iter-1:
            self.iter = iter - 1
            self.generation = self.iter
            controller_file = os.path.join(self.load_path, f'{self.iter}.zip')

            self.controller = PPO.load(controller_file)
            self.env.obs_rms = self.controller.env.obs_rms
            print(f'simulator update controller: iter {self.iter}')


    def simulate(self):
        if self.controller is None or self.env is None:
            return

        done = False
        obs = self.env.reset()
        while not done:
            action, _ = self.controller.predict(obs, deterministic=self.deterministic)
            obs, _, done, infos = self.env.step(action)
            self.env.render()

            for info in infos:
                if 'episode' in info:
                    reward = info['episode']['r']
                    print(f'simulator reward: {reward: =.5f}')


class EvogymStructureSimulator():
    def __init__(self, env_id, load_path, history_file, deterministic=False):
        self.env_id = env_id
        self.load_path = load_path
        self.history_file = os.path.join(self.load_path, history_file)
        self.deterministic = deterministic
        self.generation = None
        self.env = None
        self.controller = None

    def initialize(self):
        self.generation = -1

    def update(self):
        if not os.path.exists(self.history_file):
            time.sleep(0.1)
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
                structure_file = os.path.join(self.load_path, 'structure', f'{latest[1]}.npz')
                controller_file = os.path.join(self.load_path, 'controller', f'{latest[1]}.zip')

                structure_data = np.load(structure_file)
                structure = (structure_data['robot'], structure_data['connectivity'])
                self.controller = PPO.load(controller_file)
                if self.env is not None:
                    self.env.close()
                self.env = make_vec_envs(self.env_id, structure, 0, 1, vecnormalize=True)
                self.env.training = False
                self.env.obs_rms = self.controller.env.obs_rms
                self.generation = int(latest[0])
                print(f'simulator update controller: generation {latest[0]}  id {latest[1]}')
        else:
            time.sleep(0.1)

    def simulate(self):
        if self.controller is None or self.env is None:
            return

        done = False
        obs = self.env.reset()
        while not done:
            action, _ = self.controller.predict(obs, deterministic=self.deterministic)
            obs, _, done, infos = self.env.step(action)
            self.env.render()


def run_process(simulator, generations):
    simulator.initialize()
    count = 0
    while simulator.generation < generations-1:
        try:
            simulator.update()
            count = 0
        except:
            count += 1
            if count>10:
                raise RuntimeError('simulator has something problem.')
        simulator.simulate()


class SimulateProcess():
    def __init__(self, simulator, generations):
        self.simulator = simulator
        self.generations = generations
        self.process = None

    def __del__(self):
        if self.process is not None:
            self.process.terminate()

    def init_process(self):
        multiprocessing.set_start_method("spawn", force=True)
        self.process = Process(
            target=run_process,
            args=(self.simulator, self.generations))

    def start(self):
        self.process.start()

    def terminate(self):
        self.process.terminate()
