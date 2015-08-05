__author__ = 'martin'
from collections import Counter
import itertools


# TODO:
# Improve efficiency of this class by first counting number of DISTINCT(!) items from the container object
# and then compute tf and idf updates for each item-class just once but repeating the update with the number of
# item occurances
class TfIdf(object):
    def __init__(self, container, itemgetter_func):
        """
        :param container: any iterable that supports indexing
        :param itemgetter_func: function that takes an element of the container as input and returns a
        collections.Counter dictionary containing a set of elements and their counts.
        """
        self.container = container
        self.itemgetter_func = itemgetter_func
        self.tf_idf_dicts = {}
        self.idf_dict = Counter()
        self.refresh()

    def __getitem__(self, item):
        try:
            return self.tf_idf_dicts[item]
        except KeyError:
            tf_idf = self._tf_idf_multiply(item)
            self.tf_idf_dicts[item] = tf_idf
            return tf_idf

    def refresh(self):
        counter_dict_gen = (self.itemgetter_func(item) for (key, item) in self.container.iteritems())
        self._collect_idf(counter_dict_gen)

    def _collect_idf(self, counter_dict_list):
        self.idf_dict.clear()
        # Creating temporary sets is not very efficient
        for counter_dict in counter_dict_list:
            item_set = set(counter_dict)
            self.idf_dict.update(item_set)

    def _tf_idf_multiply(self, item):
        import math
        num_items = len(self.container)
        tf = self.itemgetter_func(self.container[item])
        return Counter({key: (1+math.log10(tf_val)) * (math.log10(float(num_items)/float((1 + self.idf_dict[key]))))
                        for key, tf_val in tf.iteritems()})




