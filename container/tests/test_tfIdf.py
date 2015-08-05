from unittest import TestCase
from asrActiveLearning.container.adapter import TfIdf
from collections import Counter
__author__ = 'martin'

class RecordStub(object):
    def __init__(self, item_counter):
        self.item_counter = item_counter

class TestTfIdf(TestCase):
    def setUp(self):
        self.rec1 = RecordStub(Counter({"a": 1, "b": 2, "c": 3}))
        self.rec2 = RecordStub(Counter({"b": 5}))
        self.container = {"one": self.rec1, "two": self.rec2}
        self.itemgetter_func = lambda x: x.item_counter
        self.tf_idf = TfIdf(self.container, self.itemgetter_func)

    def compute_expected_idf_dict(self):
        expected_idf_dict = Counter(set(self.rec1.item_counter))
        expected_idf_dict.update(set(self.rec2.item_counter))
        return expected_idf_dict

    def test_refresh(self):
        self.tf_idf.refresh()
        expected_idf_dict = self.compute_expected_idf_dict()
        self.assertDictEqual(self.tf_idf.idf_dict, expected_idf_dict)

    def test__collect_idf(self):
        expected_idf_dict = self.compute_expected_idf_dict()
        counter_dict_list = [self.rec1.item_counter, self.rec2.item_counter]
        self.assertDictEqual(self.tf_idf.idf_dict, expected_idf_dict)

    def compute_tf_idf(self, counter_dict, idf_dict):
        import math
        num_items = 2
        return Counter({key: (1+math.log10(tf_val)) * (math.log10(float(num_items)/float((1 + idf_dict[key]))))
                        for key, tf_val in counter_dict.iteritems()})

    def test__tf_idf_multiply(self):
        idf_dict = self.compute_expected_idf_dict()
        tf_idf_rec1_expected = self.compute_tf_idf(self.rec1.item_counter, idf_dict)
        tf_idf_rec2_expected = self.compute_tf_idf(self.rec2.item_counter, idf_dict)
        print tf_idf_rec2_expected
        self.assertDictEqual(tf_idf_rec1_expected, self.tf_idf["one"])
        self.assertDictEqual(tf_idf_rec2_expected, self.tf_idf["two"])
