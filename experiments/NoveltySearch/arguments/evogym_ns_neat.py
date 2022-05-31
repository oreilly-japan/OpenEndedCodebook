import argparse

from evogym import BASELINE_ENV_NAMES

def get_args():
    parser = argparse.ArgumentParser(
        description='Evogym NovelrySearch experiment with NEAT'
    )
    parser.add_argument(
        '-n', '--name',
        default='', type=str,
        help='experiment name (default: "{task}_{robot}")'
    )
    parser.add_argument(
        '-t', '--task',
        default='Walker-v0', type=str,
        help='evogym environment id (default: Walker-v0)'
    )
    parser.add_argument(
        '-r', '--robot',
        default='cat', type=str,
        help='robot structure name (default: cat, built on "envs/evogym/robot_files/", if "default", load default robot of task)'
    )

    parser.add_argument(
        '-p', '--pop-size',
        default=200, type=int,
        help='population size of NEAT (default: 200)'
    )
    parser.add_argument(
        '-g', '--generation',
        default=500, type=int,
        help='iterations of NEAT (default: 500)'
    )
    parser.add_argument(
        '--ns-threshold',
        default=0.1, type=float,
        help='initial threshold to add to novelty archive (default: 0.1)'
    )
    parser.add_argument(
        '--num-knn',
        default=5, type=int,
        help='number of nearest neighbors to calculate novelty (default: 5)'
    )
    parser.add_argument(
        '--mcns',
        default=0.0, type=float,
        help='minimal reward criterion. if not satisfy, die. (default: 0.0)'
    )

    parser.add_argument(
        '--eval-num',
        default=1, type=int,
        help='evaluation times. if probabilistic task, need more. (default: 1)'
    )
    parser.add_argument(
        '-c', '--num-cores',
        default=4, type=int,
        help='number of parallel evaluation processes (default: 4)'
    )
    parser.add_argument(
        '--no-view',
        action='store_true', default=False,
        help='not open simulation window of best robot (default: False)'
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
