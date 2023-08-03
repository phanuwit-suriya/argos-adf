import os
import subprocess
import platform
import sys

sys.path.append('../common')
from GlobalConfig import ConfigConstant

def CallPS(split=True):
    if platform.system() != 'Linux':
        os.system(
            'echo "HealthChecker needs ps command that not support in your Operating System!"')
        return

    proc = subprocess.Popen(
        ['ps', 'x', '-o' '%a'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, _ = proc.communicate()

    formatedOutputs = []
    lines = out.decode('utf-8').split('\n')[1: -2]

    try:
        if split:
            formatedOutputs = [line.split(' ') for line in lines]
        else:
            formatedOutputs = [line for line in lines]
    except IndexError as error:
        os.system(error)

    return formatedOutputs

class NodeSet:

    def __init__(self, feederList=[], processList=[], actionList=[]):
        self.feeders = set(feederList)
        self.processes = set(processList)
        self.actions = set(actionList)

    def __repr__(self):
        return 'Feeders: %s\nProcesses: %s\nActions: %s\n' % (self.feeders, self.processes, self.actions)


class HealthChecker:

    def __init__(self, gConfig, progArg, startFeeders, startProcesses, startActions):
        self._gConfig = gConfig
        self._progArg = progArg
        self._startFeeders = startFeeders
        self._startProcesses = startProcesses
        self._startActions = startActions

        self._feederPrefix = progArg.argPrefixL + progArg.argFeederNameL
        self._processPrefix = progArg.argPrefixL + progArg.argProcessNameL
        self._actionPrefix = progArg.argPrefixL + progArg.argActionNameL
        self._nodeNamePrefix = [self._feederPrefix,
                                self._processPrefix, self._actionPrefix]

    def getNodeNames(self):
        configMap = self._gConfig._configMap
        return (
            set(configMap[ConfigConstant.feeders]
                [ConfigConstant.feeders_list]),
            set(configMap[ConfigConstant.processes]
                [ConfigConstant.processes_list]),
            set(configMap[ConfigConstant.actions]
                [ConfigConstant.actions_list]),
        )

    def GetHostName(self, line):
        progArg = self._progArg

        try:
            testStr = progArg.argPrefixL + progArg.argHostL
            hostIndex = line.index(testStr) + 1
            return line[hostIndex]
        except ValueError:
            return None

    def GetRunningNodeNameGroupByHosts(self):
        hosts = {}

        for line in CallPS():
            hostName = self.GetHostName(line)

            if hostName is None:
                continue

            hosts.setdefault(hostName, NodeSet())

            if self._feederPrefix in line:
                feederName = line[line.index(self._feederPrefix) + 1]
                hosts.get(hostName).feeders.add(feederName)
            elif self._processPrefix in line:
                processName = line[line.index(self._processPrefix) + 1]
                hosts.get(hostName).processes.add(processName)
            elif self._actionPrefix in line:
                actionName = line[line.index(self._actionPrefix) + 1]
                hosts.get(hostName).actions.add(actionName)
            else:
                continue
        return hosts

    def printExitedNode(self, type, exitedNodeNames):
        totalExitedNode = len(exitedNodeNames)
        print(('Total exited %s = %d nodes.' %
                   (type, totalExitedNode)))
        if totalExitedNode:
            print('%s' % exitedNodeNames)

    def start(self):
        print('%s' % str('=' * 30))
        print('Health Checking')
        print('%s' % str('=' * 30))

        progArg, gConfig = self._progArg, self._gConfig

        startFeeders = self._startFeeders
        startProcesses = self._startProcesses
        startActions = self._startActions

        hosts = self.GetRunningNodeNameGroupByHosts()

        for hostName, runningNodeNames in hosts.items():

            feeders = gConfig.GetFeederListByHostname(hostName)
            processes = gConfig.GetProcessListByHostname(hostName)
            actions = gConfig.GetActionListByHostname(hostName)

            feederNames = set([ f.name for f in feeders ])
            processeNames = set([ p.name for p in processes ])
            actionNames = set([ a.name for a in actions ])

            exitedFeederNames = feederNames.difference(runningNodeNames.feeders)
            exitedProcesseNames = processeNames.difference(runningNodeNames.processes)
            exitedActionNames = actionNames.difference(runningNodeNames.actions)

            self.printExitedNode(type='Feeders', exitedNodeNames=exitedFeederNames)
            self.printExitedNode(type='Processes', exitedNodeNames=exitedProcesseNames)
            self.printExitedNode(type='Actions', exitedNodeNames=exitedActionNames)

            isExistIn = (lambda exitedSet: (lambda node: node.name in exitedSet))

            exitedFeeders = list(filter(isExistIn(exitedFeederNames), feeders))
            exitedProcesses = list(filter(isExistIn(exitedProcesseNames), processes))
            exitedActions = list(filter(isExistIn(exitedActionNames), actions))

            startFeeders(host=hostName, feederList=exitedFeeders)
            startProcesses(host=hostName, processList=exitedProcesses)
            startActions(host=hostName, actionList=exitedActions)
