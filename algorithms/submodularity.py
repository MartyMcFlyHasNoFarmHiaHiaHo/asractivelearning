from collections import Counter
import math
__author__ = 'martin'

class SubmodularityCoverage(object):

    def __init__(self, initial_items=None):
        if not initial_items:
            initial_items = Counter()

    def _funcG(self, tfIdfDict, coveredPhonemes):
        accum = 0.0
        # # Save repeated function-pointer reevaluation in loop
        sqrtFct = math.sqrt
        for key, value in tfIdfDict.viewitems():
            accum += sqrtFct(value+coveredPhonemes[key]) - sqrtFct(coveredPhonemes[key])
        return accum

    def _loop(self, item_pool, scoring_fct, duration_itemgetter, batch_size_seconds):
        accum_time = 0.0
        while accum_time < batch_size_seconds:


    def compute_scores(self, item_pool, scoring_fct, duration_itemgetter, batch_size_seconds):
        self._loop(item_pool, scoring_fct, duration_itemgetter, batch_size_seconds)


