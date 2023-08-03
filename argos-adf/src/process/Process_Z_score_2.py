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
class ProcessExample(ProcessAbst):

    def __init__(self, progArg):
        self._progArg = progArg
        self.data = []
        self.flag = 0
        self._configFile = self._progArg.GetConfigFile()
        if (self._configFile == None):
            self._configFile = '../starter/config.json'
        self._gConfig = GlobalConfig(self._configFile)

        # A one-time call to Initialize() is mandatory
        self.Initialize(self._progArg, self._gConfig)
        self.processName = self._progArg.GetProcessName()
        self.host = self._progArg.GetHost()
        self._comm = INodeComm(self.host, self._gConfig)
        self._comm.RegisterChannel(self.processName, self.processName)

    def AddData(self, binary_output):
        self._comm.AddDatapointToChannel(self.processName, self.processName, binary_output)

    def Endpoint_Postpoll_Hook_Impl(self, inputName, numPoints, lastEpTime, datapoints):

        for dp in datapoints:
            self.data.append(dp)
        print (len(self.data))

        ### parameters ###
        algorithm = 'Z-score'
        buffer = 10000

        # Z-score parameters
        windowSize = 1000
        threshold_Zscore = 3

        ##################

        if len(self.data) >= buffer: # limit self.data memory as buffer
            self.data = self.data[-buffer:]

        if len(self.data) >= windowSize:
            windowDatapoint = self.data[len(self.data) - windowSize:len(self.data)]
            data_w = [(windowDatapoint[i].epochTime, windowDatapoint[i].value) for i in range(len(windowDatapoint))]

            # simple peak detection algorithm
            z_score = Z_score(windowDatapoint, threshold_Zscore)
            output,binary_output = z_score.outliers_modified_z_score()
            # replace invalid value
            if (len(output) == 0):
                print("No peak detected")

            # start writing json file for the first time.
            if self.flag == 0:
                # prepare data
                write_data = {'data': [data_w], 'output': [output], 'algorithm': algorithm,
                              'threshold_Zscore': threshold_Zscore, 'windowSize': windowSize}

                # write data into json file for the first time.
                with open('result_11.json', 'w') as outfile:
                    json.dump(write_data, outfile)
                print('wrote succesfully')

                #add output 1/0 to channel.
                for i in range(0, len(binary_output)):
                    self.AddData(binary_output[i])

            elif self.flag == 1: #concatenate new data and output.
                with open('result_11.json') as f:
                    read_data = json.load(f)

                #append new data
                read_data['data'].append(data_w)
                read_data['output'].append(output)

                with open('result_11.json', 'w') as f:
                    json.dump(read_data, f)

                print('added succesfully')

                # add recent data to channel.
                binary_output_updated = binary_output[-numPoints:]
                for i in range(0, len(binary_output_updated)):
                    self.AddData(binary_output_updated[i])

        self.flag = 1


if __name__ == "__main__":
    progArg = ArProgArg()
    progArg.Parse(sys.argv)
    pe = ProcessExample(progArg)
    pe.Execute()