import os
import shutil
import json


def initialize_experiment(experiment_name, save_path, args):
    try:
        os.makedirs(save_path)
    except:
        print(f'THIS EXPERIMENT ({experiment_name}) ALREADY EXISTS')
        print('Override? (y/n): ', end='')
        ans = input()
        if ans.lower() == 'y':
            shutil.rmtree(save_path)
            os.makedirs(save_path)
        else:
            quit()
        print()

    argument_file = os.path.join(save_path, 'arguments.json')
    with open(argument_file, 'w') as f:
        json.dump(args.__dict__, f, indent=4)


def load_experiment(expt_path):
    with open(os.path.join(expt_path, 'arguments.json'), 'r') as f:
        expt_args = json.load(f)
    return expt_args
