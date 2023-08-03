class ArProgArg:
    argPrefixS  = "-"
    argPrefixL  = "--"
    argHostS    = "h"
    argHostL    = "host"
    argPortS    = "p"
    argPortL    = "port"
    argNonRootL = "non-root"
    argConfigFileS = "c"
    argConfigFileL = "config"
    argTopologyFileS = "t"
    argTopologyFileL = "topology"
    argFeederNameL  = "feeder-name"
    argProcessNameL = "process-name"
    argActionNameL  = "action-name"

    class WorkingSet:
        def __init__(self, argv):
            self._argv = argv
            self._argc = len(argv)
            self._index = 1

    def __init__(self):
        self._funcMapS = \
        {
            ArProgArg.argHostS:self.SetArOpt_Host,
            ArProgArg.argPortS:self.SetArOpt_Port,
            ArProgArg.argConfigFileS:self.SetArOpt_ConfigFile,
            ArProgArg.argTopologyFileS:self.SetArOpt_TopologyFile
        }

        self._funcMapL = \
        {
            ArProgArg.argHostL: self.SetArOpt_Host,
            ArProgArg.argPortL: self.SetArOpt_Port,
            ArProgArg.argNonRootL: self.SetArOpt_NonRoot,
            ArProgArg.argConfigFileL: self.SetArOpt_ConfigFile,
            ArProgArg.argTopologyFileL: self.SetArOpt_TopologyFile,
            ArProgArg.argFeederNameL: self.SetArOpt_FeederName,
            ArProgArg.argProcessNameL: self.SetArOpt_ProcessName,
            ArProgArg.argActionNameL: self.SetArOpt_ActionName
        }

    def SetArOpt_Host(self, workingSet):
        if (workingSet._index >= workingSet._argc - 1):
            raise Exception()
        self._host = workingSet._argv[workingSet._index + 1]
        workingSet._index += 2

    def SetArOpt_Port(self, workingSet):
        if (workingSet._index >= workingSet._argc - 1):
            raise Exception()
        self._port = workingSet._argv[workingSet._index + 1]
        workingSet._index += 2

    def SetArOpt_NonRoot(self, workingSet):
        self._isRoot = False
        if (workingSet._index >= workingSet._argc - 1):
            raise Exception()
        self._nonRootStep = workingSet._argv[workingSet._index + 1]
        workingSet._index += 2

    def SetArOpt_ConfigFile(self, workingSet):
        if (workingSet._index >= workingSet._argc - 1):
            raise Exception()
        self._configFile = workingSet._argv[workingSet._index + 1]
        workingSet._index += 2

    def SetArOpt_TopologyFile(self, workingSet):
        if (workingSet._index >= workingSet._argc - 1):
            raise Exception()
        self._topologyFile = workingSet._argv[workingSet._index + 1]
        workingSet._index += 2

    def SetArOpt_FeederName(self, workingSet):
        if (workingSet._index >= workingSet._argc - 1):
            raise Exception()
        self._feederName = workingSet._argv[workingSet._index + 1]
        workingSet._index += 2

    def SetArOpt_ProcessName(self, workingSet):
        if (workingSet._index >= workingSet._argc - 1):
            raise Exception()
        self._processName = workingSet._argv[workingSet._index + 1]
        workingSet._index += 2

    def SetArOpt_ActionName(self, workingSet):
        if (workingSet._index >= workingSet._argc - 1):
            raise Exception()
        self._actionName = workingSet._argv[workingSet._index + 1]
        workingSet._index += 2

    def Parse(self, argv):
        self.workingSet = ArProgArg.WorkingSet(argv)
        self._executable = self.workingSet._argv[0]
        while(self.workingSet._index < self.workingSet._argc):
            str = self.workingSet._argv[self.workingSet._index]
            if str.startswith(ArProgArg.argPrefixL):
                val = str[2:]
                if (val in self._funcMapL):
                    self._funcMapL[val](self.workingSet)
                else:
                    raise Exception()
            elif str.startswith(ArProgArg.argPrefixS):
                val = str[1:]
                if (val in self._funcMapS):
                    self._funcMapS[val](self.workingSet)
                else:
                    raise Exception()
            else:
                raise Exception()

    def GetExecutable(self):
        try:
            exec = self._executable
        except AttributeError:
            exec = None
        return exec

    def GetHost(self):
        try:
            host = self._host
        except AttributeError:
            host = None
        return host

    def GetPort(self):
        try:
            port = self._port
        except AttributeError:
            port = None
        return port

    def IsRoot(self):
        try:
            isRoot = self._isRoot
        except AttributeError:
            isRoot = True
        return isRoot

    def GetNonRootStep(self):
        try:
            step = self._nonRootStep
        except AttributeError:
            step = "-1"
        return int(step)

    def GetConfigFile(self):
        try:
            configFile = self._configFile
        except AttributeError:
            configFile = None
        return configFile

    def GetTopologyFile(self):
        try:
            topologyFile = self._topologyFile
        except AttributeError:
            topologyFile = None
        return topologyFile

    def GetFeederName(self):
        try:
            feederName = self._feederName
        except AttributeError:
            feederName = None
        return feederName

    def GetProcessName(self):
        try:
            processName = self._processName
        except AttributeError:
            processName = None
        return processName

    def GetActionName(self):
        try:
            actionName = self._actionName
        except AttributeError:
            actionName = None
        return actionName



