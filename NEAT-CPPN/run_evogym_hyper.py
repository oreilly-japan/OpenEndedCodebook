import sys
import os
import shutil
import json
import random
import numpy as np
import torch


import neat_cppn
from parallel import ParallelEvaluator

import evogym.envs
from evogym import is_connected, has_actuator, get_full_connectivity, hashable

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_hyper_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from gym_utils import make_vec_envs
from simulator import SimulateProcess
from substrate import Substrate


class EvogymHyperDecoder():
    def __init__(self, env_id, robot):

        self.substrate = Substrate(env_id, robot)
        self.substrate.make_substrate()
        self.substrate.make_vectors()
        self.edge_labels, self.edge_inputs = self.substrate.get_connection_inputs([('input','output')])
        self.node_labels, self.node_inputs = self.substrate.get_node_inputs(['output'])
        self.input_nodes = self.substrate.get_nodes('input')
        self.output_nodes = self.substrate.get_nodes('output')
        self.input_dims = len(self.edge_inputs)

    def decode(self, genome, config):
        nodes = neat_cppn.create_cppn(
            genome, config,
            leaf_names=self.edge_inputs.keys(),
            node_names=['value'])

        weights = nodes[0](**self.edge_inputs).numpy()
        weights = (weights-0.5) * 20

        connections = {edge: weight for edge,weight in zip(self.edge_labels, weights)}

        biases = nodes[0](**self.node_inputs).numpy()
        biases = (biases-0.5) * 20

        biases = {node: bias for node,bias in zip(self.node_labels, biases)}

        return neat_cppn.FeedForwardNetwork.create_from_weights(
            input_keys=self.input_nodes,
            output_keys=self.output_nodes,
            biases=biases,
            weights=connections,
            weight_thr=0.5)


class EvogymEvaluator():
    def __init__(self, env_id, structure, num_eval=1):
        self.env_id = env_id
        self.structure = structure
        self.num_eval = num_eval

    def evaluate_controller(self, key, controller, generation):
        env = make_vec_envs(self.env_id, self.structure, random.randint(0,10000), 1)

        obs = env.reset()
        episode_rewards = []
        while len(episode_rewards) < self.num_eval:
            action = np.array(controller.activate(obs[0]))*2 - 1
            obs, _, done, infos = env.step([np.array(action)])

            if 'episode' in infos[0]:
                reward = infos[0]['episode']['r']
                episode_rewards.append(reward)

        results = {
            'fitness': np.mean(episode_rewards),
        }
        return results


def main():

    args = get_args()

    save_path = os.path.join(CURR_DIR, 'evogym_hyper_out', args.name)

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


    robot = np.array([
        [2,0,0,0,0],
        [1,0,0,1,1],
        [4,3,3,3,4],
        [4,3,1,3,4],
        [4,0,0,0,4]
    ])
    connectivity = get_full_connectivity(robot)
    structure = (robot, connectivity)
    robot_file = os.path.join(save_path, 'structure')
    np.savez(robot_file, robot=robot, connectivity=connectivity)


    decoder = EvogymHyperDecoder(args.task, robot)
    evaluator = EvogymEvaluator(args.task, structure, args.eval_num)

    parallel = ParallelEvaluator(
        num_workers=args.num_cores,
        evaluate_function=evaluator.evaluate_controller,
        decode_function=decoder.decode,
        parallel=True
    )


    env = make_vec_envs(args.task, structure, 0, 1)
    num_inputs = env.observation_space.shape[0]
    num_outputs = env.action_space.shape[0]

    config_path = os.path.join(UTIL_DIR, 'neat_config.ini')
    overwrite_config = [
        ('NEAT', 'pop_size', args.pop_size),
        ('DefaultGenome', 'num_inputs', decoder.input_dims),
        ('DefaultGenome', 'num_outputs', 1)
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
            structure=structure,
            decode_function=decoder.decode,
            load_path=save_path,
            history_file='history_reward.csv',
            neat_config=config,
            generations=args.generation)

        simulator.init_process()
        simulator.start()


    pop.run(fitness_function=parallel.evaluate, n=args.generation)

if __name__=='__main__':
    main()
