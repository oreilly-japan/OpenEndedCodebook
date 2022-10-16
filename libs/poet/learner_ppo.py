import os, sys
import copy
from itertools import count
from collections import OrderedDict
import numpy as np
import torch


from gym_utils import make_vec_envs

from ppo import PPO, Policy


def dummy():
    return


def transfer_step(env_kwargs, config, params, obs_rms):
    envs = make_vec_envs(**env_kwargs)
    envs.obs_rms = obs_rms

    policy = Policy(
        envs.observation_space,
        envs.action_space,
        init_log_std=config.init_log_std,
        device='cpu'
    )

    policy.load_state_dict(params)

    algo = PPO(
        policy,
        envs,
        learning_rate=config.learning_rate,
        n_steps=config.steps,
        batch_size=config.batch_size,
        n_epochs=config.epochs,
        gamma=config.gamma,
        gae_lambda=config.gae_lambda,
        clip_range=config.clip_range,
        clip_range_vf=config.clip_range,
        normalize_advantage=True,
        ent_coef=config.ent_coef,
        vf_coef=config.vf_coef,
        max_grad_norm=config.max_grad_norm,
        device='cpu',
        lr_decay=False)

    for _ in range(config.transfer_steps):
        algo.step()

    params = policy.state_dict()
    obs_rms = envs.obs_rms

    envs.close()

    return params, obs_rms


def evaluate(env_kwargs, params, obs_rms):
    envs = make_vec_envs(**env_kwargs)
    envs.training = False
    envs.obs_rms = obs_rms

    policy = Policy(envs.observation_space, envs.action_space, device='cpu')
    policy.load_state_dict(params)

    obs = envs.reset()
    done = False
    while not done:
        with torch.no_grad():
            action = policy.predict(obs, deterministic=True)
        obs, _, done, infos = envs.step(action)

        if 'episode' in infos[0]:
            reward = infos[0]['episode']['r']

    envs.close()

    return reward



class OptimizerPPO:
    def __init__(self, key, params=None, obs_rms=None):
        self.key = key
        self.params = params
        self.obs_rms = obs_rms
        self.envs = None
        self.policy = None
        self.algo = None

    def set_env_info(self, make_env_kwargs, config):
        self.make_env_kwargs_main = dict(
            **make_env_kwargs,
            num_processes=config.num_processes,
            gamma=config.gamma,
            vecnormalize=True,
            subproc=True)
        self.make_env_kwargs_transfer = dict(
            **make_env_kwargs,
            num_processes=config.num_processes,
            vecnormalize=True,
            subproc=False)
        self.make_env_kwargs_eval = dict(
            **make_env_kwargs,
            num_processes=1,
            vecnormalize=True,
            subproc=False)

    def get_core(self):
        return self.params, self.obs_rms


    def reproduce(self, config):
        key = config.get_new_opt_key()
        params, obs_rms = self.get_core()
        child = OptimizerPPO(key, params=copy.deepcopy(params), obs_rms=copy.deepcopy(obs_rms))
        return child

    def archive(self):
        self.envs.close()
        del self.envs
        del self.algo

    def admitted(self, config):
        self.envs = make_vec_envs(**self.make_env_kwargs_main)
        self.build(config)


    def save(self, path):
        pass

    def save_core(self, path, name):
        filename = os.path.join(path, f'{name}.pt')
        params, obs_rms = self.get_core()
        torch.save([params, obs_rms], filename)


    def set_core(self, core, config, reset=True):
        params, obs_rms = core
        self.params = copy.deepcopy(params)
        self.obs_rms = copy.deepcopy(obs_rms)
        if self.envs is not None:
            self.build(config)

    def build(self, config):
        if self.obs_rms is not None:
            self.envs.obs_rms = self.obs_rms

        self.policy = Policy(
            self.envs.observation_space,
            self.envs.action_space,
            init_log_std=config.init_log_std,
            device='cpu')

        if self.params is not None:
            params_ = OrderedDict(self.params.items())
            action_size = self.params['log_std'].shape
            params_['log_std'] = torch.full(action_size, config.init_log_std)
            self.policy.load_state_dict(params_)

        self.algo = PPO(
            self.policy,
            self.envs,
            learning_rate=config.learning_rate,
            n_steps=config.steps,
            batch_size=config.batch_size,
            n_epochs=config.epochs,
            gamma=config.gamma,
            gae_lambda=config.gae_lambda,
            clip_range=config.clip_range,
            clip_range_vf=config.clip_range,
            normalize_advantage=True,
            ent_coef=config.ent_coef,
            vf_coef=config.vf_coef,
            max_grad_norm=config.max_grad_norm,
            device='cpu',
            lr_decay=config.lr_decay,
            max_iter=config.max_steps)


    def get_evaluate(self, config, core=None):
        if core is None:
            params, obs_rms = self.get_core()
        else:
            params, obs_rms = core

        func = evaluate
        kwargs = {
            'env_kwargs': self.make_env_kwargs_eval,
            'params': params,
            'obs_rms': obs_rms}
        return func, kwargs


    def get_step(self, config, core=None):
        if core is None:
            self.step_self(config)
            func = dummy
            kwargs = {'hoge': {}}
            return func, kwargs
        else:
            params, obs_rms = core

            func = transfer_step
            kwargs = {'hoge': {
                'env_kwargs': self.make_env_kwargs_transfer,
                'config': config,
                'params': params,
                'obs_rms': obs_rms}
            }
            return func, kwargs

    def step_self(self, config):
        for _ in range(config.steps_per_iteration):
            self.algo.step()

    def step(self, results, config, core=None, update=True):
        if core is None:
            self.params = self.policy.state_dict()
            self.obs_rms = self.envs.obs_rms
            return self.params, self.obs_rms
        else:
            params, obs_rms = results['hoge']
            return params, obs_rms



class OptimizerPPOConfig:
    def __init__(self,
                 steps_per_iteration=4,
                 transfer_steps=4,
                 clip_range=0.1,
                 epochs=4,
                 num_mini_batch=4,
                 steps=128,
                 num_processes=4,
                 gamma=0.99,
                 learning_rate=2.5e-4,
                 gae_lambda=0.95,
                 ent_coef=0.01,
                 vf_coef=0.5,
                 max_grad_norm=0.5,
                 lr_decay=True,
                 init_log_std=0.0,
                 max_steps=2000):
        self.indexer = count(0)

        self.steps_per_iteration = steps_per_iteration
        self.transfer_steps = transfer_steps
        self.clip_range = clip_range
        self.epochs = epochs
        self.batch_size = steps * num_processes // num_mini_batch
        self.steps = steps
        self.num_processes = num_processes
        self.gamma = gamma
        self.learning_rate = learning_rate
        self.gae_lambda = gae_lambda
        self.ent_coef = ent_coef
        self.vf_coef = vf_coef
        self.max_grad_norm = max_grad_norm
        self.lr_decay = lr_decay
        self.init_log_std = init_log_std
        self.max_steps = max_steps
        

    def get_new_opt_key(self):
        return next(self.indexer)

    def make_init(self):
        key = self.get_new_opt_key()
        optimizer = OptimizerPPO(
            key=key,
        )
        return optimizer