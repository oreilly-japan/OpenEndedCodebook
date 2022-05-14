import sys
import os
import shutil
import json
import numpy as np
import torch


import me_neat
from parallel import ParallelEvaluator

import evogym.envs
from evogym import is_connected, has_actuator, get_full_connectivity, hashable

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_cppn_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from simulator import SimulateProcess
import behavioral_descriptor as BD

from ppo import run_ppo



class EvogymStructureDecoder():
    def __init__(self, structure_shape):
        self.structure_shape = structure_shape

        self.input_x, self.input_y = torch.meshgrid(torch.arange(structure_shape[0]), torch.arange(structure_shape[1]), indexing='ij')
        self.input_x = self.input_x.flatten()
        self.input_y = self.input_y.flatten()

        center = (np.array(structure_shape) - 1) / 2
        self.input_d = ((self.input_x - center[0]) ** 2 + (self.input_y - center[1]) ** 2).sqrt()

    def decode(self, genome, config):
        nodes = me_neat.create_cppn(
            genome, config,
            leaf_names=['x', 'y', 'd'],
            node_names=['empty', 'rigid', 'soft', 'hori', 'vert'])

        material = []
        for node in nodes:
            material.append(node(x=self.input_x, y=self.input_y, d=self.input_d).numpy())
        material = np.vstack(material).argmax(axis=0)

        robot = material.reshape(self.structure_shape)
        connectivity = get_full_connectivity(robot)
        return (robot, connectivity)


class EvogymStructureEvaluator():
    def __init__(self, env_id, save_path, ppo_iters, bd_dictionary, deterministic=False):
        self.env_id = env_id
        self.save_path = save_path
        self.structure_save_path = os.path.join(save_path, 'structure')
        self.controller_save_path = os.path.join(save_path, 'controller')
        self.ppo_iters = ppo_iters
        self.bd_dictionary = bd_dictionary
        self.deterministic = deterministic

        os.makedirs(self.structure_save_path, exist_ok=True)
        os.makedirs(self.controller_save_path, exist_ok=True)

    def evaluate_structure(self, key, structure, generation):

        file_structure = os.path.join(self.structure_save_path, f'{key}')
        file_controller = os.path.join(self.controller_save_path, f'{key}')
        np.savez(file_structure, robot=structure[0], connectivity=structure[1])

        fitness = run_ppo(
            env_id=self.env_id,
            structure=structure,
            train_iter=self.ppo_iters,
            save_file=file_controller,
            deterministic=self.deterministic
        )
        bd = {bd_name: bd_func.evaluate(*structure) for bd_name,bd_func in self.bd_dictionary.items()}

        results = {
            'fitness': fitness,
            'bd': bd
        }
        return results


class Constraint():
    def __init__(self, decode_function):
        self.decode_function = decode_function
        self.hashes = {}

    def eval_genome_constraint(self, genome, config, generation):
        robot = self.decode_function(genome, config)[0]
        validity = is_connected(robot) and has_actuator(robot)
        if validity:
            robot_hash = hashable(robot)
            if robot_hash in self.hashes:
                validity = False
            else:
                self.hashes[robot_hash] = True

        return validity


def main():

    args = get_args()

    save_path = os.path.join(CURR_DIR, 'evogym_cppn_out', args.name)

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


    area_size = args.shape[0]*args.shape[1]

    bd_dictionary = {
        'block density': BD.BlockDensity(name='block density', value_range=[0,1], resolution=area_size),
        'rigid density': BD.RigidDensity(name='rigid density', value_range=[0,1], resolution=area_size),
        # 'soft density': BD.SoftDensity(name='soft density', value_range=[0,1], resolution=area_size),
        # 'actuator density': BD.ActuatorDensity(name='actuator density', value_range=[0,1], resolution=area_size),
    }
    bd_axis = ['block density','rigid density']


    decoder = EvogymStructureDecoder(args.shape)
    constraint = Constraint(decoder.decode)
    evaluator = EvogymStructureEvaluator(args.task, save_path, args.ppo_iters, bd_dictionary, deterministic=args.deterministic)

    parallel = ParallelEvaluator(
        num_workers=args.num_cores,
        evaluate_function=evaluator.evaluate_structure,
        decode_function=decoder.decode,
        parallel=True
    )


    config_path = os.path.join(UTIL_DIR, 'me_config.ini')
    overwrite_config = [
        ('ME-NEAT', 'offspring_size', args.batch_size),
    ]
    config = me_neat.make_config(config_path, custom_config=overwrite_config)
    config_out_path = os.path.join(save_path, 'me_config.ini')
    config.save(config_out_path)


    pop = me_neat.Population(config)

    reporters = [
        me_neat.SaveResultReporter(save_path, list(bd_dictionary.keys())),
        me_neat.MapElitesReporter(),
        me_neat.BDDrawer(save_path, bd_dictionary[bd_axis[0]], bd_dictionary[bd_axis[1]], no_plot=args.no_plot)
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    if not args.no_view:
        simulator = SimulateProcess(
            env_id=args.task,
            load_path=save_path,
            history_file='history_reward.csv',
            generations=args.generation,
            deterministic=False
        )

        simulator.init_process()
        simulator.start()


    best_genome = pop.run(
        fitness_function=parallel.evaluate,
        constraint_function=constraint.eval_genome_constraint,
        n=args.generation
    )

    best_robot = get_structure_from_genome(best_genome, config, args.shape)
    best_fitness = best_genome.fitness

    print('best robot: \n', best_robot)
    print(f'fitness: {best_fitness: =.5f}')


if __name__=='__main__':
    main()
