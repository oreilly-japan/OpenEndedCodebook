import sys
import os
import pickle


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import mcc
import ns_neat
from parallel import EvaluatorParallel
from experiment_utils import initialize_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'maze')
sys.path.append(ENV_DIR)
from maze_genome import MazeGenome
from maze_genome_decoder import MazeGenomeDecoder
from evaluator import MazeControllerEvaluatorNS


from arguments.maze_mcc import get_bootstrap_args


import time

class ScoreReporter(ns_neat.BaseReporter):

    def __init__(self):
        self.generation = 0
        self.best = float('-inf')
        self.start_time = time.time()

    def start_generation(self, generation):
        self.generation = generation

    def post_evaluate(self, config, population, species, best_genome):
        self.best = max(self.best, best_genome.score)
        elapsed = time.time()-self.start_time
        hours = int(elapsed//3600)
        minutes = int(elapsed%3600//60)
        seconds = elapsed%60
        print(f'\rgeneration: {self.generation :3}  best: {self.best: =.3f}  elapsed: {hours:0=2}:{minutes:0=2}:{seconds:0=4.1f}',end='')


def make_random_maze(config, key, wall_gene_num, path_gene_num):
    genome = config.genome2_type(key)
    genome.configure_new(config.genome2_config)

    for _ in range(wall_gene_num-1):
        genome.mutate_add_wall(config.genome2_config)

    c = 0
    while c < path_gene_num:
        valid = genome.mutate_add_path(config.genome2_config)
        if valid:
            c += 1

    setattr(genome, 'success_keys', [])
    genome.fitness = 0
    return genome


def main():
    args = get_bootstrap_args()

    save_path = os.path.join(CURR_DIR, 'out', 'maze_mcc', 'bootstrap', args.name)

    initialize_experiment(args.name, save_path, args)


    mcc_config_file = os.path.join(CURR_DIR, 'config', 'maze_mcc.cfg')
    mcc_config = mcc.make_config(mcc.DefaultGenome, MazeGenome, mcc_config_file)
    mcc_config_out_file = os.path.join(save_path, 'maze_mcc.cfg')
    mcc_config.save(mcc_config_out_file)

    ns_config_file = os.path.join(CURR_DIR, 'config', 'maze_ns_neat.cfg')
    ns_config = ns_neat.make_config(ns_config_file)
    ns_config_out_file = os.path.join(save_path, 'maze_ns_neat.cfg')
    ns_config.save(ns_config_out_file)


    maze_config = {
        'exit_range': args.exit_range,
        'init_heading': 45,
    }
    agent_config = {
        'radius': args.radius,
        'range_finder_range': args.range_finder,
        'max_speed': args.max_speed,
        'max_angular_vel': args.max_angular_vel,
        'speed_scale': args.speed_scale,
        'angular_scale': args.angular_scale,
    }
    MazeDecoder = MazeGenomeDecoder(mcc_config.genome2_config, maze_kwargs=maze_config, agent_kwargs=agent_config)


    perMaze = min(mcc_config.genome2_limit, args.agent_num//args.maze_num)
    maze_genomes = {}
    agent_genomes = {}
    a_i = 0
    while len(maze_genomes) < args.maze_num:

        maze_genome = make_random_maze(mcc_config, len(maze_genomes), args.wall_gene_num, args.path_gene_num)

        print(f'maze {maze_genome.key+1}')

        maze_env, timesteps = MazeDecoder.decode(maze_genome, mcc_config, save=os.path.join(save_path, f'maze{maze_genome.key+1}.jpg'))

        evaluator = MazeControllerEvaluatorNS(maze_env, timesteps)
        parallel = EvaluatorParallel(
            num_workers=args.num_cores,
            evaluate_function=evaluator.evaluate_agent,
            decode_function=ns_neat.FeedForwardNetwork.create,
            print_progress=False
        )

        agent_genomes_tmp = {}
        not_found_count = 0
        print(f'search for {perMaze} solver agents')
        while len(agent_genomes_tmp) < perMaze:

            pop = ns_neat.Population(ns_config)
            pop.add_reporter(ScoreReporter())
            agent_genome = pop.run(evaluate_function=parallel.evaluate, n=400)

            if agent_genome.score>=1.0:
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
