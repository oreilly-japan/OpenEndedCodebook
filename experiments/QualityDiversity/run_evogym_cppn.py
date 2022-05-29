import sys
import os
import json
import numpy as np
import torch

import evogym.envs
from evogym import get_full_connectivity


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import me_neat
from parallel import ParallelEvaluator
from experiment_utils import initialize_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'evogym')
sys.path.append(ENV_DIR)
from evaluator import EvogymStructureEvaluatorME
from simulator import EvogymStructureSimulator, SimulateProcess
from substrate import Substrate
from constraint import EvogymStructureConstraint
import structural_bd as BD

from arguments.evogym_me_cppn import get_args


class EvogymStructureDecoder(me_neat.BaseCPPNDecoder):
    def __init__(self, size):
        self.size = size

        x, y = torch.meshgrid(torch.arange(size[0]), torch.arange(size[1]), indexing='ij')
        x = x.flatten()
        y = y.flatten()

        center = (np.array(size) - 1) / 2
        d = np.sqrt(np.square(x - center[0]) + np.square(y - center[1]))

        self.inputs = {'x': x, 'y': y, 'd': d}
        self.output_keys = ['empty', 'rigid', 'soft', 'hori', 'vert']

    def decode(self, genome, config):
        output = super().decode(genome, config)
        output = np.vstack([output[key] for key in self.output_keys])
        material = np.argmax(output, axis=0)

        robot = np.reshape(material, self.size)
        connectivity = get_full_connectivity(robot)
        return (robot, connectivity)


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'evogym_me_cppn', args.name)

    initialize_experiment(args.name, save_path, args)


    area_size = args.shape[0]*args.shape[1]

    bd_dictionary = {
        'block density': BD.BlockDensity(name='block density', value_range=[0,1], resolution=area_size),
        'rigid density': BD.RigidDensity(name='rigid density', value_range=[0,1], resolution=area_size),
        # 'soft density': BD.SoftDensity(name='soft density', value_range=[0,1], resolution=area_size),
        # 'actuator density': BD.ActuatorDensity(name='actuator density', value_range=[0,1], resolution=area_size),
    }
    bd_axis = ['block density','rigid density']


    decoder = EvogymStructureDecoder(args.shape)
    decode_function = decoder.decode

    constraint = EvogymStructureConstraint(decode_function)
    constraint_function = constraint.eval_constraint

    evaluator = EvogymStructureEvaluatorME(args.task, save_path, args.ppo_iters, bd_dictionary, deterministic=args.deterministic)
    evaluate_function = evaluator.evaluate_structure

    parallel = ParallelEvaluator(
        num_workers=args.num_cores,
        evaluate_function=evaluate_function,
        decode_function=decode_function
    )


    config_file = os.path.join(CURR_DIR, 'config', 'evogym_me_cppn.cfg')
    custom_config = [
        ('ME-NEAT', 'offspring_size', args.batch_size),
    ]
    config = me_neat.make_config(config_file, custom_config=custom_config)
    config_out_file = os.path.join(save_path, 'evogym_me_cppn.cfg')
    config.save(config_out_file)


    pop = me_neat.Population(config)

    reporters = [
        me_neat.SaveResultReporter(save_path, list(bd_dictionary.keys())),
        me_neat.MapElitesReporter(),
        me_neat.BDDrawer(save_path, bd_dictionary[bd_axis[0]], bd_dictionary[bd_axis[1]], no_plot=args.no_plot)
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    if not args.no_view:
        simulator = EvogymStructureSimulator(
            env_id=args.task,
            load_path=save_path,
            history_file='history_reward.csv')

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
