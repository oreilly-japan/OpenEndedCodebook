import os
import csv
import time
import random
import numpy as np

import multiprocessing
from multiprocessing import Process

from stable_baselines3 import PPO

from ppo.utils import make_vec_envs

class Simulator:
    def __init__(self, env_id, load_path, history_file, deterministic=False):
        self.env_id = env_id
        self.load_path = load_path
        self.history_file = os.path.join(self.load_path, history_file)
        self.deterministic = deterministic
        self.generation = -1
        self.robot = None
        self.controller = None
        self.env = None

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
                structure_file = os.path.join(self.load_path, 'structure', f'{latest[1]}.npz')
                controller_file = os.path.join(self.load_path, 'controller', f'{latest[1]}.zip')

                structure = np.load(structure_file)
                self.robot = (structure['robot'], structure['connectivity'])
                self.controller = PPO.load(controller_file)
                if self.env is not None:
                    self.env.close()
                self.env = make_vec_envs(self.env_id, self.robot, 0, 1)
                self.generation = int(latest[0])
                print(f'simulator update controller: generation {latest[0]}  id {latest[1]}')
        else:
            time.sleep(1)

    def simulate(self):
        if self.robot is None or self.controller is None or self.env is None:
            return

        done = False
        obs = self.env.reset()
        while not done:
            action, _ = self.controller.predict(obs, deterministic=self.deterministic)
            obs, _, done, infos = self.env.step(action)
            self.env.render()


def run_process(env_id, load_path, history_file, generations, deterministic=False):
    simulator = Simulator(env_id, load_path, history_file, deterministic=deterministic)
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
    def __init__(self, env_id, load_path, history_file, generations, deterministic=False):
        self.env_id = env_id
        self.load_path = load_path
        self.history_file = history_file
        self.generations = generations
        self.deterministic = deterministic
        self.process = None

    def __del__(self):
        self.process.terminate()

    def init_process(self):
        multiprocessing.set_start_method("spawn", force=True)
        self.process = Process(
            target=run_process,
            args=(self.env_id, self.load_path, self.history_file, self.generations, self.deterministic))

    def start(self):
        self.process.start()

    def terminate(self):
        self.process.terminate()
