import Pyro4.naming
import sys
sys.path.append('../common')
from ArProgArg import *
from ArUtils import *

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

    #Start nameserver
    nsList = gConfig.GetPyroNameserverList()
    for i in range(0, len(nsList)):
        if (nsList[i].hostname == host):
            print(nsList[i].hostname + " : " + nsList[i].port)
            Pyro4.config.SERVERTYPE="multiplex"
            Pyro4.naming.startNSloop(host=host, port=int(nsList[i].port), enableBroadcast=True)
            #Pyro4.naming.startNSloop()
            break;
