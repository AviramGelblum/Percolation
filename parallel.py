import concurrent.futures


class ParallelComputing:

    def __init__(self, func, parallel_var, max_workers):
        self.func = func
        self.parallel_var = parallel_var
        self.max_workers = max_workers

    def run(self):
        with concurrent.futures.ProcessPoolExecutor(self.max_workers) as executor:
            executor.map(self.func, self.parallel_var)

    def run_not_parallel(self, series=False, index=0):
        try:
            iterator = iter(self.parallel_var)
        except TypeError:
            self.func(self.parallel_var)  # not iterable
        else:
            if series:
                for par_var in iterator:
                    self.func(par_var)
            else:
                self.func(self.parallel_var[index])  # iterable


