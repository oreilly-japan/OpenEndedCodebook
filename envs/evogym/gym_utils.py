import os
import gym
import numpy as np
import multiprocessing.pool

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.vec_env.vec_normalize import VecNormalize

def make_env(env_id, env_kwargs, seed, allow_early_resets=True):
    def _init():
        env = gym.make(env_id, **env_kwargs)
        env.action_space = gym.spaces.Box(low=-1.0, high=1.0,
            shape=env.action_space.shape, dtype=np.float)
        env.seed(seed)
        env = Monitor(env, None, allow_early_resets=True)
        return env
    return _init

def make_vec_envs(env_id, env_kwargs, seed, num_processes, gamma=None, vecnormalize=False, subproc=True, allow_early_resets=True):
    envs = [make_env(env_id, env_kwargs, seed+i, allow_early_resets=allow_early_resets) for i in range(num_processes)]

    if subproc and num_processes > 1:
        envs = SubprocVecEnv(envs)
    else:
        envs = DummyVecEnv(envs)

    if vecnormalize:
        if gamma is not None:
            envs = VecNormalize(envs, gamma=gamma)
        else:
            envs = VecNormalize(envs, norm_reward=False)
    
    return envs


from evogym import is_connected, has_actuator, get_full_connectivity

def load_robot(ROOT_DIR, robot_name, task=None):

    if robot_name=='default':
        robot_name = task
        robot_file = os.path.join(ROOT_DIR, 'envs', 'evogym', 'robot_files', f'{robot_name}.txt')
        assert os.path.exists(robot_file), f'defalt robot is not set on the task {task}'
    else:
        robot_file = os.path.join(ROOT_DIR, 'envs', 'evogym', 'robot_files', f'{robot_name}.txt')

    body = np.loadtxt(robot_file)
    assert is_connected(body), f'robot {robot_name} is not fully connected'
    assert has_actuator(body), f'robot {robot_name} have not actuator block'

    connections = get_full_connectivity(body)
    robot = {
        'body': body,
        'connections': connections
    }
    return robot
