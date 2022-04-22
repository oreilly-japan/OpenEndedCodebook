import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='boostrap maze MCC experiment'
    )

    parser.add_argument(
        '-n', '--name',
        default='default', type=str,
        help='experiment name'
    )
    parser.add_argument(
        '-agent', '--agent_num',
        default=40, type=int,
        help='number to prepare agent'
    )
    parser.add_argument(
        '-maze', '--maze_num',
        default=10, type=int,
        help='number to prepare maze'
    )
    parser.add_argument(
        '-wall', '--wall_gene_num',
        default=2, type=int,
        help='number of wall gene'
    )
    parser.add_argument(
        '-path', '--path_gene_num',
        default=2, type=int,
        help='number of path gene'
    )
    parser.add_argument(
        '-num-cores',
        default=8, type=int,
        help='num of multiprocesses'
    )

    args = parser.parse_args()

    return args
