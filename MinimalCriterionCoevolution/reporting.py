import csv
import time
import os
import pickle
import csv

class ReporterSet():
    def __init__(self):
        self.reporters = []

    def add(self, reporter):
        self.reporters.append(reporter)

    def remove(self, reporter):
        self.reporters.remove(reporter)

    def start_generation(self, gen):
        for r in self.reporters:
            r.start_generation(gen)

    def end_generation(self, config, population1, population2):
        for r in self.reporters:
            r.end_generation(config, population1, population2)

    def post_evaluate(self, config, offsprings1, offsprings2):
        for r in self.reporters:
            r.post_evaluate(config, offsprings1, offsprings2)


class SaveReporter():

    def __init__(self, save_path, genome1_name, genome2_name):
        self.generation = None

        self.save_path = save_path
        self.genome1_name = genome1_name
        self.genome2_name = genome2_name
        self.history1_file = os.path.join(save_path, f'history_{genome1_name}.csv')
        self.history2_file = os.path.join(save_path, f'history_{genome2_name}.csv')
        self.history_header = ['generation', 'id', 'parent', 'success_keys']

        self.genome1_path = os.path.join(save_path, genome1_name)
        self.genome2_path = os.path.join(save_path, genome2_name)
        os.makedirs(self.genome1_path, exist_ok=True)
        os.makedirs(self.genome2_path, exist_ok=True)

        with open(self.history1_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_header)
            writer.writeheader()

        with open(self.history2_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_header)
            writer.writeheader()


    def start_generation(self, generation):
        self.generation = generation

    def post_evaluate(self, config, survivors1, survivors2):
        self.write_history(self.history1_file, self.history_header, survivors1, self.generation)
        self.save_genomes(self.genome1_path, survivors1)

        self.write_history(self.history2_file, self.history_header, survivors2, self.generation)
        self.save_genomes(self.genome2_path, survivors1)

        if len(survivors2)>0:
            print('survive mazes')
            for s in survivors2.values():
                print(s)
                print()

    @staticmethod
    def write_history(file, headers, genomes, generation):
        with open(file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)

            for key,genome in genomes.items():
                items = {
                    'generation': generation,
                    'id': genome.key,
                    'parent': genome.parent,
                    'success_keys': genome.success_keys
                }
                writer.writerow(items)

    @staticmethod
    def save_genomes(path, genomes):
        for key,genome in genomes.items():
            file_name = os.path.join(path, f'{genome.key}.pickle')
            with open(file_name, 'wb') as f:
                pickle.dump(genome, f)

    def end_generation(self, config, pop1, pop2):
        pass


class MCCReporter():

    def __init__(self, genome1_name, genome2_name):
        self.genome1_name = genome1_name
        self.genome2_name = genome2_name
        self.generation = None
        self.generation_start_time = None
        self.generation_times = []

    def start_generation(self, generation):
        self.generation = generation
        print(f'\n ****** Running generation {generation} ****** \n')
        self.generation_start_time = time.time()

    def post_evaluate(self, config, survivors1, survivors2):
        print(f'{len(survivors1)} {self.genome1_name} survived')
        print(f'{len(survivors2)} {self.genome2_name} survived')

    def end_generation(self, config, population1, population2):
        print(f'{self.genome1_name} population size: {len(population1)}')
        print(f'{self.genome2_name} population size: {len(population2)}')

        elapsed = time.time() - self.generation_start_time
        self.generation_times.append(elapsed)
        self.generation_times = self.generation_times[-10:]
        average = sum(self.generation_times) / len(self.generation_times)
        if len(self.generation_times) > 1:
            print("Generation time: {0:.3f} sec ({1:.3f} average)".format(elapsed, average))
        else:
            print("Generation time: {0:.3f} sec".format(elapsed))
