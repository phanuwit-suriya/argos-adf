import sys
sys.path.append('../common')
from ArProgArg import *
from ProcessAbst import *

#All feeders MUST extend 'FeederAbst'
class ProcessExample(ProcessAbst):
    def __init__(self, progArg):
        self._progArg = progArg
        self._configFile = self._progArg.GetConfigFile()
        if (self._configFile == None):
            self._configFile = '../common/config_template.json'

        self._gConfig = GlobalConfig(self._configFile)

        # A one-time call to Initialize() is mandatory
        self.Initialize(self._progArg, self._gConfig)

    def Initialize_Post_Hook_Impl(self):
        self.Output_InitializeCSVFile()

    def Endpoint_Prepoll_Hook_Impl(self, inputName):
        return
        print("Pre-poll: ",inputName)

    def Endpoint_Postpoll_Hook_Impl(self, inputName, numPoints, lastEpTime, datapoints):
        dpl = []
        for dp in datapoints:
            dp.value = dp.value * 10000
            dpl.append(dp)
        self.Output_PublishDatapointList(dpl)
        self.Output_PublishDatapointListToCSVFile(inputName, datapoints)
        print("Post-poll: " + inputName + " / " + str(numPoints) + " / " + str(lastEpTime))

if __name__ == "__main__":
    progArg = ArProgArg()
    progArg.Parse(sys.argv)
    pe = ProcessExample(progArg)
    pe.Execute()