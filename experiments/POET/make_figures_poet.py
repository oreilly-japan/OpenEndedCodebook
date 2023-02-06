import os
import sys
import csv

import multiprocessing as mp


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
from experiment_utils import load_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'evogym')
sys.path.append(ENV_DIR)
from gym_utils import load_robot
from figure_drawer import EvogymDrawerPOET, pool_init_func
import custom_envs.parkour

from arguments.evogym_poet import get_figure_args



def main():

    args = get_figure_args()

    expt_path = os.path.join(CURR_DIR, 'out', 'evogym_poet', args.name)
    expt_args = load_experiment(expt_path)


    robot = load_robot(ROOT_DIR, expt_args['robot'])


    if args.specified is not None:
        niche_keys = [args.specified]
    else:
        history_file = os.path.join(expt_path, 'niches.csv')
        with open(history_file, 'r') as f:
            reader = csv.reader(f)
            histories = list(reader)[1:]
            niche_keys = [hist[1] for hist in histories]

    figure_path = os.path.join(expt_path, 'figure')
    draw_kwargs = {}
    if args.save_type=='gif':
        draw_kwargs = {
            'track': args.track_robot,
            'resolution_scale': args.resolution_scale,
            'deterministic': True
        }
    elif args.save_type=='jpg':
        draw_kwargs = {
            'interval': args.interval,
            'resolution_scale': args.resolution_scale,
            'start_timestep': args.start_timestep,
            'timestep_interval': args.timestep_interval,
            'distance_interval': args.distance_interval,
            'blur': args.blur,
            'blur_temperature': args.blur_temperature,
            'display_timestep': args.display_timestep,
            'draw_trajectory': args.draw_trajectory,
            'deterministic': True
        }
    drawer = EvogymDrawerPOET(
        env_id=expt_args['task'],
        save_path=figure_path,
        robot=robot,
        recurrent=False,
        overwrite=not args.not_overwrite,
        save_type=args.save_type, **draw_kwargs)

    draw_function = drawer.draw
    

    if not args.no_multi and args.specified is None:

        lock = mp.Lock()
        pool = mp.Pool(args.num_cores, initializer=pool_init_func, initargs=(lock,))
        jobs = []

        for key in niche_keys:
            niche_path = os.path.join(expt_path, 'niche', f'{key}')
            terrain_file = os.path.join(niche_path, 'terrain.json')
            core_file = os.path.join(niche_path, 'core', 'best.pt')
            jobs.append(pool.apply_async(draw_function, args=(key, terrain_file, core_file)))

        for job in jobs:
            job.get(timeout=None)


    else:

        lock = mp.Lock()
        lock = pool_init_func(lock)

        for key in niche_keys:
            niche_path = os.path.join(expt_path, 'niche', f'{key}')
            terrain_file = os.path.join(niche_path, 'terrain.json')
            core_file = os.path.join(niche_path, 'core', 'best.pt')
            draw_function(key, terrain_file, core_file)

if __name__=='__main__':
    main()
