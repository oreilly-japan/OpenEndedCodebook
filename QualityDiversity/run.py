import os
import shutil
import json
import random
import numpy as np
import torch
import warnings
warnings.simplefilter('ignore')

from arguments import get_args
import me_neat
import behavioral_descriptor as BD
import visualize

from pytorch_neat.cppn import create_cppn
from parallel import ParallelEvaluator
from simulator import SimulateProcess

from ppo import run_ppo
from evogym import is_connected, has_actuator, get_full_connectivity, hashable
import evogym.envs

def evaluate_bd(robot, connections, config):
    bd_dict = config.extra_info['behavioral_descriptors']
    bd = {bd_name: bd_func.evaluate(robot, connections) for bd_name,bd_func in bd_dict.items()}
    return bd

def get_cppn_input(structure_shape):
    x, y = torch.meshgrid(torch.arange(structure_shape[0]), torch.arange(structure_shape[1]))
    x, y = x.flatten(), y.flatten()
    center = (np.array(structure_shape) - 1) / 2
    d = ((x - center[0]) ** 2 + (y - center[1]) ** 2).sqrt()
    return x, y, d

def get_robot_from_genome(genome, config):
    nodes = create_cppn(genome, config, leaf_names=['x', 'y', 'd'], node_names=['empty', 'rigid', 'soft', 'hori', 'vert'])
    structure_shape = config.extra_info['structure_shape']
    x, y, d = get_cppn_input(structure_shape)
    material = []
    for node in nodes:
        material.append(node(x=x, y=y, d=d).numpy())
    material = np.vstack(material).argmax(axis=0)
    robot = material.reshape(structure_shape)
    return robot

def eval_genome_fitness(genome, config, genome_id, generation):
    robot = get_robot_from_genome(genome, config)
    connectivity = get_full_connectivity(robot)
    save_path_generation = os.path.join(config.extra_info['save_path'], f'generation_{generation}')
    save_path_structure = os.path.join(save_path_generation, 'structure', f'{genome_id}')
    save_path_controller = os.path.join(save_path_generation, 'controller')
    np.savez(save_path_structure, robot=robot, connectivity=connectivity)
    fitness = run_ppo(
        env_id=config.extra_info['environment'],
        structure=(robot, connectivity),
        train_iter=config.extra_info['train_iters'],
        saving_convention=(save_path_controller, genome_id),
        deterministic=config.extra_info['deterministic']
    )
    bd = evaluate_bd(robot, connectivity, config)
    return fitness, bd

def eval_genome_constraint(genome, config):
    robot = get_robot_from_genome(genome, config)
    validity = is_connected(robot) and has_actuator(robot)
    if validity:
        robot_hash = hashable(robot)
        if robot_hash in config.extra_info['structure_hashes']:
            validity = False
        else:
            config.extra_info['structure_hashes'][robot_hash] = True
    return validity


def main():

    args = get_args()

    root_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(root_dir, 'out', args.name)

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
            return None, None
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

    figure_save_path = os.path.join(save_path, 'bd_map')
    os.makedirs(figure_save_path)
    Drawer = visualize.ProgressDrawer(no_plot=args.no_plot)
    Drawer.initialize_figure(save_dir=figure_save_path)
    Drawer.set_bd(( bd_axis[0], bd_dictionary[bd_axis[0]] ),
                  ( bd_axis[1], bd_dictionary[bd_axis[1]] ))

    evaluator = ParallelEvaluator(args.num_cores, eval_genome_fitness, Drawer)

    structure_hashes = {}

    experiment_config = {
        'environment': args.task,
        'structure_shape': tuple(args.shape),
        'train_iters': args.ppo_iters,
        'deterministic': args.deterministic,
        'save_path': save_path,
        'structure_hashes': structure_hashes,
        'behavioral_descriptors': bd_dictionary,
    }

    neat_config_path = os.path.join(root_dir, 'neat_config.ini')

    pop = me_neat.Population(
        neat_config_path,
        experiment_config,
        args.pop_size,
        evaluator.evaluate_fitness,
        eval_genome_constraint)

    reporters = [
        me_neat.MapElitesReporter(),
        me_neat.SaveResultReporter(save_path, list(bd_dictionary.keys()))
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)

    if not args.no_view:
        simulator = SimulateProcess(
            args.task,
            save_path,
            args.generation,
            deterministic=False)
        simulator.init_process()
        simulator.start()

    pop.run(n=args.generation)

    best_robot = get_robot_from_genome(pop.best_genome, pop.config)
    best_fitness = pop.best_genome.fitness

    print('best robot: \n', best_robot)
    print(f'fitness: {best_fitness: =.5f}')

if __name__=='__main__':
    main()
