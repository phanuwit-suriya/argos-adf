from datetime import datetime
from json_metric import *
from time_format import *
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import time

##################### Constant Section ##############################

class SyntConstant:
    SECONDS_PER_DAY = 86400.0

##################### Time-related Section ##########################

class SyntTimeSpan:

    @staticmethod
    def GetEpochTime(dateTimeString):
        return datetime.strptime(dateTimeString, TimeFormat.LOCALTIME_ISO8601).timestamp()

    def __init__(self, epStart, epEnd, epRes):
        if (epStart.__class__ != str):
            raise Exception()
        if (epEnd.__class__ != str):
            raise Exception()
        if (epRes.__class__ != float):
            raise Exception()
        self.epStart = SyntTimeSpan.GetEpochTime(epStart) #Unit: seconds
        self.epEnd   = SyntTimeSpan.GetEpochTime(epEnd)   #Unit: seconds
        self.epRes   = epRes                              #Unit: seconds (with ms fraction)

    def GetStart(self): return self.epStart
    def GetEnd(self): return self.epEnd
    def GetResolution(self): return self.epRes

#################### Metric-related Section #########################

class SyntSerializableBase(object):
    def __init__(self):
        pass
    def SerializeToJson(self):
        return self.SerializeToJsonImpl()
    def SerializeToJsonImpl(self):
        raise NotImplementedError
    def DeSerializeFromJson(self, jsonStr):
        return self.DeSerializeFromJsonImpl(jsonStr)
    def DeSerializeFromJsonImpl(self, jsonStr):
        raise NotImplementedError

class SyntInstanceModelBase(SyntSerializableBase):
    def __init__(self):
        self.name = None
        self.parameter = {}
        self.timeSpan = None

    def SetName(self, name):
        if (name.__class__ != str):
            raise Exception()
        self.name = name

    def GetName(self):
        return self.name

    def AddParameter(self, paramName, paramVal):
        self.parameter[paramName] = paramVal

    def GetParameter(self, paramName):
        return self.parameter[paramName]

    def GetAllParameters(self):
        return self.parameter.items()

    def SetTimeSpan(self, timeSpan):
        if (timeSpan.__class__ != SyntTimeSpan):
            raise Exception()
        self.timeSpan = timeSpan

    def GetTimeSpan(self):
        return self.timeSpan

    def CopyAttributesForJsonMetric(self, dest):
        #Name
        dest.SetName(self.GetName())

        #Parameters
        allParams = self.GetAllParameters()
        for (key, value) in allParams:
            dest.AddParameter(key, value)

        #Timespan / Start-End epoch time
        timeSpan = self.GetTimeSpan()
        if timeSpan == None:
            return dest
        epStart = timeSpan.GetStart()
        epEnd = timeSpan.GetEnd()
        dest.SetStartFromEpochTime(epStart)
        dest.SetEndFromEpochTime(epEnd)
        return dest

class SyntSignalDesc(SyntInstanceModelBase):
    def __init__(self):
        super(SyntSignalDesc, self).__init__()
    def SerializeToJsonImpl(self):
        return self.CopyAttributesForJsonMetric(JsonSignal()).GetJsonString()
    def DeSerializeFromJsonImpl(self, jsonStr):
        raise NotImplementedError #TODO Implement this.

class SyntNoiseDesc(SyntInstanceModelBase):
    def __init__(self):
        super(SyntNoiseDesc, self).__init__()
    def SerializeToJsonImpl(self):
        return self.CopyAttributesForJsonMetric(JsonNoise()).GetJsonString()
    def DeSerializeFromJsonImpl(self, jsonStr):
        raise NotImplementedError #TODO Implement this.

class SyntAnomalyDesc(SyntInstanceModelBase):
    def __init__(self):
        super(SyntAnomalyDesc, self).__init__()
    def SerializeToJsonImpl(self):
        return self.CopyAttributesForJsonMetric(JsonAnomaly()).GetJsonString()
    def DeSerializeFromJsonImpl(self, jsonStr):
        raise NotImplementedError #TODO Implement this.

