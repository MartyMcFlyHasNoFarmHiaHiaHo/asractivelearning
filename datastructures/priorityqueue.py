from activeLearning.logs import log, debug, warn
import heapq
import bisect
import sortedcontainers
from activeLearning.tools.decorators import do_profile

class HeapList(list):
    '''just a list but with an insort (insert into sorted position)'''
    # def insort(self,x):
    #         self=bisect.insort(self, x)

    def push(self, item):
        heapq.heappush(self, item)


class SortedList(list):
    '''just a list but with an insort (insert into sorted position)'''
    def insort(self,x):
            self=bisect.insort(self, x)

class MetaDataList(list):
    def __init__(self, binValue, *args, **kwds):
        super(MetaDataList, self).__init__(*args, **kwds)
        self.binValue = binValue

    def __cmp__(self, other):
        if self.binValue < other.binValue:
            return -1
        elif self.binValue > other.binValue:
            return 1
        else:
            return 0

    def insort(self,x):
            self=bisect.insort(self, x)

# class bucketQueue(object):
#     def __init__(self, precision=4, tuningCycle=1000):
#         # self._binValList = sortedlist()
#         # self._valBinPtrDict = {}
#         # self._itemValBinDict = {}
#         self._heap = HeapList()
#         self._itemToSetDict = {}
#         self._valToSetDict = {}
#         self._precision = precision
#         self._tuningCycle = tuningCycle
#         self._count = 0
#
#     def __str__(self):
#         string = "Bucket Queue\n--------------\n\n"
#         string = "{0}Word Count: {1}\nRounding precision: {2}\n\
#             Number of values {3}".format(string, self._count, self._precision, \
#                                          len(self._binValList))
#         return string
#
#     def getTopElementsString(self, n):
#         items = self.getTopElements(n)
#         string = "Bucket Queue {0} Top Elements\n".format(n)
#         string = "{0}---ID --- || ---RATIO--- \n".format(string)
#         for word, value in items:
#             string = "{0}{1:52} | {2:<}\n".format(string, word.id, value)
#         return string
#
#     def getTopElements(self, n):
#         count = 0
#         items = []
#         for value in reversed(self._binValList):
#             bin = self._valBinPtrDict[value]
#             for element in bin:
#                 if count == n:
#                     return items
#                 items.append((element, value))
#                 count += 1
#         return items
#
#     def isItemValInQueue(self, item):
#         if item in self._itemValBinDict:
#             return True
#         else:
#             return False
#
#     def push(self, item, value):
#         value = round(value, self._precision)
#
#         try:
#             bin = self._itemToSetDict[item]
#             bin.remove(item)
#             if len(bin) == 0:
#                 del bin
#         except:
#             pass
#
#         try:
#             bin = self._valToSetDict[value]
#         except:
#             bin = MetaDataSet(value)
#             self._heap.push(bin)
#
#         bin.add(item)
#         self._itemToSetDict[item] = bin
#         self._count += 1
    # def push(self, item, value):
    #     value = round(value, self._precision)
    #     if self.isItemValInQueue(item):
    #         warn("(Item, Value) pair already in queue")
    #         return
    #
    #     if value in self._valBinPtrDict:
    #         bin = self._valBinPtrDict[value]
    #         bin.add(item)
    #     else:
    #         bin = MetaDataSet(value)
    #         bin.add(item)
    #         self._valBinPtrDict[value] = bin
    #         self._binValList.insort(value)
    #
    #     self._itemValBinDict[item] = bin
    #     self._count += 1
    #
    # def update(self, item, value):
    #     self._heap
    #     self.remove(item)
    #     self.push(item, value)
    #
    # def remove(self, item):
    #     # value = round(value, self._precision)
    #     if not self.isItemValInQueue(item):
    #         raise Exception("Item is not in queue!")
    #
    #     bin = self._itemValBinDict[item]
    #     bin.remove(item)
    #     value = bin.binValue
    #     del self._itemValBinDict[item]
    #
    #     if len(bin) == 0:
    #         del self._valBinPtrDict[value]
    #         self._binValList.remove(value)
    #
    #     self._count -= 1
    #
    # def max(self):
    #     if self._count > 0:
    #         maxVal = self._binValList[-1]
    #     else:
    #         maxVal = float("-inf")
    #     return maxVal
    #
    # def isEmpty(self):
    #     if self._count > 0:
    #         return False
    #     else:
    #         return True
    #
    # def pop(self):
    #     maxVal = self.max()
    #     bin = self._valBinPtrDict[maxVal]
    #     item = None
    #     for element in bin:
    #         item = element
    #         break
    #     self.remove(item)
    #     return item, maxVal


