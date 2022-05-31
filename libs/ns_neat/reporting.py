import csv
import os
import pickle
import csv
import numpy as np

from neat_cppn import BaseReporter, StdOutReporter


class SaveResultReporter(BaseReporter):

    def __init__(self, save_path):
        self.generation = None

        self.save_path = save_path
        self.history_pop_file = os.path.join(self.save_path, 'history_pop.csv')
        self.history_pop_header = ['generation', 'id', 'novelty', 'reward', 'species', 'parent1', 'parent2']
        self.history_novelty_file = os.path.join(self.save_path, 'history_novelty.csv')
        self.history_novelty_header = ['generation', 'id', 'novelty', 'reward', 'species', 'parent1', 'parent2']
        self.history_reward_file = os.path.join(self.save_path, 'history_reward.csv')
        self.history_reward_header = ['generation', 'id', 'novelty', 'reward', 'species', 'parent1', 'parent2']

        self.genome_path = os.path.join(self.save_path, 'genome')
        os.makedirs(self.genome_path, exist_ok=True)

        with open(self.history_pop_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_pop_header)
            writer.writeheader()

        with open(self.history_novelty_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_novelty_header)
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
                    'novelty': genome.fitness,
                    'reward': genome.reward,
                    'species': species.get_species_id(genome.key),
                    'parent1': genome.parent1,
                    'parent2': genome.parent2
                }
                writer.writerow(items)

        current_novelty = max(population.values(), key=lambda z: z.fitness)
        items = {
            'generation': self.generation,
            'id': current_novelty.key,
            'novelty': current_novelty.fitness,
            'reward': current_novelty.reward,
            'species': species.get_species_id(current_novelty.key),
            'parent1': current_novelty.parent1,
            'parent2': current_novelty.parent2
        }
        with open(self.history_novelty_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.history_novelty_header)
            writer.writerow(items)
        novelty_file = os.path.join(self.genome_path, f'{current_novelty.key}.pickle')
        with open(novelty_file, 'wb') as f:
            pickle.dump(current_novelty, f)

        current_reward = max(population.values(), key=lambda z: z.reward)
        items = {
            'generation': self.generation,
            'id': current_reward.key,
            'novelty': current_reward.fitness,
            'reward': current_reward.reward,
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


class NoveltySearchReporter(StdOutReporter):

    def post_evaluate(self, config, population, species, best_genome):
        fitnesses = [c.fitness for c in population.values()]
        fit_mean = np.mean(fitnesses)
        fit_std = np.std(fitnesses)
        print('Population\'s average fitness: {0:3.5f} stdev: {1:3.5f}'.format(fit_mean, fit_std))

        rewards = [c.reward for c in population.values()]
        rew_mean = np.mean(rewards)
        rew_std = np.std(rewards)
        best_species_id = species.get_species_id(best_genome.key)
        print('Population\'s average reward : {0:3.5f} stdev: {1:3.5f}'.format(rew_mean, rew_std))
        print(
            'Best reward: {0:3.5f} - size: {1!r} - species {2} - id {3}'.format(best_genome.reward,
                                                                                 best_genome.size(),
                                                                                 best_species_id,
                                                                                 best_genome.key))