class SyntMetric(SyntSerializableBase):

    #TODO: Work on the part for storing raw datapoints

    def __init__(self, name, start, end, res):
        if (name.__class__ != str):
            raise Exception()
        self.name = name
        self.timeSpan = SyntTimeSpan(start, end, res)
        self.seqSize = math.floor(
            (self.timeSpan.GetEnd() - self.timeSpan.GetStart()) / self.timeSpan.GetResolution())

        #TODO: Use seqSize for both Time/Data sequence initializations so that we can be sure they
        # are at the same size.
        self.timeSeq = self.InitializeTimeSequence()
        self.dataSeq = self.InitializeDataSequence()
        self.index = 0;
        self.signals = []
        self.noises = []
        self.anomalies = []

    def AddSignal(self, signal):
        if signal.__class__ != SyntSignalDesc:
            raise Exception()
        self.signals.append(signal)

    def GetSignal(self, index):
        if (index >= len(self.signals)) or (index < 0):
            return None
        return self.signals[index]

    def GetSignalCount(self):
        return len(self.signals)

    def AddNoise(self, noise):
        if noise.__class__ != SyntNoiseDesc:
            raise Exception()
        self.noises.append(noise)

    def GetNoise(self, index):
        if (index >= len(self.noises)) or (index < 0):
            return None
        return self.noises[index]

    def GetNoiseCount(self):
        return len(self.noises)

    def AddAnomaly(self, anomaly):
        if anomaly.__class__ != SyntAnomalyDesc:
            raise Exception()
        self.anomalies.append(anomaly)

    def GetAnomaly(self, index):
        if (index >= len(self.anomalies)) or (index < 0):
            return None
        return self.anomalies[index]

    def GetAnomalyCount(self):
        return len(self.anomalies)

    def InitializeTimeSequence(self):
        return np.arange(
                self.timeSpan.GetStart(), 
                self.timeSpan.GetEnd(), 
                self.timeSpan.GetResolution())

    def InitializeDataSequence(self):
        return np.zeros(self.seqSize)

    def GetTimeSpan(self): return self.timeSpan

    def GetTimeSpanStart(self): return self.timeSpan.GetStart()

    def GetTimeSpanEnd(self): return self.timeSpan.GetEnd()

    def GetTimeSpanResolution(self): return self.timeSpan.GetResolution()

    def GetSequenceSize(self): return self.seqSize

    def GetTimeSequenceAsNumpy(self): return self.timeSeq

    def GetDateTimeSequenceAsNumpy(self):
        dateTimeList = []
        for epTime in self.timeSeq:
            dateTimeList.append(datetime.fromtimestamp(epTime))

        return dateTimeList

    def GetDataSequenceAsNumpy(self): return self.dataSeq

    def ResetIndex(self):
        self.index = 0

    def GetIndex(self):
        return self.index

    def SetIndex(self, index):
        self.index = index

    def GetCurrent(self):
        if (self.index >= self.seqSize):
            return False, None, None
        return True, self.timeSeq[self.index], self.dataSeq[self.index]

    def SetCurrent(self):
        if (self.index >= self.seqSize):
            return False
        self.dataSeq[self.index] = value

    def GetAndAdvance(self):
        if (self.index >= self.seqSize):
            return False, None, None
        stashedIndex = self.index
        self.index += 1
        return True, self.timeSeq[stashedIndex], self.dataSeq[stashedIndex]

    def SetAndAdvance(self, value):
        if (self.index >= self.seqSize):
            return False
        self.dataSeq[self.index] = value
        self.index += 1
        return True

    def Show(self):
        dateTimeList = self.GetDateTimeSequenceAsNumpy()
        plt.figure()
        plt.plot(dateTimeList, self.dataSeq)
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter(TimeFormat.LOCALTIME_ISO8601_NO_SECONDS))
        af = plt.gcf()
        af.autofmt_xdate()
        plt.show()

    def SerializeToJsonImpl(self):
        jsonMetric = JsonMetric()

        jsonMetric.SetName(self.name)

        #TimeSpan
        jsonMetric.SetTimeSpan(\
            self.timeSpan.GetStart(),\
            self.timeSpan.GetEnd(),\
            self.timeSpan.GetResolution())
        
        #Signals#
        signalCount = self.GetSignalCount()
        for i in range(0, signalCount):
            signal = self.GetSignal(i)
            if (signal == None):
                continue
            jSignal = signal.CopyAttributesForJsonMetric(
                JsonSignal())
            jsonMetric.AddSignal(jSignal)

        #Noises#
        noiseCount = self.GetNoiseCount()
        for i in range(0, noiseCount):
            noise = self.GetNoise(i)
            if (noise == None):
                continue
            jNoise = noise.CopyAttributesForJsonMetric(
                JsonNoise())
            jsonMetric.AddNoise(jNoise)

        #Anomaly#
        anomalyCount = self.GetAnomalyCount()
        for i in range(0, anomalyCount):
            anomaly = self.GetAnomaly(i)
            if (anomaly == None):
                continue
            jAnomaly = anomaly.CopyAttributesForJsonMetric(
                JsonAnomaly())
            jsonMetric.AddAnomaly(jAnomaly)

        #Datapoints#
        index = self.GetIndex()
        self.ResetIndex()
        
        while(True):
            valid, curTime, curVal = self.GetAndAdvance()
            if (not valid):
                break

            jsonMetric.AddSingleDatapoint(curTime, curVal)

        self.SetIndex(index)

        return jsonMetric.GetJsonString()

    @staticmethod
    def DeSerializeFromJsonImpl(self, jsonStr):

        _dict = json.loads(jsonStr)

        # TimeSpan

        # Signals#


        # Noises#


        # Anomaly#


        # Datapoints#

        return
        

