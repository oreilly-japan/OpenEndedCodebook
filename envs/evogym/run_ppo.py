import os
import csv
import time
import numpy as np
import torch

from ppo import Policy, PPO

from gym_utils import make_vec_envs
import ppo_config as default_config

def evaluate(policy, envs, num_eval=1, deterministic=False):

    obs = envs.reset()
    episode_rewards = []
    while len(episode_rewards) < num_eval:
        with torch.no_grad():
            action = policy.predict(obs, deterministic=deterministic)
        obs, _, done, infos = envs.step(action)

        for info in infos:
            if 'episode' in info:
                episode_rewards.append(info['episode']['r'])
    return np.mean(episode_rewards)


def run_ppo(env_id, robot, train_iters, eval_interval, save_file, config=None, deterministic=False, save_iter=False, history_file=None):

    if config is None:
        config = default_config

    train_envs = make_vec_envs(env_id, robot, config.seed, config.num_processes, gamma=config.gamma, vecnormalize=True)

    eval_envs = make_vec_envs(env_id, robot, config.seed, config.eval_processes, gamma=None, vecnormalize=True)
    eval_envs.training = False

    policy = Policy(
        train_envs.observation_space,
        train_envs.action_space,
        init_log_std=config.init_log_std,
        device='cpu'
    )

    algo = PPO(
        policy,
        train_envs,
        learning_rate=config.learning_rate,
        n_steps=config.steps,
        batch_size=config.steps*config.num_processes//config.num_mini_batch,
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
        max_iter=train_iters*10)


    if save_iter:
        interval = time.time()
        torch.save([policy.state_dict(), train_envs.obs_rms], os.path.join(save_file, '0.pt'))

        history_header = ['iteration', 'reward']
        items = {
            'iteration': 0,
            'reward': 0
        }
        with open(history_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=history_header)
            writer.writeheader()
            writer.writerow(items)

    max_reward = float('-inf')

    for iter in range(train_iters):
        
        algo.step()

        if (iter+1) % eval_interval == 0:
            eval_envs.obs_rms = train_envs.obs_rms.copy()
            reward = evaluate(policy, eval_envs, num_eval=config.eval_processes, deterministic=deterministic)
            if reward > max_reward:
                max_reward = reward
                if not save_iter:
                    torch.save([policy.state_dict(), train_envs.obs_rms], save_file + '.pt')

            if save_iter:
                now = time.time()
                log_std = policy.log_std.mean()
                print(f'iteration: {iter+1:=5}  elapsed times: {now-interval:.3f}  reward: {reward:6.3f}  log_std: {log_std:.5f}')
                interval = now

                torch.save([policy.state_dict(), train_envs.obs_rms], os.path.join(save_file, f'{iter+1}.pt'))

                items = {
                    'iteration': iter+1,
                    'reward': reward
                }
                with open(history_file, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=history_header)
                    writer.writerow(items)

    train_envs.close()
    eval_envs.close()

    return max_reward
