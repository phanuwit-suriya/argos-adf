import naive_dd as ndd

#Unnecessary
import csv
import numpy as np
from matplotlib import pyplot as plt

class DiscordDiscovery:

    defaultWindowStep = 1
    defaultSAXword    = 8

    class Param:
        def __init__(self):
            self.minWindowSize = 16

    class Param_gpu:
        def __init__(self):
            self.data = None
            self.knowledgeWindowSize = 0
            self.windowStep = 1
            self.minWindowSize = 16

    class DiscordRange:
        def __init__(self, startIndex, endIndex):
            self.startIndex = startIndex
            self.endIndex   = endIndex

    def __init__(self, param):
#        TODO: move this to each local method
#        if (param.__class__ != DiscordDiscovery.Param):
#            raise Exception()

        self.param = param
        return

    def NaiveDiscoveryImpl(self, data, windowSize, windowStep, saxWord, impl=0, threads=1):

        if (not (threads > 1)):
            return ndd.HS_NaiveDetect(data, windowSize, windowStep, saxWord)
        else:
            return ndd.HS_NaiveDetect_mt(data, windowSize, windowStep, saxWord, threads)

    def NaiveDiscovery(self, data, threads=1):
        rangeList = []
        knowledgeWindowSize = len(data)
        windowSize          = self.param.minWindowSize
        knowledgeRatio = knowledgeWindowSize / windowSize
        k = 0
        while (knowledgeRatio >= 10):
            indices = self.NaiveDiscoveryImpl(\
                data, windowSize, DiscordDiscovery.defaultWindowStep, DiscordDiscovery.defaultSAXword, threads=threads)
            start_index = int(indices[0])
            end_index = int(indices[1])
            rangeList.append([start_index, end_index])
            windowSize += self.param.minWindowSize
            knowledgeRatio = knowledgeWindowSize / windowSize
            k += 1

        rangeSize     = len(rangeList)
        left_bd       = rangeList[rangeSize - 1][0]
        right_bd      = rangeList[rangeSize - 1][1]
        left_largest  = left_bd
        right_largest = right_bd
        alarm = True
        for i in range(rangeSize - 1, -1, -1):
            left_test = rangeList[i][0]
            right_test = rangeList[i][1]
            if ((left_bd <= right_test) and (right_bd >= left_test)):
                if (left_bd < left_test): left_bd = left_test
                if (right_bd > right_test): right_bd = right_test
            else:
                alarm = False

        if (alarm == True):
            return DiscordDiscovery.DiscordRange(left_largest, right_largest)

        return None

    def NaiveDiscovery_SingleFrame(self, data, useGPU=False, numThreads=8):

        if (self.param.__class__ !=  DiscordDiscovery.Param_gpu):
            raise Exception()

        if (len(data) > self.param.knowledgeWindowSize):
            raise Exception()

        if (useGPU):
            startIndices, stopIndices =         \
                ndd.HS_NaiveDetect_gpu(         \
                data,                           \
                self.param.knowledgeWindowSize, \
                self.param.windowStep,          \
                self.param.minWindowSize)
        else:
            startIndices, stopIndices =         \
                ndd.HS_NaiveDetect_cpu(         \
                data,                           \
                self.param.knowledgeWindowSize, \
                self.param.windowStep,          \
                self.param.minWindowSize,       \
                numThreads)


        if (startIndices != None) and (stopIndices != None):
            if (len(startIndices) > 0):
                return DiscordDiscovery.DiscordRange(startIndices[0], stopIndices[0])
        return None

    def NaiveDiscovery_MultiFrame(self, data, useGPU=False, numThreads=8):
        if (self.param.__class__ !=  DiscordDiscovery.Param_gpu):
            raise Exception()

        if (useGPU):
            startIndices, stopIndices =         \
                ndd.HS_NaiveDetect_gpu(         \
                data,                           \
                self.param.knowledgeWindowSize, \
                self.param.windowStep,          \
                self.param.minWindowSize)
        else:
            startIndices, stopIndices =         \
                ndd.HS_NaiveDetect_cpu(         \
                data,                           \
                self.param.knowledgeWindowSize, \
                self.param.windowStep,          \
                self.param.minWindowSize,       \
                numThreads)

        if (len(startIndices) != len(stopIndices)):
            raise Exception()

        ddList = []
        for i in range(0, len(startIndices)):
            ddList.append(DiscordDiscovery.DiscordRange(startIndices[i], stopIndices[i]))

        return ddList
        

