import os
import time
import numpy as np

from multiprocessing import Process

from stable_baselines3 import PPO
from stable_baselines3.common.utils import get_linear_fn

from utils import make_vec_envs

def simulate(ppo_file, make_env_func, make_env_args, deterministic):
    env = make_env_func(*make_env_args)

    while True:
        model = PPO.load(ppo_file)
        done = False
        obs = env.reset()
        while not done:
            action, _states = model.predict(obs,deterministic=deterministic)
            obs, _, done, infos = env.step(action)
            env.render()

            for info in infos:
                if 'episode' in info:
                    reward = info['episode']['r']
                    print(f'reward: {reward: =.5f}')


def run_ppo(
    env_id,
    structure,
    deterministic):

    num_processes = 4

    ppo_steps = 2**7
    num_mini_batch = 2**2
    ppo_epochs = 2**3

    num_update = 100

    learning_steps = 50

    ppo_tmp_file = '.ppo/tmp'
    os.makedirs('.ppo/',exist_ok=True)

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
        gamma=0.99,
        clip_range=0.3,
        ent_coef=0.01,
        policy_kwargs={'log_std_init': 0.0, 'ortho_init': True,'squash_output':False})

    model.save(ppo_tmp_file)

    p = Process(
        target=simulate,
        kwargs={
            'ppo_file':ppo_tmp_file,
            'make_env_func': make_vec_envs,
            'make_env_args': (env_id,structure,0,1),
            'deterministic': deterministic
        }
    )
    p.start()

    for i in range(num_update):
        start = time.time()
        model.learn(total_timesteps=learning_steps*ppo_steps*num_processes)
        model.save(ppo_tmp_file)
        print(f'\nupdate: {i+1}  elapsed time: {time.time()-start: =.3f}  log_std: {np.mean(model.policy.log_std.detach().numpy()): =.3f}')

    p.terminate()
