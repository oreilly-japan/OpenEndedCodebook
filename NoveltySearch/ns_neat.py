import random

import neat

from reporting import SaveResultReporter, NoveltySearchReporter

def make_config(config_file, extra_info, custom_config):
    config = neat.Config(neat.DefaultGenome,
                         neat.DefaultReproduction,
                         neat.DefaultSpeciesSet,
                         neat.DefaultStagnation,
                         config_file,
                         extra_info=extra_info,
                         custom_config=custom_config)
    return config

class Population(neat.Population):

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        self.archive = {}
        self.novelty_threshold = config.extra_info['threshold_init']
        self.time_out = 0

    def run(self, evaluate_function, n=None):
        """
        Runs NEAT's genetic algorithm for at most n generations.  If n
        is None, run until solution is found or extinction occurs.
        The user-provided fitness_function must take only two arguments:
            1. The population as a list of (genome id, genome) tuples.
            2. The current configuration object.
        The return value of the fitness function is ignored, but it must assign
        a Python float to the `fitness` member of each genome.
        The fitness function is free to maintain external state, perform
        evaluations in parallel, etc.
        It is assumed that fitness_function does not modify the list of genomes,
        the genomes themselves (apart from updating the fitness member),
        or the configuration object.
        """

        if self.config.no_fitness_termination and (n is None):
            raise RuntimeError("Cannot have no generational limit with no fitness termination")

        k = 0
        while n is None or k < n:
            k += 1

            self.reporters.start_generation(self.generation)

            # Evaluate all genomes using the user-provided function.
            evaluate_function(list(self.population.items()), self.config, self.generation)

            self.evaluate_novelty_fitness()

            # Gather and report statistics.
            best = None
            for g in self.population.values():
                reward = getattr(g, 'reward', None)
                if reward is None:
                    raise RuntimeError("Reward not assigned to genome {}".format(g.key))

                if best is None or reward > best.reward:
                    best = g
            self.reporters.post_evaluate(self.config, self.population, self.species, best)

            # Track the best genome ever seen.
            if self.best_genome is None or best.reward > self.best_genome.reward:
                self.best_genome = best

            if not self.config.no_fitness_termination:
                # End if the fitness threshold is reached.
                fv = self.fitness_criterion(g.reward for g in self.population.values())
                if fv >= self.config.fitness_threshold:
                    self.reporters.found_solution(self.config, self.generation, best)
                    break

            # Create the next generation from the current generation.
            self.population = self.reproduction.reproduce(self.config, self.species,
                                                          self.config.pop_size, self.generation)

            # Check for complete extinction.
            if not self.species.species:
                self.reporters.complete_extinction()

                # If requested by the user, create a completely new population,
                # otherwise raise an exception.
                if self.config.reset_on_extinction:
                    self.population = self.reproduction.create_new(self.config.genome_type,
                                                                   self.config.genome_config,
                                                                   self.config.pop_size)
                else:
                    raise CompleteExtinctionException()

            # Divide the new population into species.
            self.species.speciate(self.config, self.population, self.generation)

            self.reporters.end_generation(self.config, self.population, self.species)

            self.generation += 1

        if self.config.no_fitness_termination:
            self.reporters.found_solution(self.config, self.generation, self.best_genome)

        return self.best_genome

    def evaluate_novelty_fitness(self):
        new_archive = {}
        for key,genome in self.population.items():

            reward = getattr(genome, 'reward', None)
            if reward is None:
                raise RuntimeError("reward not assigned to genome {}".format(genome.key))

            if reward < self.config.extra_info['MCNS']:
                genome.fitness = -1
                continue

            distances_archive = self._map_distance(key, genome, self.archive)
            distances_new_arhicve = self._map_distance(key, genome, new_archive)
            distances_current = self._map_distance(key, genome, self.population)

            distances_archive.update(distances_new_arhicve)
            novelty_archive = self._knn(list(distances_archive.values()))

            if novelty_archive > self.novelty_threshold:
                new_archive[key] = genome

            distances_current.update(distances_archive)
            novelty = self._knn(
                list(distances_current.values()),
                k=self.config.extra_info['neighbors'])

            genome.fitness = novelty

        self._update_novelty_archive(new_archive)

    def _map_distance(self, key1, genome1, genomes):
        distances = {}
        for key2,genome2 in genomes.items():
            if key1==key2:
                continue

            d = self.config.extra_info['metric'](genome1.data, genome2.data)
            distances[key2] = d

        return distances

    def _knn(self, distances, k=1):
        if len(distances)==0:
            return float('inf')

        distances.sort()

        knn = distances[:k]
        density = sum(knn) / len(distances)
        return density

    def _update_novelty_archive(self, new_archive):
        if len(new_archive)>0:
            self.time_out = 0
        else:
            self.time_out += 1

        if self.time_out >= 5:
            self.novelty_threshold *= 0.95
            if self.novelty_threshold < self.config.extra_info['threshold_floor']:
                self.novelty_threshold = self.config.extra_info['threshold_floor']
            self.time_out = 0

        # if more than four individuals added in last generation then raise threshold
        if len(new_archive) >= 4:
            self.novelty_threshold *= 1.2

        self.archive.update(new_archive)
