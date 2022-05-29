import argparse

from evogym import BASELINE_ENV_NAMES

def get_args():
    parser = argparse.ArgumentParser(
        description='Evogym MapElites experiment with CPPN'
    )

    parser.add_argument(
        '-n', '--name',
        default='', type=str,
        help='experiment name (default: "{task}")'
    )
    parser.add_argument(
        '-t', '--task',
        default='Walker-v0', type=str,
        help='target task id'
    )
    parser.add_argument(
        '--shape',
        default=[5,5], nargs='+', type=int,
        help='robot shape (useage: "--shape {height} {width}", default: (5,5))'
    )

    parser.add_argument(
        '-b', '--batch-size',
        default=4, type=int,
        help='genome num to evaluate in one generation'
    )
    parser.add_argument(
        '-g', '--generation',
        default=500, type=int,
        help='neat iterations'
    )

    parser.add_argument(
        '--ppo-iters',
        default=5, type=int,
        help='ppo learning iterations'
    )
    parser.add_argument(
        '--deterministic',
        action='store_true', default=False,
        help='evaluate robot on deterministic simulation'
    )

    parser.add_argument(
        '--num-cores',
        default=1, type=int,
        help='num of multiprocesses'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true', default=False,
        help='not plot progress figure'
    )
    parser.add_argument(
        '--no-view',
        action='store_true', default=False,
        help='not view simulation of best robot'
    )
    args = parser.parse_args()

    if args.name=='':
        args.name = args.task

    assert args.task in BASELINE_ENV_NAMES,\
        f'argumented task id "{args.task}" is not prepared, so pick from ['+', '.join(BASELINE_ENV_NAMES)+'].'

    assert len(args.shape)==2, 'argument error: use "--shape" option as "--shape {height} {width}"'

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
        '--deterministic',
        action='store_true', default=False,
        help='robot act deterministic'
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
