import os
import csv
import argparse
import json
import numpy as np

import multiprocessing as mp

from PIL import Image
import imageio
from pygifsicle import gifsicle

from stable_baselines3 import PPO
from ppo.utils import make_vec_envs

import evogym.envs


def get_args():
    parser = argparse.ArgumentParser(description='make robot gifs')
    parser.add_argument(
        '-n', '--name', default='', type=str, help='experiment name')
    parser.add_argument(
        '-r', '--resolution-ratio', default=0.2, type=float, help='image resolution ratio (default: 0.2 -> 256:144)')
    parser.add_argument(
        '--num-cores', default=1, type=int, help='num of multiprocesses')
    parser.add_argument(
        '--deterministic', action='store_true', default=False, help='robot act deterministic')
    parser.add_argument(
        '--not-overwrite', action='store_true', default=False, help='skip process if already gif exists (default: overwrite)'
    )

    args = parser.parse_args()

    assert args.name!='', 'argumented error: input "--name {experiment name}"'

    return args


def save_robot_gif(exp_path, env_id, generation, number, resolution, deterministic, not_overwrite):

    generation_path = os.path.join(exp_path, f'generation_{generation}')
    structure_file = os.path.join(generation_path, 'structure', f'{number}.npz')
    controller_file = os.path.join(generation_path, 'controller', f'{number}.zip')

    gif_path = os.path.join(generation_path, 'gif')
    os.makedirs(gif_path, exist_ok=True)

    gif_file = os.path.join(gif_path, f'{number}.gif')

    if os.path.exists(gif_file) and not_overwrite:
        return

    structure_data = np.load(structure_file)
    structure = (structure_data['robot'], structure_data['connectivity'])

    env = make_vec_envs(env_id, structure, 1000, 1, allow_early_resets=False)
    env.get_attr("default_viewer", indices=None)[0].set_resolution(resolution)

    model = PPO.load(controller_file)

    done = False
    obs = env.reset()
    img = env.render(mode='img')
    imgs = [img]
    while not done:
        action, _ = model.predict(obs, deterministic=deterministic)
        obs, _, done, infos = env.step(action)
        img = env.render(mode='img')
        imgs.append(img)

    env.close()

    imageio.mimsave(gif_file, imgs, duration=(1/50.0))

    gifsicle(sources=gif_file,
             destination=gif_file,
             optimize=False,
             colors=64,
             options=["--optimize=3","--no-warnings"])

    print(f'robot (generation: {generation}, number: {number}) ... done')
    return


if __name__=='__main__':
    args = get_args()

    resolution = (1280*args.resolution_ratio, 720*args.resolution_ratio)


    root_dir = os.path.dirname(os.path.abspath(__file__))
    exp_path = os.path.join(root_dir, 'out', args.name)

    with open(os.path.join(exp_path, 'arguments.json'), 'r') as f:
        exp_args = json.load(f)

    history_file = os.path.join(exp_path, 'history_pop.csv')
    with open(history_file, 'r') as f:
        reader = csv.reader(f)
        robot_history = list(reader)[1:]


    pool = mp.Pool(args.num_cores)
    jobs = []

    for robot in robot_history:
        generation = robot[0]
        number = robot[1]

        func_args = (exp_path, exp_args['task'], generation, number, resolution, args.deterministic, args.not_overwrite)

        jobs.append(pool.apply_async(save_robot_gif, func_args))

    for job in jobs:
        job.get(timeout=None)
