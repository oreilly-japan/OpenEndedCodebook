"""
Gathers (via the reporting interface) and provides (to callers and/or a file)
the most-fit genomes and information on genome/species fitness and species sizes.
"""
import copy
import csv
import time

from neat.math_util import mean, stdev, median2
from neat.reporting import BaseReporter


class ReporterSet(object):
    """
    Keeps track of the set of reporters
    and gives methods to dispatch them at appropriate points.
    """
    def __init__(self):
        self.reporters = []

    def add(self, reporter):
        self.reporters.append(reporter)

    def remove(self, reporter):
        self.reporters.remove(reporter)

    def start_generation(self, gen):
        for r in self.reporters:
            r.start_generation(gen)

    def end_generation(self, config, population):
        for r in self.reporters:
            r.end_generation(config, population)

    def post_evaluate(self, config, population, best_genome):
        for r in self.reporters:
            r.post_evaluate(config, population, best_genome)

    def post_reproduction(self, config, population):
        for r in self.reporters:
            r.post_reproduction(config, population)

    def found_solution(self, config, generation, best):
        for r in self.reporters:
            r.found_solution(config, generation, best)

    def info(self, msg):
        for r in self.reporters:
            r.info(msg)


class MapElitesReporter(object):
    def __init__(self):
        self.generation = None
        self.generation_start_time = None
        self.generation_times = []

    def start_generation(self, generation):
        self.generation = generation
        print('\n ****** Running generation {0} ****** \n'.format(generation))
        self.generation_start_time = time.time()

    def end_generation(self, config, population):
        elapsed = time.time() - self.generation_start_time
        self.generation_times.append(elapsed)
        self.generation_times = self.generation_times[-10:]
        average = sum(self.generation_times) / len(self.generation_times)
        if len(self.generation_times) > 1:
            print("Generation time: {0:.3f} sec ({1:.3f} average)".format(elapsed, average))
        else:
            print("Generation time: {0:.3f} sec".format(elapsed))

    def post_evaluate(self, config, population, best_genome):
        fitnesses = [c.fitness for c in population.values()]
        fit_mean = mean(fitnesses)
        fit_std = stdev(fitnesses)
        best_bd_str = '('+ ', '.join(map(str,best_genome.bd)) + ')'
        print('Population size {}'.format(len(population)))
        print('Population\'s average fitness: {0:3.5f} stdev: {1:3.5f}'.format(fit_mean, fit_std))
        print(
            'Best fitness: {0:3.5f} - size: {1!r}  bd {2} - id {3}'.format(best_genome.fitness,
                                                                                 best_genome.size(),
                                                                                 best_bd_str,
                                                                                 best_genome.key))

    def found_solution(self, config, generation, best):
        print('\nBest individual in generation {0} meets fitness threshold - complexity: {1!r}'.format(
            self.generation, best.size()))

    def info(self, msg):
        print(msg)


class StatisticsReporter(BaseReporter):
    """
    Gathers (via the reporting interface) and provides (to callers and/or a file)
    the most-fit genomes and information on genome/species fitness and species sizes.
    """
    def __init__(self):
        BaseReporter.__init__(self)
        self.most_fit_genomes = []
        self.generation_statistics = []

    def post_evaluate(self, config, population, best_genome):
        self.most_fit_genomes.append(copy.deepcopy(best_genome))

        bd_stats = {}
        for bd, g in population.items():
            species_stats[bbd] = g
        self.generation_statistics.append(species_stats)

    def get_fitness_stat(self, f):
        stat = []
        for stats in self.generation_statistics:
            scores = []
            for species_stats in stats.values():
                scores.extend(species_stats.values())
            stat.append(f(scores))

        return stat

    def get_fitness_mean(self):
        """Get the per-generation mean fitness."""
        return self.get_fitness_stat(mean)

    def get_fitness_stdev(self):
        """Get the per-generation standard deviation of the fitness."""
        return self.get_fitness_stat(stdev)

    def get_fitness_median(self):
        """Get the per-generation median fitness."""
        return self.get_fitness_stat(median2)

    def best_unique_genomes(self, n):
        """Returns the most n fit genomes, with no duplication."""
        best_unique = {}
        for g in self.most_fit_genomes:
            best_unique[g.key] = g
        best_unique_list = list(best_unique.values())

        def key(genome):
            return genome.fitness

        return sorted(best_unique_list, key=key, reverse=True)[:n]

    def best_genomes(self, n):
        """Returns the n most fit genomes ever seen."""
        def key(g):
            return g.fitness

        return sorted(self.most_fit_genomes, key=key, reverse=True)[:n]

    def best_genome(self):
        """Returns the most fit genome ever seen."""
        return self.best_genomes(1)[0]

    def save(self):
        self.save_genome_fitness()
        self.save_species_count()
        self.save_species_fitness()

    def save_genome_fitness(self,
                            delimiter=' ',
                            filename='fitness_history.csv'):
        """ Saves the population's best and average fitness. """
        with open(filename, 'w') as f:
            w = csv.writer(f, delimiter=delimiter)

            best_fitness = [c.fitness for c in self.most_fit_genomes]
            avg_fitness = self.get_fitness_mean()

            for best, avg in zip(best_fitness, avg_fitness):
                w.writerow([best, avg])

    def save_species_count(self, delimiter=' ', filename='speciation.csv'):
        """ Log speciation throughout evolution. """
        with open(filename, 'w') as f:
            w = csv.writer(f, delimiter=delimiter)
            for s in self.get_species_sizes():
                w.writerow(s)

    def save_species_fitness(self, delimiter=' ', null_value='NA', filename='species_fitness.csv'):
        """ Log species' average fitness throughout evolution. """
        with open(filename, 'w') as f:
            w = csv.writer(f, delimiter=delimiter)
            for s in self.get_species_fitness(null_value):
                w.writerow(s)

    def get_species_sizes(self):
        all_species = set()
        for gen_data in self.generation_statistics:
            all_species = all_species.union(gen_data.keys())

        max_species = max(all_species)
        species_counts = []
        for gen_data in self.generation_statistics:
            species = [len(gen_data.get(sid, [])) for sid in range(1, max_species + 1)]
            species_counts.append(species)

        return species_counts

    def get_species_fitness(self, null_value=''):
        all_species = set()
        for gen_data in self.generation_statistics:
            all_species = all_species.union(gen_data.keys())

        max_species = max(all_species)
        species_fitness = []
        for gen_data in self.generation_statistics:
            member_fitness = [gen_data.get(sid, []) for sid in range(1, max_species + 1)]
            fitness = []
            for mf in member_fitness:
                if mf:
                    fitness.append(mean(mf))
                else:
                    fitness.append(null_value)
            species_fitness.append(fitness)

        return species_fitness
