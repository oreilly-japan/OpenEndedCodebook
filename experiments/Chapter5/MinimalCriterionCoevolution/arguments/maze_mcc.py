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
        help='name of bootstrap to use as initial state (default: default)'
    )

    parser.add_argument(
        '-g', '--generation',
        default=1000, type=int,
        help='iterations (default: 1000)'
    )

    parser.add_argument(
        '--agent-criterion',
        default=1, type=int,
        help='minimal number to solve maze for each agent to survive (default: 1)'
    )
    parser.add_argument(
        '--maze-criterion',
        default=1, type=int,
        help='minimal number of agent to solve for each maze to survive (default: 1)'
    )

    parser.add_argument(
        '--agent-pop',
        default=160, type=int,
        help='maximum size of agent population (default: 160)'
    )
    parser.add_argument(
        '--maze-pop',
        default=40, type=int,
        help='maximum size of maze population (default: 40)'
    )

    parser.add_argument(
        '--agent-limit',
        default=0, type=int,
        help='resource limit of agent (default: 0, it means no limit)'
    )
    parser.add_argument(
        '--maze-limit',
        default=4, type=int,
        help='recourse limit of maze'
    )

    parser.add_argument(
        '--agent-batch',
        default=40, type=int,
        help='agent number to evaluate in one iteration (default: 40)'
    )
    parser.add_argument(
        '--maze-batch',
        default=10, type=int,
        help='maze number to evaluate in one iteration (default: 10)'
    )

    parser.add_argument(
        '-c', '--num-cores',
        default=4, type=int,
        help='number of parallel evaluation processes (default: 4)'
    )
    parser.add_argument(
        '--print-maze',
        action='store_true', default=False,
        help='print detail of survived maze genome every generation (default: False)'
    )

    args = parser.parse_args()

    if args.name==None:
        args.name = args.bootstrap
    
    assert args.agent_limit >= 0 and args.maze_limit >= 0, 'set agent limit and maze limit 0 and over.'
    if args.agent_limit > 0:
        assert args.agent_limit > args.agent_criterion, 'set agent limit greater than agent criteria.'
    if args.maze_limit > 0:
        assert args.maze_limit > args.maze_criterion, 'set maze limit greater than maze criteria.'

    return args


def get_bootstrap_args():
    parser = argparse.ArgumentParser(
        description='bootstrap maze MCC experiment'
    )

    parser.add_argument(
        '-n', '--name',
        default='default', type=str,
        help='bootstrap name (default: default)'
    )

    parser.add_argument(
        '--agent-num',
        default=20, type=int,
        help='number of agent to prepare (default: 20)'
    )
    parser.add_argument(
        '--maze-num',
        default=10, type=int,
        help='number of maze to prepare (default: 10)'
    )

    parser.add_argument(
        '--wall-gene-num',
        default=2, type=int,
        help='initial number of wall gene (default: 2)'
    )
    parser.add_argument(
        '--path-gene-num',
        default=2, type=int,
        help='initial number of path gene (default: 2)'
    )

    parser.add_argument(
        '--exit-range',
        default=5.0, type=float,
        help='range of judgment that reached the goal (default: 5.0)'
    )
    parser.add_argument(
        '--radius',
        default=5.0, type=float,
        help='radius of agent (default: 5.0)'
    )
    parser.add_argument(
        '--range-finder',
        default=100.0, type=float,
        help='range of agent\'s range finder (default: 100.0)'
    )
    parser.add_argument(
        '--max-speed',
        default=5.0, type=float,
        help='agent max speed (default: 5.0)'
    )
    parser.add_argument(
        '--max-angular-vel',
        default=8.0, type=float,
        help='agent max angular velocity (default: 5.0)'
    )
    parser.add_argument(
        '--speed-scale',
        default=2.0, type=float,
        help='nn output scaler for speed (default: 2.0)'
    )
    parser.add_argument(
        '--angular-scale',
        default=3.0, type=float,
        help='nn output scaler for angular velocity (default: 3.0)'
    )

    parser.add_argument(
        '-c', '--num-cores',
        default=4, type=int,
        help='number of parallel evaluation processes (default: 4)'
    )

    args = parser.parse_args()

    assert args.agent_num % args.maze_num == 0, 'set agent num as an integral multiple of maze num.'

    return args


def get_figure_args():
    parser = argparse.ArgumentParser(
        description='make plot of maze and solver agent'
    )

    parser.add_argument(
        'name',
        type=str,
        help='name of experiment for making figures'
    )

    parser.add_argument(
        '-sg', '--start-generation',
        default=0, type=int,
        help='draw all of mazes produced since this generation (default: 0)'
    )
    parser.add_argument(
        '-eg', '--end-generation',
        default=2**16, type=int,
        help='draw all of mazes produced up to this generation (default: 2^16)'
    )

    parser.add_argument(
        '-cb', '--colorbar',
        action='store_true', default=False,
        help='plot colorbar of timestep (default: False)'
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
        help='do without using multiprocess. if error occur, try this option. (default: False)'
    )

    args = parser.parse_args()

    assert args.name is not None, 'argumented error: input "{experiment name}"'

    return args
