import gym
import numpy as np

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.vec_env.vec_normalize import VecNormalize

def make_env(env_id, robot, seed, rank):
    def _init():
        env = gym.make(env_id, body=robot[0], connections=robot[1])
        env.action_space = gym.spaces.Box(low=-1.0, high=1.0,
            shape=(env.get_actuator_indices('robot').size,), dtype=np.float)
        env.seed(seed + rank)
        env = Monitor(env, None, allow_early_resets=True)
        return env
    return _init

def make_vec_envs(env_id, robot, seed, num_processes):
    envs = [make_env(env_id, robot, seed, i) for i in range(num_processes)]
    if num_processes > 1:
        envs = SubprocVecEnv(envs)
    else:
        envs = DummyVecEnv(envs)
    envs = VecNormalize(envs, norm_reward=False)
    return envs
