import random

import neat
from neat import nn

from reporting import ReporterSet, SaveResultReporter, MapElitesReporter

class Population:

    def __init__(self, config_file, extra_info, pop_size, fitness_function, constraint_function=None):
        self.reporters = ReporterSet()
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                  neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                  config_file, extra_info=extra_info,
                                  custom_config=[('NEAT', 'pop_size', pop_size)])
        self.generation = 0
        self.best_genome = None
        self.population_pool = None
        self.population_map = {}
        self.fitness_function = fitness_function
        self.constraint_function = constraint_function
        self.fitness_criterion = max

    def add_reporter(self, reporter):
        self.reporters.add(reporter)

    def remove_reporter(self, reporter):
        self.reporters.remove(reporter)

    def create_init_population(self):
        population_pool = {}
        while len(population_pool) < self.config.pop_size:
            key = (self.generation, len(population_pool))
            genome = self.config.genome_type(key)
            genome.configure_new(self.config.genome_config)

            if self.constraint_function is not None:
                if self.constraint_function(genome, self.config):
                    population_pool[key] = genome
            else:
                population_pool[key] = genome
        self.population_pool = population_pool

    def reproduction(self):
        population_pool = {}
        while len(population_pool) < self.config.pop_size:
            key = (self.generation, len(population_pool))

            if len(self.population_map)>1:
                parents = self.random_selection(2)
                child = self.crossover(key,parents[0],parents[1])

            elif len(self.population_map)==1:
                parent = self.random_selection(1)
                child = self.mutate(key,child)

            else:
                raise RuntimeError("No population")

            if self.constraint_function is not None:
                if self.constraint_function(child, self.config):
                    population_pool[key] = child
            else:
                population_pool[key] = child
        self.population_pool = population_pool

    def run(self, n=None):
        if self.population_pool is None:
            self.create_init_population()

        k = 0
        while n is None or k<n:
            k += 1

            self.reporters.start_generation(self.generation)

            # Evaluate and map population pool.
            self.mapping()

            # Gather and report statistics.
            best = None
            for g in self.population_map.values():
                if g.fitness is None:
                    raise RuntimeError("Fitness not assigned to genome {}".format(g.key))

                if best is None or g.fitness > best.fitness:
                    best = g
            self.reporters.post_evaluate(self.config, self.population_map, best)

            # Track the best genome ever seen.
            if self.best_genome is None or best.fitness > self.best_genome.fitness:
                self.best_genome = best

            if not self.config.no_fitness_termination:
                # End if the fitness threshold is reached.
                fv = self.fitness_criterion(g.fitness for g in self.population_map.values())
                if fv >= self.config.fitness_threshold:
                    self.reporters.found_solution(self.config, self.generation, best)
                    break

            self.reporters.end_generation(self.config, self.population_pool)

            self.generation += 1

            # Create the next generation from the current generation.
            self.reproduction()

        if not self.config.no_fitness_termination:
            self.reporters.found_solution(self.config, self.generation, self.best_genome)

        return self.best_genome

    def mapping(self):
        # Evaluate all genomes using the user-provided function.
        self.fitness_function(list(self.population_pool.items()), self.config, self.generation)

        for g in self.population_pool.values():
            bd = getattr(g,'bd',None)
            if bd is None:
                raise RuntimeError("bd not assigned to genome {}".format(g.key))

            bd_key = tuple(list(bd.values()))
            old = self.population_map.get(bd_key)
            if old is None or g.fitness > old.fitness:
                self.population_map[bd_key] = g


    def random_selection(self, num):
        candidates = list(self.population_map.values())
        picked = []
        for _ in range(num):
            genome = random.choice(candidates)
            picked.append(genome)
        return picked

    def crossover(self, gid, parent1, parent2):
        child = self.config.genome_type(gid)
        child.configure_crossover(parent1, parent2, self.config.genome_config)
        child.mutate(self.config.genome_config)
        return child

    def mutate(self, gid, parent):
        child = self.config.genome_type(gid)
        child.configure_crossover(parent, parent, self.config.genome_config)
        child.mutate(self.config.genome_config)
        return child
