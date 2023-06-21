import csv
import time
import os
import csv
import pickle
import numpy as np

class ReporterSet:
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

    def post_evaluate(self, config, offsprings, best_genome):
        for r in self.reporters:
            r.post_evaluate(config, offsprings, best_genome)

    def found_solution(self, config, population, best_genome):
        for r in self.reporters:
            r.found_solution(config, population, best_genome)


class BaseReporter:
    def start_generation(self, generation):
        pass

    def post_evaluate(self, config, offsprings, best):
        pass

    def end_generation(self, config, population):
        pass

    def found_solution(self, config, population, best_genome):
        pass


class SaveResultReporter(BaseReporter):

    def __init__(self, save_path, bd_names):
        self.save_path = save_path
        self.history_pop_file = os.path.join(self.save_path, 'history_pop.csv')
        self.history_pop_header = ['generation', 'id'] + bd_names + ['fitness', 'parent']
        self.history_fitness_file = os.path.join(self.save_path, 'history_fitness.csv')
        self.history_fitness_header = ['generation', 'id'] + bd_names + ['fitness', 'parent']
        self.generation = None

        self.genome_path = os.path.join(self.save_path, 'genome')
        os.makedirs(self.genome_path, exist_ok=True)

        with open(self.history_pop_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_pop_header)
            writer.writeheader()

        with open(self.history_fitness_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_fitness_header)
            writer.writeheader()

    def start_generation(self, generation):
        self.generation = generation

    def post_evaluate(self, config, offsprings, best_genome):
        with open(self.history_pop_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_pop_header)
            for key,genome in offsprings.items():
                items = {
                    'generation': self.generation,
                    'id': key,
                    'fitness': genome.fitness,
                    'parent': genome.parent
                }
                items.update(**genome.bd)

                writer.writerow(items)

        items = {
            'generation': self.generation,
            'id': best_genome.key,
            'fitness': best_genome.fitness,
            'parent': best_genome.parent
        }
        items.update(**best_genome.bd)
        with open(self.history_fitness_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_fitness_header)
            writer.writerow(items)
        best_file = os.path.join(self.genome_path, f'{best_genome.key}.pickle')
        with open(best_file, 'wb') as f:
            pickle.dump(best_genome, f)


class MapElitesReporter(BaseReporter):

    def __init__(self):
        self.generation = None
        self.generation_start_time = None
        self.generation_times = []

    def start_generation(self, generation):
        self.generation = generation
        print('\n ****** Running generation {} ****** \n'.format(generation))
        self.generation_start_time = time.time()

    # def post_evaluate(self, config, offsprings, best_genome):
        # pass

    def end_generation(self, config, population):

        print('Population size {}'.format(len(population)))

        fitnesses = [c.fitness for c in population.values()]
        fit_mean = np.mean(fitnesses)
        fit_std = np.std(fitnesses)
        print("Population's average fitness: {0:3.5f} stdev: {1:3.5f}".format(fit_mean, fit_std))

        best = max(population.values(), key=lambda z: z.fitness)
        best_bd_str = '(' + ', '.join(map(str, list(best.bd.values()))) + ')'
        print('Best fitness: {0:3.5f} - id {1} - bd {2}'.format(best.fitness, best.key, best_bd_str))

        elapsed = time.time() - self.generation_start_time
        self.generation_times.append(elapsed)
        self.generation_times = self.generation_times[-10:]
        average = sum(self.generation_times) / len(self.generation_times)
        if len(self.generation_times) > 1:
            print('Generation time: {0:.3f} sec ({1:.3f} average)'.format(elapsed, average))
        else:
            print('Generation time: {0:.3f} sec'.format(elapsed))
