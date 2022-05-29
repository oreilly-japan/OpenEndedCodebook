import random
import itertools
from copy import deepcopy

class Reproduction():
    def __init__(self, population, config):
        self.config = config
        self.indexer = itertools.count(max(population.keys())+1)

        for _,genome in population.items():
            setattr(genome, 'generation', -1)
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
