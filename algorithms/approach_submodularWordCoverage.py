from activeLearning.logs import log, debug, warn
from collections import Counter
# from types import FloatType
import numpy as np
# import scipy.sparse as sparse
import math
import heapq
import persistent

# Misc
from activeLearning.tools.decorators import Memoized

# AL imports
import activeLearning.tools.trainUserModels as trainUserModels
from activeLearning.tools.bucketPQ import FastBucketQueue


estimatedModel, noisyOracleModel = trainUserModels.getTrainedModels()

# class PriorityQueue(object):
#     def __init__(self):
#         self._queue = []
#         self._index = 0
#
#     def push(self, item, priority):
#         heapq.heappush(self._queue, (-priority, self._index, item))
#         self._index += 1
#
#     def pop(self):
#         if self.isEmpty():
#             raise Exception("Priority Queue is empty")
#         priority, index, item = heapq.heappop(self._queue)
#         priority = -priority
#     def isEmpty(self):
#         return len(self._queue) == 0
#
#     def __len__(self):
#         return len(self._queue)
#
#     def max(self):
#         if not self._queue:
#             return -np.inf
#         else:
#             return - self._queue[0][0]

class SubmodularWordCoverage(persistent.Persistent):
    def __init__(self, janusHelper, alConfig, wordController):
            self.janusHelper = janusHelper
            self.wordController = wordController
            self.alConfig = alConfig
            self._coveredPhonemes = None
            self._valueCoveredVectors = 0.0
            self.annotationCosts = 0.0
            self.noisyAnnotationCosts = 0.0

    # non decreasing monotone concave function g()
    def _funcG(self, tfIdfDict, coveredPhonemes):
        accum = 0.0
        # # Save repeated function-pointer reevaluation in loop
        sqrtFct = math.sqrt
        for key, value in tfIdfDict.viewitems():
            accum += sqrtFct(value+coveredPhonemes[key]) - sqrtFct(coveredPhonemes[key])
        return accum

    def isClose(self, a, b, rtol=1.e-5, atol=1.e-8, equal_nan=False):
        def within_tol(x, y, atol, rtol):
            with np.errstate(invalid='ignore'):
                result = np.less_equal(abs(x-y), atol + rtol * abs(y))
                if np.isscalar(a) and np.isscalar(b):
                    result = bool(result)
                    return result
                x = np.array(a, copy=False, subok=True, ndmin=1)
                y = np.array(b, copy=False, subok=True, ndmin=1)
                xfin = np.isfinite(x)
                yfin = np.isfinite(y)
                if all(xfin) and all(yfin):
                    return within_tol(x, y, atol, rtol)
                else:
                    finite = xfin & yfin
                    cond = np.zeros_like(finite, subok=True)
                    # Because we're using boolean indexing, x & y must be the
                    # same shape.
                    # Ideally, we'd just do x, y = broadcast_arrays(x, y). It's
                    # in
                    # lib.stride_tricks, though, so we can't import it
                    # here.SubmodularWordCoverageCostRatiox = x *
                    # ones_like(cond)
                    y = y * np.ones_like(cond)
                    # Avoid subtraction with infinite/nan values...
                    cond[finite] = within_tol(x[finite], y[finite], atol, rtol)
                    # Check for equality of infinite values...
                    cond[~finite] = (x[~finite] == y[~finite])
                    if equal_nan:
                        # Make NaN == NaN
                        both_nan = np.isnan(x) & np.isnan(y)
                        cond[both_nan] = both_nan[both_nan]
                        return cond

    # Compute submodular gain
    def _computeGain(self, adapter, cnWordIdx, coveredPhonemes, valueCoveredVectors):
        wordObj = adapter[cnWordIdx]

        if not wordObj._transcribed:
            gain = self._funcG(wordObj._tfIdfDict, coveredPhonemes)
        else:
            gain = 0.0

        return gain

    def _initGains(self, cnWordIterator, coveredPhonemes, valueCoveredVectors):
        gainDict = {}

        for adapter, cnWordIdx in cnWordIterator:
            gain = self._computeGain(adapter, cnWordIdx, coveredPhonemes, valueCoveredVectors)
            gainDict[(adapter, cnWordIdx)] = gain
        return gainDict

    @Memoized(capacity=50000)
    def _estimatedGPCosts(self, length, durationSec):
        return estimatedModel.score2(length, durationSec)

    @Memoized(capacity=50000)
    def _noisyGPCosts(self, length, durationSec):
        return noisyOracleModel.score2(length, durationSec)

    def _scoreFcnFast(self, numWords, durationSec):
        durationSec = round(durationSec, ndigits=2)
        return self._estimatedGPCosts(numWords, durationSec)

    def _scoreFcnFastNoisy(self, numWords, durationSec):
        durationSec = round(durationSec, ndigits=2)
        return self._noisyGPCosts(numWords, durationSec)


    def _mainLoop(self, wordController, batchSizeSec):
        assert(batchSizeSec > 0.0)

        valueCoveredVectors = self._valueCoveredVectors

        # Init coveredPhonemes
        if self._coveredPhonemes is not None:
            coveredPhonemes = self._coveredPhonemes.copy()
        else:
            coveredPhonemes = Counter()
            # coveredPhonemes = sparse.csc_matrix((1, self.wordController._numPhonemes))


        # Prepare datastructures
        log("Computing submodular gains")
        candidateList = []
        gainDict = self._initGains(wordController, coveredPhonemes, valueCoveredVectors)
        gainQueue = FastBucketQueue()
        checkedCnWordSet = set()
        for (adapter, cnWordIdx), gain in gainDict.iteritems():
            cnWord = adapter[cnWordIdx]
            if not cnWord._marked and not cnWord._transcribed and not cnWord.ignore:
                gainQueue.push((adapter, cnWordIdx), gain)

        i = 0
        accumTime = 0.0
        log('Number of marked words: {0}, -> {1} percent marked'.format(self.wordController.getNumMarkedWords(),\
                                                                        self.wordController.getNumMarkedWords() / self.wordController.getNumWords() ))
        reportAfterSamples = 10000
        while len(gainQueue) > 0 and accumTime < batchSizeSec:

            # Get top element from list and add to selected set
            (adapter, cnWordIdx), candidateGain = gainQueue.pop()
            candidateCnWord = adapter[cnWordIdx]

            # Update Gain, ratio, cost
            # if candidateCnWord not in checkedCnWordSet:
            candidateGain = self._computeGain(adapter, cnWordIdx, coveredPhonemes, valueCoveredVectors)
            # print("\n\nIteration {0}, word: {1}\nGain: {2}, Costs: {3}, Ratio: {4}, Frames: {5}".format(i, candidateCnWord.id, candidateGain, costs, candidateRatio, candidateCnWord.duration))
            # assert(candidateGain >= 0), "Gain must be non-negative in order to be submodular"

            # print "Queue.max(): {0}".format(gainQueue.max())
            if candidateCnWord in checkedCnWordSet or candidateGain >= gainQueue.max():
                # print("--> Selected!")
                candidateList.append((adapter, cnWordIdx))
                candidateAdapter = adapter
                wordPos = cnWordIdx
                candidateAdapter.assignWordToSegment(wordPos)
                # coveredPhonemes.update(candidateCnWord._tfIdfDict)
                coveredPhonemes += candidateCnWord._tfIdfDict
                valueCoveredVectors += candidateGain
                checkedCnWordSet.clear()
                candidateCnWord._marked = True
                accumTime += candidateCnWord.durationSec
                candidateCnWord.utility = candidateGain
                # candidateCnWord._score = i

                # # Update gain neighbor words
                # leftSeg, rightSeg = candidateAdapter.getNeighborSegments(wordPos)
                # if leftSeg is None and wordPos > 0:
                #     leftWord = candidateAdapter[wordPos-1]
                #     neighGain, neighRatio, neighCosts = self._computeRatioGain(leftWord, coveredPhonemes, valueCoveredVectors)
                #     gainQueue.update(leftWord, neighRatio)
                #     # print("--> word: {1}\nGain: {2}, Costs: {3}, Ratio: {4}, Frames: {5}"\
                #           # .format(i, leftWord.id, neighGain, neighCosts, neighRatio, leftWord.duration))
                #
                # if rightSeg is None and wordPos < candidateAdapter.getNumWords()-1:
                #     rightWord = candidateAdapter[wordPos+1]
                #     neighGain, neighRatio, neighCosts = self._computeRatioGain(rightWord, coveredPhonemes, valueCoveredVectors)
                #     gainQueue.update(rightWord, neighRatio)
                #     # print("--> word: {1}\nGain: {2}, Costs: {3}, Ratio: {4}, Frames: {5}"\
                #           # .format(i, rightWord.id, neighGain, neighCosts, neighRatio, rightWord.duration))
                # TODO remove
                i += 1
                # print candidateAdapter.visualizeSegments()

                if i%reportAfterSamples == 0:
                    log('Number of marked words: {0}, -> {1} percent marked'.format(i, float(i) / float(self.wordController.getNumWords()) ))

            else:
                # print("--> Refused!")
                gainQueue.push((adapter, cnWordIdx), candidateGain)
                checkedCnWordSet.add(candidateCnWord)

            if len(gainQueue) <= 10:
                debug("Priority queue has only {0} elements left".format(len(gainQueue)))

        log("Sampled {0} hours of words".format(accumTime/3600.0))

        return candidateList, coveredPhonemes, valueCoveredVectors

    def getScores(self, wordController=None, batchSizeSec=None):
        log('Approach submodular sentence/utterance coverage (tf-idf vector based): calculating scores')


        if batchSizeSec is None:
            batchSizeSec = float("inf")

        if wordController:
            self.wordController = wordController

        log('Number of words: {0}'.format(self.wordController.getNumWords()))


        # outsourced to make it accessible for unit testing
        candidateList, coveredPhonemes, valueCoveredVectors = self._mainLoop(self.wordController, batchSizeSec)

        # Save scores
        for i, (adapter, cnWordIdx) in enumerate(candidateList):
            #print key
            cnWord = adapter[cnWordIdx]
            cnWord._score = float(i)

        # Set instance variables after everything else has been done
        # to ensure consistency that if an error occurs and the iteration is restarted
        # no left-overs of the last iterations are contained in coveredPhonemes
        # or valueCoveredVectors.
        self._coveredPhonemes = coveredPhonemes
        self._valueCoveredVectors = valueCoveredVectors

        # Get estimated annotation time information
        # from activeLearning.tools.contextManagers import DebugLogging
        self.annotationCosts = 0.0
        self.annotationCostsWithoutSupervised = 0.0
        # with DebugLogging("{0}.visualization".format(self.alConfig.logFile)):
        #     for key, adapter in self.wordController.confusionNetworkAdapters.iteritems():
        #         debug("\n{0}".format(adapter.visualizeSegments()))

        for key, adapter in self.wordController.confusionNetworkAdapters.iteritems():
            # Visualize Costs
            for segment in adapter.getSegmentIterator():
                costs = self._scoreFcnFast(len(segment), segment.durationSec)
                # debug("\n{0} segment, costs {1}".format(segment, costs))
                self.annotationCostsWithoutSupervised += costs

        for key, adapter in self.wordController.confusionNetworkAdapters.iteritems():
            # Visualize Costs
            for subSeg in adapter.getMarkedAndSupervisedSegments():
                subSegDuration = sum(x.durationSec for x in subSeg)
                costs = self._scoreFcnFast(len(subSeg), subSegDuration)
                # debug("\n{0} segment, costs {1}".format(segment, costs))
                self.annotationCosts+= costs

        # Clear Cost-Model cache
        self._estimatedGPCosts.clear()

        # Get noisy annotation time information
        self.noisyAnnotationCosts = 0.0
        self.noisyAnnotationCostsWithoutSupervised = 0.0
        for key, adapter in self.wordController.confusionNetworkAdapters.iteritems():
            for segment in adapter.getSegmentIterator():
                costs = self._scoreFcnFastNoisy(len(segment), segment.durationSec)
                self.noisyAnnotationCostsWithoutSupervised += costs

        for key, adapter in self.wordController.confusionNetworkAdapters.iteritems():
            # Visualize Costs
            for subSeg in adapter.getMarkedAndSupervisedSegments():
                subSegDuration = sum(x.durationSec for x in subSeg)
                costs = self._scoreFcnFastNoisy(len(subSeg), subSegDuration)
                # debug("\n{0} segment, costs {1}".format(segment, costs))
                self.noisyAnnotationCosts += costs
        # Clear Cost-Model cache
        self._noisyGPCosts.clear()

        return candidateList

    def iterationReport(self, iteration, logger, storagePath):
        from activeLearning.tools.segmentStatistics import logMergingStatistics
        from activeLearning.tools.segmentStatistics import logSegmentStatistics
        import os
        logger.info("Costs based on whole segments (including already supervised words:")
        logger.info("Estimated annotation costs (hrs): {0}".format(float(self.annotationCosts)/3600.0))
        logger.info("Noisy annotation costs (hrs): {0}".format(float(self.noisyAnnotationCosts)/3600.0))
        logger.info("Costs based only on currently choosen words:")
        logger.info("Estimated annotation costs (hrs): {0}".format(float(self.annotationCostsWithoutSupervised)/3600.0))
        logger.info("Noisy annotation costs (hrs): {0}".format(float(self.noisyAnnotationCostsWithoutSupervised)/3600.0))
        logger.info("Covered Phonemes:\n{0}\n\n".format(self._coveredPhonemes))
        ## More information:
        # How many single sided segment extensions?
        # How many merges?
        # How many new segments?
        logMergingStatistics(logger, self.wordController)
        logSegmentStatistics(logger, self.wordController, os.path.join(storagePath, "segmentStatistics_iteration{0}.txt".format(iteration)))


def samplingObjectFactory(janusHelper, alConfig, wordController):
    return SubmodularWordCoverage(janusHelper, alConfig, wordController)
