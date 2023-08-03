import os
import platform
import sys
import time
import subprocess

from HealthChecker import HealthChecker

sys.path.append('../common')
from ArProgArg import *
from ArUtils import *

class Starter:
    def __init__(self, progArg):
        self._isRoot = True

        self._progArg = progArg
        self._configFile = self._progArg.GetConfigFile()
        if (self._configFile == None):
            self._configFile = '../common/config_template.json'

        self._gConfig = GlobalConfig(self._configFile)
        self._arUtils = ArUtils(self._gConfig)

        self._nsList = self._gConfig.GetPyroNameserverList()
        self._hostList = self._gConfig.GetPyroHostList()

        self._pyExec = self._gConfig.GetPythonExecutable()

        if (self._progArg.IsRoot()):
            self.RootProcedure()
        else:
            step = self._progArg.GetNonRootStep()
            self.NonRootProcedure(step)

    ########## Root ##########
    def RootProcedure(self):
        # Start non-root starters remotely here
        allHostList = {}
        for i in range(0, len(self._hostList)):
            allHostList[self._hostList[i]] = self._hostList[i]
        for i in range(0, len(self._nsList)):
            allHostList[self._nsList[i].hostname] = self._nsList[i].hostname

        arUtils = self._arUtils
        gConfig = self._gConfig

        nonRootOpt = " " + ArProgArg.argPrefixL + ArProgArg.argNonRootL
        hostOpt = " " + ArProgArg.argPrefixL + ArProgArg.argHostL
        configOpt = " " + ArProgArg.argPrefixL + ArProgArg.argConfigFileL
        exec = " " + progArg.GetExecutable()
        if (exec == None):
            raise Exception()

        # Start the first step of non-root starter
        maxNonRootStep = 5
        for step in range(0, maxNonRootStep):
            stepStr = " " + str(step) + " "
            baseCmd = gConfig.GetPythonExecutable() + exec + nonRootOpt + stepStr +\
                configOpt + " " + self._configFile + hostOpt
            for (key, value) in allHostList.items():
                cmd = baseCmd + " " + key
                print("[Root Starter]: Starting non-root starter [" +
                      str(step) + "] on: " + key)
                print("CMD: %s" % cmd)
                ##### NOTE: THERE IS A KNOWN ISSUE THAT WHEN STARTER FORKS NODES THROUGH SSH, AN ACTION WILL NOT BE ABLE TO SAVE IMAGES OF ANOMALIES #####
                #arUtils.ForkRemoteOSProcess(cmd, key)
                arUtils.ForkLocalOSProcess(cmd)

            # Make sure all instances started in the 1st step have already initiated properly
            time.sleep(0.2)

    ########## Non-root ##########
    def IsAbsolutePath(self, path):
        return path.startswith("/")

    def NonRootProcedure(self, step):
        host = self._progArg.GetHost()
        if (host == None):
            raise Exception()
        print("I am non-root starter running on: " + host)
        if (step == 0):
            self.StartPyroNameserver(host)
        elif (step == 1):
            self.StartPyroDataserver(host)
        elif (step == 2):
            self.StartFeederNodes(host)
        elif (step == 3):
            self.StartProcessNodes(host)
        elif (step == 4):
            self.StartActionNodes(host)

    def StartPyroDataserver(self, host):
        print('Starting Dataservers...')
        # Start dataserver processes locally
        arUtils = self._arUtils
        gConfig = self._gConfig

        # Resolve absolute path for config file
        configPathTemp = self._configFile
        if (not self.IsAbsolutePath(configPathTemp)):
            curAbsPath = os.getcwd() + "/"
        else:
            curAbsPath = ""
        configFilePath = " " + curAbsPath + configPathTemp

        # Resolve absolute path for dataserver file
        dataserverPathTemp = gConfig.GetPyroDataserverPath()
        if (not self.IsAbsolutePath(dataserverPathTemp)):
            curAbsPath = os.getcwd() + "/"
        else:
            curAbsPath = ""
        dataserverPath = " " + curAbsPath + dataserverPathTemp

        hostOpt = " " + ArProgArg.argPrefixL + ArProgArg.argHostL + " " + host
        configOpt = " " + ArProgArg.argPrefixL + ArProgArg.argConfigFileL

        cmd = gConfig.GetPythonExecutable() + dataserverPath +\
            configOpt + configFilePath + hostOpt
        arUtils.ForkLocalOSProcess(cmd)

    def StartPyroNameserver(self, host):
        print('Starting Nameservers...')
        # Start nameserver processes locally
        arUtils = self._arUtils
        gConfig = self._gConfig

        # Resolve absolute path for config file
        configFilePathTemp = self._configFile
        if (not self.IsAbsolutePath(configFilePathTemp)):
            curAbsPath = os.getcwd() + "/"
        else:
            curAbsPath = ""
        configFilePath = " " + curAbsPath + configFilePathTemp

        # Resolve absolute path for nameserver file
        nameserverPathTemp = gConfig.GetPyroNameserverPath()
        if (not self.IsAbsolutePath(nameserverPathTemp)):
            curAbsPath = os.getcwd() + "/"
        else:
            curAbsPath = ""
        nameserverPath = " " + curAbsPath + nameserverPathTemp

        hostOpt = " " + ArProgArg.argPrefixL + ArProgArg.argHostL + " " + host
        configOpt = " " + ArProgArg.argPrefixL + ArProgArg.argConfigFileL

        cmd = gConfig.GetPythonExecutable() + nameserverPath +\
            configOpt + configFilePath + hostOpt
        arUtils.ForkLocalOSProcess(cmd)

    def StartFeederNodes(self, host, feederList=None):
        # Start feeders processes locally
        arUtils = self._arUtils
        gConfig = self._gConfig

        hostOpt = " " + ArProgArg.argPrefixL + ArProgArg.argHostL + " " + host
        configOpt = " " + ArProgArg.argPrefixL + ArProgArg.argConfigFileL
        feederOpt = " " + ArProgArg.argPrefixL + ArProgArg.argFeederNameL + " "

        baseCmd = gConfig.GetPythonExecutable() + " "

        # Resolve absolute path for config file
        configFilePathTemp = self._configFile
        if (not self.IsAbsolutePath(configFilePathTemp)):
            curAbsPath = os.getcwd() + "/"
        else:
            curAbsPath = ""
        configFilePath = " " + curAbsPath + configFilePathTemp

        if feederList is None:
            feederList = gConfig.GetFeederListByHostname(host)

        for i, feeder in enumerate(feederList):
            if i == 0:
                print('Starting Feeders...')
            # Resolve absolute path for feeder files
            if (not self.IsAbsolutePath(feeder.path)):
                curAbsPath = os.getcwd() + "/"
            else:
                curAbsPath = ""
            feederPath = " " + curAbsPath + feeder.path
            cmd = baseCmd + feederPath + configOpt + configFilePath + hostOpt +\
                feederOpt + feeder.name
            arUtils.ForkLocalOSProcess(cmd)
            print("Feeders on " + host + ": " + cmd)

    def StartProcessNodes(self, host, processList=None):
        # Start processes locally
        arUtils = self._arUtils
        gConfig = self._gConfig

        hostOpt = " " + ArProgArg.argPrefixL + ArProgArg.argHostL + " " + host
        configOpt = " " + ArProgArg.argPrefixL + ArProgArg.argConfigFileL
        processOpt = " " + ArProgArg.argPrefixL + ArProgArg.argProcessNameL + " "

        baseCmd = gConfig.GetPythonExecutable() + " "

        # Resolve absolute path for config file
        if (not self.IsAbsolutePath(self._configFile)):
            curAbsPath = os.getcwd() + "/"
        else:
            curAbsPath = ""
        configFilePath = " " + curAbsPath + self._configFile

        if processList is None:
            processList = gConfig.GetProcessListByHostname(host)

        for i, process in enumerate(processList):
            if i == 0:
                print('Starting Processes...')
            # Resolve absolute path for process files
            if (not self.IsAbsolutePath(process.path)):
                curAbsPath = os.getcwd() + "/"
            else:
                curAbsPath = ""
            processPath = " " + curAbsPath + process.path

            cmd = baseCmd + processPath + configOpt + configFilePath + hostOpt +\
                processOpt + process.name
            arUtils.ForkLocalOSProcess(cmd)
            print("Processes on " + host + ": " + cmd)

    def StartActionNodes(self, host, actionList=None):
        # Start actions locally
        arUtils = self._arUtils
        gConfig = self._gConfig

        hostOpt = " " + ArProgArg.argPrefixL + ArProgArg.argHostL + " " + host
        configOpt = " " + ArProgArg.argPrefixL + ArProgArg.argConfigFileL
        actionOpt = " " + ArProgArg.argPrefixL + ArProgArg.argActionNameL + " "

        baseCmd = gConfig.GetPythonExecutable() + " "

        # Resolve absolute path for config file
        if (not self.IsAbsolutePath(self._configFile)):
            curAbsPath = os.getcwd() + "/"
        else:
            curAbsPath = ""
        configFilePath = " " + curAbsPath + self._configFile

        if actionList is None:
            actionList = gConfig.GetActionListByHostname(host)

        for i, action in enumerate(actionList):
            if i == 0:
                print('Starting Actions...')
            # Resolve absolute path for action files
            if (not self.IsAbsolutePath(action.path)):
                curAbsPath = os.getcwd() + "/"
            else:
                curAbsPath = ""
            actionPath = " " + curAbsPath + action.path

            cmd = baseCmd + actionPath + configOpt + configFilePath + hostOpt +\
                actionOpt + action.name

            arUtils.ForkLocalOSProcess(cmd)
            print("Actions on " + host + ": " + cmd)

if __name__ == "__main__":
    progArg = ArProgArg()
    progArg.Parse(sys.argv)
    starter = Starter(progArg)
    if starter._progArg.IsRoot():
        sleepIntervalInSec = 900

        gConfig, progArg = starter._gConfig, starter._progArg

        healthChecker = HealthChecker(
            gConfig=gConfig,
            progArg=progArg,
            startFeeders=starter.StartFeederNodes,
            startProcesses=starter.StartProcessNodes,
            startActions=starter.StartActionNodes,
        )
    
        while True:
            healthChecker.start()
            time.sleep(sleepIntervalInSec)
