import sys
import os
import shutil
import json
import random
import numpy as np


import neat_cppn
from parallel import ParallelEvaluator

import evogym.envs
from evogym import is_connected, has_actuator, get_full_connectivity

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from gym_utils import make_vec_envs
from simulator import SimulateProcess


def eval_genome(genome, env_id, structure, config, num_eval=1, **kwargs):
    controller = neat_cppn.nn.FeedForwardNetwork.create(genome, config)

    env = make_vec_envs(env_id, structure, random.randint(0,10000), 1)

    obs = env.reset()
    episode_rewards = []
    while len(episode_rewards) < num_eval:
        action = np.array(controller.activate(obs[0]))*2 - 1
        obs, _, done, infos = env.step([np.array(action)])

        if 'episode' in infos[0]:
            reward = infos[0]['episode']['r']
            episode_rewards.append(reward)

    results = {
        'fitness': np.mean(episode_rewards),
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

    config_path = os.path.join(UTIL_DIR, 'neat_config.ini')
    overwrite_config = [
        ('NEAT', 'pop_size', args.pop_size),
        ('DefaultGenome', 'num_inputs', num_inputs),
        ('DefaultGenome', 'num_outputs', num_outputs)
    ]
    config = neat_cppn.make_config(config_path, custom_config=overwrite_config)
    config_out_path = os.path.join(save_path, 'neat_config.ini')
    config.save(config_out_path)


    pop = neat_cppn.Population(config)

    reporters = [
        neat_cppn.SaveResultReporter(save_path),
        neat_cppn.StdOutReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    if not args.no_view:
        simulator = SimulateProcess(
            env_id=args.task,
            structure=structure,
            load_path=save_path,
            history_file='history_reward.csv',
            neat_config=config,
            generations=args.generation)

        simulator.init_process()
        simulator.start()


    pop.run(evaluator.evaluate, n=args.generation)

if __name__=='__main__':
    main()
