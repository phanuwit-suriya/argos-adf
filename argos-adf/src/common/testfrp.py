from ArUtils import *

if __name__ == "__main__":
    gConfig = GlobalConfig('config_template.json')
    arUtils = ArUtils(gConfig)
    arUtils.ForkRemoteOSProcess('python3 fakeproc.py')
    arUtils.ForkLocalOSProcess('python3 fakeproc.py')

