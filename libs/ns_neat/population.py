from neat_cppn import Population
from . import metrices


class CompleteExtinctionException(Exception):
    pass

class Population(Population):

    def __init__(self, config, initial_state=None, constraint_function=None):
        super().__init__(config, initial_state=initial_state, constraint_function=constraint_function)

        self.archive = {}
        self.novelty_threshold = config.threshold_init
        self.time_out = 0
        self.metric_func = getattr(metrices, config.metric, None)
        assert self.metric_func is not None, f'metric {config.metric} is not impelemented in distances.py'

    def run(self, evaluate_function, constraint_function=None, n=None):

        if self.config.no_fitness_termination and (n is None):
            raise RuntimeError("Cannot have no generational limit with no fitness termination")

        k = 0
        while n is None or k < n:
            k += 1

            self.reporters.start_generation(self.generation)

            # Evaluate all genomes using the user-provided function.
            evaluate_function(self.population, self.config, self.generation)

            self.evaluate_novelty_fitness()

            # Gather and report statistics.
            best = None
            for g in self.population.values():
                score = getattr(g, 'score', None)
                if score is None:
                    raise RuntimeError("Score not assigned to genome {}".format(g.key))

                if best is None or score > best.score:
                    best = g
            self.reporters.post_evaluate(self.config, self.population, self.species, best)

            # Track the best genome ever seen.
            if self.best_genome is None or best.score > self.best_genome.score:
                self.best_genome = best

            if not self.config.no_fitness_termination:
                # End if the fitness threshold is reached.
                fv = self.fitness_criterion(g.score for g in self.population.values())
                if fv >= self.config.fitness_threshold:
                    self.reporters.found_solution(self.config, self.generation, best)
                    break

            # Create the next generation from the current generation.
            self.population = self.reproduction.reproduce(
                self.config, self.species, self.config.pop_size, self.generation,
                constraint_function=constraint_function)

            # Check for complete extinction.
            if not self.species.species:
                self.reporters.complete_extinction()

                # If requested by the user, create a completely new population,
                # otherwise raise an exception.
                if self.config.reset_on_extinction:
                    self.population = self.reproduction.create_new(
                        self.config.genome_type, self.config.genome_config, self.config.pop_size,
                        constraint_function=constraint_function)
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

            score = getattr(genome, 'score', None)
            if score is None:
                raise RuntimeError("score not assigned to genome {}".format(genome.key))

            if score < self.config.mcns:
                genome.fitness = -1
                continue

            distances_archive = self.map_distance(key, genome, self.archive)
            distances_new_archive = self.map_distance(key, genome, new_archive)
            distances_current = self.map_distance(key, genome, self.population)

            distances_archive.update(distances_new_archive)
            novelty_archive = self.knn(list(distances_archive.values()))

            if novelty_archive > self.novelty_threshold:
                new_archive[key] = genome

            distances_current.update(distances_archive)
            novelty = self.knn(
                list(distances_current.values()),
                k=self.config.neighbors)

            genome.fitness = novelty

        self.update_novelty_archive(new_archive)

    def map_distance(self, key1, genome1, genomes):
        distances = {}
        for key2,genome2 in genomes.items():
            if key1==key2:
                continue

            d = self.metric_func(genome1.data, genome2.data)
            distances[key2] = d

        return distances

    def knn(self, distances, k=1):
        if len(distances)==0:
            return float('inf')

        distances = sorted(distances)

        knn = distances[:k]
        density = sum(knn) / len(knn)
        return density

    def update_novelty_archive(self, new_archive):
        if len(new_archive)>0:
            self.time_out = 0
        else:
            self.time_out += 1

        if self.time_out >= 5:
            self.novelty_threshold *= 0.95
            if self.novelty_threshold < self.config.threshold_floor:
                self.novelty_threshold = self.config.threshold_floor
            self.time_out = 0

        # if more than four individuals added in last generation then raise threshold
        if len(new_archive) >= 4:
            self.novelty_threshold *= 1.2

        self.archive.update(new_archive)
