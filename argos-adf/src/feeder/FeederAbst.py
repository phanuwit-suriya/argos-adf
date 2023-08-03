import Pyro4
import calendar
import json
import os
import pandas
import requests
import signal
import sys
import threading
import time
sys.path.append('../common')
from GlobalConfig import *
from INodeComm import *

class FeederAbst:

    hbLoggerDir = "../../hb_logger"

    ########## Initlization & Finalization ##########
    #Important note!: Every instance that inherite this class should class these method in their constructor/destructor
    def Initialize(self, progArg, globalConfig):

        signal.signal(signal.SIGINT, self.SigInt_handler)
        self._progArg = progArg
        self._globalConfig = globalConfig

        self._isExecuting = True
        self._feederName = self._progArg.GetFeederName()
        if (self._feederName == None):
            raise Exception()
        self._host = self._progArg.GetHost()
        if (self._host == None):
            raise Exception()
        self._globalConfig = globalConfig
        self._type = globalConfig.GetFeederType(self._feederName)
        if (self._type == None):
            raise Exception()

        #Initialize communication channel (Creates a channel with the name of the feeder)
        self._comm = INodeComm(self._host, self._globalConfig)
        self._comm.RegisterChannel(self._feederName, self._feederName)

        #Initialize specifically according to the type of Feeder
        if (self._type == FeederEndPointEnum.Graphite):
            self._address = ""
            self._file = None
            self._replaySpeed = None
            self._replayOffset = None
            self._isFirstPoll = True
            self.Endpoint_Graphite_PollInit()
        elif (self._type == FeederEndPointEnum.ArCSV):
            self._address = None
            self._file = globalConfig.GetFeederFile(self._feederName)
            self._replaySpeed = globalConfig.GetFeederReplaySpeed(self._feederName)
            self._replayOffset = globalConfig.GetFeederReplayOffset(self._feederName)
            self._isFirstPoll = True
            self.Endpoint_ArCSV_PollInit()
        else:
            raise Exception()

        self._pollInterval = float(globalConfig.GetFeederPollInterval(self._feederName))

        self._originalStdOut = sys.stdout
        self._originalStdErr = sys.stderr
        self._logFile = open(self._feederName + ".log", 'w')
        sys.stdout = self._logFile
        sys.stderr = self._logFile

        #Initialize Heart Beat Logger
        #self._hbLoggerFilename = os.path.join(hbLoggerDir, "f_" + self._feederName + ".log"
        #hbLogFile = open(self._hbLoggerFilename, "w")
        #hbLogFile.write("[\n]")
        #close(hbLogFile)

    def Finalize(self):
        return

    #def HbLog(self, activityMessage):
    #    hbLogFile = open(self._hbLoggerFilename, "a")
    #    hbLogFile.seek(1, 2)
    #    hbLogFile.write("{}\n]")
    #    close(hbLogFile)

    ########## Manipulation ##########
    def Execute(self):
        #Poll-then-Write: Polls the specified endpoint and updates its own buffer as necessary
        ptwThread = threading.Thread(target=self.WaitToPoll)
        ptwThread.start()

        #Serves companion nodes (i.e. Feeders/Processes/Actions that want to communicate with this node)
        commThread = threading.Thread(target=self._comm.HandleRequestLoop)
        commThread.start()

    def WaitToPoll(self):
        while(self._isExecuting):
            self.Endpoint_Poll()
            time.sleep(self.Endpoint_GetPollDurationSec())

    def Terminate(self):
        self._comm.ExitRequestLoop()
        self._isExecuting = False

    def SigInt_handler(self, signum, frame):
        self.Terminate()
        self.Finalize()

    ########## Endpoint ##########
    def Endpoint_Poll(self):
        type = self.Endpoint_GetType()
        if (self._type == FeederEndPointEnum.Graphite):
            self.Endpoint_Graphite_Poll()
        elif (self._type == FeederEndPointEnum.ArCSV):
            self.Endpoint_ArCSV_Poll()
    def Endpoint_Graphite_PrePollHook_Impl(self):
        return
    def Endpoint_Graphite_PostPollHook_Impl(self, numPoints, datapoint):
        return
    def Endpoint_ArCSV_PrePollHook_Impl(self):
        return
    def Endpoint_ArCSV_PostPollHook_Impl(self, numPoints, datapoint):
        return
    
    def Endpoint_Graphite_PollInit(self):
        self._endpoint      = self._globalConfig.GetFeederEndpoint(self._feederName)
        self._address       = self._globalConfig.GetFeederAddress(self._feederName)
        self._startLookback = self._globalConfig.GetFeederStartLookback(self._feederName)
        self._lastEpTime    = calendar.timegm(time.gmtime()) - self._startLookback
    def Endpoint_Graphite_BuildRequestString(self, metricAddress, startEpTime, endEpTime):
        return "target=" + metricAddress + "&from=" + \
            str(startEpTime) + "&until=" + str(endEpTime) + "&format=json"
    def Endpoint_Graphite_Poll(self):
        self.Endpoint_Graphite_PrePollHook_Impl()

        #Poll the Graphite endpoint for datapoints falling in between the specified period
        curEpTime = calendar.timegm(time.gmtime())
        adjustedCurEpTime = curEpTime - self._globalConfig.GetFeederTimelag(self._feederName)
        requestStr = self.Endpoint_Graphite_BuildRequestString(self._address, adjustedCurEpTime - self._startLookback, adjustedCurEpTime)
        print(str(curEpTime) + " : " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curEpTime))))
        print(str(adjustedCurEpTime) + " : " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(adjustedCurEpTime))))
        print("\t" + requestStr)
        response = requests.post(self._endpoint, data=requestStr)
        response.encoding = "utf-8"

        try:
            data = json.loads(response.text)
        except Exception as e:
            return
            #raise e

        #Filters for new datapoint and returns if any
        rawDatapointList = data[0]["datapoints"]
        datapointList = []
        for i in range(0, len(rawDatapointList)):
            datapoint = self.CreateDatapoint(rawDatapointList[i][1], rawDatapointList[i][0])
            if (datapoint.epochTime > self._lastEpTime):
                self.Endpoint_Graphite_AddData(datapoint)
                datapointList.append(datapoint)
                self._lastEpTime = datapoint.epochTime

        self.Endpoint_Graphite_PostPollHook_Impl(len(datapointList), datapointList)

        sys.stdout.flush()
        sys.stderr.flush()

    def Endpoint_Graphite_AddData(self, datapoint):
        self._comm.AddDatapointToChannel(self._feederName, self._feederName, datapoint)

    def Endpoint_ArCSV_PollInit(self):
        dataframe = pandas.read_csv(self._file, engine='python', header=None, encoding='utf-8')
        self._fileData = dataframe.values
        self._fileDataIndex = 0
        self._lastEpTime = calendar.timegm(time.gmtime())
        replaySpeed = float(self.Endpoint_GetReplaySpeed())
        if (replaySpeed != 0.0):
            self._replayFraction = 1.0/float(self.Endpoint_GetReplaySpeed())
        else:
            self._replayFraction = 0.0
    def Endpoint_ArCSV_FirstPoll(self):
        data = self._fileData
        numPoints = 0
        retData = []
        for i in range(0, len(data) - 1):
            datapoint = self.CreateDatapoint(data[i][0], data[i][3])
            self.Endpoint_ArCSV_AddData(datapoint)
            retData.append(datapoint)
            numPoints = numPoints + 1
            if ((data[i+1][0] - data[0][0]) >= self._replayOffset):
                break
        self._fileDataIndex = numPoints
        self._lastEpTime = calendar.timegm(time.gmtime())

        return retData
    def Endpoint_ArCSV_Poll(self):
        self.Endpoint_ArCSV_PrePollHook_Impl()

        if (self._isFirstPoll):
            retData = self.Endpoint_ArCSV_FirstPoll()
            if (retData != None):
                numPoints = len(retData)
            else:
                numPoints = 0
            self._isFirstPoll = False
            self.Endpoint_ArCSV_PostPollHook_Impl(numPoints, retData)
            return

        retData     = []
        data        = self._fileData
        index       = self._fileDataIndex
        curEpTime   = calendar.timegm(time.gmtime())
        diffEpTime  = curEpTime - self._lastEpTime

        if (index >= len(data) - 1):
            self.Endpoint_ArCSV_PostPollHook_Impl(0, None)
            return
        numPoints = 0
        if (self._replayFraction == 0.0):
            for i in range(0, len(data)):
                datapoint = self.CreateDatapoint(data[i][0], data[i][3])

                self.Endpoint_ArCSV_AddData(datapoint)
                retData.append(datapoint)

                numPoints += 1
            self._fileDataIndex = len(data) - 1
        else:
            accEpTime = 0
            while((diffEpTime > accEpTime) and (index < len(data) - 1)):
                actualDelay = int(data[index + 1][0]) - int(data[index][0])
                replayDelay = actualDelay * self._replayFraction
                datapoint   = self.CreateDatapoint(data[index][0], data[index][3])

                self.Endpoint_ArCSV_AddData(datapoint)
                retData.append(datapoint)

                numPoints += 1
                accEpTime += replayDelay
                index += 1
            self._fileDataIndex = index
            self._lastEpTime = calendar.timegm(time.gmtime())

        self.Endpoint_ArCSV_PostPollHook_Impl(numPoints, retData)

    def Endpoint_ArCSV_AddData(self, datapoint):
        self._comm.AddDatapointToChannel(self._feederName, self._feederName, datapoint)

    def Endpoint_GetType(self):
        type = self._type
        return type

    def Endpoint_SetType(self, type):
        self._type = type

    def Endpoint_GetPollDurationSec(self):
        return self._pollInterval

    def Endpoint_SetPollDurationSec(self, sec):
        self._pollInterval = sec

    def Endpoint_GetReplaySpeed(self):
        return self._replaySpeed

    def Endpoint_SetReplaySpeed(self, sec):
        self._replaySpeed = sec

    def Endpoint_GetReplayOffset(self):
        return self._replayOffset

    def Endpoint_SetReplayOffset(self, sec):
        self._replayOffset = sec

    ########## Helpers ##########
    def CreateDatapoint(self, epochTimeStr, valueStr):
        epochTime = 0
        value = 0.0
        try:
            epochTime = int(epochTimeStr)
        except ValueError:
            epochTime = 0
        except TypeError:
            epochTime = 0

        try:
            value = float(valueStr)
        except ValueError:
            value = 0.0
        except TypeError:
            value = 0.0

        return Datapoint(epochTime, value)
