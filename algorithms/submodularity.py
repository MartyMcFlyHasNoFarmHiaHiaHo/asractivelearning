from collections import Counter
import math
__author__ = 'martin'

class SubmodularityCoverage(object):

    def __init__(self, item_pool_dict, initial_covered_set=None, kernel=math.sqrt):
        if not initial_covered_set:
            initial_covered_set = Counter()
        self.covered_elems = initial_covered_set 
        self.item_pool_dict = item_pool_dict
        self.kernel = kernel
        self._build_queue()

    def _build_queue(self):
        from asractivelearning.datastructures.priorityqueue import FastBucketQueue
        self.queue = FastBucketQueue()
        for (item_key, elem_set) in self.item_pool.iteritems():
            gain = self._compute_gain(elem_set, self.covered_elems)
            self.queue.push(item_key, gain)

    def _compute_gain(self, elem_set, covered_elem):
        accum_gain = 0.0
        # # Save repeated function-pointer reevaluation in loop
        sqrtFct = self.kernel 
        for key, value in elem_set.viewitems():
            accum_gain += sqrtFct(value+covered_elem[key]) - sqrtFct(covered_elem[key])
        return accum_gain

    def draw_sample(self):


    def __iter__(self):
        return self

    def next(self):
        self.draw_sample()



    def compute_scores(self, item_pool, scoring_fct, duration_itemgetter, batch_size_seconds):
        self._loop(item_pool, scoring_fct, duration_itemgetter, batch_size_seconds)