class MetaValueSet(set):
    def __init__(self, metaValue, *args, **kwds):
        super(MetaValueSet, self).__init__(*args, **kwds)
        self.metaValue = metaValue

    def __lt__(self, other):
        if  self.metaValue < other.metaValue:
            return True
        else:
            return False

class FastBucketQueue(object):
    def __init__(self, initIterable = None):
        self._bucketList = sortedcontainers.SortedList(iterable = initIterable)
        self._valToBucketMap = {}
        self._itemToBucketMap = {}
        self._count = 0

    def __len__(self):
        return self._count

    def __str__(self):
        print


    def push(self, item, val):
        if item in self._itemToBucketMap:
            raise Exception("Item already in Queue")
        try:
            bucketSet = self._valToBucketMap[val]
        except:
            bucketSet = MetaValueSet(val)
            self._valToBucketMap[val] = bucketSet
            self._bucketList.add(bucketSet)
        bucketSet.add(item)
        self._itemToBucketMap[item] = bucketSet
        self._count += 1


    def pop(self):
        if self._count == 0:
            raise Exception("No item in queue")
        maxBucketSet = self._bucketList[-1]
        val = maxBucketSet.metaValue
        item = maxBucketSet.pop()

        if len(maxBucketSet) == 0:
            del self._valToBucketMap[val]
            self._bucketList.pop()

        del self._itemToBucketMap[item]
        self._count -= 1
        return item, val


    def update(self, item, val):
        try:
            bucketSet = self._itemToBucketMap[item]
            bucketSet.remove(item)
        except:
            raise Exception("Item is not in Queue, cant update item")

        if len(bucketSet) == 0:
            del self._valToBucketMap[bucketSet.metaValue]
            self._bucketList.pop(self._bucketList.bisect_left(bucketSet))

        del self._itemToBucketMap[item]
        self._count -= 1
        self.push(item, val)


    def max(self):
        try:
            maxVal = self._bucketList[-1].metaValue
        except:
            maxVal = float("-inf")
        return maxVal

#
# class OldbucketQueue(object):
#     def __init__(self, precision=4):
#         self._valList = sortedlist()
#         self._valPointerDict = {}
#         self._pointerDict = {}
#         self._precision = precision
#         self._count = 0
#
#     def debugPrint(self):
#         for key, val in self._valPointerDict.iteritems():
#             print "\n--------\n Value {0}".format(key)
#             val.fwd_print()
#             print self._valList
#
#     def push(self, item, value):
#         if item in self._pointerDict:
#             warn("Item {0} already in queue".format(item))
#             return
#
#         val = round(value, self._precision)
#
#         if val in self._valPointerDict:
#             linkedList = self._valPointerDict[val]
#         else:
#             linkedList = DoubleLinkedList(val)
#             self._valPointerDict[val] = linkedList
#             self._valList.insort(val)
#
#         node = linkedList.insert(item)
#         self._pointerDict[item] = (node, linkedList)
#         self._count += 1
#
#     def remove(self, item):
#         if self._count < 1:
#             raise Exception("No items in queue")
#         if not item in self._pointerDict:
#             raise Exception ("Item not found")
#
#         node, linkedList = self._pointerDict[item]
#         node.remove()
#         self._pointerDict.pop(item)
#         del node
#         if linkedList.isEmpty():
#             self._valList.remove(linkedList.metaData)
#             self._valPointerDict.pop(linkedList.metaData)
#             del linkedList
#         self._count -= 1
#
#     def isEmpty(self):
#         if self._count < 1:
#             return True
#         else:
#             return False
#
#     def update(self, item, value):
#         if not item in self._pointerDict:
#             raise Exception ("Item not found")
#         self.remove(item)
#         self.push(item, value)
#
#
#     def pop(self):
#         if self._count < 1:
#             raise Exception("No items in queue")
#
#         maxVal, linkedList = self.getMaxBin()
#         node = linkedList.tail
#         item = node.data
#         self.remove(item)
#         return item, maxVal
#
#     def max(self):
#         if self._count < 1:
#             maxVal = int("-inf")
#         else:
#             print self._count
#             maxVal, linkedList = self.getMaxBin()
#         return maxVal
#
#     def getMaxBin(self):
#         if self._count < 1:
#             raise Exception("No items in queue")
#         maxVal = self._valList[-1]
#         return maxVal, self._valPointerDict[maxVal]
