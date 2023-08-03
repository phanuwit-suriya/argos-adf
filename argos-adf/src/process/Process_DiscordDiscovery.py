import sys
sys.path.append('../common')
from ArProgArg import *
from ProcessAbst import *
sys.path.append('../models/DiscordDiscovery_2')
from DiscordDiscovery import *

from matplotlib import pyplot as plt

#All feeders MUST extend 'FeederAbst'
class ProcessDiscordDiscovery(ProcessAbst):

    bufferSize_str          = "BufferSize"
    knowledgeWindowSize_str = "KnowledgeWindowSize"
    sensitivity_str         = "Sensitivity"
    knowledgeRatio          = 10

    def __init__(self, progArg):
        self._progArg = progArg
        self._configFile = self._progArg.GetConfigFile()
        if (self._configFile == None):
            self._configFile = '../common/config_template.json'

        self._gConfig = GlobalConfig(self._configFile)

        # A one-time call to Initialize() is mandatory
        self.Initialize(self._progArg, self._gConfig)
        print("Process '" + self._processName + "' started . . .")

        self.data = []
        #self.bufferSize = 2000000
        #self.knowledgeWindowSize = 1500#1500#720
        self.parameters = self._properties.parameters
        self.bufferSize = int(self.parameters[ProcessDiscordDiscovery.bufferSize_str])
        self.knowledgeWindowSize = int(self.parameters[ProcessDiscordDiscovery.knowledgeWindowSize_str])
        self.sensitivity = int(self.parameters[ProcessDiscordDiscovery.sensitivity_str])

        self.ddParam = DiscordDiscovery.Param_gpu()
        #self.ddParam.minWindowSize = 35#35#64#24
        #self.ddParam.minWindowSize = \
        #    int((self.knowledgeWindowSize / ProcessDiscordDiscovery.knowledgeRatio) / self.sensitivity)
        self.ddParam.minWindowSize = \
            int(float(self.knowledgeWindowSize) / 5.0)
        self.ddParam.knowledgeWindowSize = self.knowledgeWindowSize
        self.ddParam.windowStep = 1
        self.ddParam.detectionFocus = 1
        self.dd = DiscordDiscovery(self.ddParam)
        self.anomalyFrameCounter = 1

    def Endpoint_Postpoll_Hook_Impl(self, inputName, numPoints, lastEpTime, datapoints):

        print("\tNew datapoints: " + str(len(datapoints)))
        if (len(datapoints) <= 0):
            return

        for dp in datapoints:
            self.data.append(dp)

        #Store the knowledge
        if (len(self.data) > self.bufferSize):
            self.data = self.data[len(self.data)-self.bufferSize:]

        #Find for anomaly in the knowledge window
        vdata = []
        knowledgeWindowSize = self.knowledgeWindowSize
        if (len(self.data) < knowledgeWindowSize):
            knowledgeWindowSize = len(self.data)

        if (knowledgeWindowSize < self.knowledgeWindowSize):
            return

        dataOffset = len(self.data) - knowledgeWindowSize
        for i in range(dataOffset, len(self.data)):
            vdata.append(self.data[i].value)

        ########## ORIGINAL IMPLEMENTATION ##########
        #ddRange = self.dd.NaiveDiscovery(vdata, threads=8)

        ########## SINGLE-FRAME IMPLEMENTATION ##########
        ddRange = self.dd.NaiveDiscovery_SingleFrame(vdata, useGPU=False)

        #Publish the output in the binary with timestamp form
        outputDPList = []
        if ddRange != None:
            frameStartIndex    = ddRange.startIndex
            frameEndIndex      = ddRange.endIndex
            frameStartEpoch    = self.data[dataOffset + frameStartIndex].epochTime
            frameEndEpoch      = self.data[dataOffset + frameEndIndex].epochTime
            frameStartDateTime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frameStartEpoch)))
            frameEndDateTime   = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frameEndEpoch)))
            print("\tAnomaly: Index[" + str(frameStartIndex) + " - " + str(frameEndIndex) + "], Epoch["\
            + str(frameStartEpoch) + " - " + str(frameEndEpoch) + "], DateTime[" + frameStartDateTime\
            + " - " + frameEndDateTime + "]")
            j = 0
            for i in range(dataOffset, len(self.data)):
                if (j>=ddRange.startIndex) and (j<=ddRange.endIndex):
                    outputDPList.append([self.data[dataOffset + j].epochTime, 1.0])
                else:
                    outputDPList.append([self.data[dataOffset + j].epochTime, 0.0])
                j += 1

            anomalyFrame = Datapoint(self.anomalyFrameCounter, outputDPList)
            self.anomalyFrameCounter += 1
            self.Output_PublishDatapoint(anomalyFrame)
        else:
            print("\t\tAnomaly not found . . .")

        #if ddRange != None:
        #    plt.figure()
        #    plt.plot(vdata)
        #    start_index = ddRange.startIndex
        #    end_index = ddRange.endIndex
        #    plt.axvspan(start_index, end_index, facecolor='r', alpha=0.3)
        #    plt.axvline(start_index, color='r')
        #    plt.axvline(end_index, color='r')
        #    plt.show()

if __name__ == "__main__":
    progArg = ArProgArg()
    progArg.Parse(sys.argv)
    pe = ProcessDiscordDiscovery(progArg)
    pe.Execute()
