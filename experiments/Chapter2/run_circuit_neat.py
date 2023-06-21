import sys
import os


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import neat_cppn
from parallel import EvaluatorParallel
from experiment_utils import initialize_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'circuit')
sys.path.append(ENV_DIR)
from evaluator import CircuitEvaluator, load_circuit


from arguments.circuit_neat import get_args


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'circuit_neat', args.name)

    initialize_experiment(args.name, save_path, args)


    decode_function = neat_cppn.FeedForwardNetwork.create

    input_data, output_data = load_circuit(ROOT_DIR, args.task)
    evaluator = CircuitEvaluator(input_data, output_data, error_type=args.error)
    evaluate_function = evaluator.evaluate_circuit

    parallel = EvaluatorParallel(
        num_workers=args.num_cores,
        evaluate_function=evaluate_function,
        decode_function=decode_function
    )


    config_file = os.path.join(CURR_DIR, 'config', 'circuit_neat.cfg')
    custom_config = [
        ('NEAT', 'pop_size', args.pop_size),
        ('DefaultGenome', 'num_inputs', input_data.shape[1]),
        ('DefaultGenome', 'num_outputs', output_data.shape[1]),
    ]
    config = neat_cppn.make_config(config_file, custom_config=custom_config)
    config_out_file = os.path.join(save_path, 'circuit_neat.cfg')
    config.save(config_out_file)


    pop = neat_cppn.Population(config)

    figure_path = os.path.join(save_path, 'figure')
    reporters = [
        neat_cppn.SaveResultReporter(save_path),
        neat_cppn.StdOutReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    try:
        best_genome = pop.run(fitness_function=parallel.evaluate, n=args.generation)

        print()
        print('best circuit result:')
        evaluator.print_result(decode_function(best_genome, config.genome_config))

    finally:
        neat_cppn.figure.make_species(save_path)

if __name__=='__main__':
    main()
