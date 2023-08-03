class ArUtilsIntf:

    def ForkRemoteOSProcess(self, command, host=None, port=None, user=None, absPath=None, async=True):
        return self.ForkRemoteOSProcessImpl(command, host, port, user, absPath, async)
    def ForkRemoteOSProcessImpl(self, command, host, port, user, absPath, async):
        raise NotImplementedError

    def ForkLocalOSProcess(self, command, absPath=None, async=True):
        return self.ForkLocalOSProcessImpl(command, absPath, async)
    def ForkLocalOSProcessImpl(self, command, absPath, async):
        raise NotImplementedError
