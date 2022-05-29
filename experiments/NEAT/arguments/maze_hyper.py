import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='Maze Hyper-NEAT experiment'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        help='experiment name (default: "{task}")'
    )
    parser.add_argument(
        '-t', '--task',
        default='medium', type=str,
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
        '--use-hidden',
        action='store_true', default=False,
        help='make hidden nodes on NN substrate'
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
