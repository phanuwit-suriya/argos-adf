from datetime import datetime
from time_format import *
import json

#####################################################################
#
# This class aims to provide a serialization / de-serialization
# utility for metrics that is human readable / editable. 
#
#####################################################################

def ConvertEpochTimeToLocalTimeString(epTime):
    localTime = datetime.fromtimestamp(epTime)
    return localTime.strftime(TimeFormat.LOCALTIME_ISO8601)

def ConvertLocalTimeStringToEpochTime(time):
    return datetime.strptime(
        time, TimeFormat.LOCALTIME_ISO8601).timestamp()

class JsonInstanceModel(dict):
    KEY_NAME = "name"
    KEY_PARAMETERS = "parameters"
    KEY_START = "start"
    KEY_END = "end"

    def __init__(self):
        self.clear()
        self[JsonInstanceModel.KEY_PARAMETERS] = {}

    def SetName(self, name):
        if (name.__class__ != str):
            raise Exception()
        self[JsonInstanceModel.KEY_NAME] = name

    def GetName(self):
        if (JsonInstanceModel.KEY_NAME in self):
            return self[JsonInstanceMode.KEY_NAME]
        return None

    def AddParameter(self, parameter, value):
        if (parameter.__class__ != str):
            raise Exception()
        self[parameter] = value

    def GetParameter(self, parameter):
        if (parameter.__class__ != str):
            raise Exception()
        paramDict = self[JsonInstanceModel.KEY_PARAMETERS]
        if (parameter in paramDict):
            return paramDict[parameter]
        return None

    def SetStartFromEpochTime(self, start):
        if (start.__class__ != int) and (start.__class__ != float):
            raise Exception()
        self[JsonInstanceModel.KEY_START] = \
            ConvertEpochTimeToLocalTimeString(start)

    def GetStartAsEpochTime(self):
        if not (JsonInstanceModel.KEY_START in self):
            raise Exception()
        epStart = ConvertLocalTimeStringToEpochTime(
            self[JsonInstanceModel.KEY_START])
        return epStart

    def SetEndFromEpochTime(self, end):
        if (end.__class__ != int) and (end.__class__ != float):
            raise Exception()
        epStart = self.GetStartAsEpochTime()
        if epStart == None:
            raise Exception()
        if end < epStart:
            raise Exception()
        self[JsonInstanceModel.KEY_END] = \
            ConvertEpochTimeToLocalTimeString(end)

    def GetEndAsEpochTime(self):
        if not (KEY_END in self):
            raise Exception()
        epEnd = ConvertLocalTimeStringToEpochTime(
            self[JsonInstanceModel.KEY_END])

    def GetJsonString(self):
        return json.dumps(self)

class JsonSignal(JsonInstanceModel):
    def __init__(self):
        return

class JsonNoise(JsonInstanceModel):
    def __init__(self):
        return

class JsonAnomaly(JsonInstanceModel):
    def __init__(self):
        return

