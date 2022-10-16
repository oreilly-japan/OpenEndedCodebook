import random
from itertools import count
from copy import deepcopy

class Reproduction:
    def __init__(self, population, config):
        self.config = config
        self.indexer = count(max(population.keys())+1)

        node_index = 0
        for _,genome in population.items():
            setattr(genome, 'generation', -1)
            setattr(genome, 'parent', -1)
            if getattr(genome, 'success_keys', None) is None:
                setattr(genome, 'success_keys', [])
            if hasattr(genome, 'nodes'):
                node_index = max(node_index, max(genome.nodes.keys()))
            
        if node_index>0 and hasattr(config, 'node_indexer'):
            config.node_indexer = count(node_index+1)

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
