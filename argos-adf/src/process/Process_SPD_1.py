import sys
import json

from ProcessAbst import *
sys.path.append('../common')
from ArProgArg import *
from INodeComm import *
from GlobalConfig import *

sys.path.append('../models/PeakDetection')
from PeakDetectionAlgorithm import *
from Modified_zscore import *


# All processes MUST extend 'ProcessAbst'
class ProcessSPD(ProcessAbst):

    bufferSize_str = "BufferSize"
    k_str          = "k"
    threshold_str  = "threshold"
    mode_str       = "mode"
    algorithm      = "SPD"
    windowSize     = 1000

    def __init__(self, progArg):
        self._progArg = progArg
        self.data = []
        self.flag = 0
        self._configFile = self._progArg.GetConfigFile()
        if (self._configFile == None):
            self._configFile = '../starter/config.json'
        self._gConfig = GlobalConfig(self._configFile)
        self.processName =self._progArg.GetProcessName()
        self.host = self._progArg.GetHost()
        # A one-time call to Initialize() is mandatory
        self.Initialize(self._progArg, self._gConfig)
        self._comm = INodeComm(self.host, self._gConfig)
        self._comm.RegisterChannel(self.processName, self.processName)

        self.parameters = self._properties.parameters
        self.bufferSize = int(self.parameters[ProcessSPD.bufferSize_str])
        self.window_k   = int(self.parameters[ProcessSPD.k_str])
        self.threshold  = int(self.parameters[ProcessSPD.threshold_str])
        self.mode       = int(self.parameters[ProcessSPD.mode_str])

    def AddData(self, binary_output):
        self._comm.AddDatapointToChannel(self.processName, self.processName, binary_output)

    def Endpoint_Postpoll_Hook_Impl(self, inputName, numPoints, lastEpTime, datapoints):

        if (len(datapoints) <= 0):
            return

        for dp in datapoints:
            self.data.append(dp)

        if len(self.data) > self.bufferSize: # limit self.data memory as buffer
            self.data = self.data[-self.bufferSize:]

        if len(self.data) >= ProcessSPD.windowSize:
            windowDatapoint = self.data[-ProcessSPD.windowSize:]

            # simple peak detection algorithm
            peak_detection = PeakDetection(windowDatapoint, self.window_k, self.threshold, self.mode)
            anomalies,binary_output = peak_detection.PeakDetect()
            data_w = [(windowDatapoint[i].epochTime, windowDatapoint[i].value) for i in range(len(windowDatapoint))]

            # start writing json file for the first time.
            if self.flag == 0:
                # prepare data
                write_data = {'data': [data_w], 'anomalies': [anomalies], 'algorithm': ProcessSPD.algorithm, 'mode': self.mode,
                              'threshold': self.threshold, 'window_k': self.window_k}

                # write data into json file for the first time.
                with open('result_1.json', 'w') as outfile:
                    json.dump(write_data, outfile)

                #add binary anomalies to channel.
                for i in range(0, len(binary_output)):
                    self.AddData(binary_output[i])

            elif self.flag == 1: #concatenate new data and anomalies.
                with open('result_1.json') as f:
                    read_data = json.load(f)

                #append new data
                read_data['data'].append(data_w)
                read_data['anomalies'].append(anomalies)

                with open('result_1.json', 'w') as f:
                    json.dump(read_data, f)

                # add recent data to channel.
                binary_output_updated = binary_output[-numPoints:]
                for i in range(0, len(binary_output_updated)):
                    self.AddData(binary_output_updated[i])

            self.flag = 1

if __name__ == "__main__":
    progArg = ArProgArg()
    progArg.Parse(sys.argv)
    pe = ProcessSPD(progArg)
    pe.Execute()