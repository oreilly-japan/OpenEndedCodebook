import os
import time
# from copy import deepcopy
import numpy as np
import torch

from multiprocessing import Process

from stable_baselines3 import PPO
from stable_baselines3.common.utils import get_linear_fn

from utils import make_vec_envs


def simulate(ppo_file, make_env_func, make_env_args, deterministic):
    env = make_env_func(*make_env_args)

    while True:
        # print('a')
        model = PPO.load(ppo_file)
        done = False
        obs = env.reset()
        while not done:
            action, _states = model.predict(obs,deterministic=deterministic)
            # print(action)
            obs, _, done, infos = env.step(action)
            env.render()

            for info in infos:
                if 'episode' in info:
                    reward = info['episode']['r']
                    print(f'reward: {reward: =.5f}')


class Runner():
    def __init__(self, make_env_func, make_env_args, deterministic):
        self.make_env_func = make_env_func
        self.make_env_args = make_env_args
        self.deterministic = deterministic
        self.model = None
        self.process = None

    def set_model(self,model):
        # self.model = deepcopy(model)
        self.model = model

    def excute(self):
        kwargs = {
            'model': self.model,
            'make_env_func': self.make_env_func,
            'make_env_args': self.make_env_args,
            'deterministic': self.deterministic,
        }
        self.process = Process(target=simulate, kwargs=kwargs)
        self.process.start()

    def terminate(self):
        self.process.terminate()


def run_ppo(
    env_id,
    structure,
    probabilistic):

    num_processes = 4

    ppo_steps = 2**7
    num_mini_batch = 2*2
    ppo_epochs = 2**3

    num_update = 100
    learning_steps = 2**5 * ppo_steps * num_processes

    ppo_tmp_file = '.ppo/tmp'
    os.makedirs('.ppo/',exist_ok=True)

    # runner = Runner(make_vec_envs, (env_id,structure,0,1), not probabilistic)


    train_env = make_vec_envs(env_id, structure, 0, num_processes)
    train_env.reset()

    model = PPO(
        "MlpPolicy",
        train_env,
        n_steps=ppo_steps*num_processes,
        batch_size=ppo_steps//num_mini_batch*num_processes,
        n_epochs=ppo_epochs,
        learning_rate=3e-4,
        verbose=0,
        clip_range=0.3,
        ent_coef=0.01,
        policy_kwargs={'log_std_init': 0.0, 'ortho_init': True,'squash_output':True})

    model.save(ppo_tmp_file)

    # print(model.policy)
    # print(model.policy.requires_grad)

    # runner.set_model(model.policy)

    p = Process(
        target=simulate,
        kwargs={
            'ppo_file':ppo_tmp_file,
            'make_env_func': make_vec_envs,
            'make_env_args': (env_id,structure,0,1),
            'deterministic': not probabilistic
        }
    )
    p.start()

    for i in range(num_update):
        # runner.excute()
        start = time.time()
        model.learn(total_timesteps=learning_steps)
        model.save(ppo_tmp_file)
        # model.policy.optimizer.zero_grad()
        print(f'\nupdate: {i+1}  elapsed time: {time.time()-start: =.3f}  log_std: {np.mean(model.policy.log_std.detach().numpy()): =.3f}')
        # runner.terminate()
        # runner.set_model(model.policy)

    p.terminate()
