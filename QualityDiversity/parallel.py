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
    def __init__(self, num_workers, decode_function, evaluate_function, timeout=None, parallel=True):
        self.num_workers = num_workers
        self.decode_function = decode_function
        self.evaluate_function = evaluate_function
        self.timeout = timeout
        self.parallel = parallel
        self.pool = NonDaemonPool(num_workers) if parallel and num_workers>0 else None

    def __del__(self):
        if self.parallel:
            self.pool.close() # should this be terminate?
            self.pool.join()

    def evaluate(self, genomes, config, generation):

        if self.parallel:
            phenomes = {key: self.decode_function(genome, config.genome_config) for key,genome in genomes.items()}

            jobs = {}
            for key,phenome in phenomes.items():
                args = (key, phenome, generation)
                jobs[key] = self.pool.apply_async(self.evaluate_function, args=args)

            # assign the fitness back to each genome
            for key,genome in genomes.items():
                results = jobs[key].get(timeout=self.timeout)
                for attr, data in results.items():
                    setattr(genome, attr, data)

        else:
            for key,genome in genomes.items():
                phenome = self.decode_function(genome, config.genome_config)

                args = (key, phenome, generation)
                results = self.evaluate_function(*args)
                for attr, data in results.items():
                    setattr(genome, attr, data)
