import time
import Pyro4
from GlobalConfig import *
from INodeChannelImpl import *
from INodeCommIntf import *
from NodeReg import *

class INodeCommImpl(INodeCommIntf):
    def __init__(self, currentHostname, globalConfig):
        if (globalConfig.__class__ != GlobalConfig):
            raise Exception()

        nameserverListTemp = globalConfig.GetPyroNameserverList()
        self._nameserverList = []
        for i in range(0, len(nameserverListTemp)):
            try:
                ns = Pyro4.locateNS(nameserverListTemp[i].hostname,
                                    int(nameserverListTemp[i].port))
                self._nameserverList.append(ns)
            except Exception as e:
                raise Exception()

        Pyro4.expose(Datapoint)
        exposedDatapoint = self._daemon = Pyro4.Daemon(currentHostname)
        self._daemon.register(exposedDatapoint)
        self._channelMap = {}

    def GetObjectName(self, namespace, objectName):
        return str(namespace) +\
               str(INodeCommIntf.delimiter) +\
               str(objectName)

    def Lookup(self, namespace, objectName):
        lookupName = self.GetObjectName(namespace, objectName)
        uri = None
        for i in range(0, len(self._nameserverList)):
            ns = self._nameserverList[i]
            uri = ns.lookup(lookupName, return_metadata=False)
            if (uri != None):
                break;
        if (uri != None):
            obj = Pyro4.Proxy(uri)
        else:
            obj = None
        return obj

    def InitializeDataserverNode(self):
        uri = self._daemon.register(NodeReg)
        for i in range(0, len(self._nameserverList)):
            ns = self._nameserverList[i]
            ns.register(self.GetObjectName(INodeCommIntf.dataservers, INodeCommIntf.nodereg), uri)

    def RegisterNodeSpaceImpl(self):
        pass

    def RegisterNodeImpl(self, regData):
        nodeReg = self.Lookup(INodeCommIntf.dataservers, INodeCommIntf.nodereg)
        print(nodeReg)
        pass

    def HandleRequestLoopImpl(self):
        self._daemon.requestLoop()

    def ExitRequestLoopImpl(self):
        self._daemon.shutdown()

    def BuildChannelID(self, nodeName, channelName):
        return str(nodeName) + ":" + str(channelName)

    def RegisterChannelImpl(self, nodeName, channelName):
        channelID = self.BuildChannelID(nodeName, channelName)
        channel = INodeChannelImpl(channelID)
        self._channelMap[channelID] = channel

        #Register the channel with Pyro4 nameservers
        uri = self._daemon.register(channel)
        for ns in self._nameserverList:
            ns.register(channelID, uri)

    def SetChannelBufferSizeImpl(self, nodeName, channelName, bufferSize):
        channelID = self.BuildChannelID(nodeName, channelName)
        channel = self._channelMap[channelID]
        channel.SetBufferSize(bufferSize)
        print("Setting channel buffer to "+str(bufferSize))

    def AddDatapointToChannelImpl(self, nodeName, channelName, datapoint):
        channelID = self.BuildChannelID(nodeName, channelName)
        if (datapoint.__class__ != Datapoint):
            raise Exception()

        #TODO: We can optimize for local operation here
        #if (channelID in self._channelMap):
        #    channel = self._channelMap[channelID]
        #    channel.AddDatapoint(datapoint.epochTime, datapoint.value)

        channel = None
        for ns in self._nameserverList:
            uri = ns.lookup(channelID)
            if (uri != None):
                channel = Pyro4.Proxy(uri)
                break;
        return channel.AddDatapoint(datapoint.epochTime, datapoint.value)

    def RetrieveDatapointListFromChannelImpl(self, nodeName, channelName):
        channelID = self.BuildChannelID(nodeName, channelName)
        #if (not channelID in self._channelMap):
        #    return None

        #TODO: We can optimize for local operation here

        channel = None
        for ns in self._nameserverList:
            uri = ns.lookup(channelID)
            if (uri != None):
                channel = Pyro4.Proxy(uri)
                break;

        [epochTimeList, valueList] = channel.RetriveDatapointList()
        if len(epochTimeList) != len(valueList):
            time.sleep(1)
            [epochTimeList_retry, valueList_retry] = channel.RetriveDatapointList()
            if len(epochTimeList_retry) != len(valueList_retry):
                print("EpochTimeList: " + str(len(epochTimeList)) + " / " + "ValueList: " + str(len(valueList)))
                #TODO: This seems to cause problem in the case that the lengths of the lists are not the same
                #TODO: Don't know yet why this happens; should investigate. Maybe using Pyro's SynchronizeObject
                #raise Exception()

        datapointList = []
        for i in range(0, len(epochTimeList)):
            datapointList.append(Datapoint(epochTimeList[i], valueList[i]))

        return datapointList

