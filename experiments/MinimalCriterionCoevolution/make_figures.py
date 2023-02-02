import sys
import os
import csv
import ast
import pickle
import matplotlib.pyplot as plt

import multiprocessing as mp


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import mcc
from experiment_utils import load_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'maze')
sys.path.append(ENV_DIR)
from maze_genome import MazeGenome
from maze_genome_decoder import MazeGenomeDecoder
from maze_environment_numpy import MazeEnvironment


from arguments.maze_mcc import get_figure_args


def make_figure(maze_key, maze_file, maze_decode_function, maze_config, agent_file, agent_decode_function, agent_config, figure_file, colorbar=False):

    with open(agent_file, 'rb') as f:
        agent_genome = pickle.load(f)

    with open(maze_file, 'rb') as f:
        maze_genome = pickle.load(f)

    controller = agent_decode_function(agent_genome, agent_config)
    maze, timesteps = maze_decode_function(maze_genome, maze_config)

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

    plt.savefig(figure_file, bbox_inches='tight')
    plt.close()


    print(f'maze genome {maze_key} ... done')
    return


def main():

    args = get_figure_args()


    expt_path = os.path.join(CURR_DIR, 'out', 'maze_mcc', 'main', args.name)
    expt_args = load_experiment(expt_path)
    bootstrap_path = os.path.join(CURR_DIR, 'out', 'maze_mcc', 'bootstrap', expt_args['bootstrap'])
    bootstrap_args = load_experiment(bootstrap_path)

    config_file = os.path.join(expt_path, 'maze_mcc.cfg')
    config = mcc.make_config(mcc.DefaultGenome, MazeGenome, config_file)


    bootstrap_args = load_experiment(bootstrap_path)
    maze_config = {
        'exit_range': bootstrap_args['exit_range'],
        'init_heading': 45,
    }
    agent_config = {
        'radius': bootstrap_args['radius'],
        'range_finder_range': bootstrap_args['range_finder'],
        'max_speed': bootstrap_args['max_speed'],
        'max_angular_vel': bootstrap_args['max_angular_vel'],
        'speed_scale': bootstrap_args['speed_scale'],
        'angular_scale': bootstrap_args['angular_scale'],
    }
    MazeDecoder = MazeGenomeDecoder(config.genome2_config, maze_kwargs=maze_config, agent_kwargs=agent_config)
    maze_decode_function = MazeDecoder.decode

    agent_decode_function = mcc.FeedForwardNetwork.create


    figure_path = os.path.join(expt_path, 'figure')
    os.makedirs(figure_path, exist_ok=True)


    maze_history_file = os.path.join(expt_path, 'history_maze.csv')
    with open(maze_history_file, 'r') as f:
        reader = csv.reader(f)
        histories = list(reader)[1:]

        condition = lambda z: z >= args.start_generation and z < args.end_generation
        pairs = [(int(hist[1]), ast.literal_eval(hist[3])[0]) for hist in histories if condition(int(hist[0]))]


    if not args.no_multi:

        pool = mp.Pool(args.num_cores)
        jobs = []

        for maze_key, agent_key in pairs:

            figure_file = os.path.join(figure_path, f'{maze_key}.jpg')
            maze_genome_file = os.path.join(expt_path, 'maze', f'{maze_key}.pickle')
            agent_genome_file = os.path.join(expt_path, 'agent', f'{agent_key}.pickle')

            if os.path.exists(figure_file) and args.not_overwrite:
                continue

            func_args = (maze_key, maze_genome_file, maze_decode_function, config.genome2_config,
                        agent_genome_file, agent_decode_function, config.genome1_config, figure_file)
            func_kwargs = {
                'colorbar': args.colorbar,
            }
            jobs.append(pool.apply_async(make_figure, args=func_args, kwds=func_kwargs))

        for job in jobs:
            job.get(timeout=None)


    else:

        for maze_key, agent_key in pairs:

            figure_file = os.path.join(figure_path, f'{maze_key}.jpg')
            maze_file = os.path.join(expt_path, 'maze', f'{maze_key}.pickle')
            agent_file = os.path.join(expt_path, 'agent', f'{agent_key}.pickle')

            if os.path.exists(figure_file) and args.not_overwrite:
                continue

            func_args = (maze_key, maze_file, maze_decode_function, config.genome2_config,
                        agent_file, agent_decode_function, config.genome1_config, figure_file)
            func_kwargs = {
                'colorbar': args.colorbar,
            }

            make_figure(*func_args, **func_kwargs)

if __name__=='__main__':
    main()
