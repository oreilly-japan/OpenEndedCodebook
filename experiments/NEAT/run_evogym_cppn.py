import sys
import os

import evogym.envs


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import neat_cppn
from parallel import EvaluatorParallel
from experiment_utils import initialize_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'evogym')
sys.path.append(ENV_DIR)
from evaluator import EvogymStructureEvaluator
from simulator import EvogymStructureSimulator, SimulateProcess
from cppn_decoder import EvogymStructureDecoder
from substrate import Substrate
from constraint import EvogymStructureConstraint


from arguments.evogym_cppn import get_args


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'evogym_cppn', args.name)

    initialize_experiment(args.name, save_path, args)


    decoder = EvogymStructureDecoder(args.shape)
    decode_function = decoder.decode

    constraint = EvogymStructureConstraint(decode_function)
    constraint_function = constraint.eval_constraint

    evaluator = EvogymStructureEvaluator(args.task, save_path, args.ppo_iters, args.evaluation_interval, deterministic=not args.probabilistic)
    evaluate_function = evaluator.evaluate_structure

    parallel = EvaluatorParallel(
        num_workers=args.num_cores,
        evaluate_function=evaluate_function,
        decode_function=decode_function
    )


    config_file = os.path.join(CURR_DIR, 'config', 'evogym_cppn.cfg')
    custom_config = [
        ('NEAT', 'pop_size', args.pop_size),
    ]
    config = neat_cppn.make_config(config_file, custom_config=custom_config)
    config_out_file = os.path.join(save_path, 'evogym_cppn.cfg')
    config.save(config_out_file)


    pop = neat_cppn.Population(config, constraint_function=constraint_function)

    reporters = [
        neat_cppn.SaveResultReporter(save_path),
        neat_cppn.StdOutReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    if not args.no_view:
        simulator = EvogymStructureSimulator(
            env_id=args.task,
            load_path=save_path,
            history_file='history_reward.csv',
            deterministic=not args.probabilistic)

        simulate_process = SimulateProcess(
            simulator=simulator,
            generations=args.generation)

        simulate_process.init_process()
        simulate_process.start()


    pop.run(
        fitness_function=parallel.evaluate,
        constraint_function=constraint_function,
        n=args.generation
    )

if __name__=='__main__':
    main()
