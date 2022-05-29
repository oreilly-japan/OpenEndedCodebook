import gym
import numpy as np
import multiprocessing.pool

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.vec_env.vec_normalize import VecNormalize


def make_env(env_id, robot, seed, rank, allow_early_resets):
    def _init():
        env = gym.make(env_id, body=robot[0], connections=robot[1])
        env.action_space = gym.spaces.Box(low=-1.0, high=1.0,
            shape=env.action_space.shape, dtype=np.float)
        env.seed(seed + rank)
        env = Monitor(env, None, allow_early_resets=allow_early_resets)
        return env
    return _init

def make_vec_envs(env_id, robot, seed, num_processes, allow_early_resets=True, vecnormalize=False):
    envs = [make_env(env_id, robot, seed, i, allow_early_resets=allow_early_resets) for i in range(num_processes)]
    if num_processes > 1:
        envs = SubprocVecEnv(envs)
    else:
        envs = DummyVecEnv(envs)
    if vecnormalize:
        envs = VecNormalize(envs, norm_reward=False)
    return envs


from evogym import is_connected, has_actuator, get_full_connectivity

def load_robot(robot_file):
    robot = np.loadtxt(robot_file)
    assert is_connected(robot), f'robot {args.robot} is not fully connected'
    assert has_actuator(robot), f'robot {args.robot} have not actuator block'

    connectivity = get_full_connectivity(robot)
    structure = (robot, connectivity)
    
    return structure
