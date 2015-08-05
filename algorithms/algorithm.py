import itertools 

class SamplingAlgorithm(object):

    def __init__(self, algorithm_core, takewhile_condition=True):
        self.algorithm = algorithm_core
        self.condition = takewhile_condition

    def _loop(self):
        iterator = iter(self.algorithm)
        sampled_items = itertools.takewhile(self.condition, iterator)
        return sampled_items

    def run(self, *args, **kwargs):
        return self._loop()

