import intervaltree

__author__ = 'martin'


class IntervalBookKeeper(intervaltree.IntervalTree):

    @staticmethod
    def compute_overlap(interval1, interval2):
        if interval1.begin < interval1.begin:
            low_interval = interval1
            high_interval = interval2
        else:
            low_interval = interval2
            high_interval = interval1
        return low_interval.end - high_interval.begin

    def get_interval_overlap(self, interval):
        overlapping_intervals = self.search(interval.begin, interval.end)
        overlap = sum(IntervalBookKeeper.compute_overlap(interval, overlap_interval)
                      for overlap_interval in overlapping_intervals)
        return overlap
