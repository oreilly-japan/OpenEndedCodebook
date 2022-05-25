import sys
import os
import shutil
import json
import numpy as np
import torch


import neat_cppn
from parallel import ParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'maze_hyper_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from drawer import DrawReporter
from maze_environment_numpy import MazeEnvironment



class MazeNNDecoder():
    def __init__(self):
        self.input_nodes = {
            'sensor270': [np.cos(270/180*np.pi), np.sin(270/180*np.pi), 1, 1, 0, 0, 0],
            'sensor315': [np.cos(315/180*np.pi), np.sin(315/180*np.pi), 1, 1, 0, 0, 0],
            'sensor0'  : [np.cos(  0/180*np.pi), np.sin(  0/180*np.pi), 1, 1, 0, 0, 0],
            'sensor45' : [np.cos( 45/180*np.pi), np.sin( 45/180*np.pi), 1, 1, 0, 0, 0],
            'sensor90' : [np.cos( 90/180*np.pi), np.sin( 90/180*np.pi), 1, 1, 0, 0, 0],
            'sensor180': [np.cos(180/180*np.pi), np.sin(180/180*np.pi), 1, 1, 0, 0, 0],
            'rader0'   : [np.cos(  0/180*np.pi), np.sin(  0/180*np.pi), 2, 0, 1, 0, 0],
            'rader90'  : [np.cos( 90/180*np.pi), np.sin( 90/180*np.pi), 2, 0, 1, 0, 0],
            'rader180' : [np.cos(180/180*np.pi), np.sin(180/180*np.pi), 2, 0, 1, 0, 0],
            'rader270' : [np.cos(270/180*np.pi), np.sin(270/180*np.pi), 2, 0, 1, 0, 0]
        }
        self.hidden_nodes = {
            'hidden60' : [np.cos( 60/180*np.pi)/2, np.sin( 60/180*np.pi)/2, 0.5, 0, 0, 0, 0],
            'hidden180': [np.cos(180/180*np.pi)/2, np.sin(180/180*np.pi)/2, 0.5, 0, 0, 0, 0],
            'hidden300': [np.cos(300/180*np.pi)/2, np.sin(300/180*np.pi)/2, 0.5, 0, 0, 0, 0]
        }
        self.output_nodes = {
            'actuator_rotate': [0, 0, 0, 0, 0, 1, 0],
            'actuator_speed' : [0, 0, 0, 0, 0, 0, 1]
        }

        edges = {}
        edges.update(self.make_edge_inputs(inputs=self.input_nodes, outputs=self.hidden_nodes))
        edges.update(self.make_edge_inputs(inputs=self.input_nodes, outputs=self.output_nodes))
        edges.update(self.make_edge_inputs(inputs=self.hidden_nodes, outputs=self.output_nodes))

        edge_inputs = np.vstack(list(edges.values()))
        edge_inputs = torch.from_numpy(edge_inputs)

        self.edges = list(edges.keys())
        self.edge_inputs = {
            'x1'     : edge_inputs[:,0],
            'y1'     : edge_inputs[:,1],
            'd1'     : edge_inputs[:,2],
            'sensor1': edge_inputs[:,3],
            'rader1' : edge_inputs[:,4],
            'rotate1': edge_inputs[:,5],
            'speed1' : edge_inputs[:,6],
            'x2'     : edge_inputs[:,7],
            'y2'     : edge_inputs[:,8],
            'd2'     : edge_inputs[:,9],
            'sensor2': edge_inputs[:,10],
            'rader2' : edge_inputs[:,11],
            'rotate2': edge_inputs[:,12],
            'speed2' : edge_inputs[:,13]
        }

        nodes = {}
        blank = np.zeros(7)
        nodes.update(self.make_node_inputs(self.hidden_nodes, blank))
        nodes.update(self.make_node_inputs(self.output_nodes, blank))

        node_inputs = np.vstack(list(nodes.values()))
        node_inputs = torch.from_numpy(node_inputs)

        self.nodes = list(nodes.keys())
        self.node_inputs = {
            'x1'     : node_inputs[:,0],
            'y1'     : node_inputs[:,1],
            'd1'     : node_inputs[:,2],
            'sensor1': node_inputs[:,3],
            'rader1' : node_inputs[:,4],
            'rotate1': node_inputs[:,5],
            'speed1' : node_inputs[:,6],
            'x2'     : node_inputs[:,7],
            'y2'     : node_inputs[:,8],
            'd2'     : node_inputs[:,9],
            'sensor2': node_inputs[:,10],
            'rader2' : node_inputs[:,11],
            'rotate2': node_inputs[:,12],
            'speed2' : node_inputs[:,13]
        }

    @staticmethod
    def make_edge_inputs(inputs, outputs):
        edge_inputs = {}
        for node_i,geo_i in inputs.items():
            for node_o,geo_o in outputs.items():
                edge_inputs[(node_i, node_o)] = geo_i + geo_o
        return edge_inputs

    @staticmethod
    def make_node_inputs(nodes, blank):
        node_inputs = {}
        for node,geo in nodes.items():
            node_inputs[node] = np.hstack([geo, blank])
        return node_inputs


    def decode(self, genome, config):
        nodes = neat_cppn.create_cppn(
            genome, config,
            leaf_names=self.edge_inputs.keys(),
            node_names=['value'])

        weights = nodes[0](**self.edge_inputs).numpy()
        weights = (weights-0.5) * 20

        connections = {edge: weight for edge,weight in zip(self.edges, weights)}

        biases = nodes[0](**self.node_inputs).numpy()
        biases = (biases-0.5) * 20

        biases = {node: bias for node,bias in zip(self.nodes, biases)}

        return neat_cppn.FeedForwardNetwork.create_from_weights(
            input_keys=list(self.input_nodes.keys()),
            output_keys=list(self.output_nodes.keys()),
            biases=biases,
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

    save_path = os.path.join(CURR_DIR, 'maze_hyper_out', args.name)

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
