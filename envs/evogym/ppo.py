import os
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.utils import get_linear_fn

from gym_utils import make_vec_envs
import ppo_config as default_config

def evaluate(model, envs, num_eval=1, deterministic=False):

    obs = envs.reset()
    episode_rewards = []
    while len(episode_rewards) < num_eval:
        action, _state = model.predict(obs,deterministic=deterministic)
        obs, _, done, infos = envs.step(action)

        for info in infos:
            if 'episode' in info:
                episode_rewards.append(info['episode']['r'])
    return np.mean(episode_rewards)


def run_ppo(env_id, structure, train_iters, save_file, config=None, evaluation=True, deterministic=False, save_iter=None):

    if config is None:
        config = default_config

    train_envs = make_vec_envs(env_id, structure, config.seed, config.num_processes, vecnormalize=True)
    train_envs.reset()

    if evaluation:
        eval_envs = make_vec_envs(env_id, structure, config.seed, config.eval_processes, vecnormalize=True)

    model = PPO(
        "MlpPolicy",
        train_envs,
        n_steps = config.steps * config.num_processes,
        batch_size = config.steps // config.num_mini_batch * config.num_processes,
        n_epochs = config.epochs,
        learning_rate = config.learning_rate,
        verbose = 0,
        gamma = config.gamma,
        clip_range = config.clip_range,
        ent_coef = config.ent_coef,
        policy_kwargs = config.policy_kwargs)

    if save_iter is not None:
        model.save(os.path.join(save_file, '0'), include=['env'])

    steps_by_iter = config.learning_steps * config.steps * config.num_processes
    max_reward = float('-inf')

    for i in range(train_iters):

        model.learn(total_timesteps=steps_by_iter)

        if evaluation:
            eval_envs.obs_rms = train_envs.obs_rms
            reward = evaluate(model, eval_envs, num_eval=config.eval_processes, deterministic=deterministic)
            if reward > max_reward:
                max_reward = reward
                model.save(save_file, include=['env'])

        if save_iter is not None:
            model.save(os.path.join(save_file, str(i+1)), include=['env'])

    return
