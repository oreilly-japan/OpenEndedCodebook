import os, sys
import copy
from itertools import count
from collections import OrderedDict
import numpy as np
import torch


from gym_utils import make_vec_envs

from a2c_ppo_acktr import algo
from a2c_ppo_acktr.model import Policy
from a2c_ppo_acktr.storage import RolloutStorage


def dummy():
    return

def update_linear_schedule(optimizer, epoch, total_num_epochs, initial_lr):
    """Decreases the learning rate linearly"""
    lr = initial_lr - (initial_lr * (epoch / float(total_num_epochs)))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


def transfer_step(make_env_kwargs, config, params, obs_rms):
    envs = make_vec_envs(**make_env_kwargs)
    envs.obs_rms = obs_rms

    actor_critic = Policy(
        envs.observation_space.shape,
        envs.action_space,
        base_kwargs={'recurrent': config.recurrent_policy})
    actor_critic.to('cpu')

    actor_critic.load_state_dict(params)

    agent = algo.PPO(
        actor_critic,
        config.clip_param,
        config.ppo_epoch,
        config.num_mini_batch,
        config.value_loss_coef,
        config.entropy_coef,
        lr=config.lr,
        eps=config.eps,
        max_grad_norm=config.max_grad_norm)

    rollouts = RolloutStorage(config.num_steps, config.num_processes,
                              envs.observation_space.shape, envs.action_space,
                              actor_critic.recurrent_hidden_state_size)

    obs = envs.reset()
    rollouts.obs[0].copy_(torch.from_numpy(obs))
    rollouts.to('cpu')

    for j in range(config.transfer_steps):

        for step in range(config.num_steps):
            with torch.no_grad():
                value, action, action_log_prob, recurrent_hidden_states = actor_critic.act(
                    rollouts.obs[step], rollouts.recurrent_hidden_states[step],
                    rollouts.masks[step])

            obs, reward, done, infos = envs.step(action)

            masks = torch.FloatTensor(
                [[0.0] if done_ else [1.0] for done_ in done])
            bad_masks = torch.FloatTensor(
                [[0.0] if 'bad_transition' in info.keys() else [1.0]
                 for info in infos])
            rollouts.insert(torch.from_numpy(obs), recurrent_hidden_states, action,
                            action_log_prob, value, torch.unsqueeze(torch.from_numpy(reward),1), masks, bad_masks)

        with torch.no_grad():
            next_value = actor_critic.get_value(
                rollouts.obs[-1], rollouts.recurrent_hidden_states[-1],
                rollouts.masks[-1]).detach()

        rollouts.compute_returns(next_value, config.use_gae, config.gamma,
                                 config.gae_lambda, config.use_proper_time_limits)

        value_loss, action_loss, dist_entropy = agent.update(rollouts)

        rollouts.after_update()

    params = actor_critic.state_dict()
    obs_rms = envs.obs_rms

    return params, obs_rms


def evaluate(make_env_kwargs, recurrent, params, obs_rms):
    envs = make_vec_envs(**make_env_kwargs)
    envs.training = False
    envs.obs_rms = obs_rms

    actor_critic = Policy(
        envs.observation_space.shape,
        envs.action_space,
        base_kwargs={'recurrent': recurrent})
    actor_critic.to('cpu')

    actor_critic.load_state_dict(params)

    obs = envs.reset()
    done = False
    recurrent_hidden_states = torch.zeros(
        1, actor_critic.recurrent_hidden_state_size, device='cpu')
    masks = torch.zeros(1, 1, device='cpu')
    while not done:
        _, action, _, recurrent_hidden_states = actor_critic.act(torch.from_numpy(obs), recurrent_hidden_states, masks, deterministic=True)
        obs, _, done, infos = envs.step(action.detach())

        if 'episode' in infos[0]:
            reward = infos[0]['episode']['r']

    return reward



