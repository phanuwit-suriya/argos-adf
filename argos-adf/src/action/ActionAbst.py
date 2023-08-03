import calendar
import signal
import sys
import threading
import time
sys.path.append('../common')
from GlobalConfig import *
from INodeComm import *

class ActionAbst:
    strOutput   = "output"
    strFeedback = "feedback"
    ########## Initlization & Finalization ##########
    # Important note!: Every instance that inherite this class should class these method in their constructor/destructor
    def Initialize_Pre_Hook_Impl(self):
        return
    def Initialize_Post_Hook_Impl(self):
        return
    def Initialize(self, progArg, globalConfig):
        self.Initialize_Pre_Hook_Impl()

        signal.signal(signal.SIGINT, self.SigInt_handler)
        self._progArg = progArg
        self._globalConfig = globalConfig
        self._isExecuting = True

        self._actionName = self._progArg.GetActionName()
        if (self._actionName == None):
            raise Exception()
        self._host = self._progArg.GetHost()
        if (self._host == None):
            raise Exception()

        # Initialize communication channel (Creates a channel with the name of the feeder)
        self._comm = INodeComm(self._host, self._globalConfig)
        self._comm.RegisterChannel(self._actionName, "Output")
        self._comm.RegisterChannel(self._actionName, "Feedback")

        self._properties = self._globalConfig.GetActionByName(self._actionName)

        self._originalStdOut = sys.stdout
        self._originalStdErr = sys.stderr
        self._logFile = open(self._actionName + ".log", 'w')
        sys.stdout = self._logFile
        sys.stderr = self._logFile

        self.Initialize_Post_Hook_Impl()
        return

    def Finalize(self):
        return

     ########## Manipulation ##########
    def Execute(self):
        #Serves companion nodes (i.e. Feeders/Processes/Actions that want to communicate with this node)
        commThread = threading.Thread(target=self._comm.HandleRequestLoop)
        commThread.start()

        self.Endpoint_PollInit()

    def WaitToPoll(self):
        while(self._isExecuting):
            time.sleep(self.GetPollDurationSec())
            self.Endpoint_Poll()

    def Terminate(self):
        self._comm.ExitRequestLoop()
        self._isExecuting = False

    def SigInt_handler(self, signum, frame):
        self.Terminate()
        self.Finalize()

    ########## Endpoint ##########
    def Endpoint_PollInit(self):
        feederList = self._properties.inputFeederList
        processList = self._properties.inputProcessList

        for feeder in feederList:
            t = threading.Thread(target=self.Endpoint_Poll,args=(feeder,))
            t.start()

        for process in processList:
            t = threading.Thread(target=self.Endpoint_Poll, args=(process,))
            t.start()

        return

    def Endpoint_Prepoll_Hook_Impl(self, inputName, inputType):
        return
    def Endpoint_Postpoll_Hook_Impl(self, inputName, inputType, numPoints, lastEpTime, datapoints):
        return
    def Endpoint_Poll(self, inputInfo):
        type         = inputInfo.type
        name         = inputInfo.name
        pollInterval = int(inputInfo.pollInterval)
        bufferSize   = int(inputInfo.bufferSize)
        lastEpTime   = 0

        while (self._isExecuting):
            time.sleep(pollInterval)

            curEpTime = calendar.timegm(time.gmtime())
            print(str(curEpTime) + " : " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curEpTime))) + " '" + name  + "'")

            self.Endpoint_Prepoll_Hook_Impl(name, type)

            rawDpList = self._comm.RetrieveDatapointListFromChannel(name, name)
            dpList = []

            for dp in rawDpList:
                if (dp.epochTime > lastEpTime):
                    dpList.append(dp)
                    lastEpTime = dp.epochTime

            self.Endpoint_Postpoll_Hook_Impl(name, type, len(dpList), lastEpTime, dpList)

            sys.stdout.flush()
            sys.stderr.flush()

        return

    def Output_PublishDatapoint(self, dp):
        self._comm.AddDatapointToChannel(self._actionName, ActionAbst.strOutput, dp)

    def Output_PublishDatapointList(self, dpList):
        for i in range(0, len(dpList)):
            self._comm.AddDatapointToChannel(self._actionName, ActionAbst.strOutput, dpList[i])

    def Output_PublishFeedback(self):
        #TODO: This method is to be defined in another issue.
        return

    #QUALIFY: This is mainly used for debug and qualifying features of the framework and can be hook by the pre/post-poll hook
    def Output_InitializeCSVFile(self):
        feederList = self._properties.inputFeederList
        processList = self._properties.inputProcessList

        self._allFhMap = {}
        self._feederFhMap = {}
        for feeder in feederList:
            feedername = feeder.name
            filename = str(self._actionName) + "_tf_" + str(feedername) + "--" + str(feedername) + ".csv"
            fh = open(filename, "w")
            self._feederFhMap[feedername] = fh
            self._allFhMap[feedername] = fh

        self._processFhMap = {}
        for process in processList:
            processname = process.name
            filename = str(self._actionName) + "_tp_" + str(processname) + "--" + str(processname) + ".csv"
            fh = open(filename, "w")
            self._processFhMap[processname] = fh
            self._allFhMap[processname] = fh

        return

    def Output_FinalizeCSVFile(self):
        for key, value in self._allFnMap:
            value.close()

    def Output_PublishDatapointListToCSVFile(self, name, dpList):
        fh = self._allFhMap[name]
        for dp in dpList:
            info = str(dp.epochTime) + ", " + str(dp.value) + "\n"
            fh.write(info)
        return

