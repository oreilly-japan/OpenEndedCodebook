import os
import sys
import csv
import argparse
import json
import pickle
import numpy as np

import multiprocessing as mp

from PIL import Image
import imageio
from pygifsicle import gifsicle


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_utils')
sys.path.append(UTIL_DIR)
from gym_utils import make_vec_envs

import evogym.envs

from neat.nn import FeedForwardNetwork


def get_args():
    parser = argparse.ArgumentParser(
        description='make robot gifs'
    )
    parser.add_argument(
        '-n', '--name',
        type=str,
        help='experiment name'
    )
    parser.add_argument(
        '-r', '--resolution-ratio',
        default=0.2, type=float,
        help='image resolution ratio (default: 0.2 -> 256:144)'
    )
    parser.add_argument(
        '-s', '--specific',
        type=int,
        help='make gif for only specified robot (how to: "-s {id}")'
    )
    parser.add_argument(
        '--num-cores',
        default=1, type=int,
        help='num of multiprocesses'
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


def save_robot_gif(exp_path, env_id, structure, key, resolution, not_overwrite, neat_config):

    genome_file = os.path.join(exp_path, 'genome', f'{key}.pickle')

    gif_path = os.path.join(exp_path, 'gif')
    os.makedirs(gif_path, exist_ok=True)

    gif_file = os.path.join(gif_path, f'{key}.gif')

    if os.path.exists(gif_file) and not_overwrite:
        return

    with open(genome_file, 'rb') as f:
        genome = pickle.load(f)


    env = make_vec_envs(env_id, structure, 1000, 1, allow_early_resets=False)
    env.get_attr("default_viewer", indices=None)[0].set_resolution(resolution)

    controller = FeedForwardNetwork.create(genome, neat_config)

    done = False
    obs = env.reset()
    img = env.render(mode='img')
    imgs = [img]
    while not done:
        action = controller.activate(obs[0])
        obs, _, done, infos = env.step([np.array(action)])
        img = env.render(mode='img')
        imgs.append(img)

    env.close()

    imageio.mimsave(gif_file, imgs, duration=(1/50.0))

    gifsicle(sources=gif_file,
             destination=gif_file,
             optimize=False,
             colors=64,
             options=["--optimize=3","--no-warnings"])

    print(f'genome {key} ... done')
    return


if __name__=='__main__':
    args = get_args()

    resolution = (1280*args.resolution_ratio, 720*args.resolution_ratio)


    exp_path = os.path.join(CURR_DIR, 'evogym_out', args.name)

    with open(os.path.join(exp_path, 'arguments.json'), 'r') as f:
        exp_args = json.load(f)

    neat_config_file = os.path.join(exp_path, 'neat_config.pickle')
    with open(neat_config_file, 'rb') as f:
        neat_config = pickle.load(f)

    structure_file = os.path.join(exp_path, 'structure.npz')
    structure_data = np.load(structure_file)
    structure = (structure_data['robot'], structure_data['connectivity'])


    robot_ids = []

    if args.specific is not None:
        robot_ids = [specific]

    else:
        files = [
            'history_reward.csv',
            'history_novelty.csv'
        ]
        for file in files:

            history_file = os.path.join(exp_path, file)
            with open(history_file, 'r') as f:
                reader = csv.reader(f)
                histories = list(reader)[1:]
                robot_ids.extend([hist[1] for hist in histories])

    robot_ids = list(set(robot_ids))

    if not args.no_multi:

        pool = mp.Pool(args.num_cores)
        jobs = []

        for key in robot_ids:

            func_args = (exp_path, exp_args['task'], structure, key, resolution, args.not_overwrite, neat_config)

            jobs.append(pool.apply_async(save_robot_gif, func_args))

        for job in jobs:
            job.get(timeout=None)


    else:

        for key in robot_ids:

            func_args = (exp_path, exp_args['task'], structure, key, resolution, args.not_overwrite, neat_config)

            save_robot_gif(*func_args)