class JsonMetric(dict):
    KEY_NAME       = "name"
    KEY_CATEGORY   = "category"
    KEY_SIGNALS    = "signals"
    KEY_NOISES     = "noises"
    KEY_ANOMALIES  = "anomalies"
    KEY_DATAPOINTS = "datapoints"

    #Required key
    KEY_START     = "start"
    KEY_END       = "end"
    KEY_RESOLUTION= "resolution"

    def __init__(self):
        self.clear()
        self[JsonMetric.KEY_SIGNALS] = []
        self[JsonMetric.KEY_NOISES] = []
        self[JsonMetric.KEY_ANOMALIES] = []
        self[JsonMetric.KEY_DATAPOINTS] = []

        #Unserialized members
        self.epStart = None
        self.epEnd = None
        self.epRes = None

    def CopyKeyValue(self, tempDict, key, object_type = None):
        if key in tempDict:
            self[key] = tempDict[key]

    def InitFromString(self, jsonStr):
        tempDict = json.load(jsonStr)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_NAME)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_CATEGORY)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_SIGNALS, JsonSignal)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_NOISES, JsonNoise)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_ANOMALIES, JsonAnomaly)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_DATAPOINTS)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_START)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_END)
        self.CopyKeyValue(tempDict, JsonMetric.KEY_RESOLUTION)

    def CheckTimeSpanKeys(self):
        if not JsonMetric.KEY_START in self:
            return False
        if not JsonMetric.KEY_END in self:
            return False
        if not JsonMetric.KEY_RESOLUTION in self:
            return False
        return True

    def SetTimeSpan(self, epStart, epEnd, epRes):
        self[JsonMetric.KEY_START] = \
            ConvertEpochTimeToLocalTimeString(epStart)
        self.epStart = epStart

        self[JsonMetric.KEY_END] = \
            ConvertEpochTimeToLocalTimeString(epEnd)
        self.epEnd = epEnd

        self[JsonMetric.KEY_RESOLUTION] =  epRes
        self.epRes = epRes

    def GetTimeSpan(self):
        #TODO: Work on this

    def SetName(self, name):
        if name.__class__ != str:
            raise Exception()
        self[JsonMetric.KEY_NAME] = name

    def GetName(self):
        if JsonMetric.KEY_NAME in self:
            return self[JsonMetric.KEY_NAME]
        return None

    def SetCategory(self, category):
        if category.__class__ != str:
            raise Exception()
        self[JsonMetric.KEY_CATEGORY] = category

    def GetCategory(self):
        if JsonMetric.KEY_CATEGORY in self:
            return self[JsonMetric.KEY_CATEGORY]
        return None

    def AddSignal(self, signal):
        if (signal.__class__ != JsonSignal):
            raise Exception()
        self[JsonMetric.KEY_SIGNALS].append(signal)

    def GetSignal(self, index):
        signals = self[JsonMetric.KEY_SIGNALS]
        if index > len(signals) - 1 or index < 0:
            return None
        return signals[index]

    def AddNoise(self, noise):
        if (noise.__class__ != JsonNoise):
            raise Exception()
        self[JsonMetric.KEY_NOISES].append(noise)

    def GetNoise(self, index):
        noises = self[JsonMetric.KEY_NOISES]
        if index > len(noises) - 1 or index < 0:
            return None
        return noises[index]

    def AddAnomaly(self, anomaly):
        if (anomaly.__class__ != JsonAnomaly):
            raise Exception()
        self[JsonMetric.KEY_ANOMALIES].append(anomaly)

    def GetAnomaly(self, index):
        anomalies = self[JsonMetric.KEY_ANOMALIES]
        if index > len(anomalies) - 1 or index < 0:
            return None
        return anomalies[index]

    def AddSingleDatapoint(self, epochTime, value):
        if not self.CheckTimeSpanKeys():
            raise Exception()
        lastIdx = len(self[JsonMetric.KEY_DATAPOINTS]) - 1
        if (lastIdx >= 0):
            lastEpTime = ConvertLocalTimeStringToEpochTime(\
                (self[JsonMetric.KEY_DATAPOINTS][lastIdx][0]))
            if (epochTime - lastEpTime != self.epRes):
                raise Exception()
        else:
            if (epochTime != self.epStart):
                raise Exception()
        localTimeStr = ConvertEpochTimeToLocalTimeString(epochTime)
        self[JsonMetric.KEY_DATAPOINTS].append((localTimeStr, value))

    def GetJsonString(self):
        return json.dumps(self)

class JsonMetricList(list):
    def __init__(self):
        self.clear()

    def AddMetric(self, metric):
        if (metric.__class__ != JsonMetric):
            raise Exception()
        self.append(metric)

    def GetMetric(self, index):
        if index > len(self) - 1 or index < 0:
            return None
        return self[index]

    def GetJsonString(self):
        return json.dumps(self)
        

if __name__ == "__main__":
    signal = JsonSignal()
    signal.SetName("Test Signal")
    signal.SetStartFromEpochTime(0)

    noise = JsonNoise()
    noise.SetName("Test Noise")
    noise.SetStartFromEpochTime(1000)
    noise.SetEndFromEpochTime(2000)

    anomaly = JsonAnomaly()
    anomaly.SetName("Deviation")
    anomaly.SetStartFromEpochTime(3000)
    anomaly.SetEndFromEpochTime(7000)

    metric = JsonMetric()
    metric.SetName("TestMetric")
    metric.AddSignal(signal)
    metric.AddNoise(noise)
    metric.AddAnomaly(anomaly)

    metricList = JsonMetricList()
    metricList.AddMetric(metric)

    print(metricList.GetJsonString())
    

