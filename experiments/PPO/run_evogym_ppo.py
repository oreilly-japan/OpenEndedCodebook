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
from ppo import run_ppo
from simulator import EvogymControllerSimulatorPPO, SimulateProcess
from gym_utils import make_vec_envs, load_robot


from arguments.evogym_ppo import get_args

class ppoConfig():
    def __init__(self, args):
        self.num_processes = args.num_processes
        self.eval_processes = 2
        self.seed = 1
        self.steps = args.steps
        self.num_mini_batch = args.num_mini_batch
        self.epochs = args.epochs
        self.learning_rate = args.learning_rate
        self.gamma = args.gamma
        self.clip_range = args.clip_range
        self.ent_coef = 0.01

        self.learning_steps = 50

        self.policy_kwargs = {
            'log_std_init'  : 0.0,
            'ortho_init'    : True,
            'squash_output' : False,
        }


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', 'evogym_ppo', args.name)

    initialize_experiment(args.name, save_path, args)


    structure = load_robot(ROOT_DIR, args.robot, task=args.task)

    ppo_config = ppoConfig(args)


    controller_path = os.path.join(save_path, 'controller')
    os.makedirs(controller_path, exist_ok=True)

    if not args.no_view:
        simulator = EvogymControllerSimulatorPPO(
            env_id=args.task,
            structure=structure,
            load_path=controller_path,
            deterministic=args.deterministic)

        simulate_process = SimulateProcess(
            simulator=simulator,
            generations=args.ppo_iters)

        simulate_process.init_process()
        simulate_process.start()


    history_file = os.path.join(save_path, 'history.csv')
    run_ppo(
        env_id=args.task,
        structure=structure,
        train_iters=args.ppo_iters,
        save_file=controller_path,
        config=ppo_config,
        deterministic=args.deterministic,
        save_iter=1,
        history_file=history_file)

if __name__=='__main__':
    main()