if __name__ == "__main__":
    #csvFile     = "../../feeder/1_tie_processing_time.csv"; lw = 800; step = 1; swin = 32
    csvFile     = "../../feeder/1_tie_processing_time.csv"; lw = 640; step = 20; swin = 32
    #csvFile     = "../../feeder/2_c152rab.csv"; lw = 1800; step = 100; swin = 90
    #csvFile     = "../../feeder/2_c152rab.csv"; lw = 1800; step = 100; swin = 180
    #csvFile     = "../../feeder/2_c152rab.csv"; lw = 800; step = 100; swin = 40
    #csvFile     = "../../feeder/2_c152rab.csv"; lw = 1500; step = 100; swin = 75

    fh = open(csvFile, "rt", encoding="utf8")
    csvReader = csv.reader(fh, delimiter=',')
    data = []
    for line in csvReader:
        if (line[3] == "None"):
            data.append(0.0)
        else:
            data.append(np.float32(line[3]))

    gddParam = DiscordDiscovery.Param_gpu()
    gddParam.data = data
    gddParam.knowledgeWindowSize = lw
    gddParam.windowStep = step
    gddParam.minWindowSize = swin

    dd = DiscordDiscovery(gddParam)
    #ddRange = dd.NaiveDiscovery_gpu(gddParam.data)

    #plt.figure()
    #plt.plot(data)
    #for i in range(0, len(r1)):
    #    start_index = ddRange.startIndex
    #    end_index = dd.Range.stopIndex
    #    plt.axvspan(start_index, end_index, facecolor='r', alpha=0.3)
    #    plt.axvline(start_index, color='r')
    #    plt.axvline(end_index, color='r')
    #plt.show()

    MULTIFRAMES = True
    SINGLEFRAME = False


    dList = []
    ########## MULTI-FRAME IMPLEMENTATION ##########
    if MULTIFRAMES:
        ddRange = dd.NaiveDiscovery_MultiFrame(data, useGPU=False)

        if (ddRange != None):
            for i in range(0, len(ddRange)):
                dList.append([ddRange[i].startIndex, ddRange[i].endIndex])
    ########## SINGLE-FRAME IMPLEMENTATION ##########
    elif SINGLEFRAME:
        for i in range(0, len(data)-lw, step):
            dataw = data[i:i + lw]
            ddRange = dd.NaiveDiscovery_SingleFrame(dataw, useGPU=False)

            if (ddRange != None):
                dList.append([ddRange.startIndex + i, ddRange.endIndex + i])
    ########## ORIGINAL IMPLEMENTATION ##########
    else:
        for i in range(0, len(data)-lw, step):
            dataw = data[i:i + lw]
            ddRange = dd.NaiveDiscovery(dataw, threads=1)

            if (ddRange != None):
                dList.append([ddRange.startIndex + i, ddRange.endIndex + i])


    plt.figure()
    plt.plot(data)
    for i in range(0, len(dList)):
        start_index = dList[i][0]
        end_index = dList[i][1]
        plt.axvspan(start_index, end_index, facecolor='r', alpha=0.3)
        plt.axvline(start_index, color='r')
        plt.axvline(end_index, color='r')
    plt.show()

"""if __name__ == "__main__":
    #csvFile     = "../../feeder/1_tie_processing_time.csv"; lw = 640; step = 20; swin = 16
    csvFile = "../../feeder/2_c152rab.csv"; lw = 1500; step = 200; swin = 64
    #csvFile = "../hs/2_c152rab.csv"; lw = 640; step = 20; swin = 16
    #csvFile = "../hs/test1.csv"; lw = 320; step = 10; swin = 16
    #csvFile = "../hs/test2.csv"; lw = 640; step = 20; swin = 16

    fh = open(csvFile, "rt", encoding="utf8")
    csvReader = csv.reader(fh, delimiter=',')
    data = []
    for line in csvReader:
        if (line[3] == "None"):
            data.append(0.0)
        else:
            data.append(np.float32(line[3]))

    ddParam = DiscordDiscovery.Param()
    ddParam.minWindowSize = swin
    dd = DiscordDiscovery(ddParam)
    dList = []
    for i in range(0, len(data)-lw, step):
        dataw = data[i:i + lw]
        ddRange = dd.NaiveDiscovery(dataw, threads=1)

        if (ddRange != None):
            dList.append([ddRange.startIndex + i, ddRange.endIndex + i])

    plt.figure()
    plt.plot(data)
    for i in range(0, len(dList)):
        start_index = dList[i][0]
        end_index = dList[i][1]
        plt.axvspan(start_index, end_index, facecolor='r', alpha=0.3)
        plt.axvline(start_index, color='r')
        plt.axvline(end_index, color='r')
    plt.show()"""
