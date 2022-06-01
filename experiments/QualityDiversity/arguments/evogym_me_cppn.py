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
        help='evogym environment id (default: Walker-v0)'
    )
    parser.add_argument(
        '-s', '--shape',
        default=[5,5], nargs='+', type=int,
        help='robot shape (default: (5,5), useage: "--s {height} {width}")'
    )

    parser.add_argument(
        '-b', '--batch-size',
        default=4, type=int,
        help='genome number to evaluate in one generation (default: 4)'
    )
    parser.add_argument(
        '-g', '--generation',
        default=500, type=int,
        help='iterations of NEAT (default: 500)'
    )

    parser.add_argument(
        '-i', '--ppo-iters',
        default=5, type=int,
        help='learning iterations of PPO algo. on the more complex task, need more. (default: 5)'
    )
    parser.add_argument(
        '-d', '--deterministic',
        action='store_true', default=False,
        help='evaluate robot on deterministic action (default: False)'
    )

    parser.add_argument(
        '-c', '--num-cores',
        default=1, type=int,
        help='number of parallel evaluation processes (default: 1)'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true', default=False,
        help='not open window of progress figure (default: False)'
    )
    parser.add_argument(
        '--no-view',
        action='store_true', default=False,
        help='not open simulation window of best robot (default: False)'
    )
    args = parser.parse_args()

    if args.name=='':
        args.name = args.task

    assert args.task in BASELINE_ENV_NAMES,\
        f'argumented task id "{args.task}" is not prepared, so pick from ['+', '.join(BASELINE_ENV_NAMES)+'].'

    assert len(args.shape)==2, 'argument error: use "-s --shape" option as "-s {height} {width}"'

    return args


def get_gif_args():
    parser = argparse.ArgumentParser(
        description='make robot gifs'
    )

    parser.add_argument(
        'name',
        type=str,
        help='name of experiment for making gifs'
    )
    parser.add_argument(
        '-r', '--resolution',
        default=0.2, type=float,
        help='image resolution ratio (default: 0.2 -> 256:144)'
    )
    parser.add_argument(
        '-s', '--specified',
        type=int,
        help='input id, make gif for the only specified robot (usage: "-s {id}")'
    )
    parser.add_argument(
        '-d', '--deterministic',
        action='store_true', default=False,
        help='robot act deterministic (default: False)'
    )

    parser.add_argument(
        '-c', '--num-cores',
        default=1, type=int,
        help='number of parallel making processes (default: 1)'
    )
    parser.add_argument(
        '--not-overwrite',
        action='store_true', default=False,
        help='skip process if already gif exists (default: False)'
    )
    parser.add_argument(
        '--no-multi',
        action='store_true', default=False,
        help='do without using multiprocessing. if error occur, try this option. (default: False)'
    )

    args = parser.parse_args()

    assert args.name is not None, 'argumented error: input "{experiment name}"'

    return args
