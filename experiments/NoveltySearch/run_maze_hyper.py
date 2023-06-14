import os
import sys

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import ns_neat
from experiment_utils import initialize_experiment
from parallel import EvaluatorParallel

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'maze')
sys.path.append(ENV_DIR)
from cppn_decoder import MazeHyperDecoder
from evaluator import MazeControllerEvaluatorNS
from maze_drawer import MazeReporterNS
from maze_environment_numpy import MazeEnvironment
from substrate import Substrate

from arguments.maze_ns_hyper import get_args


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'maze_ns_hyper', args.name)

    initialize_experiment(args.name, save_path, args)


    maze_env = MazeEnvironment.read_environment(ROOT_DIR, args.task)


    substrate = Substrate()
    decoder = MazeHyperDecoder(substrate, use_hidden=args.use_hidden)
    decode_function = decoder.decode

    evaluator = MazeControllerEvaluatorNS(maze_env, args.timesteps)
    evaluate_function = evaluator.evaluate_agent

    parallel = EvaluatorParallel(
        num_workers=args.num_cores,
        evaluate_function=evaluate_function,
        decode_function=decode_function
    )


    config_file = os.path.join(CURR_DIR, 'config', 'maze_ns_hyper.cfg')
    custom_config = [
        ('NS-NEAT', 'pop_size', args.pop_size),
        ('NS-NEAT', 'metric', 'manhattan'),
        ('NS-NEAT', 'threshold_init', args.ns_threshold),
        ('NS-NEAT', 'threshold_floor', 0.25),
        ('NS-NEAT', 'neighbors', args.num_knn),
        ('NS-NEAT', 'mcns', args.mcns),
    ]
    config = ns_neat.make_config(config_file, custom_config=custom_config)
    config_out_file = os.path.join(save_path, 'maze_ns_hyper.cfg')
    config.save(config_out_file)


    pop = ns_neat.Population(config)

    figure_path = os.path.join(save_path, 'progress')
    reporters = [
        ns_neat.SaveResultReporter(save_path),
        ns_neat.NoveltySearchReporter(True),
        MazeReporterNS(maze_env, args.timesteps, figure_path, decode_function, args.generation, no_plot=args.no_plot)
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    try:
        pop.run(evaluate_function=parallel.evaluate, n=args.generation)
    finally:
        ns_neat.figure.make_species(save_path)

if __name__=='__main__':
    main()
