"""
Runs evaluation functions in parallel subprocesses
in order to evaluate multiple genomes at once.
"""
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


class ParallelEvaluator(object):
    def __init__(self, kwargs, num_workers, evaluate_function, timeout=None, parallel=True):
        """
        fitness_function should take one argument, a tuple of
        (genome object, config object), and return
        a single float (the genome's fitness).
        constraint_function should take one argument, a tuple of
        (genome object, config object), and return
        a single bool (the genome's validity).
        """
        self.kwargs = kwargs
        self.num_workers = num_workers
        self.evaluate_function = evaluate_function
        self.timeout = timeout
        self.parallel = parallel
        self.pool = NonDaemonPool(num_workers) if parallel and num_workers>0 else None


    def __del__(self):
        if self.parallel:
            self.pool.close() # should this be terminate?
            self.pool.join()

    def evaluate(self, genomes, config, generation):
        kwargs = dict(**self.kwargs, config=config, generation=generation)

        if self.parallel:
            jobs = []
            for key, genome in genomes:
                jobs.append(self.pool.apply_async(self.evaluate_function, args=(genome,), kwds=kwargs))

            # assign the fitness back to each genome
            for job, (_, genome) in zip(jobs, genomes):
                results = job.get(timeout=self.timeout)
                for attr, data in results.items():
                    setattr(genome, attr, data)

        else:
            for i, (_, genome) in enumerate(genomes):
                results = self.evaluate_function(genome, **kwargs)
                for attr, data in results.items():
                    setattr(genome, attr, data)


class MCCParallelEvaluator(object):
    def __init__(self, kwargs, num_workers, evaluate_function, decode_function1, decode_function2, timeout=None):
        """
        fitness_function should take one argument, a tuple of
        (genome object, config object), and return
        a single float (the genome's fitness).
        constraint_function should take one argument, a tuple of
        (genome object, config object), and return
        a single bool (the genome's validity).
        """
        self.kwargs = kwargs
        self.num_workers = num_workers
        self.evaluate_function = evaluate_function
        self.decode_function1 = decode_function1
        self.decode_function2 = decode_function2
        self.timeout = timeout

        lock = mp.Lock()
        self.pool = NonDaemonPool(num_workers, initargs=(lock,))
        self.manager = mp.Manager()


    def __del__(self):
        self.pool.close() # should this be terminate?
        self.pool.join()

    def evaluate(self, offsprings1, offsprings2, population1, population2, config, generation):
        kwargs = dict(**self.kwargs, config=config, generation=generation, evaluate_function=self.evaluate_function)

        offsprings1_decoded = [self.decode_function1(genome1, config.genome1_config) for (_,genome1) in offsprings1]
        offsprings2_decoded = [self.decode_function2(genome2, config.genome2_config) for (_,genome2) in offsprings2]

        population1_decoded = [self.decode_function1(genome1, config.genome1_config) for (_,genome1) in population1]
        population2_decoded = [self.decode_function2(genome2, config.genome2_config) for (_,genome2) in population2]

        offsprings1_success_num = [self.manager.Value('i', 0) for _ in range(len(offsprings1))]
        offsprings2_success_num = [self.manager.Value('i', 0) for _ in range(len(offsprings2))]

        population1_success_num = [self.manager.Value('i', len(genome1.success_keys)) for (_,genome1) in population1]
        population2_success_num = [self.manager.Value('i', len(genome2.success_keys)) for (_,genome2) in population2]


        # evaluate genome1
        self.evalute_one_side(offsprings1, offsprings1_decoded, offsprings1_success_num,
                              population2, population2_decoded, population2_success_num, kwargs)
        # evaluate genome2
        self.evalute_one_side(population1, population1_decoded, population1_success_num,
                              offsprings2, offsprings2_decoded, offsprings2_success_num, kwargs)

        for (_,genome1), num in zip(offsprings1, offsprings1_success_num):
            genome1.fitness = num.value
        for (_,genome2), num in zip(offsprings2, offsprings2_success_num):
            genome2.fitness = num.value

    def evalute_one_side(self, genomes1, phenos1, nums1, genomes2, phenos2, nums2, kwargs):
        jobs = []
        for g1_i in range(len(phenos1)):
            for g2_i in range(len(phenos2)):
                args = (phenos1[g1_i], nums1[g1_i],
                        phenos2[g2_i], nums2[g2_i])
                jobs.append(self.pool.apply_async(self.conditioned_evaluation, args=args, kwds=kwargs))

        for g1_key, genome1 in genomes1:
            for g2_key, genome2 in genomes2:
                success = jobs.pop(0).get(timeout=self.timeout)

                if success:
                    genome1.success_keys.append(g2_key)
                    genome2.success_keys.append(g1_key)

    @staticmethod
    def conditioned_evaluation(pheno1, achieve1, pheno2, achieve2, config, evaluate_function, **kwargs):
        count_up = False

        if achieve1.value >= config.genome1_limit or achieve2.value >= config.genome2_limit:
            return count_up
        if achieve1.value >= config.genome1_criteria and achieve2.value >= config.genome2_criteria:
            return count_up

        success = evaluate_function(pheno1, pheno2)

        if success:
            if (achieve1.value < config.genome1_criteria and achieve2.value < config.genome2_limit) or \
               (achieve2.value < config.genome2_criteria and achieve1.value < config.genome1_limit):

               achieve1.value += 1
               achieve2.value += 1

               count_up = True

        return count_up
