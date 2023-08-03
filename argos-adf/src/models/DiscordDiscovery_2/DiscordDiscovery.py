import dd as ndd

#Unnecessary
import csv
import numpy as np
from matplotlib import pyplot as plt

class DiscordDiscovery:

    class Param:
        def __init__(self):
            self.minSubWindowSize = 16

    class Param_gpu:
        def __init__(self):
            self.data = None
            self.knowledgeWindowSize = 0
            self.windowStep = 1
            self.minSubWindowSize = 16
            self.detectionFocus = 0

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

    def NaiveDiscovery_SingleFrame(self, data, useGPU=False, numThreads=8):

        if (self.param.__class__ !=  DiscordDiscovery.Param_gpu):
            raise Exception()

        if (len(data) > self.param.knowledgeWindowSize):
            raise Exception()

        if (useGPU):
            startIndices, stopIndices, fStartIndices, fStopIndices = \
                ndd.dd_gpu(                     \
                data,                           \
                self.param.knowledgeWindowSize, \
                self.param.windowStep,          \
                self.param.minSubWindowSize,    \
                self.param.detectionFocus)
        else:
            startIndices, stopIndices, fStartIndices, fStopIndices = \
                ndd.dd_cpu(                     \
                data,                           \
                self.param.knowledgeWindowSize, \
                self.param.windowStep,          \
                self.param.minSubWindowSize,    \
                self.param.detectionFocus,      \
                numThreads)


        if (startIndices != None) and (stopIndices != None):
            if (len(startIndices) > 0):
                for i in range(0, len(startIndices)):
                    if (stopIndices[i] > fStopIndices[i] - (0.3*(fStopIndices[i] - fStartIndices[i]))):
                        return DiscordDiscovery.DiscordRange(startIndices[i], stopIndices[i])
        return None

    def NaiveDiscovery_MultiFrame(self, data, useGPU=False, numThreads=8):
        if (self.param.__class__ !=  DiscordDiscovery.Param_gpu):
            raise Exception()

        if (useGPU):
            startIndices, stopIndices, fStartIndices, fStopIndices = \
                ndd.dd_gpu(                     \
                data,                           \
                self.param.knowledgeWindowSize, \
                self.param.windowStep,          \
                self.param.minSubWindowSize,    \
                self.param.detectionFocus)
        else:
            startIndices, stopIndices, fStartIndices, fStopIndices = \
                ndd.dd_cpu(                     \
                data,                           \
                self.param.knowledgeWindowSize, \
                self.param.windowStep,          \
                self.param.minSubWindowSize,    \
                self.param.detectionFocus,      \
                numThreads)

        if (len(startIndices) != len(stopIndices)):
            raise Exception()

        ddList = []
        lastAnomalyStopIndex = -1
        for i in range(0, len(startIndices)):
            #if (stopIndices[i] > fStopIndices[i] - (self.param.minSubWindowSize)):
            if (stopIndices[i] > fStopIndices[i] - (0.3*(fStopIndices[i] - fStartIndices[i]))):
                if (startIndices[i] > lastAnomalyStopIndex):
                    lastAnomalyStopIndex = stopIndices[i]
                    ddList.append(DiscordDiscovery.DiscordRange(startIndices[i], stopIndices[i]))

        return ddList
        

if __name__ == "__main__":
    #csvFile     = "../../feeder/1_tie_processing_time.csv"; lw = 800; step = 1; swin = 32
    #csvFile     = "../../feeder/1_tie_processing_time.csv"; lw = 640; step = 20; swin = 32
    csvFile     = "../../feeder/1_tie_processing_time.csv"; lw = 640; step = 20; swin = 64
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
    gddParam.minSubWindowSize = swin
    gddParam.detectionFocus = 0

    dd = DiscordDiscovery(gddParam)

    MULTIFRAMES = False
    SINGLEFRAME = True


    dList = []
    ########## MULTI-FRAME IMPLEMENTATION ##########
    if MULTIFRAMES:
        ddRange = dd.NaiveDiscovery_MultiFrame(data, useGPU=False, numThreads=8)

        if (ddRange != None):
            for i in range(0, len(ddRange)):
                dList.append([ddRange[i].startIndex, ddRange[i].endIndex])
    ########## SINGLE-FRAME IMPLEMENTATION ##########
    elif SINGLEFRAME:
        for i in range(0, len(data)-lw, step):
            dataw = data[i:i + lw]
            ddRange = dd.NaiveDiscovery_SingleFrame(dataw, useGPU=False)

            if (ddRange != None):
                print("Anomaly Found")
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

