import math
import persistent
from collections import Counter

# Misc
from activeLearning.tools.decorators import Memoized
from activeLearning.logs import log, debug, warn
import numpy as np

# AL imports
import activeLearning.tools.trainUserModels as trainUserModels
from activeLearning.tools.bucketPQ import FastBucketQueue


estimatedModel, noisyOracleModel = trainUserModels.getTrainedModels()

class SubmodularWordCoverageCostRatio(persistent.Persistent):
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

    def _computeRatioGain(self, adapter, cnWordIdx, coveredPhonemes, valueCoveredVectors):
        # if wordObj.id == "BABEL_BP_107_74986_20120416_011927_inLine@314.01,6":
        #     import ipdb; ipdb.set_trace()  # XXX BREAKPOINT

        # Catch useless crap
        # if wordObj.duration <= 0:
        #     return 0.0, -1.0, 0.0
        wordObj = adapter[cnWordIdx]
       

        if not wordObj._transcribed:
            gain = self._funcG(wordObj._tfIdfDict, coveredPhonemes) 

            # gain -= valueCoveredVectors
            gain2 = gain

            if self.isClose(gain, 0, rtol=1e-05, atol=1e-05, equal_nan=False):
                gain2 = np.finfo(np.float32).eps
        else:
            gain2 = np.finfo(np.float32).eps

        # Costs of word with respect to possible context
        # This costs are negative if there is a reduction
        costs = self._userModel(adapter, cnWordIdx)


        # Reduced word costs [ wordCosts - reduction ]
        if costs <= 0:
            # ratio = float("inf")
            ratio = gain2 * (-costs)
        else:
            ratio = gain2 / costs


        # print wordObj
        # print "Gain: {0}, Costs: {1}, Ratio {2}".format(gainOfVector, costs, gain)
        return gain2, ratio, costs 

    def _initGains(self, cnWordIterator, coveredPhonemes, valueCoveredVectors):
        gainDict = {}

        for adapter, cnWordIdx in cnWordIterator:
            gain, ratio, costs = self._computeRatioGain(adapter, cnWordIdx, coveredPhonemes, valueCoveredVectors)
            gainDict[(adapter, cnWordIdx)] = ratio
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

    def _userModel(self, adapter, cnWordIdx):
        wordObj = adapter[cnWordIdx]

        # def _linearModel(wordSeq, start, stop):
        #     costs = 0.0
        #     for word in wordSeq:
        #         costs += word.durationSec
        #     return costs

        def _assembleUserModelCosts(adapter, cnWordIdx, scoreFcn):
            leftSeg, rightSeg = adapter.getNeighborSegments(cnWordIdx)
            wordObj = adapter[cnWordIdx]

            if leftSeg == rightSeg and leftSeg is not None:
                #TODO
                costs = scoreFcn(len(leftSeg), leftSeg.durationSec)
                # debug("This should not happen! Costs {0}".format(costs))
            elif leftSeg is not None and rightSeg is not None:
                costsLeft = scoreFcn(len(leftSeg), leftSeg.durationSec)
                costsRight = scoreFcn(len(rightSeg), rightSeg.durationSec)
                costsWhole = scoreFcn(len(leftSeg)+len(rightSeg)+1,\
                                      leftSeg.durationSec  + \
                                      rightSeg.durationSec + \
                                      wordObj.durationSec)
                costs = costsWhole - (costsLeft + costsRight )
                # debug("Merge costs {0}".format(costs))
            elif leftSeg is not None:
                costsLeft = scoreFcn(len(leftSeg), leftSeg.durationSec)
                costsWhole = scoreFcn(len(leftSeg)+1, leftSeg.durationSec\
                                      + wordObj.durationSec)
                costs = costsWhole - (costsLeft )
                # debug("Left segment costs {0}".format(costs))
            elif rightSeg is not None:
                costsRight = scoreFcn(len(rightSeg), rightSeg.durationSec)
                costsWhole = scoreFcn(len(rightSeg)+1, rightSeg.durationSec\
                                      + wordObj.durationSec)
                costs = costsWhole - (costsRight )
                # debug("Right segment cost {0}".format(costs))
            else:
                costs = scoreFcn(1, wordObj.durationSec)
                
            return costs

        try:
            # costs = _assembleUserModelCosts(wordObj, self._estimatedModel.score)
            # costs = _assembleUserModelCosts(wordObj, self._scoreFcnMemoizeWrapper)
            costs = _assembleUserModelCosts(adapter, cnWordIdx, self._scoreFcnFast)
        except Exception as e:
            debug("Error at word in utterance {0}".format(wordObj.id))
            debug(e)
            raise
        # costs = _assembleUserModelCosts(wordObj, _linearModel)
        return costs


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
        for (adapter, cnWordIdx), ratio in gainDict.iteritems():
            cnWord = adapter[cnWordIdx]
            if not cnWord._marked and not cnWord._transcribed and not cnWord.ignore:
                gainQueue.push((adapter, cnWordIdx), ratio)

        i = 0
        accumTime = 0.0
        accumTimeFrameDurations = 0.0
        try:
            log('Number of marked words: {0}, -> {1} percent marked'.format(self.wordController.getNumMarkedWords(),\
                                                                        self.wordController.getNumMarkedWords() / self.wordController.getNumWords() ))
        except:
            import ipdb; ipdb.set_trace()
        reportAfterSamples = 10000
        while len(gainQueue) > 0 and accumTime < batchSizeSec:

            # Get top element from list and add to selected set
            (adapter, cnWordIdx), candidateRatio = gainQueue.pop()
            candidateCnWord = adapter[cnWordIdx]

            # Update Gain, ratio, cost
            # if candidateCnWord not in checkedCnWordSet:
            candidateGain, candidateRatio, costs = self._computeRatioGain(adapter, cnWordIdx, coveredPhonemes, valueCoveredVectors)
            # debug("Costs: {0}".format(costs))
            # print("\n\nIteration {0}, word: {1}\nGain: {2}, Costs: {3}, Ratio: {4}, Frames: {5}".format(i, candidateCnWord.id, candidateGain, costs, candidateRatio, candidateCnWord.duration))
            # assert(candidateGain >= 0), "Gain must be non-negative in order to be submodular"

            # print "Queue.max(): {0}".format(gainQueue.max())
            if candidateCnWord in checkedCnWordSet or candidateRatio >= gainQueue.max():
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

                # Cost-insensitive way to compute accumTime
                #accumTime += candidateCnWord.durationSec
                accumTimeFrameDurations += candidateCnWord.durationSec

                # Cost-sensitive way to compute accumTime (inaccurate because costs can be lowered through forming segments)
                accumTime += costs
                candidateCnWord.cost = costs
                candidateCnWord.utility = candidateGain
                candidateCnWord.ratio = candidateRatio
                candidateCnWord._score = i

               


                # Update gain neighbor words
                leftSeg, rightSeg = candidateAdapter.getNeighborSegments(wordPos)
                # if leftSeg is None and wordPos > 0:
                if wordPos > 0 and not candidateAdapter[wordPos-1]._marked and not candidateAdapter[wordPos-1].ignore:
                    try:
                        neighGain, neighRatio, neighCosts = self._computeRatioGain(adapter, wordPos-1, coveredPhonemes, valueCoveredVectors)
                        gainQueue.update((adapter, wordPos-1), neighRatio)
                        adapter[wordPos-1].cost = neighCosts
                        adapter[wordPos-1].utility = neighGain
                        adapter[wordPos-1].ratio = neighRatio
                    except:
                        warn(("Adapter {0} wordpos {1}".format(adapter.cnId, wordPos)))
                        warn(adapter.visualizeWordsChain())
                        warn(adapter.visualizeSegments())
                        raise
                    # print("--> word: {1}\nGain: {2}, Costs: {3}, Ratio: {4}, Frames: {5}"\
                          # .format(i, leftWord.id, neighGain, neighCosts, neighRatio, leftWord.duration))

                # if rightSeg is None and wordPos < candidateAdapter.getNumWords()-1:
                if wordPos < candidateAdapter.getNumWords()-1 and not candidateAdapter[wordPos+1]._marked and not candidateAdapter[wordPos+1].ignore:
                    neighGain, neighRatio, neighCosts = self._computeRatioGain(adapter, wordPos+1, coveredPhonemes, valueCoveredVectors)
                    gainQueue.update((adapter, wordPos+1), neighRatio)
                    adapter[wordPos+1].cost = neighCosts
                    adapter[wordPos+1].utility = neighGain
                    adapter[wordPos+1].ratio = neighRatio
                    # print("--> word: {1}\nGain: {2}, Costs: {3}, Ratio: {4}, Frames: {5}"\
                          # .format(i, rightWord.id, neighGain, neighCosts, neighRatio, rightWord.duration))
                i += 1
                # print candidateAdapter.visualizeSegments()


                # # TODO Remove
                # for adapter, idx in candidateAdapter:
                #     newGain, newRatio, newCosts = self._computeRatioGain(adapter, idx, coveredPhonemes, valueCoveredVectors)
                #     adapter[idx].cost = newCosts
                #     adapter[idx].utility = newGain 
                #     adapter[idx].ratio = newRatio

                # TODO REMOVE
                # debug("\n{0}".format(adapter.visualizeSegments().encode('utf-8')))
                # debug("\nCandidate: \nRatio {0}\nUtility {1}\nCosts {2}".format(candidateRatio, candidateGain, costs))
                # TODO remove
                # import ipdb; ipdb.set_trace()

                if i%reportAfterSamples == 0:
                    log('Number of marked words: {0}, -> {1} percent marked'.format(i, float(i) / float(self.wordController.getNumWords()) ))

            else:
                # print("--> Refused!")
                gainQueue.push((adapter, cnWordIdx), candidateRatio)
                checkedCnWordSet.add(candidateCnWord)

            if len(gainQueue) <= 10:
                debug("Priority queue has only {0} elements left".format(len(gainQueue)))

        log("Sampled {0} hours of words \
                (annotation cost model roughly predicts {0} hours of annotation)".format(accumTimeFrameDurations/3600.0, accumTime))


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

                # print segment
                # print segment.durationSec
                # print len(segment)
                costs = self._scoreFcnFast(len(segment), segment.durationSec)
                # debug("\n{0} segment, costs {1}".format(segment, costs))
                self.annotationCostsWithoutSupervised += costs

        for key, adapter in self.wordController.confusionNetworkAdapters.iteritems():
            # Visualize Costs
            for subSeg in adapter.getMarkedAndSupervisedSegments():
                # print "\nSubseg:"
                # for word in subSeg:
                #     print word
                subSegDuration = sum(x.durationSec for x in subSeg)
                # print subSegDuration
                # print len(subSeg)
                costs = self._scoreFcnFast(len(subSeg), subSegDuration)
                # debug("\n{0} segment, costs {1}".format(segment, costs))
                self.annotationCosts += costs

        # Clear Cost-Model cache
        self._estimatedGPCosts.clear()

        # Get noisy annotation time information
        self.noisyAnnotationCosts = 0.0
        self.noisyAnnotationCostsWithoutSupervised = 0.0
        for key, adapter in self.wordController.confusionNetworkAdapters.iteritems():
            # Visualize Costs
            for subSeg in adapter.getMarkedAndSupervisedSegments():
                # print "\nSubseg:"
                # for word in subSeg:
                #     print word
                subSegDuration = sum(x.durationSec for x in subSeg)
                # print subSegDuration
                # print len(subSeg)
                subSegDuration = sum(x.durationSec for x in subSeg)
                costs = self._scoreFcnFastNoisy(len(subSeg), subSegDuration)
                # debug("\n{0} segment, costs {1}".format(segment, costs))
                self.noisyAnnotationCosts += costs

        for key, adapter in self.wordController.confusionNetworkAdapters.iteritems():
            for segment in adapter.getSegmentIterator():
                costs = self._scoreFcnFastNoisy(len(segment), segment.durationSec)
                self.noisyAnnotationCostsWithoutSupervised += costs


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
    return SubmodularWordCoverageCostRatio(janusHelper, alConfig, wordController)
