import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='Maze NEAT experiment'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        help='experiment name (default: "{task}")'
    )
    parser.add_argument(
        '-t', '--task',
        default='medium', type=str,
        help='maze name (default: medium, built on "envs/maze/maze_files/")'
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
