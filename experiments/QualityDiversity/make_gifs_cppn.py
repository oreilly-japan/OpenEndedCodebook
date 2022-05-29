import os
import sys
import csv

import multiprocessing as mp


import evogym.envs

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import neat_cppn
from experiment_utils import load_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'evogym')
sys.path.append(ENV_DIR)
from make_gif_funcs import save_structure_gif, pool_init_func


from arguments.evogym_me_cppn import get_gif_args


def main():

    args = get_gif_args()

    resolution = (1280*args.resolution_ratio, 720*args.resolution_ratio)

    expt_path = os.path.join(CURR_DIR, 'out', 'evogym_me_cppn', args.name)
    expt_args = load_experiment(expt_path)


    gif_path = os.path.join(expt_path, 'gif')
    os.makedirs(gif_path, exist_ok=True)


    robot_ids = {}

    if args.specified is not None:
        robot_ids = {
            'specified': [args.specified]
        }
    else:
        files = {
            'population': 'history_pop.csv',
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

                gif_file = os.path.join(save_path, f'{key}.gif')
                ppo_file = os.path.join(expt_path, 'controller', f'{key}.zip')
                structure_file = os.path.join(expt_path, 'structure', f'{key}.npz')

                if os.path.exists(gif_file) and args.not_overwrite:
                    continue

                func_args = (expt_args['task'], key, ppo_file, structure_file, gif_file, resolution)
                func_kwargs = {
                    'deterministic': args.deterministic,
                }
                jobs.append(pool.apply_async(save_structure_gif, args=func_args, kwds=func_kwargs))

        for job in jobs:
            job.get(timeout=None)


    else:

        lock = mp.Lock()
        lock = pool_init_func(lock)

        for metric,ids in robot_ids.items():
            save_path = os.path.join(gif_path, metric)
            os.makedirs(save_path, exist_ok=True)
            for key in ids:

                gif_file = os.path.join(save_path, f'{key}.gif')
                ppo_file = os.path.join(expt_path, 'controller', f'{key}.zip')
                structure_file = os.path.join(expt_path, 'structure', f'{key}.npz')

                if os.path.exists(gif_file) and args.not_overwrite:
                    continue

                func_args = (expt_args['task'], key, ppo_file, structure_file, gif_file, resolution)
                func_kwargs = {
                    'deterministic': args.deterministic,
                }
                save_structure_gif(*func_args, **func_kwargs)

if __name__=='__main__':
    main()
