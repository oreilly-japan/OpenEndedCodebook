import sys
import os
import shutil
import json
import pickle
import random
import numpy as np
import warnings
warnings.simplefilter('ignore')


import evogym.envs
from evogym import is_connected, has_actuator, get_full_connectivity


from neat.nn import FeedForwardNetwork

import ns_neat
import distances
from parallel import ParallelEvaluator

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(CURR_DIR, 'evogym_utils')
sys.path.append(UTIL_DIR)
from arguments import get_args
from gym_utils import make_vec_envs
from simulator import SimulateProcess
# from drawer import ProgressDrawer



def eval_genome(genome, env_id, structure, config, num_eval=1, **kwargs):
    controller = FeedForwardNetwork.create(genome, config)

    env = make_vec_envs(env_id, structure, random.randint(0,10000), 1)

    obs = env.reset()

    t = env.env_method('get_time')[0]
    point = np.mean(
        env.env_method('object_pos_at_time', time=t, object_name='robot')[0],
        axis=1)
    diff = np.zeros(point.shape)

    episode_rewards = []
    episode_data = []
    while len(episode_rewards) < num_eval:
        action = controller.activate(obs[0])
        obs, _, done, infos = env.step([np.array(action)])

        t = env.env_method('get_time')[0]
        point_ = np.mean(
            env.env_method('object_pos_at_time', time=t, object_name='robot')[0],
            axis=1)

        if 'episode' in infos[0]:
            episode_rewards.append(infos[0]['episode']['r'])
            episode_data.append(diff)
            diff = np.zeros(point.shape)
        else:
            diff += np.abs(point_-point)

        point = point_

    reward = np.mean(episode_rewards)
    data = list(np.mean(np.vstack(episode_data),axis=0))

    return reward, data


def main():

    args = get_args()

    # root_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(CURR_DIR, 'evogym_out', args.name)

    try:
        os.makedirs(save_path)
    except:
        print(f'THIS EXPERIMENT ({args.name}) ALREADY EXISTS')
        print('Override? (y/n): ', end='')
        ans = input()
        if ans.lower() == 'y':
            shutil.rmtree(save_path)
            os.makedirs(save_path)
        else:
            return None, None
        print()

    argument_file = os.path.join(save_path, 'arguments.json')
    with open(argument_file, 'w') as f:
        json.dump(args.__dict__, f, indent=4)


    # figure_save_path = os.path.join(save_path, 'bd_map')
    # os.makedirs(figure_save_path)
    # Drawer = visualize.ProgressDrawer(no_plot=args.no_plot)
    # Drawer.initialize_figure(save_dir=figure_save_path)
    Drawer = None

    robot = np.array([
        [3,3,3,3,3],
        [3,3,3,3,3],
        [3,3,0,3,3],
        [3,3,0,3,3],
        [3,3,0,3,3]
    ])
    connectivity = get_full_connectivity(robot)
    structure = (robot, connectivity)
    robot_file = os.path.join(save_path, 'structure')
    np.savez(robot_file, robot=robot, connectivity=connectivity)


    seed = 0
    env = make_vec_envs(args.task, structure, seed, 1)

    num_inputs = env.observation_space.shape[0]
    num_outputs = env.action_space.shape[0]

    evaluator_kwargs = {
        'env_id': args.task,
        'structure': structure,
        'eval_num': args.eval_num
    }
    evaluator = ParallelEvaluator(evaluator_kwargs, args.num_cores, eval_genome)

    config_path = os.path.join(UTIL_DIR, 'neat_config.ini')
    novelty_config = {
        'metric': distances.manhattan,
        'threshold_init': 0.1,
        'threshold_floor': 0.1,
        'neighbors': 15,
        'MCNS': 0.0
    }
    overwrite_config = [
        ('NEAT', 'pop_size', args.pop_size),
        ('DefaultGenome', 'num_inputs', num_inputs),
        ('DefaultGenome', 'num_outputs', num_outputs)
    ]
    config = ns_neat.make_config(config_path, novelty_config, overwrite_config)
    with open(os.path.join(save_path, 'neat_config.pickle'), 'wb') as f:
        pickle.dump(config, f)

    pop = ns_neat.Population(config)
    reporters = [
        ns_neat.SaveResultReporter(save_path),
        ns_neat.NoveltySearchReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)

    if not args.no_view:
        simulator = SimulateProcess(
            args.task,
            structure,
            save_path,
            pop.config,
            args.generation)
        simulator.init_process()
        simulator.start()

    pop.run(evaluator.evaluate, n=args.generation)

if __name__=='__main__':
    main()
