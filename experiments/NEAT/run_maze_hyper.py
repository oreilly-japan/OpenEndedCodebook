import os
import sys

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import neat_cppn
from experiment_utils import initialize_experiment
from parallel import EvaluatorParallel

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'maze')
sys.path.append(ENV_DIR)
from cppn_decoder import MazeHyperDecoder
from evaluator import MazeControllerEvaluator
from maze_drawer import MazeReporterNEAT
from maze_environment_numpy import MazeEnvironment
from substrate import Substrate

from arguments.maze_hyper import get_args


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'maze_hyper', args.name)

    initialize_experiment(args.name, save_path, args)


    maze_env = MazeEnvironment.read_environment(ROOT_DIR, args.task)


    substrate = Substrate()
    decoder = MazeHyperDecoder(substrate, use_hidden=args.use_hidden)
    decode_function = decoder.decode

    evaluator = MazeControllerEvaluator(maze_env, args.timesteps)
    evaluate_function = evaluator.evaluate_agent

    parallel = EvaluatorParallel(
        num_workers=args.num_cores,
        evaluate_function=evaluate_function,
        decode_function=decode_function
    )


    config_file = os.path.join(CURR_DIR, 'config', 'maze_hyper.cfg')
    custom_config = [
        ('NEAT', 'pop_size', args.pop_size),
        ('DefaultGenome', 'num_inputs', decoder.input_dims),
        ('DefaultGenome', 'num_outputs', decoder.output_dims)
    ]
    config = neat_cppn.make_config(config_file, custom_config=custom_config)
    config_out_file = os.path.join(save_path, 'maze_hyper.cfg')
    config.save(config_out_file)


    pop = neat_cppn.Population(config)

    figure_path = os.path.join(save_path, 'progress')
    reporters = [
        neat_cppn.SaveResultReporter(save_path),
        neat_cppn.StdOutReporter(True),
        MazeReporterNEAT(maze_env, args.timesteps, figure_path, decode_function, args.generation, no_plot=args.no_plot)
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    try:
        pop.run(fitness_function=parallel.evaluate, n=args.generation)
    finally:
        neat_cppn.figure.make_species(save_path)

if __name__=='__main__':
    main()
