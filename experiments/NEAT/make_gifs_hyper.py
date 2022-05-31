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
from cppn_decoder import EvogymHyperDecoder
from substrate import Substrate
from gym_utils import load_robot
from make_gif_funcs import save_controller_gif, pool_init_func


from arguments.evogym_hyper import get_gif_args


def main():

    args = get_gif_args()

    resolution = (1280*args.resolution, 720*args.resolution)

    expt_path = os.path.join(CURR_DIR, 'out', 'evogym_hyper', args.name)
    expt_args = load_experiment(expt_path)


    structure = load_robot(ROOT_DIR, expt_args['robot'], task=expt_args['task'])


    substrate = Substrate(expt_args['task'], structure[0])
    decoder = EvogymHyperDecoder(substrate, use_hidden=expt_args['use_hidden'])
    decode_function = decoder.decode


    config_file = os.path.join(expt_path, 'evogym_hyper.cfg')
    config = neat_cppn.make_config(config_file)


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
