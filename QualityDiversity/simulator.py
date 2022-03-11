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
    def __init__(self, env_id, save_dir, deterministic=False):
        self.env_id = env_id
        self.save_dir = save_dir
        self.history_file = os.path.join(self.save_dir, 'history_best.csv')
        self.deterministic = deterministic
        self.generation = -1
        self.robot = None
        self.model = None
        self.env = None

    def update(self):
        if not os.path.exists(self.history_file):
            return

        lines = []
        with open(self.history_file, 'r') as f:
            reader = csv.reader(f)
            lines = list(reader)

        columns = lines[0]
        assert columns[0]=='generation' and columns[1]=='birth' and columns[2]=='no.',\
            'simulator error: best_history_file columns is supposed to [generation, birh, no., ...]'

        if len(lines)>1:
            latest = lines[-1]
            if self.generation<int(latest[0]):
                path_generation = os.path.join(self.save_dir, f'generation_{latest[1]}')
                structure_file = os.path.join(path_generation, 'structure', f'{latest[2]}.npz')
                controller_file = os.path.join(path_generation, 'controller', f'{latest[2]}.zip')

                structure = np.load(structure_file)
                self.robot = (structure['robot'], structure['connectivity'])
                self.model = PPO.load(controller_file)
                if self.env is not None:
                    self.env.close()
                self.env = make_vec_envs(self.env_id, self.robot, 0, 1)
                self.generation = int(latest[0])
        else:
            time.sleep(1)

    def simulate(self):
        if self.robot is None or self.model is None or self.env is None:
            return

        done = False
        obs = self.env.reset()
        while not done:
            action, _ = self.model.predict(obs, deterministic=self.deterministic)
            obs, _, done, infos = self.env.step(action)
            self.env.render()


def run_process(env_id, save_dir, generations, deterministic=False):
    simulator = Simulator(env_id, save_dir, deterministic=deterministic)
    while True:
        simulator.update()
        simulator.simulate()

        if simulator.generation > generations:
            break

class SimulateProcess:
    def __init__(self, env_id, save_dir, generations, deterministic=False):
        self.env_id = env_id
        self.save_dir = save_dir
        self.generations = generations
        self.deterministic = deterministic
        self.process = None

    def init_process(self):
        multiprocessing.set_start_method("spawn", force=True)
        self.process = Process(
            target=run_process,
            args=(self.env_id, self.save_dir, self.generations, self.deterministic))

    def start(self):
        self.process.start()

    def terminate(self):
        self.process.terminate()
