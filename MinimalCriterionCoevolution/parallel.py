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
