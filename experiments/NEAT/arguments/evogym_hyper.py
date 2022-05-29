import argparse

from evogym import BASELINE_ENV_NAMES

def get_args():
    parser = argparse.ArgumentParser(
        description='Evogym Hyper-NEAT experiment'
    )
    parser.add_argument(
        '-n', '--name',
        default='', type=str,
        help='experiment name (default: "{task}_{robot}")'
    )
    parser.add_argument(
        '-t', '--task',
        default='Walker-v0', type=str,
        help='target task id'
    )
    parser.add_argument(
        '-r', '--robot',
        default='cat', type=str,
        help='robot structure name (built in "envs/evogym/robot_files/{name}.txt")'
    )

    parser.add_argument(
        '-p', '--pop-size',
        default=200, type=int,
        help='population size of neat'
    )
    parser.add_argument(
        '-g', '--generation',
        default=500, type=int,
        help='neat iterations'
    )
    parser.add_argument(
        '--use-hidden',
        action='store_true', default=False,
        help='make hidden nodes on NN substrate'
    )

    parser.add_argument(
        '--eval-num',
        default=1, type=int,
        help='if probabilistic task, need a certain times'
    )
    parser.add_argument(
        '--num-cores',
        default=4, type=int,
        help='num of multiprocesses'
    )
    parser.add_argument(
        '--no-view',
        action='store_true', default=False,
        help='not view simulation of best robot'
    )
    args = parser.parse_args()

    if args.name=='':
        args.name = f'{args.task}_{args.robot}'

    assert args.task in BASELINE_ENV_NAMES,\
        f'argumented task id "{args.task}" is not prepared, pick from ['+', '.join(BASELINE_ENV_NAMES)+'].'

    return args


def get_gif_args():
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
