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
from evaluator import EvogymControllerEvaluator
from simulator import EvogymControllerSimulator, SimulateProcess
from gym_utils import make_vec_envs, load_robot


from arguments.evogym_neat import get_args


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'evogym_neat', args.name)

    initialize_experiment(args.name, save_path, args)


    robot = load_robot(ROOT_DIR, args.robot, task=args.task)


    decode_function = neat_cppn.FeedForwardNetwork.create

    evaluator = EvogymControllerEvaluator(args.task, robot, args.eval_num)
    evaluate_function = evaluator.evaluate_controller

    parallel = EvaluatorParallel(
        num_workers=args.num_cores,
        evaluate_function=evaluate_function,
        decode_function=decode_function
    )


    env = make_vec_envs(args.task, robot, 0, 1)
    num_inputs = env.observation_space.shape[0]
    num_outputs = env.action_space.shape[0]
    env.close()

    config_file = os.path.join(CURR_DIR, 'config', 'evogym_neat.cfg')
    custom_config = [
        ('NEAT', 'pop_size', args.pop_size),
        ('DefaultGenome', 'num_inputs', num_inputs),
        ('DefaultGenome', 'num_outputs', num_outputs)
    ]
    config = neat_cppn.make_config(config_file, custom_config=custom_config)
    config_out_file = os.path.join(save_path, 'evogym_neat.cfg')
    config.save(config_out_file)


    pop = neat_cppn.Population(config)

    reporters = [
        neat_cppn.SaveResultReporter(save_path),
        neat_cppn.StdOutReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    if not args.no_view:
        simulator = EvogymControllerSimulator(
            env_id=args.task,
            robot=robot,
            decode_function=decode_function,
            load_path=save_path,
            history_file='history_reward.csv',
            genome_config=config.genome_config)

        simulate_process = SimulateProcess(
            simulator=simulator,
            generations=args.generation)

        simulate_process.init_process()
        simulate_process.start()


    try:
        pop.run(fitness_function=parallel.evaluate, n=args.generation)
    finally:
        neat_cppn.figure.make_species(save_path)

if __name__=='__main__':
    main()
