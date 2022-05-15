import sys
import os
import shutil
import json
import numpy as np
import torch


import neat_cppn
from parallel import ParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'maze_cppn_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from drawer import DrawReporter
from maze_environment_numpy import MazeEnvironment


class MazeNNDecoder():
    def __init__(self):
        self.input_nodes = {
            'sensor270': [np.cos(270/180*np.pi), np.sin(270/180*np.pi), 1, 0],
            'sensor315': [np.cos(315/180*np.pi), np.sin(315/180*np.pi), 1, 0],
            'sensor0'  : [np.cos(  0/180*np.pi), np.sin(  0/180*np.pi), 1, 0],
            'sensor45' : [np.cos( 45/180*np.pi), np.sin( 45/180*np.pi), 1, 0],
            'sensor90' : [np.cos( 90/180*np.pi), np.sin( 90/180*np.pi), 1, 0],
            'sensor180': [np.cos(180/180*np.pi), np.sin(180/180*np.pi), 1, 0],
            'rader0'   : [np.cos(  0/180*np.pi), np.sin(  0/180*np.pi), 0, 1],
            'rader90'  : [np.cos( 90/180*np.pi), np.sin( 90/180*np.pi), 0, 1],
            'rader180' : [np.cos(180/180*np.pi), np.sin(180/180*np.pi), 0, 1],
            'rader270' : [np.cos(270/180*np.pi), np.sin(270/180*np.pi), 0, 1]
        }
        self.output_nodes = {
            'actuator_rotate': [1, 0],
            'actuator_speed' : [0, 1]
        }

        cppn_inputs = np.vstack([
            np.vstack([node_i + node_o for node_i in self.input_nodes.values()]) \
                for node_o in self.output_nodes.values() ])
        cppn_inputs = torch.from_numpy(cppn_inputs).clone()

        self.inputs = {
            'x'     : cppn_inputs[:,0],
            'y'     : cppn_inputs[:,1],
            'sensor': cppn_inputs[:,2],
            'rader' : cppn_inputs[:,3],
            'rotate': cppn_inputs[:,4],
            'speed' : cppn_inputs[:,5]
        }

    def decode(self, genome, config):
        nodes = neat_cppn.create_cppn(
            genome, config,
            leaf_names=self.inputs.keys(),
            node_names=['edge_weight'])

        weights = nodes[0](**self.inputs).numpy()
        weights = np.reshape(weights, (len(self.input_nodes), len(self.output_nodes)))
        weights = (weights-0.5) * 20

        connections = {}
        for i_i,node_i in enumerate(self.input_nodes.keys()):
            for o_i,node_o in enumerate(self.output_nodes.keys()):
                connections[(node_i,node_o)] = weights[i_i,o_i]

        return neat_cppn.FeedForwardNetwork.create_from_weights(
            input_keys=list(self.input_nodes.keys()),
            output_keys=list(self.output_nodes.keys()),
            weights=connections,
            weight_thr=0.5)


class MazeEvaluator():
    def __init__(self, maze, timesteps):
        self.maze = maze
        self.timesteps = timesteps

    def evaluate_agent(self, key, controller, generation):
        self.maze.reset()

        done = False
        for i in range(self.timesteps):
            obs = self.maze.get_observation()
            action = controller.activate(obs)
            done = self.maze.update(action)
            if done:
                break

        if done:
            reward = 1.0
        else:
            distance = self.maze.get_distance_to_exit()
            reward = (self.maze.initial_distance - distance) / self.maze.initial_distance

        last_loc = self.maze.get_agent_location()
        results = {
            'fitness': reward,
            'data': [last_loc[0], last_loc[1]]
        }
        return results



def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'maze_cppn_out', args.name)

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


    maze_env_config = os.path.join(UTIL_DIR, f'{args.task}_maze.txt')
    maze_env = MazeEnvironment.read_environment(maze_env_config)


    decoder = MazeNNDecoder()
    evaluator = MazeEvaluator(maze_env, args.timesteps)
    parallel = ParallelEvaluator(
        num_workers=args.num_cores,
        evaluate_function=evaluator.evaluate_agent,
        decode_function=decoder.decode
    )


    config_path = os.path.join(UTIL_DIR, 'neat_config.ini')
    overwrite_config = [
        ('NEAT', 'pop_size', args.pop_size),
    ]
    config = neat_cppn.make_config(config_path, custom_config=overwrite_config)
    config_out_path = os.path.join(save_path, 'neat_config.ini')
    config.save(config_out_path)


    pop = neat_cppn.Population(config)

    figure_path = os.path.join(save_path, 'progress')
    reporters = [
        neat_cppn.SaveResultReporter(save_path),
        neat_cppn.StdOutReporter(True),
        DrawReporter(maze_env, args.timesteps, figure_path, decoder.decode, no_plot=args.no_plot)
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)


    pop.run(fitness_function=parallel.evaluate, n=args.generation)

if __name__=='__main__':
    main()
