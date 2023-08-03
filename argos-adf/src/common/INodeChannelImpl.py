import Pyro4
from Datapoint import *

@Pyro4.expose
class INodeChannelImpl:

    def __init__(self, channelName):
        self._name = channelName
        self._bufferSize = 1000000
        self._epochTimeList = []
        self._valueList = []

    def SetBufferSize(self, size):
        self._bufferSize = size

    def AddDatapoint(self, epochTime, value):

        if (epochTime == None) or (value == None):
            return

        self._epochTimeList.append(epochTime)
        self._valueList.append(value)

        itemCount = len(self._valueList)
        removeCount = 0
        if (itemCount > self._bufferSize):
            removeCount = itemCount - self._bufferSize

        if (removeCount > 0):
            del self._epochTimeList[0:removeCount - 1]
            del self._valueList[0:removeCount - 1]

    def RetriveDatapointList(self):
        return [self._epochTimeList, self._valueList]
