import json

class PyroNameServer:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

class PyroDataserver:
    def __init__(self, hostname):
        self.hostname = hostname

class FeederNode:
    def __init__(self):
        self.name = None
        self.hostname = None
        self.metric = None
        self.path = None

class FeederEndPointEnum:
    Graphite = 0
    ArCSV = 1

class ProcessNode:
    class InputType:
        feeder = 0
        process = 1
    class Input:
        def __init__(self):
            self.type = None
            self.name = None
            self.pollInterval = None
            self.bufferSize = None
    def __init__(self):
        self.name = None
        self.hostname = None
        self.path = None
        self.inputFeederList = []
        self.inputProcessList = []
        self.parameters = None

class ActionNode:
    class InputType:
        feeder = 0
        process = 1
    class Input:
        def __init__(self):
            self.type = None
            self.name = None
            self.pollInterval = None
            self.bufferSize = None
    def __init__(self):
        self.name = None
        self.hostname = None
        self.path = None
        self.inputFeederList = []
        self.inputProcessList = []
        self.slackIsEnable = False
        self.slackToken = ""
        self.slackChannel = ""
        self.saveAnomalyImage = False
        self.anomalyImagePath = "./"

class ConfigConstant:
    ########## Pyro4 ##########
    pyro                 = "Pyro"
    pyro_nameserver_path = "NameserverPath"
    pyro_nameservers     = "Nameservers"
    pyro_hostname        = "Hostname"
    pyro_port            = "Port"
    pyro_hosts           = "Hosts"
    pyro_dataserver_path = "DataserverPath"
    pyro_dataservers     = "Dataservers"
    ########## Python ##########
    python            = "Python"
    python_executable = "Executable"
    ########## SSH ##########
    ssh            = "SSH"
    ssh_executable = "Executable"
    ########## Feeders ##########
    feeders               = "Feeders"
    feeders_list          = "List"
    feeders_hostname      = "Hostname"
    feeders_path          = "Path"
    feeders_type          = "Type"
    feeders_typeDict      = \
    {
        "Graphite":FeederEndPointEnum.Graphite,
        "ArCSV":FeederEndPointEnum.ArCSV
    }
    feeders_endpoint      = "Endpoint"
    feeders_address       = "Address"
    feeders_startLookback = "Start_lookback"
    feeders_timelag       = "Time-lag"
    feeders_file          = "File"
    feeders_pollInterval  = "Poll_interval"
    feeders_replaySpeed   = "Replay_speed"
    feeders_replayOffset  = "Replay_offset"
    ########## Processes ##########
    processes                              = "Processes"
    processes_list                         = "List"
    processes_hostname                     = "Hostname"
    processes_path                         = "Path"
    processes_input                        = "Input"
    processes_input_feeders                = "Feeders"
    processes_input_feeders_name           = "Name"
    processes_input_feeders_pollInteval    = "Poll_interval"
    processes_input_feeders_bufferSize     = "Buffer_size"
    processes_input_processes              = "Processes"
    processes_input_processes_name         = "Name"
    processes_input_processes_pollInterval = "Poll_interval"
    processes_input_processes_bufferSize   = "Buffer_size"
    processes_parameters                   = "Parameters"
    ########## Actions ##########
    actions                                = "Actions"
    actions_list                           = "List"
    actions_hostname                       = "Hostname"
    actions_path                           = "Path"
    actions_input                          = "Input"
    actions_input_feeders                  = "Feeders"
    actions_input_feeders_name             = "Name"
    actions_input_feeders_pollInteval      = "Poll_interval"
    actions_input_feeders_bufferSize       = "Buffer_size"
    actions_input_processes                = "Processes"
    actions_input_processes_name           = "Name"
    actions_input_processes_pollInterval   = "Poll_interval"
    actions_input_processes_bufferSize     = "Buffer_size"
    actions_slack                          = "Slack"
    actions_slack_enable                   = "Enable"
    actions_slack_token                    = "SlackToken"
    actions_slack_channel                  = "SlackChannel"
    actions_anomalyReport                  = "AnomalyReport"
    actions_anomalyReport_saveAnomalyImage = "SaveAnomalyImage"
    actions_anomalyReport_imagePath        = "ImagePath"