class OptimizerPPO():
    def __init__(self, key, params=None, obs_rms=None):
        self.key = key
        self.params = params
        self.obs_rms = obs_rms
        self.envs = None
        self.actor_critic = None
        self.agent = None
        self.rollouts = None
        self.step_count = 0

    def set_env_info(self, make_env_kwargs, config):
        self.make_env_kwargs_main = {**make_env_kwargs, **{'num_processes': config.num_processes, 'vecnormalize': True, 'subproc': True}}
        self.make_env_kwargs_transfer = {**make_env_kwargs, **{'num_processes': config.num_processes, 'vecnormalize': True, 'subproc': False}}
        self.make_env_kwargs_eval = {**make_env_kwargs, **{'num_processes': 1, 'vecnormalize': True}}

    def get_core(self):
        return self.params, self.obs_rms


    def reproduce(self, config):
        key = config.get_new_opt_key()
        params, obs_rms = self.get_core()
        child = OptimizerPPO(key, params=copy.deepcopy(params), obs_rms=copy.deepcopy(obs_rms))
        return child

    def archive(self):
        del self.envs
        del self.agent
        del self.rollouts

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

        self.actor_critic = Policy(
            self.envs.observation_space.shape,
            self.envs.action_space,
            base_kwargs={'recurrent': config.recurrent_policy})

        if self.params is not None:
            params_ = OrderedDict(self.params.items())
            action_size = self.params['dist.logstd._bias'].shape
            params_['dist.logstd._bias'] = torch.zeros(action_size)
            self.actor_critic.load_state_dict(params_)

        self.agent = algo.PPO(
            self.actor_critic,
            config.clip_param,
            config.ppo_epoch,
            config.num_mini_batch,
            config.value_loss_coef,
            config.entropy_coef,
            lr=config.lr,
            eps=config.eps,
            max_grad_norm=config.max_grad_norm)

        self.rollouts = RolloutStorage(config.num_steps, config.num_processes,
            self.envs.observation_space.shape, self.envs.action_space,
            self.actor_critic.recurrent_hidden_state_size)

        obs = self.envs.reset()
        self.rollouts.obs[0].copy_(torch.from_numpy(obs))
        self.rollouts.to('cpu')

        self.step_count = 0
    

    def get_evaluate(self, config, core=None):
        if core is None:
            params, obs_rms = self.get_core()
        else:
            params, obs_rms = core

        func = evaluate
        kwargs = {
            'make_env_kwargs': self.make_env_kwargs_eval,
            'recurrent': config.recurrent_policy,
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
                'make_env_kwargs': self.make_env_kwargs_transfer,
                'config': config,
                'params': params,
                'obs_rms': obs_rms}
            }
            return func, kwargs

    def step_self(self, config):
        for _ in range(config.steps_per_iteration):

            if config.use_linear_lr_decay:
                update_linear_schedule(self.agent.optimizer, self.step_count, config.max_steps, config.lr)

            for step in range(config.num_steps):
                with torch.no_grad():
                    value, action, action_log_prob, recurrent_hidden_states = self.actor_critic.act(
                        self.rollouts.obs[step], self.rollouts.recurrent_hidden_states[step],
                        self.rollouts.masks[step])

                obs, reward, done, infos = self.envs.step(action)

                masks = torch.FloatTensor(
                    [[0.0] if done_ else [1.0] for done_ in done])
                bad_masks = torch.FloatTensor(
                    [[0.0] if 'bad_transition' in info.keys() else [1.0]
                    for info in infos])
                self.rollouts.insert(torch.from_numpy(obs), recurrent_hidden_states, action,
                                action_log_prob, value, torch.unsqueeze(torch.from_numpy(reward),1), masks, bad_masks)

            with torch.no_grad():
                next_value = self.actor_critic.get_value(
                    self.rollouts.obs[-1], self.rollouts.recurrent_hidden_states[-1],
                    self.rollouts.masks[-1]).detach()

            self.rollouts.compute_returns(next_value, config.use_gae, config.gamma,
                                    config.gae_lambda, config.use_proper_time_limits)

            value_loss, action_loss, dist_entropy = self.agent.update(self.rollouts)

            self.rollouts.after_update()

            self.step_count += 1

    def step(self, results, config, core=None, update=True):
        if core is None:
            self.params = self.actor_critic.state_dict()
            self.obs_rms = self.envs.obs_rms
            return self.params, self.obs_rms
        else:
            params, obs_rms = results['hoge']
            return params, obs_rms



class OptimizerPPOConfig():
    def __init__(self,
                 steps_per_iteration=4,
                 transfer_steps=4,
                 clip_param=0.1,
                 ppo_epoch=4,
                 num_mini_batch=4,
                 num_steps=128,
                 num_processes=4,
                 gamma=0.99,
                 lr=2.5e-4,
                 eps=1e-5,
                 use_gae=True,
                 gae_lambda=0.95,
                 entropy_coef=0.01,
                 value_loss_coef=0.5,
                 max_grad_norm=0.5,
                 use_linear_lr_decay=True,
                 max_steps=4*10000,
                 use_proper_time_limits=False,
                 recurrent_policy=False):
        self.indexer = count(0)

        self.steps_per_iteration = steps_per_iteration
        self.transfer_steps = transfer_steps
        self.clip_param = clip_param
        self.ppo_epoch = ppo_epoch
        self.num_mini_batch = num_mini_batch
        self.num_steps = num_steps
        self.num_processes = num_processes
        self.gamma = gamma
        self.lr = lr
        self.eps = eps
        self.use_gae = use_gae
        self.gae_lambda = gae_lambda
        self.entropy_coef = entropy_coef
        self.value_loss_coef = value_loss_coef
        self.max_grad_norm = max_grad_norm
        self.use_linear_lr_decay = use_linear_lr_decay
        self.max_steps = max_steps
        self.use_proper_time_limits = use_proper_time_limits
        self.recurrent_policy = recurrent_policy
        

    def get_new_opt_key(self):
        return next(self.indexer)

    def make_init(self):
        key = self.get_new_opt_key()
        optimizer = OptimizerPPO(
            key=key,
        )
        return optimizer