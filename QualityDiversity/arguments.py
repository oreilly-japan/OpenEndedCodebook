import argparse

Environments = [
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
    parser = argparse.ArgumentParser(description='MapElites experiment')
    parser.add_argument(
        '-n', '--name', default='', type=str, help='experiment name (default: env id)')
    parser.add_argument(
        '-e', '--env', default='Walker-v0', type=str, help='target environment id')
    parser.add_argument(
        '-g', '--generation', default=100, type=int, help='neat iterations')
    parser.add_argument(
        '--num-cores', default=1, type=int, help='num of multiprocesses')
    parser.add_argument(
        '--ppo-iters', default=5, type=int, help='ppo iterations')
    parser.add_argument(
        '--height', default=5, type=int, help='robot height')
    parser.add_argument(
        '--width', default=5, type=int, help='robot width')
    parser.add_argument(
        '--no-plot', action='store_false', default=False, help='The interval of saving progress figure')
    parser.add_argument(
        '--no-view', action='store_false', default=False, help='view simulation of best robot')
    args = parser.parse_args()

    if args.name=='':
        args.name = args.env

    assert args.env in Environments,\
        f'argumented environment "{args.env}" is not prepared, so pick from ['+', '.join(Environments)+'].'

    return args
