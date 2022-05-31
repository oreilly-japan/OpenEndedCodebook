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
        self.history_pop_header = ['generation', 'id', 'reward', 'species', 'parent1', 'parent2']
        self.history_reward_file = os.path.join(self.save_path, 'history_reward.csv')
        self.history_reward_header = ['generation', 'id', 'reward', 'species', 'parent1', 'parent2']

        self.genome_path = os.path.join(self.save_path, 'genome')
        os.makedirs(self.genome_path, exist_ok=True)

        with open(self.history_pop_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_pop_header)
            writer.writeheader()

        with open(self.history_reward_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_reward_header)
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
                    'reward': genome.fitness,
                    'species': species.get_species_id(genome.key),
                    'parent1': genome.parent1,
                    'parent2': genome.parent2
                }
                writer.writerow(items)

        current_reward = max(population.values(), key=lambda z: z.fitness)
        items = {
            'generation': self.generation,
            'id': current_reward.key,
            'reward': current_reward.fitness,
            'species': species.get_species_id(current_reward.key),
            'parent1': current_reward.parent1,
            'parent2': current_reward.parent2
        }
        with open(self.history_reward_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_reward_header)
            writer.writerow(items)
        reward_file = os.path.join(self.genome_path, f'{current_reward.key}.pickle')
        with open(reward_file, 'wb') as f:
            pickle.dump(current_reward, f)

    def found_solution(self, config, generation, best):
        pass
