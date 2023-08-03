from GlobalConfig import *

if __name__ == "__main__":
    gConfig = GlobalConfig('config_template.json')
    print(gConfig._configMap["Pyro"])
    a = gConfig.GetPyroNameserverList()
    for i in range(0, len(a)):
        print(a[i].hostname, a[i].port)

    b = gConfig.GetPyroHostList()
    for i in range(0, len(b)):
        print(b[i])
