import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='Novelty Search experiment'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        help='experiment name (default: maze name)'
    )
    parser.add_argument(
        '-t', '--task',
        default='hard', type=str,
        help='target maze name'
    )
    parser.add_argument(
        '-p', '--pop-size',
        default=500, type=int,
        help='population size of neat'
    )
    parser.add_argument(
        '-g', '--generation',
        default=500, type=int,
        help='neat iterations'
    )
    parser.add_argument(
        '--ns-threshold',
        default=6.0, type=float,
        help='initial threshold for novelty archive'
    )
    parser.add_argument(
        '--num-knn',
        default=15, type=int,
        help='num of nearest neighbors'
    )
    parser.add_argument(
        '--mcns',
        default=0.01, type=float,
        help='minimal goal fitness criterion'
    )
    parser.add_argument(
        '--timesteps',
        default=400, type=int,
        help='maze solving simulator steps'
    )
    parser.add_argument(
        '--num-cores',
        default=4, type=int,
        help='num of multiprocesses'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true', default=False,
        help='not plot progress figure'
    )
    args = parser.parse_args()

    if args.name is None:
        args.name = args.task

    return args
