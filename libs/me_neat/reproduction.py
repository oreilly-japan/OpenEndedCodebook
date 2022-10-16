import random
import itertools
from copy import deepcopy

class Reproduction:
    def __init__(self, config, genome_type):
        self.config = config
        self.genome_type = genome_type
        self.indexer = itertools.count(0)

    def create_new(self, key):
        genome = self.genome_type(key)
        genome.configure_new(self.config)
        return genome

    def mutate(self, key, genome):
        genome_ = deepcopy(genome)
        genome_.mutate(self.config)
        genome_.key = key
        return genome_

    def create_init(self, offspring_size, generation, constraint_function=None):
        population = {}
        while len(population) < offspring_size:
            key = next(self.indexer)
            genome = self.create_new(key)

            if constraint_function is not None:
                while not constraint_function(genome, self.config, generation):
                    genome = self.create_new(key)

            setattr(genome, 'generation', generation)
            setattr(genome, 'parent', [-1])
            population[key] = genome

        return population

    def create_offsprings(self, population, offspring_size, generation, constraint_function=None):
        if len(population) == 0:
            raise RuntimeError("No population")

        offsprings = {}
        while len(offsprings) < offspring_size:
            key = next(self.indexer)

            parent_key, parent = random.choice(list(population.items()))
            offspring = self.mutate(key, parent)

            if constraint_function is not None:
                while not constraint_function(offspring, self.config, generation):
                    parent_key, parent = random.choice(list(population.items()))
                    offspring = self.mutate(key, parent)

            setattr(offspring, 'fitness', None)
            setattr(offspring, 'generation', generation)
            setattr(offspring, 'parent', parent_key)
            offsprings[key] = offspring

        return offsprings

    def reproduce(self, population, offspring_size, generation, constraint_function=None):
        if len(population)==0:
            population = self.create_init(offspring_size, generation, constraint_function=constraint_function)
        else:
            population = self.create_offsprings(population, offspring_size, generation, constraint_function=constraint_function)

        return population
