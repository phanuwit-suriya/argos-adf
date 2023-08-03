import sys
import time
sys.path.append('../common')
from ArProgArg import *
from ArUtils import *
from INodeComm import *

if __name__ == "__main__":
    arProgArg = ArProgArg()
    arProgArg.Parse(sys.argv)

    configFile = arProgArg.GetConfigFile()
    if (configFile == None):
        configFile = "../common/config_template.json"

    gConfig = GlobalConfig(configFile)
    arUtils = ArUtils(gConfig)

    host = arProgArg.GetHost()
    if (host == None):
        raise Exception()

    # Start nameserver
    dsList = gConfig.GetPyroDataserverList()

    try:
        comm = INodeComm(host, gConfig)
    except Exception:
        print('Cannot communicate with nodes.')
        quit()

    execute = False
    for i in range(0, len(dsList)):
        if (dsList[i].hostname == host):
            print(dsList[i].hostname)
            comm.InitializeDataserverNode()
            comm.RegisterNode(None)
            execute = True
            break

    if (execute):
        comm.HandleRequestLoop()
