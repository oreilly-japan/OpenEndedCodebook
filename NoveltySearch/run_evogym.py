import sys
import os
import shutil
import json
import pickle
import random
import numpy as np


import evogym.envs
from evogym import is_connected, has_actuator, get_full_connectivity


import ns_neat
from parallel import ParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from gym_utils import make_vec_envs
from simulator import SimulateProcess


def calc_covar(vec, align=True):
    ave = np.mean(vec,axis=0)
    if align:
        vec_align = (vec-ave).T
    else:
        vec_align = vec.T
    comb_indices = np.tril_indices(vec.shape[1],k=0)
    covar = np.mean(vec_align[comb_indices[0]]*vec_align[comb_indices[1]],axis=1)
    return covar

def eval_genome(genome, env_id, structure, config, num_eval=1, **kwargs):
    controller = ns_neat.nn.FeedForwardNetwork.create(genome, config)

    env = make_vec_envs(env_id, structure, random.randint(0,10000), 1)

    obs = env.reset()

    # pos = env.env_method('get_pos_com_obs', object_name='robot')[0]
    # pos_data = [0,0]

    obs_data = []
    act_data = []

    episode_rewards = []
    episode_data = []
    while len(episode_rewards) < num_eval:
        action = np.array(controller.activate(obs[0]))*2 - 1
        obs_data.append(obs)
        act_data.append(action)
        obs, _, done, infos = env.step([np.array(action)])

        # pos_ = env.env_method('get_pos_com_obs', object_name='robot')[0]

        if 'episode' in infos[0]:
            obs_data = np.vstack(obs_data)
            obs_cov = calc_covar(obs_data)

            act_data = np.clip(np.vstack(act_data),-1,1)
            act_cov = calc_covar(act_data, align=False)

            data = np.hstack([obs_cov,act_cov])
            episode_data.append(data)

            obs_data = []
            act_data = []
            # pos_data = [0,0]
            # rad_data = [0,0]
            reward = infos[0]['episode']['r']
            # if np.mean(pos_data)<0.3:
                # reward = -3.
            episode_rewards.append(reward)
        # else:
            # pos_diff = pos_-pos
            # pos_data[0] += np.maximum(pos_diff, 0)
            # pos_data[1] += np.maximum(-pos_diff, 0)

        # pos = pos_

    results = {
        'reward': np.mean(episode_rewards),
        'data': list(np.mean(np.vstack(episode_data),axis=0))
    }
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
            return
        print()

    argument_file = os.path.join(save_path, 'arguments.json')
    with open(argument_file, 'w') as f:
        json.dump(args.__dict__, f, indent=4)


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


    evaluator_kwargs = {
        'env_id': args.task,
        'structure': structure,
        'eval_num': args.eval_num
    }
    evaluator = ParallelEvaluator(evaluator_kwargs, args.num_cores, eval_genome)


    env = make_vec_envs(args.task, structure, 0, 1)
    num_inputs = env.observation_space.shape[0]
    num_outputs = env.action_space.shape[0]

    config_path = os.path.join(UTIL_DIR, 'ns_config.ini')
    overwrite_config = [
        ('NEAT', 'pop_size', args.pop_size),
        ('NEAT', 'metric', 'manhattan'),
        ('NEAT', 'threshold_init', args.ns_threshold),
        ('NEAT', 'threshold_floor', 0.001),
        ('NEAT', 'neighbors', args.num_knn),
        ('NEAT', 'mcns', args.mcns),
        ('DefaultGenome', 'num_inputs', num_inputs),
        ('DefaultGenome', 'num_outputs', num_outputs)
    ]
    config = ns_neat.make_config(config_path, custom_config=overwrite_config)
    config_out_path = os.path.join(save_path, 'ns_config.ini')
    config.save(config_out_path)


    pop = ns_neat.Population(config)

    reporters = [
        ns_neat.SaveResultReporter(save_path),
        ns_neat.NoveltySearchReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    if not args.no_view:
        simulator = SimulateProcess(
            env_id=args.task,
            structure=structure,
            load_path=save_path,
            history_file='history_novelty.csv',
            neat_config=pop.config,
            generations=args.generation)

        simulator.init_process()
        simulator.start()

    pop.run(evaluator.evaluate, n=args.generation)

if __name__=='__main__':
    main()
