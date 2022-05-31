import os
import sys
from glob import glob

import multiprocessing as mp


import evogym.envs

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
from experiment_utils import load_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'evogym')
sys.path.append(ENV_DIR)
from gym_utils import load_robot
from make_gif_funcs import save_controller_ppo_gif, pool_init_func


from arguments.evogym_ppo import get_gif_args


def main():

    args = get_gif_args()

    resolution = (1280*args.resolution, 720*args.resolution)

    expt_path = os.path.join(CURR_DIR, 'out', 'evogym_ppo', args.name)
    expt_args = load_experiment(expt_path)


    structure = load_robot(ROOT_DIR, expt_args['robot'], task=expt_args['task'])


    gif_path = os.path.join(expt_path, 'gif')
    os.makedirs(gif_path, exist_ok=True)

    controller_path = os.path.join(expt_path, 'controller')

    if args.specified is not None:
        controller_files = [os.path.join(controller_path, f'{args.specified}.zip')]
    else:
        controller_files = glob(os.path.join(controller_path, '*.zip'))


    if not args.no_multi and args.specified is None:

        lock = mp.Lock()
        pool = mp.Pool(args.num_cores, initializer=pool_init_func, initargs=(lock,))
        jobs = []

        for controller_file in controller_files:

            iter = int(os.path.splitext(os.path.basename(controller_file))[0])
            gif_file = os.path.join(gif_path, f'{iter}.gif')

            if os.path.exists(gif_file) and args.not_overwrite:
                continue

            func_args = (expt_args['task'], structure, iter, controller_file, gif_file, resolution)
            func_kwargs = {
                'deterministic': expt_args['deterministic'],
            }
            jobs.append(pool.apply_async(save_controller_ppo_gif, args=func_args, kwds=func_kwargs))

        for job in jobs:
            job.get(timeout=None)


    else:

        lock = mp.Lock()
        lock = pool_init_func(lock)

        for controller_file in controller_files:

            iter = int(os.path.splitext(os.path.basename(controller_file))[0])
            gif_file = os.path.join(gif_path, f'{iter}.gif')

            if os.path.exists(gif_file) and args.not_overwrite:
                continue

            func_args = (expt_args['task'], structure, iter, controller_file, gif_file, resolution)
            func_kwargs = {
                'deterministic': expt_args['deterministic'],
            }
            save_controller_ppo_gif(*func_args, **func_kwargs)

if __name__=='__main__':
    main()
