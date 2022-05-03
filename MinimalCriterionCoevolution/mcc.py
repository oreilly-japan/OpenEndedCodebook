import pickle
import random
import itertools
from copy import deepcopy

import neat

from mcc_config import MCCConfig

from reporting import ReporterSet, SaveReporter, MCCReporter

def make_config(genome1, genome2, config_file, extra_info, custom_config):
    config = MCCConfig(genome1,
                       genome2,
                       config_file,
                       extra_info=extra_info,
                       custom_config=custom_config)
    return config

class Reproduction():
    def __init__(self, population, config):
        self.config = config
        self.indexer = itertools.count(max(population.keys())+1)

        for _,genome in population.items():
            setattr(genome, 'generation', 0)
            setattr(genome, 'parent', -1)
            if getattr(genome, 'success_keys', None) is None:
                setattr(genome, 'success_keys', [])

    def create_offsprings(self, population, offspring_size, generation):
        offsprings = {}
        while len(offsprings) < offspring_size:
            key = next(self.indexer)
            parent_key = random.choice(list(population.keys()))
            offspring = deepcopy(population[parent_key])
            offspring.mutate(self.config)
            offspring.key = key

            setattr(offspring, 'generation', generation)
            setattr(offspring, 'success_keys', [])
            setattr(offspring, 'parent', parent_key)

            offsprings[key] = offspring
        return offsprings


class Population(neat.Population):

    def __init__(self, config, genome1_pop_file, genome2_pop_file):

        self.reporters = ReporterSet()
        self.config = config
        self.generation = 0

        self.genome1_pop = pickle.load(open(genome1_pop_file, 'rb'))
        self.genome2_pop = pickle.load(open(genome2_pop_file, 'rb'))

        self.genome1_reproduction = Reproduction(self.genome1_pop, config.genome1_config)
        self.genome2_reproduction = Reproduction(self.genome2_pop, config.genome2_config)

    def run(self, evaluate_function, n=None):
        if n is None:
            n = self.config.generation - self.generation

        k = 0
        while n is None or k < n:
            k += 1

            self.reporters.start_generation(self.generation)

            genome1_offsprings = self.genome1_reproduction.create_offsprings(self.genome1_pop, self.config.genome1_offspring_size, self.generation)
            genome2_offsprings = self.genome2_reproduction.create_offsprings(self.genome2_pop, self.config.genome2_offspring_size, self.generation)

            # Evaluate all genomes using the user-provided function.
            evaluate_function(list(genome1_offsprings.items()), list(genome2_offsprings.items()),
                              list(self.genome1_pop.items()), list(self.genome2_pop.items()), self.config, self.generation)

            genome1_survivors = {key: genome for key,genome in genome1_offsprings.items() if genome.fitness>=1}
            genome2_survivors = {key: genome for key,genome in genome2_offsprings.items() if genome.fitness>=1}

            self.reporters.post_evaluate(self.config, genome1_survivors, genome2_survivors)

            self.genome1_pop = self.update_pop(self.genome1_pop, genome1_survivors, self.config.genome1_pop_size, self.config.genome1_config)
            self.genome2_pop = self.update_pop(self.genome2_pop, genome2_survivors, self.config.genome2_pop_size, self.config.genome2_config)

            self.reporters.end_generation(self.config, self.genome1_pop, self.genome2_pop)

            self.generation += 1

        return

    @staticmethod
    def update_pop(pop, survivors, pop_size, config):
        pop_unite = list(pop.values()) + list(survivors.values())
        pop_unite = sorted(pop_unite, key=lambda g: g.generation)
        pop_alive = {g.key: g for g in pop_unite[-pop_size:]}
        return pop_alive
