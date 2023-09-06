import sys
import os

import evogym.envs


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURR_DIR))

LIB_DIR = os.path.join(ROOT_DIR, 'libs')
sys.path.append(LIB_DIR)
from experiment_utils import initialize_experiment

ENV_DIR = os.path.join(ROOT_DIR, 'envs', 'evogym')
sys.path.append(ENV_DIR)
from run_ppo import run_ppo
from simulator import EvogymControllerSimulatorPPO, SimulateProcess
from gym_utils import load_robot


from arguments.evogym_ppo import get_args

class PpoConfig:
    def __init__(self, args):
        self.num_processes = args.num_processes
        self.eval_processes = 1
        self.seed = 1

        self.steps = args.steps
        self.num_mini_batch = args.num_mini_batch
        self.epochs = args.epochs
        self.learning_rate = args.learning_rate
        self.gamma = args.gamma
        self.clip_range = args.clip_range
        self.ent_coef = 0.01
        self.vf_coef = 0.5
        self.max_grad_norm = 0.5
        self.lr_decay = True
        self.gae_lambda = 0.95
        self.init_log_std = args.init_log_std


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'evogym_ppo', args.name)

    initialize_experiment(args.name, save_path, args)


    robot = load_robot(ROOT_DIR, args.robot, task=args.task)

    ppo_config = PpoConfig(args)


    controller_path = os.path.join(save_path, 'controller')
    os.makedirs(controller_path, exist_ok=True)

    if not args.no_view:
        simulator = EvogymControllerSimulatorPPO(
            env_id=args.task,
            robot=robot,
            load_path=controller_path,
            interval=args.evaluation_interval,
            deterministic=not args.probabilistic)

        simulate_process = SimulateProcess(
            simulator=simulator,
            generations=args.train_iters)

        simulate_process.init_process()
        simulate_process.start()


    history_file = os.path.join(save_path, 'history.csv')
    run_ppo(
        env_id=args.task,
        robot=robot,
        train_iters=args.train_iters,
        eval_interval=args.evaluation_interval,
        save_file=controller_path,
        config=ppo_config,
        deterministic=not args.probabilistic,
        save_iter=True,
        history_file=history_file)

if __name__=='__main__':
    main()
