
import os
import csv
import time

import multiprocessing.pool
import multiprocessing as mp

import random
from itertools import count
import numpy as np

from .niche import Niche

class NoDaemonProcess(mp.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.

# class Pool(mp.pool.Pool):
#     Process = NoDaemonProcess

class NonDaemonPool(mp.pool.Pool):
    def Process(self, *args, **kwds):
        proc = super(NonDaemonPool, self).Process(*args, **kwds)
        proc.__class__ = NoDaemonProcess
        return proc


class POET:
    def __init__(self, 
                 environment_config,
                 optimizer_config,
                 save_path,
                 num_workers=10,
                 niche_num=10,
                 reproduction_num=10,
                 admit_child_num=1,
                 reproduce_interval=30,
                 transfer_interval=15,
                 save_core_interval=15,
                 repro_threshold=5.0,
                 mc_lower=1,
                 mc_upper=10,
                 clip_reward_lower=0,
                 clip_reward_upper=10,
                 novelty_knn=1,
                 novelty_threshold=0.1,
                 reset_optimizer=True,
                 reset_pool=False):

        self.env_config = environment_config
        self.opt_config = optimizer_config
        
        self.niche_num = niche_num
        self.reproduction_num = reproduction_num
        self.admit_child_num = admit_child_num

        self.reproduce_interval = reproduce_interval
        self.transfer_interval = transfer_interval
        self.save_core_interval = save_core_interval
        
        self.repro_threshold = repro_threshold

        self.mc_lower = mc_lower
        self.mc_upper = mc_upper
        
        self.clip_reward_lower = clip_reward_lower
        self.clip_reward_upper = clip_reward_upper
        self.novelty_knn = novelty_knn
        self.novelty_threshold = novelty_threshold

        self.reset_optimizer = reset_optimizer

        self.iteration = 0
        self.iteration_start_time = None
        self.niches = {}
        self.niches_archive = {}
        self.niche_indexer = count(0)

        self.reset_pool = reset_pool
        self.num_workers = num_workers
        if self.reset_pool:
            self.pool = None
        else:
            self.pool = NonDaemonPool(self.num_workers)

        self.save_path = save_path
        self.niche_path = os.path.join(save_path, 'niche')
        os.makedirs(self.niche_path, exist_ok=True)

        self.history_file = os.path.join(save_path, 'niches.csv')
        self.history_header = ['iteration', 'key', 'parent']
        with open(self.history_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_header)
            writer.writeheader()
    
    def get_new_niche_key(self):
        return next(self.niche_indexer)

    def initialize_niche(self):
        print('-----   Initialize   -----')

        key = self.get_new_niche_key()
        niche = Niche(key, self.iteration)
        environment = self.env_config.make_init()
        optimizer = self.opt_config.make_init()
        niche.set_environment(environment)
        niche.set_optimizer(optimizer)
        niche.unite(self.env_config, self.opt_config)
        self.add_niche(key, niche)

        print(f'initialized niches: {key: =6}')
        print()

    def add_niche(self, key, niche):
        # print(f'admitted: niche {key: =6}')
        niche.admitted(self.env_config, self.opt_config)
        niche.init_log(self.niche_path, save_core=self.save_core_interval>0)
        self.niches[key] = niche

        with open(self.history_file, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_header)
            items = {
                    'iteration': self.iteration,
                    'key': key,
                    'parent': niche.parent
            }
            writer.writerow(items)

        flood = len(self.niches) - self.niche_num
        if flood > 0:
            archive_keys = sorted(self.niches.keys())[:flood]
            for key in archive_keys:
                niche = self.niches.pop(key)
                niche.archive()
                self.niches_archive[key] = niche

                print(f'archived niche: {key: =6}')


    def evaluate_niches(self, niches, imigrant_cores=None):
        for key,niche in niches.items():
            niche.start_evaluate(self.pool, self.env_config, self.opt_config, imigrant_cores=imigrant_cores)
        
        for key,niche in niches.items():
            reward = niche.end_evaluate(self.env_config, self.opt_config, imigrant_cores=imigrant_cores)
    
    def develop_niches(self):
        print('-----   Develop   -----')

        for key, niche in self.niches.items():
            niche.start_step(self.pool, self.env_config, self.opt_config)

        for key, niche in self.niches.items():
            niche.end_step(self.env_config, self.opt_config)

        self.evaluate_niches(self.niches)

        print('  niche     steps    reward      best  ')
        print('            =====   ========   ========')
        for key,niche in self.niches.items():
            print(f' {key: =6} :   {niche.steps: =5}   {niche.reward: =+8.2f}   {niche.best_reward: =+8.2f}')
        print()

    def transfer(self, reciever_niches, child=False):
        
        imigrant_niche_cores = {niche_key: niche.get_optimizer_core() for niche_key,niche in self.niches.items()}

        self.evaluate_niches(reciever_niches, imigrant_cores=imigrant_niche_cores)

        # start adaptation of accepts and get adapted
        adapts = {}
        for reciever_key,reciever_niche in reciever_niches.items():
            accepted_keys = reciever_niche.get_accepted_keys(imigrant_niche_cores.keys())
            if len(accepted_keys)==0:
                continue

            accepted_cores = {accepted_key: imigrant_niche_cores[accepted_key] for accepted_key in accepted_keys}
            reciever_niche.start_step(self.pool, self.env_config, self.opt_config, imigrant_cores=accepted_cores)
            adapted_cores = reciever_niche.end_step(self.env_config, self.opt_config, imigrant_cores=accepted_cores)
            adapts[reciever_key] = adapted_cores

        # start evaluation of adapteds on paralle process
        for reciever_key,adapted_cores in adapts.items():
            reciever_niche = reciever_niches[reciever_key]
            reciever_niche.start_evaluate(self.pool, self.env_config, self.opt_config, imigrant_cores=adapted_cores, invasion=True)

        # finish evalution and invaded optimizer
        if not child:
            print('  niche     transferred    from     reward ')
            print('            ===========   ======   ========')
            print_end = '\n'
        else:
            print_end = '   '

        for reciever_key,reciever_niche in reciever_niches.items():
            invader = {}
            if reciever_key in adapts:
                adapted_cores = adapts[reciever_key]
                invader = reciever_niche.end_evaluate(self.env_config, self.opt_config, imigrant_cores=adapted_cores, invasion=True, reset_optimizer=self.reset_optimizer)
                assert len(invader)<2
                if len(invader)==1:
                    invader_key = list(invader.keys())[0]
                    reward = invader[invader_key]
                    print(f' {reciever_key: =6} :           yes   {invader_key: =6}   {reward: =+8.2f}', end=print_end)

            if reciever_key not in adapts or len(invader)==0:
                print(f' {reciever_key: =6} :            no                    ', end=print_end)

    def transfer_entirely(self):
        print('-----   Transfer   -----')
        self.transfer(self.niches)
        print()

    def pass_mc(self, niche):
        return niche.reward > self.mc_lower and niche.reward < self.mc_upper

    def get_novelty_score(self, niche, archives):
        keys = archives.keys()
        transferred_rewards = niche.get_transferred_rewards(keys)
        transferred_rewards = np.clip(transferred_rewards, self.clip_reward_lower, self.clip_reward_upper)

        distances = []
        for _,archive_niche in archives.items():
            archive_transferred_rewards = archive_niche.get_transferred_rewards(keys)
            archive_transferred_rewards = np.clip(archive_transferred_rewards, self.clip_reward_lower, self.clip_reward_upper)
            distance = np.linalg.norm(transferred_rewards - archive_transferred_rewards)
            distances.append(distance)

        knn_distances = np.sort(distances)[:self.novelty_knn]
        novelty_score = knn_distances.mean()
        return novelty_score

    def get_child_niches(self, reproduction_num):
        print('reproduce child niches')

        all_niches = dict(list(self.niches.items()) + list(self.niches_archive.items()))
        niche_cores = {key: niche.get_optimizer_core() for key,niche in self.niches.items()}
        self.evaluate_niches(all_niches, imigrant_cores=niche_cores)

        parent_niches = [niche for niche in self.niches.values() if niche.reward>self.repro_threshold]

        if len(parent_niches) == 0:
            print('  no parent niches')
            return []

        all_niche_cores = {key: niche.get_optimizer_core() for key,niche in all_niches.items()}

        child_niche_candidates = {}
        for _ in range(reproduction_num):
            
            parent_niche = random.choice(parent_niches)
            child_key = self.get_new_niche_key()
            child_niche = parent_niche.reproduce(child_key, self.iteration, self.env_config, self.opt_config)
            child_niche_candidates[child_key] = child_niche

        # evaluation self
        self.evaluate_niches(child_niche_candidates)

        # evaluate niches, passed mc, by all niches
        child_niches_pass = {key: niche for key,niche in child_niche_candidates.items() if self.pass_mc(niche)}
        self.evaluate_niches(child_niches_pass, imigrant_cores=all_niche_cores)

        child_niches = []
        print('  child     parent    reward     mc     novelty')
        print('            ======   ========   ====   ========')
        for child_key,child_niche in child_niche_candidates.items():

            print(f' {child_key: =6} :   {child_niche.parent: =6}   {child_niche.reward: =+8.2f}', end='   ')

            if child_key in child_niches_pass:
                novelty_score = self.get_novelty_score(child_niche, all_niches)
                if novelty_score > self.novelty_threshold:
                    child_niches.append((child_key, child_niche, novelty_score))
                    print(f'pass   {novelty_score: =8.2f}')
                else:
                    print(f'fail   {novelty_score: =8.2f}')
            else:
                print('fail')

        #sort child list according to novelty for high to low
        child_niches = sorted(child_niches, key=lambda x: x[2], reverse=True)
        return child_niches

    def discover_new_niches(self):
        print('-----   Discover   -----')

        child_niches = self.get_child_niches(self.reproduction_num)

        if len(child_niches) == 0:
            print('  no child niches, continue')
            return

        print('transfer to child niche')
        print('  niche     transferred    from     reward    admitted')
        print('            ===========   ======   ========   ========')
        admitted = 0
        for niche_key,child_niche,_ in child_niches:

            self.transfer({niche_key: child_niche}, child=True)

            if self.pass_mc(child_niche):
                print('     yes')
                self.add_niche(niche_key, child_niche)
                admitted += 1
                if admitted >= self.admit_child_num:
                    break
            else:
                print('      no')

        print()
        
    def update_niche_status(self):
        keys = self.niches.keys()
        for key,niche in self.niches.items():
            niche.reset_transferred_rewards(keys)

    def start_iteration(self):
        print(f'********************  ITERATION {self.iteration+1: =6}   ********************')
        self.iteration_start_time = time.time()
        print()

        if self.reset_pool:
            self.pool = NonDaemonPool(self.num_workers)

    def end_iteration(self):
        save_core = self.save_core_interval > 0 and (self.iteration+1) % self.save_core_interval == 0
        for key,niche in self.niches.items():
            niche.save_log(save_core=save_core)

        iteration_end_time = time.time()
        print(f'elapsed time: {iteration_end_time-self.iteration_start_time: =.1f} sec')
        print('\n')

        if self.reset_pool:
            self.pool.close()
            self.pool.join()

    
    def optimize(self, iterations=2000):
        
        while self.iteration < iterations:
            self.start_iteration()

            if len(self.niches) > 1 and self.iteration % self.transfer_interval == 0:
                self.transfer_entirely()

            if self.iteration > 0 and self.iteration % self.reproduce_interval == 0:
                self.discover_new_niches()

            self.update_niche_status()

            self.develop_niches()

            self.end_iteration()

            self.iteration += 1


            