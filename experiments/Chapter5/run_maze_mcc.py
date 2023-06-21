import sys
import os
import numpy as np


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import mcc
from parallel import MCCEvaluatorParallel
from experiment_utils import initialize_experiment, load_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'maze')
sys.path.append(ENV_DIR)
from maze_genome import MazeGenome
from maze_genome_decoder import MazeGenomeDecoder


from arguments.maze_mcc import get_args


class MazeReporter(mcc.BaseReporter):

    def end_generation(self, config, agent_genomes, maze_genomes):
        maze_areas = [maze_genome.get_maze_area() for maze_genome in maze_genomes.values()]
        maze_junctures = [maze_genome.get_juncture_num() for maze_genome in maze_genomes.values()]
        maze_path_length = [maze_genome.get_path_length() for maze_genome in maze_genomes.values()]
        nn_conns = [len([1 for conn_gene in agent_genome.connections.values() if conn_gene.enabled]) for agent_genome in agent_genomes.values()]

        print( '   statistics         min      ave      max')
        print( '                    =======  =======  =======')
        print(f'maze area        :  {np.min(maze_areas): =7.1f}  {np.mean(maze_areas): =7.1f}  {np.max(maze_areas): =7.1f}')
        print(f'maze junctures   :  {np.min(maze_junctures): =7.1f}  {np.mean(maze_junctures): =7.1f}  {np.max(maze_junctures): =7.1f}')
        print(f'maze path length :  {np.min(maze_path_length): =7.1f}  {np.mean(maze_path_length): =7.1f}  {np.max(maze_path_length): =7.1f}')
        print(f'nn connections   :  {np.min(nn_conns): =7.1f}  {np.mean(nn_conns): =7.1f}  {np.max(nn_conns): =7.1f}')


def simulate_maze(controller, maze_phenome, generation):
    maze, timesteps = maze_phenome
    maze.reset()
    done = False
    for i in range(timesteps):
        obs = maze.get_observation()
        action = controller.activate(obs)
        done = maze.update(action)
        if done:
            break
    return done


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'maze_mcc', 'main', args.name)

    initialize_experiment(args.name, save_path, args)


    config_file = os.path.join(CURR_DIR, 'config', 'maze_mcc.cfg')
    custom_config = [
        ('MCC', 'generation', args.generation),
        ('MCC', 'genome1_pop_size', args.agent_pop),
        ('MCC', 'genome2_pop_size', args.maze_pop),
        ('MCC', 'genome1_criterion', args.agent_criterion),
        ('MCC', 'genome2_criterion', args.maze_criterion),
        ('MCC', 'genome1_offspring_size', args.agent_batch),
        ('MCC', 'genome2_offspring_size', args.maze_batch),
        ('MCC', 'genome1_limit', args.agent_limit),
        ('MCC', 'genome2_limit', args.maze_limit)
    ]
    config = mcc.make_config(mcc.DefaultGenome, MazeGenome, config_file, custom_config=custom_config)
    config_out_file = os.path.join(save_path, 'maze_mcc.cfg')
    config.save(config_out_file)


    bootstrap_path = os.path.join(CURR_DIR, 'out', 'maze_mcc', 'bootstrap', args.bootstrap)
    bootstrap_args = load_experiment(bootstrap_path)
    maze_config = {
        'exit_range': bootstrap_args['exit_range'],
        'init_heading': 45,
    }
    agent_config = {
        'radius': bootstrap_args['radius'],
        'range_finder_range': bootstrap_args['range_finder'],
        'max_speed': bootstrap_args['max_speed'],
        'max_angular_vel': bootstrap_args['max_angular_vel'],
        'speed_scale': bootstrap_args['speed_scale'],
        'angular_scale': bootstrap_args['angular_scale'],
    }
    MazeDecoder = MazeGenomeDecoder(config.genome2_config, maze_kwargs=maze_config, agent_kwargs=agent_config)
    maze_decode_function = MazeDecoder.decode

    agent_decode_function = mcc.FeedForwardNetwork.create

    evaluator = MCCEvaluatorParallel(
        num_workers=args.num_cores,
        evaluate_function=simulate_maze,
        decode_function1=agent_decode_function,
        decode_function2=maze_decode_function,
    )


    agent_bootstrap_file = os.path.join(bootstrap_path, 'agent_genomes.pickle')
    maze_bootstrap_file = os.path.join(bootstrap_path, 'maze_genomes.pickle')
    assert os.path.exists(agent_bootstrap_file) or not os.path.exists(maze_bootstrap_file),\
        f'bootstrap {args.bootstrap} is incomplete, run "python bootstrap_maze.py -n {args.bootstrap}".'

    pop = mcc.Population(config, agent_bootstrap_file, maze_bootstrap_file)

    reporters = [
        mcc.SaveResultReporter(save_path, 'agent', 'maze', pop.genome1_pop, pop.genome2_pop),
        mcc.MCCReporter('agent', 'maze', print_genome2=args.print_maze),
        MazeReporter(),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    pop.run(evaluate_function=evaluator.evaluate)

if __name__=='__main__':
    main()
