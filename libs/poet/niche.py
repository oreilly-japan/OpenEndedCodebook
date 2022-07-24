import os
import csv
import numpy as np


class Niche():
    def __init__(self, key, iteration, parent=None):
        self.key = key
        self.iteration = iteration
        self.parent = parent

        self.environemt = None
        self.optimizer = None

        self.steps = 0
        self.developed = False
        
        self.score = float('-inf')
        self.best_score = float('-inf')
        self.recent_scores = []
        self.transferred_scores = {}
        self.transferred_from = parent

        self.processes = {}

        self.history_file = None
        self.history_header = None
        self.core_path = None

    def set_environment(self, environment):
        self.environment = environment

    def set_optimizer(self, optimizer):
        self.optimizer = optimizer
    
    def unite(self, env_config, opt_config):
        env_info = self.environment.get_env_info(env_config)
        self.optimizer.set_env_info(env_info, opt_config)

    def get_optimizer_core(self):
        return self.optimizer.get_core()


    def reproduce(self, new_niche_key, iteration, env_config, opt_config):
        new_environment = self.environment.reproduce(env_config)
        new_optimizer = self.optimizer.reproduce(opt_config)
        new_niche = Niche(new_niche_key, iteration, parent=self.key)
        new_niche.set_environment(new_environment)
        new_niche.set_optimizer(new_optimizer)
        new_niche.unite(env_config, opt_config)
        return new_niche

    def archive(self):
        self.environment.archive()
        self.optimizer.archive()


    def admitted(self, env_config, opt_config):
        self.environment.admitted(env_config)
        self.optimizer.admitted(opt_config)

    def init_log(self, niche_path, save_core=False):
        save_path = os.path.join(niche_path, f'{self.key}')
        os.makedirs(save_path, exist_ok=True)

        self.environment.save(save_path)
        self.optimizer.save(save_path)

        self.history_file = os.path.join(save_path, 'history.csv')
        self.history_header = ['step', 'score', 'transferred_from']

        with open(self.history_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_header)
            writer.writeheader()

        self.core_path = os.path.join(save_path, 'core')
        os.makedirs(self.core_path, exist_ok=True)

        self.save_log(save_core=save_core)

    def save_log(self, save_core=False):
        with open(self.history_file, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_header)
            items = {
                    'step': self.steps,
                    'score': self.score,
                    'transferred_from': self.transferred_from
            }
            writer.writerow(items)

        self.transferred_from = None

        if save_core:
            self.optimizer.save_core(self.core_path, self.steps)

        if self.score > self.best_score:
            self.best_score = self.score
            self.optimizer.save_core(self.core_path, 'best')


    def start_step(self, pool, env_config, opt_config, imigrant_cores=None):
        assert len(self.processes)==0

        self.processes = {}
        if imigrant_cores is None:
            processes = {}
            func, kwargs = self.optimizer.get_step(opt_config)
            for key,kwds in kwargs.items():
                processes[key] = pool.apply_async(func, kwds=kwds)
            self.processes[self.key] = processes
        
        else:
            for imigrant_key,imigrant_core in imigrant_cores.items():
                processes = {}
                func, kwargs = self.optimizer.get_step(opt_config, core=imigrant_core)
                for key,kwds in kwargs.items():
                    processes[key] = pool.apply_async(func, kwds=kwds)
                self.processes[imigrant_key] = processes

    def end_step(self, env_config, opt_config, imigrant_cores=None):
        assert len(self.processes)>0

        cores = {}
        if imigrant_cores is None:
            if not self.developed:
                assert self.key in self.processes
                results = {}
                processes = self.processes.pop(self.key)
                for key in list(processes.keys()):
                    results[key] = processes.pop(key).get()
                cores[self.key] = self.optimizer.step(results, opt_config)
                self.steps += 1
        
        else:
            for imigrant_key,imigrant_core in imigrant_cores.items():
                assert imigrant_key in self.processes
                results = {}
                processes = self.processes.pop(imigrant_key)
                for key in list(processes.keys()):
                    results[key] = processes.get(key).get()
                cores[imigrant_key] = self.optimizer.step(results, opt_config, core=imigrant_core, update=False)

        assert len(self.processes)==0

        return cores


    def start_evaluate(self, pool, env_config, opt_config, imigrant_cores=None, invasion=False):
        assert len(self.processes)==0

        self.processes = {}
        if imigrant_cores is None:
            func, kwargs = self.optimizer.get_evaluate(opt_config)
            self.processes[self.key] = pool.apply_async(func, kwds=kwargs)
        
        else:
            for imigrant_key,imigrant_core in imigrant_cores.items():
                if not invasion and imigrant_key in self.transferred_scores:
                    self.processes[imigrant_key] = pool.apply_async(self.transferred_scores.get, args=(imigrant_key,))

                else:
                    func, kwargs = self.optimizer.get_evaluate(opt_config, core=imigrant_core)
                    self.processes[imigrant_key] = pool.apply_async(func, kwds=kwargs)

    def end_evaluate(self, env_config, opt_config, imigrant_cores=None, invasion=False, reset_optimizer=True):

        scores = {}
        if imigrant_cores is None:
            assert self.key in self.processes
            score = self.processes.pop(self.key).get()
            scores[self.key] = score

            self.score = score
            self.recent_scores.append(score)
            while len(self.recent_scores)>5:
                self.recent_scores.pop(0)

            # if score > self.best_score:
            #     self.best_score = score
            #     if self.core_path is not None:
            #         self.optimizer.save_core(self.core_path, 'best')

        else:
            for imigrant_key,_ in imigrant_cores.items():
                assert imigrant_key in self.processes
                score = self.processes.pop(imigrant_key).get()
                scores[imigrant_key] = score
        
        if invasion:
            assert self.key not in scores

            max_imigrant_key, max_imigrant_score = max(scores.items(), key=lambda z: z[1])
            if max_imigrant_score > self.score:
                max_imigrant_core = imigrant_cores[max_imigrant_key]
                self.optimizer.set_core(max_imigrant_core, opt_config, reset=reset_optimizer)

                self.score = max_imigrant_score
                self.recent_scores = [max_imigrant_score]
                self.transferred_scores[self.key] = max_imigrant_score
                self.transferred_from = max_imigrant_key

                # if max_imigrant_score > self.best_score:
                #     self.best_score = max_imigrant_score
                #     if self.core_path is not None:
                #         self.optimizer.save_core(self.core_path, 'best')

                return {max_imigrant_key: max_imigrant_score}
            else:
                return {}

        else:
            self.transferred_scores.update(scores)
            return scores

    def get_accepted_keys(self, keys):
        base_score = np.mean(self.recent_scores)
        accepted_keys = [key for key in keys if key!=self.key and self.transferred_scores[key]>base_score]
        return accepted_keys

    def get_transferred_scores(self, keys):
        return [self.transferred_scores[key] for key in keys]

    def reset_transferred_scores(self, keys):
        for key in keys:
            self.transferred_scores.pop(key, None)