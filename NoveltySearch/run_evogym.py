import sys
import os
import shutil
import json
import pickle
import random
import numpy as np
import warnings
warnings.simplefilter('ignore')


import evogym.envs
from evogym import is_connected, has_actuator, get_full_connectivity


from neat.nn import FeedForwardNetwork

import ns_neat
import distances
from parallel import ParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from gym_utils import make_vec_envs
from simulator import SimulateProcess
# from drawer import ProgressDrawer


PI = 3.1415926

def calc_covar(vec, align=True):
    ave = np.mean(vec,axis=0)
    if align:
        vec_align = (vec-ave).T
    else:
        vec_align = vec.T
    comb_indices = np.tril_indices(vec.shape[1],k=0)
    covar = np.mean(vec_align[comb_indices[0]]*vec_align[comb_indices[1]],axis=1)
    # return np.hstack([ave,covar])
    return covar

def eval_genome(genome, env_id, structure, config, num_eval=1, **kwargs):
    controller = FeedForwardNetwork.create(genome, config)

    env = make_vec_envs(env_id, structure, random.randint(0,10000), 1)

    obs = env.reset()

    pos = env.env_method('get_pos_com_obs', object_name='robot')[0]
    # vel = env.env_method('get_vel_com_obs', object_name='robot')[0]
    # rad = env.env_method('get_ort_obs', object_name='robot')[0]
    pos_data = [0,0]
    # rad_data = [0,0]

    obs_data = [obs]
    act_data = []

    episode_rewards = []
    episode_data = []
    while len(episode_rewards) < num_eval:
        action = np.array(controller.activate(obs[0]))
        act_data.append(action)
        obs, _, done, infos = env.step([np.array(action)])

        pos_ = env.env_method('get_pos_com_obs', object_name='robot')[0]
        # vel_ = env.env_method('get_vel_com_obs', object_name='robot')[0]
        # rad_ = env.env_method('get_ort_obs', object_name='robot')[0]

        if 'episode' in infos[0]:
            obs_data = np.vstack(obs_data)
            obs_cov = calc_covar(obs_data)
            # obs_diff = np.mean(np.abs(np.diff(obs_data,axis=0)),axis=0)
            act_data = np.clip(np.vstack(act_data),-1,1)
            act_cov = calc_covar(act_data, align=False)
            # act_diff = np.mean(np.abs(np.diff(act_data,axis=0)),axis=0)
            # data = np.hstack([obs_data, act_data])
            # data = calc_covar(data)
            # data = np.hstack([obs_diff,act_diff])
            # data = act_diff
            data = np.hstack([obs_cov,act_cov])
            episode_data.append(data)
            # episode_data.append(np.hstack([data,data2]))
            # episode_data.append(np.hstack([obs_data,act_data]))
            obs_data = [obs]
            act_data = []
            # episode_data.append(np.hstack(pos_data+rad_data))
            pos_data = np.hstack(pos_data)
            # pos_data = [0,0]
            # rad_data = [0,0]
            reward = infos[0]['episode']['r']
            # print('{: =.8f}'.format(np.mean(pos_data)))
            if np.mean(pos_data)<0.3:
                reward = -3.
            episode_rewards.append(reward)
        else:
            # pass
            obs_data.append(obs)
            pos_diff = pos_-pos
            pos_data[0] += np.maximum(pos_diff, 0)
            pos_data[1] += np.maximum(-pos_diff, 0)
            # rad_diff = (rad_-rad)%(2*PI)
            # if rad_diff<PI:
            #     rad_data[0] += rad_diff
            # else:
            #     rad_data[1] += 2*PI-rad_diff

        pos = pos_
        # rad = rad_

    results = {
        'reward': np.mean(episode_rewards),
        'data': list(np.mean(np.vstack(episode_data),axis=0))
    }
    # print(results)
    return results


def main():

    args = get_args()

    save_path = os.path.join(CURR_DIR, 'evogym_out', args.name)

    try:
        os.makedirs(save_path)
    except:
        print(f'THIS EXPERIMENT ({args.name}) ALREADY EXISTS')
        print('Override? (y/n): ', end='')
        ans = input()
        if ans.lower() == 'y':
            shutil.rmtree(save_path)
            os.makedirs(save_path)
        else:
            return None, None
        print()

    argument_file = os.path.join(save_path, 'arguments.json')
    with open(argument_file, 'w') as f:
        json.dump(args.__dict__, f, indent=4)


    # figure_save_path = os.path.join(save_path, 'bd_map')
    # os.makedirs(figure_save_path)
    # Drawer = visualize.ProgressDrawer(no_plot=args.no_plot)
    # Drawer.initialize_figure(save_dir=figure_save_path)
    # Drawer = None

    robot = np.array([
        [2,0,0,0,0],
        [1,0,0,1,1],
        [4,3,3,3,4],
        [4,3,1,3,4],
        [4,0,0,0,4]
    ])
    connectivity = get_full_connectivity(robot)
    structure = (robot, connectivity)
    robot_file = os.path.join(save_path, 'structure')
    np.savez(robot_file, robot=robot, connectivity=connectivity)


    seed = 0
    env = make_vec_envs(args.task, structure, seed, 1)

    num_inputs = env.observation_space.shape[0]
    num_outputs = env.action_space.shape[0]

    evaluator_kwargs = {
        'env_id': args.task,
        'structure': structure,
        'eval_num': args.eval_num
    }
    evaluator = ParallelEvaluator(evaluator_kwargs, args.num_cores, eval_genome)

    config_path = os.path.join(UTIL_DIR, 'neat_config.ini')
    novelty_config = {
        'metric': distances.manhattan,
        'threshold_init': args.ns_threshold,
        'threshold_floor': 0.001,
        'neighbors': args.num_knn,
        'MCNS': args.mcns
    }
    overwrite_config = [
        ('NEAT', 'pop_size', args.pop_size),
        ('DefaultGenome', 'num_inputs', num_inputs),
        ('DefaultGenome', 'num_outputs', num_outputs)
    ]
    config = ns_neat.make_config(config_path, novelty_config, overwrite_config)
    with open(os.path.join(save_path, 'neat_config.pickle'), 'wb') as f:
        pickle.dump(config, f)

    pop = ns_neat.Population(config)
    reporters = [
        ns_neat.SaveResultReporter(save_path),
        ns_neat.NoveltySearchReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)

    if not args.no_view:
        simulator = SimulateProcess(
            args.task,
            structure,
            save_path,
            pop.config,
            args.generation)
        simulator.init_process()
        simulator.start()

    pop.run(evaluator.evaluate, n=args.generation)

if __name__=='__main__':
    main()
