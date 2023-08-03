
class Datapoint:
    def __init__(self, epochTime, value):
        self.epochTime = epochTime
        self.value     = value

    def GetEpochTime(self):
        return self.epochTime;

    def GetValue(self):
        return self.value;