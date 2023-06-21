import argparse

from evogym import BASELINE_ENV_NAMES

def get_args():
    parser = argparse.ArgumentParser(
        description='Evogym CPPN experiment'
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
        help='robot shape (default: (5,5), useage: "--shape {height} {width}")'
    )

    parser.add_argument(
        '-p', '--pop-size',
        default=4, type=int,
        help='population size of NEAT (default: 4)'
    )
    parser.add_argument(
        '-g', '--generation',
        default=500, type=int,
        help='iterations of NEAT (default: 500)'
    )

    parser.add_argument(
        '-i', '--ppo-iters',
        default=100, type=int,
        help='learning iterations of PPO algo. on the more complex task, need more. (default: 100)'
    )
    parser.add_argument(
        '-ei', '--evaluation-interval',
        default=20, type=int,
        help='frequency to evaluate policy (default: 20)'
    )
    parser.add_argument(
        '--probabilistic',
        action='store_true', default=False,
        help='evaluate robot on probabilistic action (default: False)'
    )

    parser.add_argument(
        '-c', '--num-cores',
        default=1, type=int,
        help='number of parallel evaluation processes (default: 1)'
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


def get_figure_args():
    parser = argparse.ArgumentParser(
        description='make robot figures'
    )

    parser.add_argument(
        'name',
        type=str,
        help='name of experiment for making figures'
    )
    parser.add_argument(
        '-s', '--specified',
        type=int,
        help='input id, make figure for the only specified robot (usage: "-s {id}")'
    )

    parser.add_argument(
        '-st', '--save-type',
        type=str, default='gif',
        help='file type (default: gif, choose from [gif, jpg])'
    )

    parser.add_argument(
        '-tr', '--track-robot',
        action='store_true', default=False,
        help='track robot with camera in gif'
    )

    parser.add_argument(
        '-i', '--interval',
        type=str, default='timestep',
        help='in case of save type is jpg, type of interval for robot drawing (default: timestep, choose from [timestep, distance])'
    )
    parser.add_argument(
        '-rs', '--resolution-scale',
        type=float, default=32.0,
        help='resolution scale. <br> when output monochrome image, try this argument change. (default: 32.0)'
    )
    parser.add_argument(
        '--start-timestep',
        type=int, default=0,
        help='start timestep of render (default: 0)'
    )
    parser.add_argument(
        '-ti', '--timestep-interval',
        type=int, default=80,
        help='timestep interval for robot drawing (default: 80, if interval is hybrid, it should be about 40)'
    )
    parser.add_argument(
        '-b', '--blur',
        type=int, default=0,
        help='in case of jpg, timesteps for rendering motion blur (default: 0, 0 means no blur)'
    )
    parser.add_argument(
        '-bt', '--blur-temperature',
        type=float, default=0.6,
        help='blur temperature (default: 0.6, up to 1.0)'
    )
    parser.add_argument(
        '-di', '--distance-interval',
        type=float, default=0.8,
        help='distance interval for robot drawing'
    )
    parser.add_argument(
        '--display-timestep',
        action='store_true', default=False,
        help='display timestep above robot'
    )
    parser.add_argument(
        '--draw-trajectory',
        action='store_true', default=False,
        help='draw robot trajectory as line'
    )

    parser.add_argument(
        '--probabilistic',
        action='store_true', default=False,
        help='robot act probabilistically (default: False)'
    )

    parser.add_argument(
        '-c', '--num-cores',
        default=1, type=int,
        help='number of parallel making processes (default: 1)'
    )
    parser.add_argument(
        '--not-overwrite',
        action='store_true', default=False,
        help='skip process if already figure exists (default: False)'
    )
    parser.add_argument(
        '--no-multi',
        action='store_true', default=False,
        help='do without using multiprocessing. if error occur, try this option. (default: False)'
    )

    args = parser.parse_args()

    assert args.name is not None, 'argumented error: input "{experiment name}"'

    return args
