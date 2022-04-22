import sys
import os
import shutil
import json
import random
import pickle
import numpy as np
import warnings
warnings.simplefilter('ignore')

from neat.nn import FeedForwardNetwork

import mcc
import ns_neat
import distances
from parallel import ParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'maze_utils')
sys.path.append(UTIL_DIR)
from boostrap_arguments import get_args
from utils import make_config
from maze_genome import MazeGenome
from maze_genome_decoder import MazeGenomeDecoder

from maze_environment import MazeEnvironment

from neat import DefaultGenome



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


def make_random_maze(config, maze_num, wall_gene_num, path_gene_num):
    genomes = []
    for m_i in range(maze_num):
        genome = config.genome2_type(m_i)
        genome.configure_new(config.genome2_config)

        for __ in range(wall_gene_num-1):
            genome.mutate_add_wall(config.genome2_config)

        for __ in range(path_gene_num):
            genome.mutate_add_path(config.genome2_config)

        genomes.append(genome)

    return genomes



def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'maze_out', 'boostrap', args.name)

    try:
        os.makedirs(save_path)
    except:
        print(f'THIS BOOSTRAP ({args.name}) ALREADY EXISTS')
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


    mcc_config_path = os.path.join(UTIL_DIR, 'mcc_config.ini')
    mcc_config = mcc.make_config(DefaultGenome, MazeGenome, mcc_config_path, None, None)

    ns_config_path = os.path.join(UTIL_DIR, 'ns_config.ini')
    ns_config = ns_neat.make_config(ns_config_path, None, None)


    MazeDecoder = MazeGenomeDecoder(
        (mcc_config.genome2_config.region_max_width, mcc_config.genome2_config.region_max_height),
        (mcc_config.genome2_config.region_min_width, mcc_config.genome2_config.region_min_height),
        mcc_config.genome2_config.maze_scaler)


    maze_genomes = make_random_maze(
        mcc_config,
        args.maze_num,
        args.wall_gene_num,
        args.path_gene_num)

    perMaze = min(mcc_config.resource_limit, args.agent_num//args.maze_num)

    agent_genomes = []

    for m_i,maze_genome in enumerate(maze_genomes):

        print(f'maze genome {m_i+1}')

        maze_env, timesteps, _ = MazeDecoder.decode(maze_genome, save=os.path.join(save_path, f'{m_i+1}.jpg'))

        evaluator_kwargs = {
            'env': maze_env,
            'timesteps': timesteps}
        evaluator = ParallelEvaluator(evaluator_kwargs, args.num_cores, eval_genome)

        for a_i in range(perMaze):

            pop = ns_neat.Population(ns_config)
            agent_genome = pop.run(evaluator.evaluate, n=None)

            agent_genomes.append(agent_genome)
            print(f'\r\t found {a_i+1} / {perMaze}',end='')
        print()

if __name__=='__main__':
    main()
