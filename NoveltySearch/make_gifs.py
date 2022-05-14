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


import evogym.envs

import ns_neat

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_utils')
sys.path.append(UTIL_DIR)
from gym_utils import make_vec_envs


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
        '-s', '--specified',
        type=int,
        help='make gif for only specified robot (usage: "-s {id}")'
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


def save_robot_gif(expt_path, save_path, env_id, structure, key, resolution, config, overwrite=True):

    genome_file = os.path.join(expt_path, 'genome', f'{key}.pickle')

    gif_file = os.path.join(save_path, f'{key}.gif')

    if os.path.exists(gif_file) and not overwrite:
        return

    with open(genome_file, 'rb') as f:
        genome = pickle.load(f)


    env = make_vec_envs(env_id, structure, 1000, 1, allow_early_resets=False)
    env.get_attr("default_viewer", indices=None)[0].set_resolution(resolution)

    controller = ns_neat.FeedForwardNetwork.create(genome, config.genome_config)

    done = False
    obs = env.reset()
    img = env.render(mode='img')
    imgs = [img]
    while not done:
        action = np.array(controller.activate(obs[0]))*2 - 1
        obs, _, done, infos = env.step([action])
        img = env.render(mode='img')
        imgs.append(img)

    env.close()

    imageio.mimsave(gif_file, imgs, duration=(1/50.0))

    with lock:
        gifsicle(sources=gif_file,
                 destination=gif_file,
                 optimize=False,
                 colors=64,
                 options=["--optimize=3","--no-warnings"])

    print(f'genome {key} ... done')
    return


def pool_init_func(lock_):
    global lock
    lock = lock_

def main():

    args = get_args()

    resolution = (1280*args.resolution_ratio, 720*args.resolution_ratio)

    expt_path = os.path.join(CURR_DIR, 'evogym_out', args.name)

    with open(os.path.join(expt_path, 'arguments.json'), 'r') as f:
        expt_args = json.load(f)

    ns_config_file = os.path.join(expt_path, 'ns_config.ini')
    config = ns_neat.make_config(ns_config_file)


    structure_file = os.path.join(expt_path, 'structure.npz')
    structure_data = np.load(structure_file)
    structure = (structure_data['robot'], structure_data['connectivity'])


    gif_path = os.path.join(expt_path, 'gif')
    os.makedirs(gif_path, exist_ok=True)


    robot_ids = {}

    if args.specified is not None:
        robot_ids = {
            'specified': [args.specified]
        }

    else:
        files = {
            'reward': 'history_reward.csv',
            'novelty': 'history_novelty.csv'
        }
        for metric,file in files.items():

            history_file = os.path.join(expt_path, file)
            with open(history_file, 'r') as f:
                reader = csv.reader(f)
                histories = list(reader)[1:]
                ids = sorted(list(set([hist[1] for hist in histories])))
                robot_ids[metric] = ids


    if not args.no_multi and args.specified is None:

        lock = mp.Lock()
        pool = mp.Pool(args.num_cores, initializer=pool_init_func, initargs=(lock,))
        jobs = []

        for metric,ids in robot_ids.items():
            save_path = os.path.join(gif_path, metric)
            os.makedirs(save_path, exist_ok=True)
            for key in ids:
                func_args = (expt_path, save_path, expt_args['task'], structure, key, resolution, config)
                func_kwargs = {
                    'overwrite': not args.not_overwrite
                }
                jobs.append(pool.apply_async(save_robot_gif, args=func_args, kwds=func_kwargs))

        for job in jobs:
            job.get(timeout=None)


    else:

        for metric,ids in robot_ids.items():
            save_path = os.path.join(gif_path, metric)
            os.makedirs(save_path, exist_ok=True)
            for key in ids:
                func_args = (expt_path, save_path, expt_args['task'], structure, key, resolution, config)
                func_kwargs = {
                    'overwrite': not args.not_overwrite
                }

                save_robot_gif(*func_args, **func_kwargs)

if __name__=='__main__':
    main()
