import sys
import os
import csv
import ast
import json
import pickle


import mcc

import multiprocessing as mp


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'maze_utils')
sys.path.append(UTIL_DIR)
from maze_genome import MazeGenome
from maze_genome_decoder import MazeGenomeDecoder

import matplotlib.pyplot as plt


import argparse

def get_args():
    parser = argparse.ArgumentParser(
        description='make plot of  maze and solver agent'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        help='experiment name'
    )
    parser.add_argument(
        '--num-cores',
        default=1, type=int,
        help='num of multiprocesses'
    )
    parser.add_argument(
        '-cb', '--colorbar',
        action='store_true', default=False,
        help='plot colorbar of timestep'
    )
    parser.add_argument(
        '--not-overwrite',
        action='store_true', default=False,
        help='skip process if already gif exists (default: overwrite)'
    )
    parser.add_argument(
        '--no-multi',
        action='store_true', default=False,
        help='do without using multiprocess. if error occur, try this option.'
    )

    args = parser.parse_args()

    assert args.name is not None, 'argumented error: input "--name {experiment name}"'

    return args


def make_figure(expt_path, save_path, maze_key, agent_key, config, colorbar=False, overwrite=True):

    agent_file = os.path.join(expt_path, 'agent', f'{agent_key}.pickle')
    maze_file = os.path.join(expt_path, 'maze', f'{maze_key}.pickle')

    save_file = os.path.join(save_path, f'{maze_key}.jpg')

    if os.path.exists(save_file) and not overwrite:
        return

    with open(agent_file, 'rb') as f:
        agent_genome = pickle.load(f)

    with open(maze_file, 'rb') as f:
        maze_genome = pickle.load(f)

    controller = mcc.FeedForwardNetwork.create(agent_genome, config.genome1_config)
    MazeDecoder = MazeGenomeDecoder(config.genome2_config)
    maze, timesteps = MazeDecoder.decode(maze_genome, config.genome2_config)

    done = False
    maze.reset()
    data = [maze.get_agent_location()]
    for i in range(timesteps):
        obs = maze.get_observation()
        action = controller.activate(obs)
        done = maze.update(action)
        data.append(maze.get_agent_location())
        if done:
            break

    fig, ax = plt.subplots(figsize=(maze_genome.maze_size[0]/2, maze_genome.maze_size[1]/2))

    walls = maze.walls
    for w_i in range(walls.shape[0]):
        ax.plot(walls[w_i,:,0], walls[w_i,:,1], c='k', linewidth=3)

    start_point = maze.init_location
    exit_point = maze.exit_point
    ax.scatter(start_point[0], start_point[1], color=[0.0,0.6,0.3], s=96, marker='s')
    ax.scatter(exit_point[0], exit_point[1], color=[0.9,0.2,0.0], s=128, marker='*')

    cmap = plt.get_cmap('gist_earth')
    for i in range(len(data)-1):
        ax.plot([data[i][0],data[i+1][0]], [data[i][1],data[i+1][1]], c=cmap(int(i/timesteps*255)), linewidth=2)
    ax.axis('off')

    if colorbar:
        cmap_ax = fig.add_axes([0.9,0.16,0.02,0.66])
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0,vmax=timesteps))
        fig.colorbar(sm, cax=cmap_ax).set_label('timestep', size=9, labelpad=12, rotation=270)
        cmap_ax.tick_params(labelsize=6)

    plt.savefig(save_file, bbox_inches='tight')


    print(f'maze genome {maze_key} ... done')
    return


def main():

    args = get_args()


    expt_path = os.path.join(CURR_DIR, 'maze_out', 'main', args.name)

    config_path = os.path.join(UTIL_DIR, 'mcc_config.ini')
    config = mcc.make_config(mcc.DefaultGenome, MazeGenome, config_path)


    save_path = os.path.join(expt_path, 'figure')
    os.makedirs(save_path, exist_ok=True)


    maze_history_file = os.path.join(expt_path, 'history_maze.csv')
    with open(maze_history_file, 'r') as f:
        reader = csv.reader(f)
        histories = list(reader)[1:]
        pairs = [(int(hist[1]),ast.literal_eval(hist[3])[0]) for hist in histories]


    if not args.no_multi:

        pool = mp.Pool(args.num_cores)
        jobs = []

        for maze_key, agent_key in pairs:
            func_args = (expt_path, save_path, maze_key, agent_key, config)
            func_kwargs = {
                'colorbar': args.colorbar,
                'overwrite': not args.not_overwrite
            }
            jobs.append(pool.apply_async(make_figure, args=func_args, kwds=func_kwargs))

        for job in jobs:
            job.get(timeout=None)


    else:

        for maze_key, agent_key in pairs:
            func_args = (expt_path, save_path, maze_key, agent_key, config)
            func_kwargs = {
                'colorbar': args.colorbar,
                'overwrite': not args.not_overwrite
            }

            make_figure(*func_args, **func_kwargs)

if __name__=='__main__':
    main()
