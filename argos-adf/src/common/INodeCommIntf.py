class INodeCommIntf:

    dataservers = "Dataservers"
    nodereg     = "NodeReg"
    delimiter   = ":"

    class NodeTypeEnum:
        Data    = 0
        Feeder  = 1
        Process = 2
        Action  = 3

    class NodeRegistrationData:
        def __init__(self):
            self._type     = None
            self._hostname = None
            self._port     = None
            self._osPID    = None

    def RegisterNodeSpace(self):
        self.RegisterNodeSpaceImpl()
    def RegisterNodeSpaceImpl(self):
        raise NotImplementedError

    def RegisterNode(self, regData):
        self.RegisterNodeImpl(regData)
    def RegisterNodeImpl(self, regData):
        raise NotImplementedError

    def HandleRequestLoop(self):
        self.HandleRequestLoopImpl()
    def HandleRequestLoopImpl(self):
        raise NotImplementedError

    def ExitRequestLoop(self):
        self.ExitRequestLoopImpl()
    def ExitRequestLoopImpl(self):
        raise NotImplementedError

    def RegisterChannel(self, nodeName, channelName):
        self.RegisterChannelImpl(nodeName, channelName)
    def RegisterChannelImpl(self):
        raise NotImplementedError

    def SetChannelBufferSize(self, nodeName, channelName, bufferSize):
        self.SetChannelBufferSizeImpl(nodeName, channelName, bufferSize)
    def SetChannelBufferSizeImpl(self, nodeName, channelName, bufferSize):
        raise NotImplementedError

    def AddDatapointToChannel(self, nodeName, channelName, data):
        self.AddDatapointToChannelImpl(nodeName, channelName, data)
    def AddDatapointToChannelImpl(self, nodeName, channelName, data):
        raise NotImplementedError

    def RetrieveDatapointListFromChannel(self, nodeName, channelName):
        return self.RetrieveDatapointListFromChannelImpl(nodeName, channelName)
    def RetrieveDatapointListFromChannelImpl(self):
        raise NotImplementedError
