import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class NodeReg:

    def __init__(self):
        pass

    def AddNode(self):
        pass

    def RemoveNode(self):
        pass

    def ListAllNode(self):
        pass