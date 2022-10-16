import pickle

from .reproduction import Reproduction
from .reporting import ReporterSet


class Population:
    def __init__(self, config, genome1_pop_file, genome2_pop_file):

        self.reporters = ReporterSet()
        self.config = config
        self.generation = 0

        self.genome1_pop = pickle.load(open(genome1_pop_file, 'rb'))
        self.genome2_pop = pickle.load(open(genome2_pop_file, 'rb'))

        self.genome1_reproduction = Reproduction(self.genome1_pop, config.genome1_config)
        self.genome2_reproduction = Reproduction(self.genome2_pop, config.genome2_config)

    def add_reporter(self, reporter):
        self.reporters.add(reporter)

    def remove_reporter(self, reporter):
        self.reporters.remove(reporter)

    def run(self, evaluate_function, n=None):
        if n is None:
            n = self.config.generation - self.generation

        k = 0
        while k < n:
            k += 1

            self.reporters.start_generation(self.generation)

            genome1_offsprings = self.genome1_reproduction.create_offsprings(self.genome1_pop, self.config.genome1_offspring_size, self.generation)
            genome2_offsprings = self.genome2_reproduction.create_offsprings(self.genome2_pop, self.config.genome2_offspring_size, self.generation)

            # Evaluate all genomes using the user-provided function.
            evaluate_function(genome1_offsprings, genome2_offsprings,
                              self.genome1_pop, self.genome2_pop, self.config, self.generation)

            genome1_survivors = {key: genome for key,genome in genome1_offsprings.items() if genome.fitness>=self.config.genome1_criterion}
            genome2_survivors = {key: genome for key,genome in genome2_offsprings.items() if genome.fitness>=self.config.genome2_criterion}

            self.reporters.post_evaluate(self.config, genome1_survivors, genome2_survivors)

            self.genome1_pop = self.update_pop(self.genome1_pop, genome1_survivors, self.config.genome1_pop_size, self.config.genome1_config)
            self.genome2_pop = self.update_pop(self.genome2_pop, genome2_survivors, self.config.genome2_pop_size, self.config.genome2_config)

            self.reporters.end_generation(self.config, self.genome1_pop, self.genome2_pop)

            self.generation += 1

        return

    @staticmethod
    def update_pop(pop, survivors, pop_size, config):
        pop_unite = list(pop.items()) + list(survivors.items())
        pop_unite = sorted(pop_unite, key=lambda z: z[0])
        pop_alive = dict(pop_unite[-pop_size:])
        # pop_alive = {g.key: g for g in pop_unite[-pop_size:]}
        return pop_alive
