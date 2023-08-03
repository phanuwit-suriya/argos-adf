import sys
import time
sys.path.append('../common')
from ArProgArg import *
from GlobalConfig import *
from INodeComm import *

if __name__ == "__main__":

    progArg = ArProgArg()
    progArg.Parse(sys.argv)

    configFile = progArg.GetConfigFile()
    if configFile == None:
        raise Exception()

    host = progArg.GetHost()
    if host == None:
        raise Exception()

    feederName = progArg.GetFeederName()
    if feederName == None:
        raise Exception()

    gConfig = GlobalConfig(configFile)
    comm = INodeComm(host, GlobalConfig(configFile))

    while(True):
        data = comm.RetrieveDatapointListFromChannel(feederName, feederName)
        #data_1 = comm.RetrieveDatapointListFromChannel("test","test")
        data_1 = []
        print (str(len(data))+":"+str(len(data_1)))
        #for i in range(0, len(data)):
        #    print (str(data[i].epochTime) + " : " + str(data[i].value))
        time.sleep(1)


