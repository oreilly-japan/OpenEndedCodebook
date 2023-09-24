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
from figure_drawer import EvogymControllerDrawerPPO, pool_init_func


from arguments.evogym_ppo import get_figure_args


def main():

    args = get_figure_args()

    expt_path = os.path.join(CURR_DIR, 'out', 'evogym_ppo', args.name)
    expt_args = load_experiment(expt_path)


    robot = load_robot(ROOT_DIR, expt_args['robot'], task=expt_args['task'])


    controller_path = os.path.join(expt_path, 'controller')
    if args.specified is not None:
        controller_files = [os.path.join(controller_path, f'{args.specified}.pt')]
    else:
        controller_files = glob(os.path.join(controller_path, '*.pt'))


    figure_path = os.path.join(expt_path, 'figure')
    draw_kwargs = {}
    if args.save_type=='gif':
        draw_kwargs = {
            'track': args.track_robot,
            'resolution_scale': args.resolution_scale,
            'deterministic': not args.probabilistic
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
            'deterministic': not args.probabilistic
        }
    drawer = EvogymControllerDrawerPPO(
        save_path=figure_path,
        env_id=expt_args['task'],
        robot=robot,
        overwrite=not args.not_overwrite,
        save_type=args.save_type, **draw_kwargs)

    draw_function = drawer.draw


    if not args.no_multi and args.specified is None:

        lock = mp.Lock()
        pool = mp.Pool(args.num_cores, initializer=pool_init_func, initargs=(lock,))
        jobs = []

        for controller_file in controller_files:
            iter = int(os.path.splitext(os.path.basename(controller_file))[0])
            jobs.append(pool.apply_async(draw_function, args=(iter, controller_file)))

        for job in jobs:
            job.get(timeout=None)


    else:

        lock = mp.Lock()
        lock = pool_init_func(lock)

        for controller_file in controller_files:
            iter = int(os.path.splitext(os.path.basename(controller_file))[0])
            draw_function(iter, controller_file)

if __name__=='__main__':
    main()
