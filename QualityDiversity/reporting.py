import copy
import csv
import time
import os
import shutil
import csv
from functools import reduce

from neat.math_util import mean, stdev, median2
from neat.reporting import BaseReporter

class ReporterSet(object):

    def __init__(self):
        self.reporters = []

    def add(self, reporter):
        self.reporters.append(reporter)

    def remove(self, reporter):
        self.reporters.remove(reporter)

    def start_generation(self, gen):
        for r in self.reporters:
            r.start_generation(gen)

    def end_generation(self, config, population):
        for r in self.reporters:
            r.end_generation(config, population)

    def post_evaluate(self, config, population, best_genome):
        for r in self.reporters:
            r.post_evaluate(config, population, best_genome)

    def found_solution(self, config, generation, best):
        for r in self.reporters:
            r.found_solution(config, generation, best)

    def info(self, msg):
        for r in self.reporters:
            r.info(msg)

class SaveResultReporter(object):

    def __init__(self, save_path, bd_names):
        self.save_path = save_path
        self.history_pop_file = os.path.join(self.save_path, 'history_pop.csv')
        self.history_pop_header = ['birth', 'no.'] + bd_names + ['fitness']
        self.history_best_file = os.path.join(self.save_path, 'history_best.csv')
        self.history_best_header = ['generation', 'birth', 'no.'] + bd_names + ['fitness']
        self.generation = None

        with open(self.history_pop_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_pop_header)
            writer.writeheader()

        with open(self.history_best_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_best_header)
            writer.writeheader()

    def start_generation(self, generation):
        self.generation = generation
        save_path_structure = os.path.join(self.save_path, f"generation_{generation}", 'structure')
        save_path_controller = os.path.join(self.save_path, f"generation_{generation}", 'controller')
        os.makedirs(save_path_structure, exist_ok=True)
        os.makedirs(save_path_controller, exist_ok=True)

    def end_generation(self, config, population_pool):
        with open(self.history_pop_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_pop_header)

            for key,genome in population_pool.items():
                items = {
                    'birth': key[0],
                    'no.': key[1],
                    'fitness': genome.fitness
                }
                items.update(**genome.bd)

                writer.writerow(items)

        current_best = reduce(lambda x,y: x if x.fitness>y.fitness else y, population_pool.values())
        items = {
            'generation': self.generation,
            'birth': current_best.key[0],
            'no.': current_best.key[1],
            'fitness': current_best.fitness
        }
        items.update(**current_best.bd)
        with open(self.history_best_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_best_header)
            writer.writerow(items)

    def post_evaluate(self, config, population, best_genome):
        pass

    def found_solution(self, config, generation, best):
        pass

    def info(self, msg):
        pass


class MapElitesReporter(object):

    def __init__(self):
        self.generation = None
        self.generation_start_time = None
        self.generation_times = []

    def start_generation(self, generation):
        self.generation = generation
        print('\n ****** Running generation {0} ****** \n'.format(generation))
        self.generation_start_time = time.time()

    def end_generation(self, config, population_pool):
        elapsed = time.time() - self.generation_start_time
        self.generation_times.append(elapsed)
        self.generation_times = self.generation_times[-10:]
        average = sum(self.generation_times) / len(self.generation_times)
        if len(self.generation_times) > 1:
            print('Generation time: {0:.3f} sec ({1:.3f} average)'.format(elapsed, average))
        else:
            print('Generation time: {0:.3f} sec'.format(elapsed))

    def post_evaluate(self, config, population, best_genome):
        fitnesses = [c.fitness for c in population.values()]
        fit_mean = mean(fitnesses)
        fit_std = stdev(fitnesses)
        best_bd_str = '(' + ', '.join(map(str, list(best_genome.bd.values()))) + ')'
        print('Population size {}'.format(len(population)))
        print("Population's average fitness: {0:3.5f} stdev: {1:3.5f}".format(fit_mean, fit_std))
        print('Best fitness: {0:3.5f} - complexity: {1!r} - bd {2} - id {3}'.format(best_genome.fitness, best_genome.size(), best_bd_str, best_genome.key))

    def found_solution(self, config, generation, best):
        print('\nBest individual in generation {0} meets fitness threshold - complexity: {1!r}'.format(self.generation, best.size()))

    def info(self, msg):
        print(msg)
