
import numpy as np
import gym

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.vec_env.vec_normalize import VecNormalize as VecNormalize_

def make_env(env_id, robot, seed, rank):
    def _init():
        env = gym.make(env_id, body=robot[0], connections=robot[1])
        env.action_space = gym.spaces.Box(low=-0.4, high=0.6, shape=(env.get_actuator_indices('robot').size,), dtype=np.float)
        env.seed(seed + rank)
        env = Monitor(env, None, allow_early_resets=True)
        return env
    return _init

def make_vec_envs(env_id, robot, seed, num_processes):
    envs = [make_env(env_id, robot, seed, i) for i in range(num_processes)]
    if len(envs) > 1:
        envs = SubprocVecEnv(envs)
    else:
        envs = DummyVecEnv(envs)
    # envs = VecNormalize(envs, norm_reward=False)
    return envs

class VecNormalize(VecNormalize_):
    def __init__(self, *args, **kwargs):
        super(VecNormalize, self).__init__(*args, **kwargs)
        self.training = True

    def _obfilt(self, obs, update=True):
        if self.obs_rms:
            if self.training and update:
                self.obs_rms.update(obs)
            obs = np.clip((obs - self.obs_rms.mean) /
                          np.sqrt(self.obs_rms.var + self.epsilon),
                          -self.clipob, self.clipob)
            return obs
        else:
            return obs

    def train(self):
        self.training = True

    def eval(self):
        self.training = False
