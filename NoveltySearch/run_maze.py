import sys
import os
import shutil
import json
import random
import numpy as np
import torch
import warnings
warnings.simplefilter('ignore')


import evogym.envs
from evogym import is_connected, has_actuator, get_full_connectivity


from neat.nn import FeedForwardNetwork

import ns_neat
import distances
from parallel import ParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'maze_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from drawer import DrawReporter

from maze_environment import read_environment


def eval_genome(genome, config, env, timesteps, **kwargs):
    controller = FeedForwardNetwork.create(genome, config)
    env.reset()

    done = False
    for i in range(timesteps):
        obs = env.create_net_inputs()
        action = controller.activate(obs)
        done = env.update(action)
        if done:
            break

    if done:
        reward = 1.0
    else:
        distance = env.agent_distance_to_exit()
        reward = (env.initial_distance - distance) / env.initial_distance

    results = {
        'reward': reward,
        'data': [env.agent.location.x, env.agent.location.y]
    }
    return results


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'maze_out', args.name)

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


    maze_env_config = os.path.join(UTIL_DIR, f'{args.task}_maze.txt')
    maze_env = read_environment(maze_env_config)


    evaluator_kwargs = {
        'env': maze_env,
        'timesteps': args.timesteps,
    }
    evaluator = ParallelEvaluator(evaluator_kwargs, args.num_cores, eval_genome)


    config_path = os.path.join(UTIL_DIR, 'neat_config.ini')
    novelty_config = {
        'metric': distances.manhattan,
        'threshold_init': args.ns_threshold,
        'threshold_floor': 0.25,
        'neighbors': args.num_knn,
        'MCNS': args.mcns
    }
    overwrite_config = [
        ('NEAT', 'pop_size', args.pop_size)
    ]
    config = ns_neat.make_config(config_path, novelty_config, overwrite_config)

    pop = ns_neat.Population(config)

    figure_path = os.path.join(save_path, 'progress')
    reporters = [
        ns_neat.SaveResultReporter(save_path),
        ns_neat.NoveltySearchReporter(True),
        DrawReporter(maze_env, args.timesteps, figure_path, no_plot=args.no_plot)
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    pop.run(evaluator.evaluate, n=args.generation)

if __name__=='__main__':
    main()
