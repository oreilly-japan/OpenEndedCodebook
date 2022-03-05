import argparse
import numpy as np

from multiprocessing import Process

from ppo import run_ppo

import evogym.envs
from evogym import sample_robot, get_full_connectivity

from attachments import Environments, Structures


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--env', default='Walker-v0', help='evogym environment id')
    parser.add_argument(
        '--random', action='store_true', default=False, help='sample robot randomly')
    parser.add_argument(
        '--height', type=int, default=5, help="robot's height")
    parser.add_argument(
        '--width', type=int, default=5, help="robor's width")
    parser.add_argument(
        '--probabilistic', action='store_true', default=False, help='probabilistic action in evaluation')

    args = parser.parse_args()
    return args




if __name__=='__main__':

    args = get_args()

    robot_shape = (args.height, args.width)

    assert args.env in Environments, \
        f'argumented environment "{args.env}" is not prepared, so pick from ['+', '.join(Environments)+'].'

    if args.random:
        robot = sample_robot(robot_shape)
    else:
        if args.env in Structures:
            structure = Structures[args.env]
            connections = get_full_connectivity(structure)
            robot = (structure, connections)
        else:
            print(f'robot on the environment "{args.env}" is not defined, so sample robot randomly.')
            robot = sample_robot(robot_shape)

    print('robot structure: \n',robot[0].astype(int))

    run_ppo(args.env,robot,args.probabilistic)
