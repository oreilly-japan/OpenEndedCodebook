
import multiprocessing.pool
import multiprocessing as mp

class NoDaemonProcess(mp.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.

# class Pool(mp.pool.Pool):
#     Process = NoDaemonProcess

class NonDaemonPool(mp.pool.Pool):
    def Process(self, *args, **kwds):
        proc = super(NonDaemonPool, self).Process(*args, **kwds)
        proc.__class__ = NoDaemonProcess
        return proc

class EvaluatorParallel:
    def __init__(self, num_workers, decode_function, evaluate_function, revaluate=False, timeout=None, parallel=True, print_progress=True):
        self.num_workers = num_workers
        self.decode_function = decode_function
        self.evaluate_function = evaluate_function
        self.revaluate = revaluate
        self.timeout = timeout
        self.parallel = parallel
        self.pool = NonDaemonPool(num_workers) if parallel and num_workers>0 else None
        self.print_progress = print_progress

    def __del__(self):
        if self.pool is not None:
            self.pool.close()
            self.pool.join()

    def evaluate(self, genomes, config, generation):

        size = len(genomes)

        if self.parallel:
            phenomes = {key: self.decode_function(genome, config.genome_config) for key,genome in genomes.items()}

            jobs = {}
            for key,phenome in phenomes.items():
                # if already assinged fitness, skip evaluation
                if not self.revaluate and getattr(genomes[key], 'fitness', None) is not None:
                    continue

                args = (key, phenome, generation)
                jobs[key] = self.pool.apply_async(self.evaluate_function, args=args)

            # assign the result back to each genome
            for i,(key,genome) in enumerate(genomes.items()):
                if key not in jobs:
                    continue

                results = jobs[key].get(timeout=self.timeout)
                for attr, data in results.items():
                    setattr(genome, attr, data)

                if self.print_progress:
                    print(f'\revaluating genomes ... {i+1: =4}/{size: =4}', end='')
            if self.print_progress:
                print('evaluating genomes ... done')

        else:
            for i,(key,genome) in enumerate(genomes.items()):
                phenome = self.decode_function(genome, config.genome_config)

                args = (key, phenome, generation)
                results = self.evaluate_function(*args)
                for attr, data in results.items():
                    setattr(genome, attr, data)
                if self.print_progress:
                    print(f'\revaluating genomes ... {i+1: =4}/{size: =4}', end='')
            if self.print_progress:
                print('evaluating genomes ... done')

class MCCEvaluatorParallel:
    def __init__(self, num_workers, evaluate_function, decode_function1, decode_function2, timeout=None):
        self.num_workers = num_workers
        self.evaluate_function = evaluate_function
        self.decode_function1 = decode_function1
        self.decode_function2 = decode_function2
        self.timeout = timeout

        self.pool = NonDaemonPool(num_workers)
        self.manager = mp.Manager()

    def __del__(self):
        self.pool.close()
        self.pool.join()

    def evaluate(self, offsprings1_genome, offsprings2_genome, population1_genome, population2_genome, config, generation):

        offsprings1_phenome = {key1: self.decode_function1(genome1, config.genome1_config) for key1,genome1 in offsprings1_genome.items()}
        offsprings2_phenome = {key2: self.decode_function2(genome2, config.genome2_config) for key2,genome2 in offsprings2_genome.items()}

        population1_phenome = {key1: self.decode_function1(genome1, config.genome1_config) for key1,genome1 in population1_genome.items()}
        population2_phenome = {key2: self.decode_function2(genome2, config.genome2_config) for key2,genome2 in population2_genome.items()}

        offsprings1_count = {key1: self.manager.Value('i', 0) for key1 in offsprings1_genome.keys()}
        offsprings2_count = {key2: self.manager.Value('i', 0) for key2 in offsprings2_genome.keys()}

        population1_count = {key1: self.manager.Value('i', len(genome1.success_keys)) for key1,genome1 in population1_genome.items()}
        population2_count = {key2: self.manager.Value('i', len(genome2.success_keys)) for key2,genome2 in population2_genome.items()}


        # evaluate genome1
        self.evalute_one_side(offsprings1_genome, offsprings1_phenome, offsprings1_count,
                              population2_genome, population2_phenome, population2_count, config, generation)
        # evaluate genome2
        self.evalute_one_side(population1_genome, population1_phenome, population1_count,
                              offsprings2_genome, offsprings2_phenome, offsprings2_count, config, generation)

        for key1 in offsprings1_genome.keys():
            offsprings1_genome[key1].fitness = offsprings1_count[key1].value
        for key2 in offsprings2_genome.keys():
            offsprings2_genome[key2].fitness = offsprings2_count[key2].value

    def evalute_one_side(self, genomes1, phenomes1, counts1, genomes2, phenomes2, counts2, config, generation):
        jobs = {}
        for key1 in genomes1.keys():
            for key2 in genomes2.keys():
                args = (phenomes1[key1], counts1[key1],
                        phenomes2[key2], counts2[key2],
                        config, generation, self.evaluate_function)
                jobs[(key1, key2)] = self.pool.apply_async(self.conditioned_evaluation, args=args)

        for key1, genome1 in genomes1.items():
            for key2, genome2 in genomes2.items():
                success = jobs[(key1, key2)].get(timeout=self.timeout)

                if success:
                    genome1.success_keys.append(key2)
                    genome2.success_keys.append(key1)

    @staticmethod
    def conditioned_evaluation(phenome1, achieve1, phenome2, achieve2, config, generation, evaluate_function):
        count_up = False

        if (config.genome1_limit > 0 and achieve1.value >= config.genome1_limit) or\
           (config.genome2_limit > 0 and achieve2.value >= config.genome2_limit):
            return count_up
        if achieve1.value >= config.genome1_criterion and achieve2.value >= config.genome2_criterion:
            return count_up

        success = evaluate_function(phenome1, phenome2, generation)

        if success:
            if (achieve1.value < config.genome1_criterion and (config.genome2_limit == 0 or achieve2.value < config.genome2_limit)) or \
               (achieve2.value < config.genome2_criterion and (config.genome1_limit == 0 or achieve1.value < config.genome1_limit)):

               achieve1.value += 1
               achieve2.value += 1

               count_up = True

        return count_up
