import sys
import os
import shutil
import json
import numpy as np
import torch


import neat_cppn
from parallel import ParallelEvaluator

import evogym.envs
from evogym import is_connected, has_actuator, get_full_connectivity, hashable

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_cppn_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from simulator import SimulateProcess

from ppo import run_ppo


def get_cppn_input(structure_shape):
    x, y = torch.meshgrid(torch.arange(structure_shape[0]), torch.arange(structure_shape[1]), indexing='ij')
    x, y = x.flatten(), y.flatten()

    center = (np.array(structure_shape) - 1) / 2
    d = ((x - center[0]) ** 2 + (y - center[1]) ** 2).sqrt()
    return x, y, d

def get_structure_from_genome(genome, config, structure_shape):
    nodes = neat_cppn.create_cppn(
        genome, config,
        leaf_names=['x', 'y', 'd'],
        node_names=['empty', 'rigid', 'soft', 'hori', 'vert'])
    x, y, d = get_cppn_input(structure_shape)

    material = []
    for node in nodes:
        material.append(node(x=x, y=y, d=d).numpy())
    material = np.vstack(material).argmax(axis=0)

    robot = material.reshape(structure_shape)
    connectivity = get_full_connectivity(robot)
    return (robot, connectivity)


class CPPNEvaluator():
    def __init__(self, env_id, structure_shape, save_path, ppo_iters, deterministic=False):
        self.env_id = env_id
        self.structure_shape = structure_shape
        self.save_path = save_path
        self.structure_save_path = os.path.join(save_path, 'structure')
        self.controller_save_path = os.path.join(save_path, 'controller')
        self.ppo_iters = ppo_iters
        self.deterministic = deterministic

        os.makedirs(self.structure_save_path, exist_ok=True)
        os.makedirs(self.controller_save_path, exist_ok=True)

    def eval_genome(self, genome, config, generation, **kwargs):
        structure = get_structure_from_genome(genome, config, self.structure_shape)

        file_structure = os.path.join(self.structure_save_path, f'{genome.key}')
        file_controller = os.path.join(self.controller_save_path, f'{genome.key}')
        np.savez(file_structure, robot=structure[0], connectivity=structure[1])

        fitness = run_ppo(
            env_id=self.env_id,
            structure=structure,
            train_iter=self.ppo_iters,
            save_file=file_controller,
            deterministic=self.deterministic
        )

        results = {
            'fitness': fitness
        }
        return results


class Constraint():
    def __init__(self, structure_shape):
        self.structure_shape = structure_shape
        self.hashes = {}

    def eval_genome_constraint(self, genomes, config, generation):
        validity_list = []
        for _,genome in genomes:
            robot = get_structure_from_genome(genome, config, self.structure_shape)[0]
            validity = is_connected(robot) and has_actuator(robot)
            if validity:
                robot_hash = hashable(robot)
                if robot_hash in self.hashes:
                    validity = False
                else:
                    self.hashes[robot_hash] = True
            validity_list.append(validity)

        return validity_list


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


    evaluator = CPPNEvaluator(args.task, args.shape, save_path, args.ppo_iters, deterministic=args.deterministic)
    parallel = ParallelEvaluator({}, args.num_cores, evaluator.eval_genome)

    constraint = Constraint(args.shape)


    config_path = os.path.join(UTIL_DIR, 'neat_config.ini')
    overwrite_config = [
        ('NEAT', 'pop_size', args.pop_size),
    ]
    config = neat_cppn.make_config(config_path, custom_config=overwrite_config)
    config_out_path = os.path.join(save_path, 'neat_config.ini')
    config.save(config_out_path)


    pop = neat_cppn.Population(config)

    reporters = [
        neat_cppn.SaveResultReporter(save_path),
        neat_cppn.StdOutReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    if not args.no_view:
        simulator = SimulateProcess(
            env_id=args.task,
            load_path=save_path,
            history_file='history_reward.csv',
            generations=args.generation,
            deterministic=False)

        simulator.init_process()
        simulator.start()


    pop.run(parallel.evaluate, constraint_function=constraint.eval_genome_constraint, n=args.generation)

if __name__=='__main__':
    main()
