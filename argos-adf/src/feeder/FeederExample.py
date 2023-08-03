import sys
sys.path.append('../common')
from ArProgArg import *
from FeederAbst import *

#All feeders MUST extend 'FeederAbst'
class FeederExample(FeederAbst):
    def __init__(self, progArg):
        self._progArg = progArg
        self._configFile = self._progArg.GetConfigFile()
        if (self._configFile == None):
            self._configFile = '../common/config_template.json'

        self._gConfig = GlobalConfig(self._configFile)

        #A one-time call to Initialize() is mandatory
        self.Initialize(self._progArg, self._gConfig)

    def PostPollHook(self, numPoints, datapoint):
        print ("\tPost-poll hook: " + str(numPoints))
        for i in range(0, numPoints):
            print("\t\t" + str(datapoint[i].epochTime) + ":" + str(datapoint[i].value))

    # Feeder-specific tasks should be handled in hook functions
    def Endpoint_ArCSV_PostPollHook_Impl(self, numPoints, datapoint):
        self.PostPollHook(numPoints, datapoint)

    # Feeder-specific tasks should be handled in hook functions
    def Endpoint_Graphite_PostPollHook_Impl(self, numPoints, datapoint):
        self.PostPollHook(numPoints, datapoint)

if __name__ == "__main__":
    progArg = ArProgArg()
    progArg.Parse(sys.argv)
    fe = FeederExample(progArg)
    fe.Execute()
