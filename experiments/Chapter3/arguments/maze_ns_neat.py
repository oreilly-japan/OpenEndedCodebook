import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='Maze NovelrySearch experiment with NEAT'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        help='experiment name (default: "{task}")'
    )
    parser.add_argument(
        '-t', '--task',
        default='hard', type=str,
        help='maze name (default: hard, built on "envs/maze/maze_files/")'
    )

    parser.add_argument(
        '-p', '--pop-size',
        default=500, type=int,
        help='population size of NEAT (default: 500)'
    )
    parser.add_argument(
        '-g', '--generation',
        default=500, type=int,
        help='iterations of NEAT (default: 500)'
    )
    parser.add_argument(
        '--ns-threshold',
        default=6.0, type=float,
        help='initial threshold to add to novelty archive (default: 6.0)'
    )
    parser.add_argument(
        '--num-knn',
        default=15, type=int,
        help='number of nearest neighbors to calculate novelty (default: 15)'
    )
    parser.add_argument(
        '--mcns',
        default=0.01, type=float,
        help='minimal score criterion. if not satisfy, die. (default: 0.01)'
    )

    parser.add_argument(
        '--timesteps',
        default=400, type=int,
        help='limit of timestep for solving maze (default: 400)'
    )

    parser.add_argument(
        '-c', '--num-cores',
        default=4, type=int,
        help='number of parallel evaluation processes (default: 4)'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true', default=False,
        help='not open window of progress figure (default: False)'
    )
    args = parser.parse_args()

    if args.name is None:
        args.name = args.task

    return args
