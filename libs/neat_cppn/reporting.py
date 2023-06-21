import csv
import os
import pickle
import csv

from neat.reporting import BaseReporter, ReporterSet

class SaveResultReporter(BaseReporter):

    def __init__(self, save_path):
        self.generation = None

        self.save_path = save_path
        self.history_pop_file = os.path.join(self.save_path, 'history_pop.csv')
        self.history_pop_header = ['generation', 'id', 'fitness', 'species', 'parent1', 'parent2']
        self.history_fitness_file = os.path.join(self.save_path, 'history_fitness.csv')
        self.history_fitness_header = ['generation', 'id', 'fitness', 'species', 'parent1', 'parent2']

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

    def post_evaluate(self, config, population, species, best_genome):
        with open(self.history_pop_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_pop_header)
            for key,genome in population.items():
                items = {
                    'generation': self.generation,
                    'id': genome.key,
                    'fitness': genome.fitness,
                    'species': species.get_species_id(genome.key),
                    'parent1': genome.parent1,
                    'parent2': genome.parent2
                }
                writer.writerow(items)

        current_best = max(population.values(), key=lambda z: z.fitness)
        items = {
            'generation': self.generation,
            'id': current_best.key,
            'fitness': current_best.fitness,
            'species': species.get_species_id(current_best.key),
            'parent1': current_best.parent1,
            'parent2': current_best.parent2
        }
        with open(self.history_fitness_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_fitness_header)
            writer.writerow(items)
        best_file = os.path.join(self.genome_path, f'{current_best.key}.pickle')
        with open(best_file, 'wb') as f:
            pickle.dump(current_best, f)

    def found_solution(self, config, generation, best):
        pass
