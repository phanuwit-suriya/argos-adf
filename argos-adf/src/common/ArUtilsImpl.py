import getpass
import os
import subprocess
from GlobalConfig import *
from ArUtilsIntf import *

class ArUtilsImpl(ArUtilsIntf):
    #class Argument:
    def __init__(self, globalConfig):
        if globalConfig.__class__ != GlobalConfig:
            raise TypeError
        self._sshExecutable = globalConfig.GetSSHExecutable()

    def ForkRemoteOSProcessImpl(self, command, host, port, user, absPath, async):
        if host == None:
            host = 'localhost'
        if port == None:
            port = ''
        if user == None:
            user = getpass.getuser()
        if absPath == None:
            absPath = os.getcwd()
        cmd  = self._sshExecutable + ' -f ' + str(user) + '@' + str(host) + str(port) + " \"cd " + str(absPath) + "; "
        #cmd += "nohup " + str(command) + " 2>&1 &\""
        cmd += "nohup " + str(command) + " &\""
        #print("Remote: " + cmd)
        subprocess.call(cmd, shell=True)

    def ForkLocalOSProcessImpl(self, command, absPath, async):
        if absPath == None:
            absPath = os.getcwd()
        cmd = "cd " + str(absPath) + '; ' + str(command) + " &"
        print("Local: " + cmd)
        nullTerminal = open(os.devnull, 'w')
        # subprocess.call(cmd, shell=True)
        subprocess.call(cmd, shell=True, stdout=nullTerminal, stderr=nullTerminal)

