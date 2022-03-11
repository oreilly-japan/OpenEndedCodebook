import argparse
import numpy as np

from multiprocessing import Process

from ppo import run_ppo

import evogym.envs
from evogym import sample_robot, get_full_connectivity

from attachments import Tasks, Structures


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t', '--task', default='Walker-v0', help='evogym environment id')
    parser.add_argument(
        '--random', action='store_true', default=False, help='sample robot randomly')
    parser.add_argument(
        '--height', type=int, default=5, help="robot's height")
    parser.add_argument(
        '--width', type=int, default=5, help="robor's width")
    parser.add_argument(
        '--deterministic', action='store_true', default=False, help='robot simulation deterministic')

    args = parser.parse_args()
    return args




if __name__=='__main__':

    args = get_args()

    robot_shape = (args.height, args.width)

    assert args.task in Tasks, \
        f'argumented task "{args.task}" is not prepared, so pick from ['+', '.join(Tasks)+'].'

    if args.random:
        robot = sample_robot(robot_shape)
    else:
        if args.task in Structures:
            structure = Structures[args.task]
            connections = get_full_connectivity(structure)
            robot = (structure, connections)
        else:
            print(f'robot on the task "{args.task}" is not defined, so sample robot randomly.')
            robot = sample_robot(robot_shape)

    print('robot structure: \n',robot[0].astype(int))

    run_ppo(args.task,robot,args.deterministic)
