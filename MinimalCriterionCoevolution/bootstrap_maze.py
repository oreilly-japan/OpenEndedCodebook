import sys
import os
import shutil
import json
import pickle
import warnings
warnings.simplefilter('ignore')

from neat import DefaultGenome
from neat.nn import FeedForwardNetwork

import mcc
import ns_neat
import distances
from parallel import ParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'maze_utils')
sys.path.append(UTIL_DIR)
from arguments import get_bootstrap_args
from utils import make_config
from maze_genome import MazeGenome
from maze_genome_decoder import MazeGenomeDecoder

from maze_environment import MazeEnvironment


import time
from neat import BaseReporter

class RewardReporter(BaseReporter):

    def __init__(self):
        self.generation = 0
        self.best = float('-inf')
        self.start_time = time.time()

    def start_generation(self, generation):
        self.generation = generation

    def post_evaluate(self, config, population, species, best_genome):
        self.best = max(self.best, best_genome.reward)
        elapsed = time.time()-self.start_time
        hours = int(elapsed//3600)
        minutes = int(elapsed%3600//60)
        seconds = elapsed%60
        print(f'\rgeneration: {self.generation :3}  best: {self.best: =.3f}  elapsed: {hours:0=2}:{minutes:0=2}:{seconds:0=4.1f}',end='')



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
        'data': [env.agent.location[0], env.agent.location[1]]
        # 'data': [env.agent.location.x, env.agent.location.y]
    }
    return results


def make_random_maze(config, key, wall_gene_num, path_gene_num):
    genome = config.genome2_type(key)
    genome.configure_new(config.genome2_config)

    for __ in range(wall_gene_num-1):
        genome.mutate_add_wall(config.genome2_config)

    c = 0
    while c < path_genome_num:
    # for __ in range(path_gene_num):
        valid = genome.mutate_add_path(config.genome2_config)
        if valid:
            c += 1

    setattr(genome, 'success_keys', [])
    genome.fitness = 0
    return genome



def main():
    args = get_bootstrap_args()

    save_path = os.path.join(CURR_DIR, 'maze_out', 'bootstrap', args.name)

    try:
        os.makedirs(save_path)
    except:
        print(f'THIS BOOTSTRAP ({args.name}) ALREADY EXISTS')
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


    MazeDecoder = MazeGenomeDecoder(mcc_config.genome2_config)

    perMaze = min(mcc_config.genome2_limit, args.agent_num//args.maze_num)

    maze_genomes = {}
    agent_genomes = {}
    a_i = 0
    while len(maze_genomes) < args.maze_num:

        maze_genome = make_random_maze(mcc_config, len(maze_genomes), args.wall_gene_num, args.path_gene_num)

        print(f'maze {maze_genome.key+1}')
        print(maze_genome)

        maze_env, timesteps = MazeDecoder.decode(maze_genome, mcc_config, save=os.path.join(save_path, f'maze{maze_genome.key+1}.jpg'))

        evaluator_kwargs = {
            'env': maze_env,
            'timesteps': timesteps}
        evaluator = ParallelEvaluator(evaluator_kwargs, args.num_cores, eval_genome)

        agent_genomes_tmp = {}
        not_found_count = 0
        print(f'search for {perMaze} solver agents')
        while len(agent_genomes_tmp) < perMaze:

            pop = ns_neat.Population(ns_config)
            pop.add_reporter(RewardReporter())
            agent_genome = pop.run(evaluator.evaluate, n=400)

            if agent_genome.reward>=1.0:
                print('  found')

                setattr(agent_genome, 'success_keys', [maze_genome.key])
                agent_genome.key = a_i
                agent_genomes_tmp[a_i] = agent_genome

                maze_genome.success_keys.append(a_i)
                a_i += 1
                not_found_count = 0
            else:
                print()
                not_found_count += 1
                if not_found_count>=5:
                    break

        if len(agent_genomes_tmp)==perMaze:
            maze_genomes[maze_genome.key] = maze_genome
            agent_genomes.update(agent_genomes_tmp)
        else:
            print('release this maze genome')
        print()

    maze_genome_file = os.path.join(save_path, 'maze_genomes.pickle')
    with open(maze_genome_file, 'wb') as f:
        pickle.dump(maze_genomes, f)

    agent_genome_file = os.path.join(save_path, 'agent_genomes.pickle')
    with open(agent_genome_file, 'wb') as f:
        pickle.dump(agent_genomes, f)


if __name__=='__main__':
    main()
