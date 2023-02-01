import os
import csv
import time
import pickle
import numpy as np
import torch

import multiprocessing
from multiprocessing import Process

from ppo import Policy

from gym_utils import make_vec_envs


class EvogymControllerSimulator:
    def __init__(self, env_id, robot, decode_function, load_path, history_file, genome_config):
        self.env_id = env_id
        self.robot = robot
        self.decode_function = decode_function
        self.load_path = load_path
        self.history_file = os.path.join(load_path, history_file)
        self.genome_config = genome_config
        self.generation = None
        self.env = None
        self.controller = None

    def initialize(self):
        self.generation = -1
        self.env = make_vec_envs(self.env_id, self.robot, 0, 1)

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

class EvogymControllerSimulatorPPO:
    def __init__(self, env_id, robot, load_path, interval, deterministic=True):
        self.env_id = env_id
        self.robot = robot
        self.load_path = load_path
        self.interval = interval
        self.deterministic = deterministic
        self.iter = -interval
        self.generation = self.iter
        self.env = None
        self.controller = None

    def initialize(self):
        self.generation = -1
        self.env = make_vec_envs(self.env_id, self.robot, 0, 1, vecnormalize=True)
        self.env.training = False
        self.controller = Policy(self.env.observation_space, self.env.action_space, device='cpu')

    def update(self):

        iter = self.iter + self.interval
        controller_file = os.path.join(self.load_path, f'{iter}.pt')
        while os.path.exists(controller_file):
            iter += self.interval
            controller_file = os.path.join(self.load_path, f'{iter}.pt')

        if self.iter==iter:
            time.sleep(0.1)
            return

        if self.iter < iter-self.interval:
            self.iter = iter - self.interval
            self.generation = self.iter
            controller_file = os.path.join(self.load_path, f'{self.iter}.pt')

            params, obs_rms = torch.load(controller_file)
            self.controller.load_state_dict(params)
            self.env.obs_rms = obs_rms
            
            print(f'simulator update controller: iter {self.iter}')


    def simulate(self):
        if self.controller is None or self.env is None:
            return

        done = False
        obs = self.env.reset()
        while not done:
            with torch.no_grad():
                action = self.controller.predict(obs, deterministic=self.deterministic)
            obs, _, done, infos = self.env.step(action)
            self.env.render()

            for info in infos:
                if 'episode' in info:
                    reward = info['episode']['r']
                    print(f'simulator reward: {reward: =.5f}')


class EvogymStructureSimulator:
    def __init__(self, env_id, load_path, history_file, deterministic=True):
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
                robot_file = os.path.join(self.load_path, 'robot', f'{latest[1]}.npz')
                controller_file = os.path.join(self.load_path, 'controller', f'{latest[1]}.pt')

                robot = np.load(robot_file)

                if self.env is not None:
                    self.env.close()

                self.env = make_vec_envs(self.env_id, robot, 0, 1, vecnormalize=True)
                self.env.training = False
                self.controller = Policy(self.env.observation_space, self.env.action_space, device='cpu')

                params, obs_rms = torch.load(controller_file)
                self.controller.load_state_dict(params)
                self.env.obs_rms = obs_rms

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
            with torch.no_grad():
                action = self.controller.predict(obs, deterministic=self.deterministic)
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


class SimulateProcess:
    def __init__(self, simulator, generations):
        self.simulator = simulator
        self.generations = generations
        self.process = None

    def __del__(self):
        if self.simulator.env is not None:
            self.simulator.env.close()
            
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