class GlobalConfig:
    def __init__(self, filename):
        fh = open(filename, 'r')
        fContent = fh.read()
        fh.close()
        self._configMap = json.loads(fContent, encoding='utf-8')

    ########## Pyro4 ##########
    def GetPyroNameserverPath(self):
        return self._configMap[ConfigConstant.pyro][ConfigConstant.pyro_nameserver_path]

    def GetPyroNameserverList(self):
        nsList = self._configMap[ConfigConstant.pyro][ConfigConstant.pyro_nameservers]
        retNsList = []

        for i in range(0, len(nsList)):
            retNsList.append(PyroNameServer(nsList[i][ConfigConstant.pyro_hostname],\
                                            nsList[i][ConfigConstant.pyro_port]))
        return retNsList

    def GetPyroHostList(self):
        hostList = self._configMap[ConfigConstant.pyro][ConfigConstant.pyro_hosts]
        return hostList

    def GetPyroDataserverPath(self):
        return self._configMap[ConfigConstant.pyro][ConfigConstant.pyro_dataserver_path]

    def GetPyroDataserverList(self):
        dsList = self._configMap[ConfigConstant.pyro][ConfigConstant.pyro_dataservers]
        retDsList = []

        for i in range(0, len(dsList)):
            retDsList.append(PyroDataserver(dsList[i][ConfigConstant.pyro_hostname]))
        return retDsList

    ########## Python ##########
    def GetPythonExecutable(self):
        pythonExec = self._configMap[ConfigConstant.python][ConfigConstant.python_executable]
        return pythonExec

    ########## SSH ##########
    def GetSSHExecutable(self):
        sshExec = self._configMap[ConfigConstant.ssh][ConfigConstant.ssh_executable]
        return sshExec

    ########## Feeders ##########
    def GetFeederListByHostname(self, hostname):
        feederList = []
        allFeederList = self._configMap[ConfigConstant.feeders][ConfigConstant.feeders_list]
        for feederName in allFeederList:
            feeder = self._configMap[ConfigConstant.feeders][feederName]
            fHostname = feeder[ConfigConstant.feeders_hostname]
            fPath = feeder[ConfigConstant.feeders_path]
            if (fHostname == hostname):
                f = FeederNode()
                f.name = feederName
                f.hostname = fHostname
                f.path = fPath
                feederList.append(f)
        return feederList

    def GetFeederType(self, feederName):
        type = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_type]
        if type in ConfigConstant.feeders_typeDict:
            return ConfigConstant.feeders_typeDict[type]
        else:
            return None

    def GetFeederEndpoint(self, feederName):
        endpoint = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_endpoint]
        return endpoint

    def GetFeederAddress(self, feederName):
        address = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_address]
        return address

    def GetFeederStartLookback(self, feederName):
        startLookback = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_startLookback]
        return int(startLookback)

    def GetFeederTimelag(self, feederName):
        timelag = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_timelag]
        return int(timelag)

    def GetFeederPollInterval(self, feederName):
        pollInterval = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_pollInterval]
        return float(pollInterval)

    def GetFeederReplaySpeed(self, feederName):
        replaySpeed = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_replaySpeed]
        return int(replaySpeed)

    def GetFeederReplayOffset(self, feederName):
        replayOffset = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_replayOffset]
        return int(replayOffset)

    def GetFeederFile(self, feederName):
        file = self._configMap[ConfigConstant.feeders][feederName][ConfigConstant.feeders_file]
        return file

    ########## Processes ##########
    def GetProcessByName(self, processName):
        rawProcess = self._configMap[ConfigConstant.processes][processName]
        process = ProcessNode()
        process.name     = processName
        process.hostname = rawProcess[ConfigConstant.processes_hostname]
        process.path     = rawProcess[ConfigConstant.processes_path]

        for entry in rawProcess[ConfigConstant.processes_input][ConfigConstant.processes_input_feeders]:
            inputFeeder = ProcessNode.Input()
            inputFeeder.type         = ProcessNode.InputType.feeder
            inputFeeder.name         = entry[ConfigConstant.processes_input_feeders_name]
            inputFeeder.pollInterval = entry[ConfigConstant.processes_input_feeders_pollInteval]
            inputFeeder.bufferSize   = entry[ConfigConstant.processes_input_feeders_bufferSize]
            process.inputFeederList.append(inputFeeder)

        for entry in rawProcess[ConfigConstant.processes_input][ConfigConstant.processes_input_processes]:
            inputProcesses = ProcessNode.InputType.process
            inputProcesses = ProcessNode.Input()
            inputProcesses.name  = entry[ConfigConstant.processes_input_processes_name]
            inputProcesses.pollInterval = entry[ConfigConstant.processes_input_processes_pollInterval]
            inputProcesses.bufferSize = entry[ConfigConstant.processes_input_processes_bufferSize]
            process.inputProcessList.append(inputProcesses)

        process.parameters = rawProcess[ConfigConstant.processes_parameters]

        return process

    def GetProcessListByHostname(self, hostname):
        processList = []
        allProcessList = self._configMap[ConfigConstant.processes][ConfigConstant.processes_list]

        for processName in allProcessList:
            process = self.GetProcessByName(processName)
            if (process.hostname == hostname):
                processList.append(process)

        return processList

    ########## Actions ##########
    def GetActionByName(self, actionName):
        rawAction = self._configMap[ConfigConstant.actions][actionName]
        action = ActionNode()
        action.name     = actionName
        action.hostname = rawAction[ConfigConstant.actions_hostname]
        action.path     = rawAction[ConfigConstant.actions_path]

        for entry in rawAction[ConfigConstant.actions_input][ConfigConstant.actions_input_feeders]:
            inputFeeder = ActionNode.Input()
            inputFeeder.type         = ActionNode.InputType.feeder
            inputFeeder.name         = entry[ConfigConstant.actions_input_feeders_name]
            inputFeeder.pollInterval = entry[ConfigConstant.actions_input_feeders_pollInteval]
            inputFeeder.bufferSize   = entry[ConfigConstant.actions_input_feeders_bufferSize]
            action.inputFeederList.append(inputFeeder)

        for entry in rawAction[ConfigConstant.actions_input][ConfigConstant.actions_input_processes]:
            inputProcesses = ActionNode.Input()
            inputProcesses.type = ActionNode.InputType.process
            inputProcesses.name  = entry[ConfigConstant.actions_input_processes_name]
            inputProcesses.pollInterval = entry[ConfigConstant.actions_input_processes_pollInterval]
            inputProcesses.bufferSize = entry[ConfigConstant.actions_input_processes_bufferSize]
            action.inputProcessList.append(inputProcesses)

        #Slack
        action.slackIsEnable = rawAction[ConfigConstant.actions_slack][ConfigConstant.actions_slack_enable]
        action.slackToken    = rawAction[ConfigConstant.actions_slack][ConfigConstant.actions_slack_token]
        action.slackChannel  = rawAction[ConfigConstant.actions_slack][ConfigConstant.actions_slack_channel]

        #Anomaly reporting
        action.saveAnomalyImage = rawAction[ConfigConstant.actions_anomalyReport][ConfigConstant.actions_anomalyReport_saveAnomalyImage]
        action.anomalyImagePath = rawAction[ConfigConstant.actions_anomalyReport][ConfigConstant.actions_anomalyReport_imagePath]

        return action

    def GetActionListByHostname(self, hostname):
        actionList = []
        allActionList = self._configMap[ConfigConstant.actions][ConfigConstant.actions_list]
        for actionName in allActionList:
            action = self.GetActionByName(actionName)
            print (actionName + " : " + str(action))
            if (action.hostname == hostname):
                actionList.append(action)
        return actionList
