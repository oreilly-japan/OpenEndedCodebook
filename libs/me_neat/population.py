
import numpy as np

from .reproduction import Reproduction
from .reporting import ReporterSet

class Population:
    def __init__(self, config):
        self.config = config
        self.reporters = ReporterSet()

        if config.fitness_criterion == 'max':
            self.fitness_criterion = max
        elif config.fitness_criterion == 'min':
            self.fitness_criterion = min
        elif config.fitness_criterion == 'mean':
            self.fitness_criterion = np.mean
        elif not config.no_fitness_termination:
            raise RuntimeError(
                "Unexpected fitness_criterion: {0!r}".format(config.fitness_criterion))

        self.reproduction = Reproduction(config.genome_config, config.genome_type)

        self.generation = 0
        self.best_genome = None
        self.population = {}

    def add_reporter(self, reporter):
        self.reporters.add(reporter)

    def remove_reporter(self, reporter):
        self.reporters.remove(reporter)

    def run(self, fitness_function, constraint_function=None, n=None):
        if n is None:
            n = self.config.generation - self.generation

        k = 0
        while k<n:
            k += 1

            self.reporters.start_generation(self.generation)

            offsprings = self.reproduction.reproduce(
                self.population, self.config.offspring_size, self.generation, constraint_function=constraint_function)

            # Evaluate all offsprings using the user-provided function.
            fitness_function(offsprings, self.config, self.generation)

            # Gather and report statistics.
            best = None
            for g in offsprings.values():
                if g.fitness is None:
                    raise RuntimeError("Fitness not assigned to genome {}".format(g.key))

                if best is None or g.fitness > best.fitness:
                    best = g
            self.reporters.post_evaluate(self.config, offsprings, best)

            self.update_pop(offsprings)

            # Track the best genome ever seen.
            if self.best_genome is None or best.fitness > self.best_genome.fitness:
                self.best_genome = best

            if not self.config.no_fitness_termination:
                # End if the fitness threshold is reached.
                fv = self.fitness_criterion(g.fitness for g in self.population.values())
                if fv >= self.config.fitness_threshold:
                    self.reporters.found_solution(self.config, self.generation, best)
                    break

            self.reporters.end_generation(self.config, self.population)

            self.generation += 1

        return self.best_genome

    def update_pop(self, offsprings):
        for offspring in offsprings.values():
            bd = getattr(offspring,'bd',None)
            if bd is None:
                raise RuntimeError("bd not assigned to genome {}".format(offspring.key))

            bd_key = tuple(list(bd.values()))
            old = self.population.get(bd_key, None)
            if old is None or offspring.fitness > old.fitness:
                self.population[bd_key] = offspring
