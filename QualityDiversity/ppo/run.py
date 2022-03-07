import os
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.utils import get_linear_fn

from ppo.utils import make_vec_envs
import ppo.config as config

def evaluate(model, envs, num_eval=1, deterministic=True):
    if deterministic:
        num_eval = 1
    obs = envs.reset()
    episode_rewards = []
    while len(episode_rewards) < num_eval:
        action, _state = model.predict(obs,deterministic=deterministic)
        obs, _, done, infos = envs.step(action)

        for info in infos:
            if 'episode' in info:
                episode_rewards.append(info['episode']['r'])
    return np.mean(episode_rewards)


def run_ppo(
    env_id,
    structure,
    train_iter,
    saving_convention,
    num_eval=1,
    deterministic=True):

    controller_save_path = os.path.join(saving_convention[0], f'{saving_convention[1]}.zip')

    train_envs = make_vec_envs(env_id, structure, config.seed, config.num_processes)
    train_envs.reset()

    eval_envs = make_vec_envs(env_id, structure, config.seed, 1)

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

    steps_by_iter = config.learning_steps * config.steps * config.num_processes
    max_reward = float('-inf')

    for i in range(train_iter):

        model.learn(total_timesteps=steps_by_iter)

        reward = evaluate(model, eval_envs, num_eval=num_eval, deterministic=deterministic)
        if reward > max_reward:
            max_reward = reward
            model.save(controller_save_path)

    return reward
