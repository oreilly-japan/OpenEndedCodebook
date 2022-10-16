
import sys
import os

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
import neat_cppn
from experiment_utils import initialize_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'evogym')
sys.path.append(ENV_DIR)
from gym_utils import load_robot
import custom_envs.parkour

from poet.poet_algo import POET
from poet.learner_ppo import OptimizerPPOConfig
from poet.environment_evogym import EnvrionmentEvogymConfig


from arguments.evogym_poet import get_args


def main():

    args = get_args()
    save_path = os.path.join(CURR_DIR, 'out', 'evogym_poet', args.name)

    initialize_experiment(args.name, save_path, args)

    robot = load_robot(ROOT_DIR, args.robot)

    config_file = os.path.join(CURR_DIR, 'config', 'terrain_cppn.cfg')
    cppn_config = neat_cppn.make_config(config_file)
    cppn_config_file = os.path.join(save_path, 'evogym_terrain.cfg')
    cppn_config.save(cppn_config_file)

    env_config = EnvrionmentEvogymConfig(
        robot,
        cppn_config,
        env_id=args.task,
        max_width=args.width,
        first_platform=args.first_platform)

    opt_config = OptimizerPPOConfig(
        steps_per_iteration=args.steps_per_iteration,
        transfer_steps=args.steps_per_iteration,
        clip_range=args.clip_range,
        epochs=args.epoch,
        num_mini_batch=args.num_mini_batch,
        steps=args.steps,
        num_processes=args.num_processes,
        learning_rate=args.learning_rate,
        init_log_std=args.init_log_std,
        max_steps=args.steps_per_iteration*args.reproduce_interval*20)

    if args.task=='Parkour-v1':
        maximum_reward = args.width/10 + 10
    else:
        maximum_reward = args.width/10

    poet_pop = POET(
        env_config,
        opt_config,
        save_path,
        num_workers=args.num_cores,
        niche_num=args.niche_num,
        reproduction_num=args.reproduce_num,
        admit_child_num=args.admit_child_num,
        reproduce_interval=args.reproduce_interval,
        transfer_interval=args.transfer_interval,
        save_core_interval=args.save_interval,
        repro_threshold=maximum_reward*args.reproduce_threshold,
        mc_lower=maximum_reward*args.mc_lower,
        mc_upper=maximum_reward*args.mc_upper,
        clip_reward_lower=0,
        clip_reward_upper=maximum_reward,
        novelty_knn=1,
        novelty_threshold=0.1,
        reset_pool=args.reset_pool)

    poet_pop.initialize_niche()
    poet_pop.optimize(iterations=args.iteration)


if __name__=='__main__':
    main()