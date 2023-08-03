import os
import slackclient
import stat
import sys
sys.path.append('../common')
from GlobalConfig import *
from ArProgArg import *
from ActionAbst import *
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

#All feeders MUST extend 'FeederAbst'
class ActionExample(ActionAbst):

    #ATTENTION: The prefix of the feedback-url need to be configure properly according to the HTTP server.
    #           Argos relies on a third-party HTTP server for getting feedback from users.
    anomalyFeedbackDir = "../../anomaly_feedback"
    feedbackUrlPrefix  = "http://10.42.68.72/"
    feedbackUrlPath    = "anomaly_feedback"

    metricName_ph      = "%_metric_name_%"
    metricAddress_ph   = "%_metric_address_%"
    anomalyTimeSt_ph   = "%_anomaly_time_start_%"
    anomalyTimeEd_ph   = "%_anomaly_time_end_%"
    detectionMet_ph    = "%_detection_method_%"
    detectionParams_ph = "%_detection_parameters_%"
    anomalyImage_ph    = "%_anomaly_image_%"

    def __init__(self, progArg):
        self._progArg = progArg
        self._configFile = self._progArg.GetConfigFile()
        if (self._configFile == None):
            self._configFile = '../common/config_template.json'

        self._gConfig = GlobalConfig(self._configFile)

        # A one-time call to Initialize() is mandatory
        self.Initialize(self._progArg, self._gConfig)
        self.feederData = []
        self.processData = []
        self.bufferSize = 20000
        print("Action '" + self._actionName + "' started . . .")

        self.lastAnomalyStartEpoch = 0
        self.lastAnomalyEndEpoch = 0

        self._slackClient = None
        self._slackChannel = None
        self._slackConnected = False
        if (self._properties.slackIsEnable == True):
            slackToken         = self._properties.slackToken
            self._slackChannel = self._properties.slackChannel
            self._slackClient  = slackclient.SlackClient(slackToken)

        print("\tSlack Enable:  " + str(self._properties.slackIsEnable))
        print("\tSlack Token:   " + self._properties.slackToken)
        print("\tSlack Channel: " + self._properties.slackChannel)
        print("\tAnomaly Image: " + str(self._properties.saveAnomalyImage))
        print("\tAnomaly Path:  " + str(self._properties.anomalyImagePath))

    #Note: This generic action assumes that it consumes two inputs: one from a feeder and another from a process
    def Endpoint_Postpoll_Hook_Impl(self, inputName, inputType, numPoints, lastEpTime, datapoints):
        self.processData = []
        if (inputType == ActionNode.InputType.feeder):
            print("\t" + inputName  + ": New datapoints: " + str(len(datapoints)))
            for dp in datapoints:
                self.feederData.append(dp)

            if (len(self.feederData) > self.bufferSize):
                self.feederData = self.feederData[len(self.feederData) - self.bufferSize:]

        elif(inputType == ActionNode.InputType.process):
            print("\t" + inputName  + ": New datapoints: " + str(len(datapoints)))
            hasAnomaly = False
            for dp in datapoints:
                hasAnomaly = True
                self.processData.append(dp)

            if (hasAnomaly == True):
                frameStartIndex = -1
                frameEndIndex   = -1

                lastFrameIndex      = len(self.processData) - 1
                lastFrameLength     = len(self.processData[lastFrameIndex].value)
                frameStartEpochTime = self.processData[lastFrameIndex].value[0][0]
                frameEndEpochTime   = self.processData[lastFrameIndex].value[lastFrameLength - 1][0]

                for i in range(0, len(self.feederData)):
                    if (self.feederData[i].epochTime >= frameStartEpochTime) and (frameStartIndex == -1):
                        frameStartIndex = i
                    if (self.feederData[i].epochTime >= frameEndEpochTime) and (frameEndIndex == -1):
                        frameEndIndex = i
                if (frameStartIndex == -1) or (frameEndIndex == -1):
                    return

                ##### Logging #####
                frameStartDateTime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frameStartEpochTime))) 
                frameEndDateTime   = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frameEndEpochTime)))
                print ("\tAnomaly Frame: Index[" + str(frameStartIndex) + " - " + str(frameEndIndex) + "], Epoch["\
                    + str(frameStartEpochTime) + " - " + str(frameEndEpochTime) + "], DateTime[" + frameStartDateTime\
                    + " - " + frameEndDateTime + "]")

                anomalyIndices      = []
                frameValue = self.processData[lastFrameIndex].value
                for i in range(0, len(frameValue)):
                    if (frameValue[i][1] > 0.0):
                        anomalyIndices.append(i)

                anomalyStart = frameStartIndex + anomalyIndices[0]
                anomalyEnd   = frameStartIndex + anomalyIndices[len(anomalyIndices) - 1]
                anomalyStartEpoch = self.feederData[anomalyStart].epochTime
                anomalyEndEpoch = self.feederData[anomalyEnd].epochTime


                if (self.lastAnomalyStartEpoch <= anomalyEndEpoch) and (self.lastAnomalyEndEpoch >= anomalyStartEpoch):
                    print ("\t\tAnomaly skipped...")
                    return
                else:
                    print("\t\tAnomaly accepeted...")

                self.lastAnomalyStartEpoch = anomalyStartEpoch
                self.lastAnomalyEndEpoch = anomalyEndEpoch

                # Save image of the anomaly into a PNG file
                if (self._properties.saveAnomalyImage != True):
                    return

                ##### Create a directory under image path with the name of process #####
                feedbackUrlBody = ActionExample.feedbackUrlPath

                imageDir = os.path.join(ActionExample.anomalyFeedbackDir, inputName)
                imageDir = os.path.join(imageDir, str(frameStartEpochTime))

                feedbackUrlBody = os.path.join(feedbackUrlBody, inputName)
                feedbackUrlBody = os.path.join(feedbackUrlBody, str(frameStartEpochTime))

                try:
                    os.makedirs(imageDir)
                    st = os.stat(imageDir)
                    os.chmod(imageDir, st.st_mode | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                except OSError as exec:
                    pass
                imageDir = os.path.join(imageDir, '') #Add trailing slash

                ###### Determine image / html-page filenames #####
                anomalyFilename      = str(frameStartEpochTime) + ".png"
                anomalyFilePath      = imageDir + anomalyFilename

                htmlTemplateFilePath = "../action/index_template.php"

                htmlFilename         = "index.php"
                htmlFilePath         = imageDir + htmlFilename


                ##### Place the image file #####
                metric = []
                epochTime = []
                localTime = []
                for dp in self.feederData:
                    metric.append(dp.value)
                    epochTime.append(dp.epochTime)
                    localTime.append(time.strftime('%Y/%m/%dT%H:%M:%S', time.localtime(dp.epochTime)))

                plt.figure(figsize=(12,10), dpi=80)
                start_index = self.feederData[frameStartIndex + anomalyIndices[0]].epochTime
                end_index = self.feederData[frameStartIndex + anomalyIndices[len(anomalyIndices) - 1]].epochTime
                start_str = time.strftime('%Y/%m/%dT%H:%M:%S', time.localtime(start_index))
                end_str = time.strftime('%Y/%m/%dT%H:%M:%S', time.localtime(end_index))
                titleStr = inputName + " -- from: " + localTime[0] + " | to: " + localTime[len(localTime) - 1] + "\n" +\
                    "Anomaly found -- from: " + start_str + " | to: " + end_str
                plt.title(titleStr)
                plt.plot(epochTime, metric)
                ax = plt.gca()

                #Set the labels of whatever ticks on the x-axis
                localTimeLabels = []
                for tick in ax.get_xticks():
                    localTimeLabels.append(time.strftime('%Y/%m/%dT%H:%M:%S', time.localtime(tick)))
                ax.set_xticklabels(localTimeLabels)

                plt.axvspan(start_index, end_index, facecolor='r', alpha=0.3)
                plt.axvline(start_index, color='r')
                plt.axvline(end_index, color='r')
                plt.savefig(anomalyFilePath)

                ###### Place the html-page file #####
                feederName      = self._properties.inputFeederList[0].name
                metricAddress   = self._globalConfig.GetFeederAddress(feederName)
                processName     = self._properties.inputProcessList[0].name
                inputProcess    = self._globalConfig.GetProcessByName(processName)
                detectionMet    = inputProcess.path
                detectionParams = inputProcess.parameters

                htmlParam = {}
                htmlParam[ActionExample.metricName_ph]      = inputName
                htmlParam[ActionExample.metricAddress_ph]   = metricAddress
                htmlParam[ActionExample.anomalyTimeSt_ph]   = start_str
                htmlParam[ActionExample.anomalyTimeEd_ph]   = end_str
                htmlParam[ActionExample.detectionMet_ph]    = detectionMet
                htmlParam[ActionExample.detectionParams_ph] = str(detectionParams)
                htmlParam[ActionExample.anomalyImage_ph]    = anomalyFilename
                self.PlaceHtmlPage(htmlTemplateFilePath, htmlFilePath, htmlParam)

                #Constructing chat message
                chatMessage = "*Name:*\t`" + inputName + "`\n" +\
                              "*Anomaly:*\t`" + start_str + "` to `" + end_str + "`\n" +\
                              "*Metric:*\t`" + metricAddress + "`\n" +\
                              "*Feedback:*\t" + ActionExample.feedbackUrlPrefix + feedbackUrlBody

                # Send image of the anomaly to Slack
                if (self._slackClient != None):

                    ret = self._slackClient.api_call("chat.postMessage", channel=self._slackChannel, as_user=True, text=chatMessage)
                    if not 'ok' in ret or not ret['ok']:
                        print('Sending message error: ' + ret['error'])

                    fh = open(anomalyFilePath, 'rb')
                    ret = self._slackClient.api_call('files.upload', channels=self._slackChannel, as_user=True, filename=anomalyFilePath, file=fh.read(), filetype="auto")
                    if not 'ok' in ret or not ret['ok']:
                        print('fileUpload failed %s', ret['error'])
                    fh.close()

    def PlaceHtmlPage(self, htmlTemplate, html, htmlParam):
        fh = open(htmlTemplate, "r")
        content = fh.read()
        fh.close()

        content = content.replace(ActionExample.metricName_ph, htmlParam[ActionExample.metricName_ph])
        content = content.replace(ActionExample.metricAddress_ph, htmlParam[ActionExample.metricAddress_ph])
        content = content.replace(ActionExample.anomalyTimeSt_ph, htmlParam[ActionExample.anomalyTimeSt_ph])
        content = content.replace(ActionExample.anomalyTimeEd_ph, htmlParam[ActionExample.anomalyTimeEd_ph])
        content = content.replace(ActionExample.detectionMet_ph, htmlParam[ActionExample.detectionMet_ph])
        content = content.replace(ActionExample.detectionParams_ph, htmlParam[ActionExample.detectionParams_ph])
        content = content.replace(ActionExample.anomalyImage_ph, htmlParam[ActionExample.anomalyImage_ph])

        fh = open(html, "w")
        fh.write(content)
        fh.close()

if __name__ == "__main__":
    progArg = ArProgArg()
    progArg.Parse(sys.argv)
    ae = ActionExample(progArg)
    ae.Execute()
