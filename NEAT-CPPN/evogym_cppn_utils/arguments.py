import argparse

Tasks = [
    'Walker-v0',
    'BridgeWalker-v0',
    'CaveCrawler-v0',
    'Jumper-v0',
    'Flipper-v0',
    'Balancer-v0',
    'Balancer-v1',
    'UpStepper-v0',
    'DownStepper-v0',
    'ObstacleTraverser-v0',
    'ObstacleTraverser-v1',
    'Hurdler-v0',
    'GapJumper-v0',
    'PlatformJumper-v0',
    'Traverser-v0',
    'Lifter-v0',
    'Carrier-v0',
    'Carrier-v1',
    'Pusher-v0',
    'Pusher-v1',
    'BeamToppler-v0',
    'BeamSlider-v0',
    'Thrower-v0',
    'Catcher-v0',
    'AreaMaximizer-v0',
    'AreaMinimizer-v0',
    'WingspanMazimizer-v0',
    'HeightMaximizer-v0',
    'Climber-v0',
    'Climber-v1',
    'Climber-v2',
    'BidirectionalWalker-v0',
]

def get_args():
    parser = argparse.ArgumentParser(
        description='evogym structure evolution experiment')

    parser.add_argument(
        '-n', '--name',
        default='', type=str,
        help='experiment name (default: task id)')
    parser.add_argument(
        '-t', '--task',
        default='Walker-v0', type=str,
        help='target task id')
    parser.add_argument(
        '-p', '--pop-size',
        default=4, type=int,
        help='population size of neat')
    parser.add_argument(
        '-g', '--generation',
        default=300, type=int,
        help='neat iterations')
    parser.add_argument(
        '--num-cores',
        default=1, type=int,
        help='num of multiprocesses')
    parser.add_argument(
        '--ppo-iters',
        default=5, type=int,
        help='ppo iterations')
    parser.add_argument(
        '--shape',
        default=[5,5], nargs='+', type=int,
        help='robot shape (useage: "--shape {height} {width}", default: (5,5))')
    parser.add_argument(
        '--deterministic',
        action='store_true', default=False,
        help='evaluate robot deterministic')
    parser.add_argument(
        '--no-view',
        action='store_true', default=False,
        help='not view simulation of best robot')
    args = parser.parse_args()

    if args.name=='':
        args.name = args.task

    assert args.task in Tasks,\
        f'argumented task id "{args.task}" is not prepared, so pick from ['+', '.join(Tasks)+'].'

    assert len(args.shape)==2, 'argument error: use "--shape" option as "--shape {height} {width}"'

    return args
