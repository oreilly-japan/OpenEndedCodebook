import csv
import time
import os
import pickle
import csv

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

    def end_generation(self, config, population1, population2):
        for r in self.reporters:
            r.end_generation(config, population1, population2)

    def post_evaluate(self, config, offsprings1, offsprings2):
        for r in self.reporters:
            r.post_evaluate(config, offsprings1, offsprings2)


class BaseReporter:
    def start_generation(self, generation):
        pass

    def post_evaluate(self, config, survivors1, survivors2):
        pass

    def end_generation(self, config, population1, population2):
        pass


class SaveResultReporter(BaseReporter):

    def __init__(self, save_path, genome1_name, genome2_name, init_pop1, init_pop2):
        self.generation = 0

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

        self.write_history(self.history1_file, self.history_header, init_pop1, self.generation)
        self.save_genomes(self.genome1_path, init_pop1)

        self.write_history(self.history2_file, self.history_header, init_pop2, self.generation)
        self.save_genomes(self.genome2_path, init_pop2)


    def start_generation(self, generation):
        self.generation = generation

    def post_evaluate(self, config, survivors1, survivors2):
        self.write_history(self.history1_file, self.history_header, survivors1, self.generation)
        self.save_genomes(self.genome1_path, survivors1)

        self.write_history(self.history2_file, self.history_header, survivors2, self.generation)
        self.save_genomes(self.genome2_path, survivors2)

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


class MCCReporter(BaseReporter):

    def __init__(self, genome1_name, genome2_name, print_genome1=False, print_genome2=False):
        max_str_size = max(len(genome1_name), len(genome2_name))
        self.genome1_name = genome1_name.ljust(max_str_size)
        self.genome2_name = genome2_name.ljust(max_str_size)
        self.print_genome1 = print_genome1
        self.print_genome2 = print_genome2
        self.generation = None
        self.generation_start_time = None
        self.generation_times = []

    def start_generation(self, generation):
        self.generation = generation
        print(f'\n ****** Running generation {generation} ****** \n')
        self.generation_start_time = time.time()

    def post_evaluate(self, config, survivors1, survivors2):
        if self.print_genome1 and len(survivors1)>0:
            print(f'----- survived {self.genome1_name} -----')
            for s in survivors1.values():
                print(str(s)+'\n')

        if self.print_genome2 and len(survivors2)>0:
            print(f'----- survived {self.genome2_name} -----')
            for s in survivors2.values():
                print(str(s)+'\n')

        print(f'{self.genome1_name} survived: {len(survivors1): =3}')
        print(f'{self.genome2_name} survived: {len(survivors2): =3}')

    def end_generation(self, config, population1, population2):
        print(f'{self.genome1_name}  population size: {len(population1): =3}', end='')
        if config.genome1_limit>0:
            limited_genomes1 = [genome1 for genome1 in population1.values() if len(genome1.success_keys)>=config.genome1_limit]
            print(f'  limited: {len(limited_genomes1): =3}')
        else:
            print()

        print(f'{self.genome2_name}  population size: {len(population2): =3}', end='')
        if config.genome2_limit>0:
            limited_genomes2 = [genome2 for genome2 in population2.values() if len(genome2.success_keys)>=config.genome2_limit]
            print(f'  limited: {len(limited_genomes2): =3}')
        else:
            print()

        elapsed = time.time() - self.generation_start_time
        self.generation_times.append(elapsed)
        self.generation_times = self.generation_times[-10:]
        average = sum(self.generation_times) / len(self.generation_times)
        if len(self.generation_times) > 1:
            print("Generation time: {0:.3f} sec ({1:.3f} average)".format(elapsed, average))
        else:
            print("Generation time: {0:.3f} sec".format(elapsed))
