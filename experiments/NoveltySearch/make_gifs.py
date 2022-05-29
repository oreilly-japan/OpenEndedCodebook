import os
import sys
import csv

import multiprocessing as mp


import evogym.envs

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import ns_neat
from experiment_utils import load_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'evogym')
sys.path.append(ENV_DIR)
from gym_utils import load_robot
from make_gif_funcs import save_controller_gif, pool_init_func


from arguments.evogym_ns_neat import get_gif_args


def main():

    args = get_gif_args()

    resolution = (1280*args.resolution, 720*args.resolution)

    expt_path = os.path.join(CURR_DIR, 'out', 'evogym_ns_neat', args.name)
    expt_args = load_experiment(expt_path)


    robot_file = os.path.join(ENV_DIR, 'robot_files', f'{expt_args["robot"]}.txt')
    structure = load_robot(robot_file)


    decode_function = ns_neat.FeedForwardNetwork.create


    config_file = os.path.join(expt_path, 'evogym_ns_neat.cfg')
    config = ns_neat.make_config(config_file)


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

                gif_file = os.path.join(save_path, f'{key}.gif')
                genome_file = os.path.join(expt_path, 'genome', f'{key}.pickle')

                if os.path.exists(gif_file) and args.not_overwrite:
                    continue

                func_args = (expt_args['task'], structure, key, genome_file, config.genome_config, decode_function, gif_file, resolution)
                jobs.append(pool.apply_async(save_controller_gif, args=func_args))

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
                genome_file = os.path.join(expt_path, 'genome', f'{key}.pickle')

                if os.path.exists(gif_file) and args.not_overwrite:
                    continue

                func_args = (expt_args['task'], structure, key, genome_file, config.genome_config, decode_function, gif_file, resolution)

                save_controller_gif(*func_args)

if __name__=='__main__':
    main()
