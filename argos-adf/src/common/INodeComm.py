from INodeCommImpl import *

class INodeComm(INodeCommImpl):
    def __init__(self, currentHostname, globalConfig):
        INodeCommImpl.__init__(self, currentHostname, globalConfig)