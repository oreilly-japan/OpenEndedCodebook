import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='maze MCC experiment'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        help='experiment name (default: "{bootstrap}")'
    )
    parser.add_argument(
        '-b', '--bootstrap',
        default='default', type=str,
        help='bootstrap name to use'
    )

    parser.add_argument(
        '-g', '--generation',
        default=1000, type=int,
        help='generation num'
    )

    parser.add_argument(
        '--agent-criteria',
        default=1, type=int,
        help='minimum criteria of agent'
    )
    parser.add_argument(
        '--maze-criteria',
        default=1, type=int,
        help='minimum criteria of maze'
    )

    parser.add_argument(
        '--agent-pop',
        default=160, type=int,
        help='max agent population size'
    )
    parser.add_argument(
        '--maze-pop',
        default=40, type=int,
        help='max maze population size'
    )

    parser.add_argument(
        '--agent-limit',
        default=0, type=int,
        help='resource limit of agent'
    )
    parser.add_argument(
        '--maze-limit',
        default=4, type=int,
        help='recourse limit of maze'
    )

    parser.add_argument(
        '--agent-batch',
        default=40, type=int,
        help='batch size of agent'
    )
    parser.add_argument(
        '--maze-batch',
        default=10, type=int,
        help='batch size of maze'
    )

    parser.add_argument(
        '--num-cores',
        default=4, type=int,
        help='num of multiprocesses'
    )
    parser.add_argument(
        '--print-maze',
        action='store_true', default=False,
        help='print detail of survived maze genome every generation'
    )

    args = parser.parse_args()

    if args.name==None:
        args.name = args.bootstrap

    return args


def get_bootstrap_args():
    parser = argparse.ArgumentParser(
        description='bootstrap maze MCC experiment'
    )

    parser.add_argument(
        '-n', '--name',
        default='default', type=str,
        help='bootstrap name'
    )

    parser.add_argument(
        '--agent-num',
        default=20, type=int,
        help='number to prepare agent'
    )
    parser.add_argument(
        '--maze-num',
        default=10, type=int,
        help='number to prepare maze'
    )

    parser.add_argument(
        '--wall-gene-num',
        default=2, type=int,
        help='number of wall gene'
    )
    parser.add_argument(
        '--path-gene-num',
        default=2, type=int,
        help='number of path gene'
    )

    parser.add_argument(
        '--exit-range',
        default=5.0, type=float,
        help='range of judgment that reached the goal'
    )
    parser.add_argument(
        '--radius',
        default=5.0, type=float,
        help='agent radius'
    )
    parser.add_argument(
        '--range-finder',
        default=100.0, type=float,
        help='agent range finder range'
    )
    parser.add_argument(
        '--max-speed',
        default=5.0, type=float,
        help='agent max speed'
    )
    parser.add_argument(
        '--max-angular-vel',
        default=8.0, type=float,
        help='agent max angular velocity'
    )
    parser.add_argument(
        '--speed-scale',
        default=2.0, type=float,
        help='nn output scaler for speed'
    )
    parser.add_argument(
        '--angular-scale',
        default=3.0, type=float,
        help='nn output scaler for angular velocity'
    )

    parser.add_argument(
        '--num-cores',
        default=4, type=int,
        help='num of multiprocesses'
    )

    args = parser.parse_args()

    return args


def get_figure_args():
    parser = argparse.ArgumentParser(
        description='make plot of maze and solver agent'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        help='experiment name'
    )

    parser.add_argument(
        '-cb', '--colorbar',
        action='store_true', default=False,
        help='plot colorbar of timestep'
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
