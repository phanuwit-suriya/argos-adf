import sys
sys.path.append("common")
from synthetic_common import *

class SineHarmonic:
    def __init__(self, amplitude, freqPerDay, manifestTime):
        self.amplitude = amplitude
        self.freqPerDay = freqPerDay
        self.manifestTime = SyntTimeSpan.GetEpochTime(manifestTime) 

if __name__ == "__main__":

    #1-year / 2-hour resolution
    metric = SyntMetric(
        "Basic Sinusoidal Wave",
        "2017-01-01T00:00:00.000",
        "2017-12-31T00:00:00.000",
        7200.0)

    hmnList = [
        SineHarmonic(20.0, 0.2, "2017-01-01T00:00:00.000"),
        SineHarmonic( 0.5, 3.0, "2017-11-15T15:00:00.000")
    ]

    print ("Size: " + str(metric.GetSequenceSize()))

    startTime = metric.GetTimeSpanStart()
    while(True):
        valid, curTime, curVal = metric.GetCurrent()

        if (not valid):
            break

        val = 0.0
        for hmn in hmnList:
            if (hmn.manifestTime <= curTime):
                val += hmn.amplitude * math.cos(
                    SyntAngle.CoarseRadianAngle(
                        startTime,
                        curTime,
                        hmn.freqPerDay))

        metric.SetAndAdvance(val)
  
    metric.Show()
    print(metric.SerializeToJson())