##################### Angle Utility Section #########################

class SyntAngle:

    @staticmethod
    def CoarseRadianAngle(timeEpochStart, timeEpochCurrent, freqRevPerDay):

        if (timeEpochCurrent < timeEpochStart):
            raise Exception()

        duration = timeEpochCurrent - timeEpochStart
        return (duration / SyntConstant.SECONDS_PER_DAY) * 2.0 * math.pi * freqRevPerDay

    @staticmethod
    def FineRadianAngle(timeEpochStart, timeEpochCurrent, freqHz):
        return 
    
###################### Noise Utility Section ########################

class SyntNoise:

    def __init__(self):
        #Not implemented yet!
        pass


if __name__ == "__main__":

    metric = SyntMetric(
                "Basic Sinusoidal wave",
                "2017-12-01T09:38:42.76",
                "2018-02-01T09:38:42.769",
                3600.0)

    #Standard template parameters
    timeEpochStart = metric.GetTimeSpanStart()
    timeEpochEnd = metric.GetTimeSpanEnd()
    timeResolution = metric.GetTimeSpanResolution()
    dataSize = metric.GetSequenceSize()
    print("timeEpochStart: " + str(timeEpochStart) + 
        "\ntimeEpochEnd: " + str(timeEpochEnd) + 
        "\ntimeResolution: " + str(timeResolution))
    print ("Data size: " + str(dataSize))

    #Metric-specific parameters
    amplitude = 20       #Unit: Units
    freqRevPerDay = 0.2  #Unit: Revolution-per-day
    devAmplitude = 1
    devFreqRevPerDay = 5

    principleHarmonic = SyntSignalDesc()
    principleHarmonic.SetName("PrincipleHarmonic")
    principleHarmonic.AddParameter("CoarseFrequency", 0.2)
    principleHarmonic.SetTimeSpan(
        SyntTimeSpan(
            "2017-12-01T00:00:00.00",
            "2018-02-01T00:00:00.00", timeResolution))
    metric.AddSignal(principleHarmonic)

    anomaly_0 = SyntAnomalyDesc()
    anomaly_0.SetName("anomaly-0")
    anomaly_0.AddParameter("param_1", "1")
    anomaly_0.SetTimeSpan(
        SyntTimeSpan(
            "2017-12-01T00:00:00.00",
            "2018-02-01T00:00:00.00", timeResolution))
    metric.AddAnomaly(anomaly_0)

    noise_0 = SyntNoiseDesc()
    noise_0.SetName("noise-0")
    noise_0.AddParameter("param_2", 2.2)
    noise_0.SetTimeSpan(
        SyntTimeSpan(
            "2017-12-01T00:00:00.00",
            "2018-02-01T00:00:00.00", timeResolution))
    metric.AddNoise(noise_0)

    print(principleHarmonic.SerializeToJson() + "\n\n")
    print(anomaly_0.SerializeToJson() + "\n\n")
    print(noise_0.SerializeToJson() + "\n\n")

    jsonStr = metric.SerializeToJson()
    print(str(jsonStr) + "\n\n")

    """
    if (timeEpochEnd <= timeEpochStart):
        raise Exception()

    startTime = metric.GetTimeSpanStart()
    while(True):
        valid, curTime, curVal = metric.GetCurrent() 
        if (not valid):
            break
        val1 = (amplitude * math.cos(SyntAngle.CoarseRadianAngle(startTime, curTime, freqRevPerDay)))
        #TODO: Work on the function or a way to compare point-of-time in an easy and readable way.
        if (curTime > startTime + (metric.GetTimeSpanResolution() * 1000)):
            val2 = (devAmplitude * math.cos(SyntAngle.CoarseRadianAngle(startTime, curTime, devFreqRevPerDay)))
        else:
            val2 = 0
        metric.SetAndAdvance(val1 + val2)

    plt.figure()
    plt.plot(metric.GetDataSequenceAsNumpy())
    plt.show()
    """
