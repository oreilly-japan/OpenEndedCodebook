import sys
import os
import shutil
import json
import numpy as np
import warnings
warnings.simplefilter('ignore')

from neat import DefaultGenome
from feed_forward import FeedForwardNetwork

import mcc
from parallel import MCCParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'maze_utils')
sys.path.append(UTIL_DIR)
from arguments import get_mcc_args
from maze_genome import MazeGenome
from maze_genome_decoder import MazeGenomeDecoder



class MazeReporter():
    def __init__(self):
        pass

    def start_generation(self, generation):
        pass

    def post_evaluate(self, config, agent_survivors, maze_survivors):
        pass

    def end_generation(self, config, agent_genomes, maze_genomes):
        pass


def simulate_maze(controller, maze):
    env, timesteps = maze
    env.reset()
    done = False
    for i in range(timesteps):
        obs = env.create_net_inputs()
        action = controller.activate(obs)
        done = env.update(action)
        if done:
            break
    return done


def main():
    args = get_mcc_args()

    save_path = os.path.join(CURR_DIR, 'maze_out', 'main', args.name)

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


    config_path = os.path.join(UTIL_DIR, 'mcc_config.ini')
    overwrite_config = [
        ('MCC', 'generation', args.generation),
        ('MCC', 'genome1_pop_size', args.agent_pop),
        ('MCC', 'genome2_pop_size', args.maze_pop),
        ('MCC', 'genome1_criteria', args.agent_criteria),
        ('MCC', 'genome2_criteria', args.maze_criteria),
        ('MCC', 'genome1_offspring_size', args.agent_batch),
        ('MCC', 'genome2_offspring_size', args.maze_batch),
        ('MCC', 'genome1_limit', args.agent_limit),
        ('MCC', 'genome2_limit', args.maze_limit)
    ]
    config = mcc.make_config(DefaultGenome, MazeGenome, config_path, None, overwrite_config)


    MazeDecoder = MazeGenomeDecoder(config.genome2_config)

    evaluator = MCCParallelEvaluator(
        kwargs={},
        num_workers=args.num_cores,
        evaluate_function=simulate_maze,
        decode_function1=FeedForwardNetwork.create,
        decode_function2=MazeDecoder.decode)

    bootstrap_path = os.path.join(CURR_DIR, 'maze_out', 'bootstrap', args.bootstrap)
    agent_bootstrap_file = os.path.join(bootstrap_path, 'agent_genomes.pickle')
    maze_bootstrap_file = os.path.join(bootstrap_path, 'maze_genomes.pickle')
    assert os.path.exists(agent_bootstrap_file) or not os.path.exists(maze_bootstrap_file),\
        f'bootstrap {args.bootstrap} is incomplete, run "python bootstrap_maze.py -n {args.bootstrap}".'

    pop = mcc.Population(config, agent_bootstrap_file, maze_bootstrap_file)

    # figure_path = os.path.join(save_path, 'progress')
    reporters = [
        mcc.SaveReporter(save_path, 'agent', 'maze'),
        mcc.MCCReporter('agent', 'maze'),
        # DrawReporter(maze_env, args.timesteps, figure_path, no_plot=args.no_plot)
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    pop.run(evaluator.evaluate)

if __name__=='__main__':
    main()
