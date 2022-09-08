import os
import gym
import numpy as np
import multiprocessing.pool

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.vec_env.vec_normalize import VecNormalize

def make_env(env_id, kwargs, seed, rank, allow_early_resets):
    def _init():
        env = gym.make(env_id, **kwargs)
        env.action_space = gym.spaces.Box(low=-1.0, high=1.0,
            shape=env.action_space.shape, dtype=np.float)
        env.seed(seed + rank)
        env = Monitor(env, None, allow_early_resets=allow_early_resets)
        return env
    return _init

def make_vec_envs(env_id, structure, seed, num_processes, allow_early_resets=True, vecnormalize=False, subproc=True):
    if env_id=='Parkour-v0' or env_id=='Parkour-v1':
        kwargs = {
            'body': structure[0],
            'connections': structure[1],
            'terrain': structure[2]
        }
    else:
        kwargs = {
            'body': structure[0],
            'connections': structure[1] 
        }

    envs = [make_env(env_id, kwargs, seed, i, allow_early_resets=allow_early_resets) for i in range(num_processes)]
    if subproc and num_processes > 1:
        envs = SubprocVecEnv(envs)
    else:
        envs = DummyVecEnv(envs)
    if vecnormalize:
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

    robot = np.loadtxt(robot_file)
    assert is_connected(robot), f'robot {robot_name} is not fully connected'
    assert has_actuator(robot), f'robot {robot_name} have not actuator block'

    connectivity = get_full_connectivity(robot)
    structure = (robot, connectivity)

    return structure
