#!flask/bin/python
from flask import Flask, jsonify, request
from flask import make_response
from flask_cors import CORS
import datetime
import json
import sys
import requests

sys.path.append('../models/PeakDetection')
from PeakDetectionAlgorithm import *
from Modified_zscore import *

sys.path.append('../models/DiscordDiscovery_2')
from DiscordDiscovery import *

sys.path.append('../common')
from Datapoint import *

app = Flask(__name__) #define app using Flask
CORS(app)

class Constant:
    ######################### APIserver ############################
    model_name_SPD                = "SPD"
    model_name_Zscore             = "Z-SCORE"
    model_name_DD                 = "DD"
    model_name_2STSC              = "2STSC"
    dateTimeISOFormat             = '%Y-%m-%dT%H:%M:%SZ'
    dateTimeISO                   = 'ISO8601'
    dateTimeEpochTime             = 'epochTime'
    maxDatapointNumber            =  100000
    sensitivityExtremelyHigh      = 'extremely high'
    sensitivityExtremelyHighValue =  1
    sensitivityHigh               = 'high'
    sensitivityHighValue          =  2
    sensitivityMed                = 'medium'
    sensitivityMedValue           =  3
    sensitivityLow                = 'low'
    sensitivityLowValue           =  4
    sensitivityExtremelyLow       = 'extremely low'
    sensitivityExtremelyLowValue  =  5
    dataTypesDatapoints           = 'datapoints'
    dataTypesAnomalies            = 'anomalies'
    minThresholdZS                =  1
    maxThresholdZS                =  20
    minThresholdSPD               =  1
    maxThresholdSPD               =  40
    minWindow_K                   =  1
    maxWindow_K                   =  40
    minimumMode                   =  1
    maximumMode                   =  3
    minKnowledgeWindow            =  2
    maxKnowledgeWindow            =  3000
    minStep                       =  1
    maxStep                       =  1000

    ############################### APIclient ################################
    generate                      =  'g'
    read                          =  'r'
    prefix                        =  '-'
    json_suffix                   =  '.json'
    graphite                      =  'Graphite'
    apiEntryPoint                 =  '/argos/api/v1.0'
    generate_config               =  False
    multiple_node                 =  False
    generate_config_count         =  0
    configTemplate                =  '../common/config_template.json'
    dataTypes                     =  'data_types'
    model_name                    =  'model_name'
    metric_addr                   =  'metric_addr'
    config_gen                    =  'config_gen'

                ################# Feeders #################
    feeders                       = 'Feeders'
    feederPath                    = '../feeder/FeederExample.py'
    feeders_list                  = 'List'
    feeders_type                  = 'Type'
    feeders_endpoint              = 'Endpoint'
    feeders_address               = 'Address'
    feeders_path                  = 'Path'
    feeders_start_lookback        = 'Start_lookback'
    feeders_poll_interval         = 'Poll_interval'
    feeders_file                  = 'File'
    feeders_metric_1              = 'Metric_1'
    feeders_hostname              = 'Hostname'
    feeders_localhost             = 'localhost'

                ################ Processes ################
    processes                     = 'Processes'
    processModelPath              =  {}
    processModelPath['DD']        = '../process/Process_DiscordDiscovery.py'
    processModelPath['SPD']       = '../process/Process_SPD.py'
    processModelPath['Z-SCORE']   = '../process/Process_Z_score.py'
    processes_path                = 'Path'
    processes_input               = 'Input'
    processes_start_lookback      = 'Start_lookback'
    processes_poll_interval       = 'Poll_interval'
    processes_name                = 'Name'
    processes_list                = 'List'
    processes_model_1             = 'Model_1'
    processes_hostname            = 'Hostname'
    processes_localhost           = 'localhost'

               ################ Action ####################
    actions                       = 'Actions'
    actions_process               = 'Processes'
    actions_path                  = 'Path'
    actions_input                 = 'Input'
    actions_poll_interval         = 'Poll_interval'
    actions_name                  = 'Name'
    actions_list                  = 'List'
    actions_action_1              = 'Action_1'
    actionPath                    =  '../action/Action_Generic.py'
    actions_hostname              = 'Hostname'
    actions_localhost             = 'localhost'

             ################# Pyro #######################
    pyro                          = 'Pyro'
    hosts                         = 'Hosts'
    nameservers                   = 'Nameservers'
    hostname                      = 'Hostname'
    dataservers                   = 'Dataservers'
    localhost                     = 'localhost'

              ############## miscellaneous ################
    error_res                     = 'errorResponse'
    error_num                     = 'errorNumber'
    error_msg                     = 'errorMessage'
    data_res                      = 'dataResponse'
    datapoints                    = 'datapoints'
    anomaly_res                   = 'anomalyResponse'
    intervals                     = 'intervals'
    start_lookback                = 'start_lookback'
    poll_interval                 = 'poll_interval'
    epochTime                     = 'epochTime'
    value                         = 'value'
    start                         = 'start'
    stop                          = 'stop'
    graphite_endpoint             = 'graphite-api-endpoint'
    prefix                        = '-'



class CreateResponseWithError(Exception):
    def __init__(self,errorNumber,errorMessage):
        self.errorNumber  = errorNumber
        self.errorMessage = errorMessage

    def AddErrorNumber(self,errorNumber):
        self.errorNumber  = errorNumber

    def AddErrorMessage(self,errorMessage):
        self.errorMessage = errorMessage

    def GetJsonError(self):
        return {'errorNumber':self.errorNumber,'errorMessage':self.errorMessage}

class APIprocess:

    def __init__(self,start,end,metric_addr):
        self.start       = start
        self.end         = end
        self.metric_addr = metric_addr
        self.epoch       = datetime.datetime.utcfromtimestamp(0)

    def BuildRequestString(self):
        startEpoch = int((self.start - self.epoch).total_seconds())
        endEpoch   = int((self.end - self.epoch).total_seconds())
        string     = 'target=' + self.metric_addr + '&from=' + \
                 str(startEpoch) + '&until=' + str(endEpoch) + '&format=json'

        return string

    # request datapoint from Graphite endpoint.
    def requestDatapoints(self):
        datapoints, datapoints_class = [], []
        with open("APIserver.json", "r") as jsonFile:
            endpoint = json.load(jsonFile)["graphite-api-endpoint"]
        requestStr     = self.BuildRequestString()
        response       = requests.post(endpoint, data=requestStr)
        response       = response.json()
        pre_datapoints = response[0]['datapoints'] # it has two data.

        #change format of datapoints into (epochTime,value)
        for j in range(len(pre_datapoints)):
            epochTime = pre_datapoints[j][1]
            value     = pre_datapoints[j][0]
            try:
                value = float(value)
            except Exception as e:
                value = 0.0
            datapoints.append((epochTime,value))
            datapoints_class.append(Datapoint(epochTime, value))

        return datapoints,datapoints_class

    # Only peak detection model.
    def CreateJSONResponse_ConvertPointAnomalyToInterval(self, anomalies):
        intervals = []
        for anomaly in anomalies:
            interval = {"start":anomaly[0], "stop":anomaly[0]}
            intervals.append(interval)

        return intervals

    # Only Shape-based model.
    def CreateJSONReseponse_ConvertIntervalAnomalyToInterval(self, anomalies):
        intervals = []
        for anomaly in anomalies:
            epochTimes =  {"start":anomaly[0], "stop":anomaly[1]}
            intervals.append(epochTimes)

        return intervals

@app.route(Constant.apiEntryPoint, methods=['POST','GET'])
def get_tasks():
    dict = {"dataResponse": {}, "anomalyResponse": {}, "errorResponse": {}}
    dplist,datapoints_class = [],[]

    if not request.json:
        error = CreateResponseWithError(7, "Invalid request.")
        dict["errorResponse"] = error.GetJsonError()
        return jsonify(dict)

    try:
        data_types   = request.json['data_types'] # receive data type.
        data_range   = request.json['data_range'] #receive specific range of epochTime.
        model_param  = request.json['model_param']
        model_name   = request.json['model_name']
        metric_addr  = request.json['metric_addr']
        time_type    = data_range['type']
    except KeyError as ke:
        error = CreateResponseWithError(6, "Key " +str(ke)+" not found.")
        dict["errorResponse"] = error.GetJsonError()
        return jsonify(dict)

    #User specified date-time format in ISO-8601
    if time_type == Constant.dateTimeISO:
        try:
            start    = datetime.datetime.strptime(data_range['start'],Constant.dateTimeISOFormat)
            end      = datetime.datetime.strptime(data_range['end'], Constant.dateTimeISOFormat)
        except (KeyError,ValueError) as ke:
            error = CreateResponseWithError(6, "Key " +str(ke)+" not found.")
            dict["errorResponse"] = error.GetJsonError()
            return jsonify(dict)
        if end < start :
            error = CreateResponseWithError(4.1, "End time < start time.")
            dict["errorResponse"] = error.GetJsonError()
            return jsonify(dict)

    # User specified date-time format in term of epoch-time
    elif time_type == Constant.dateTimeEpochTime:
        try:
            start = datetime.datetime.utcfromtimestamp(float(data_range['start']))
            end   = datetime.datetime.utcfromtimestamp(float(data_range['end']))
        except KeyError as ke:
            error = CreateResponseWithError(6, "Key " +str(ke)+" not found.")
            dict["errorResponse"] = error.GetJsonError()
            return jsonify(dict)
        if end < start :
            error = CreateResponseWithError(4.1, "End time < start time.")
            dict["errorResponse"] = error.GetJsonError()
            return jsonify(dict)

    # User specified date-time format in unsupported format
    else:
        error = CreateResponseWithError(4.3, "Invalid format of selected data time.")
        dict["errorResponse"] = error.GetJsonError()
        return jsonify(dict)

    ################################################################################
    #                       Start processing the request                           #
    ################################################################################

    apiProcess   = APIprocess(start,end,metric_addr)

    try:
        datapoints,datapoints_class = apiProcess.requestDatapoints()
    except Exception as e:
        error = CreateResponseWithError(5, "No data available")
        dict["errorResponse"] = error.GetJsonError()
        return jsonify(dict)

    for data in datapoints_class:
        try:
            data.value = float(data.value)
        except Exception:
            data.value = 0.0


    if len(datapoints) >= Constant.maxDatapointNumber:
        error = CreateResponseWithError(4.2, 'Too many datapoints.')
        dict["errorResponse"] = error.GetJsonError()
        return jsonify(dict)

    for data_type in data_types:
        if data_type == Constant.dataTypesDatapoints: #user request datapoints
            for datapoint in datapoints:
                dp = {"epochTime":datapoint[0],"value":datapoint[1]}
                dplist.append(dp)
            error = CreateResponseWithError(0, "Run successfully.")
            dict["errorResponse"] = error.GetJsonError()
            dict["dataResponse"]  = {"datapoints": dplist,"dataType":"matric"}

        elif data_type == Constant.dataTypesAnomalies:
            if model_name == Constant.model_name_SPD: #  user request anomalies processed by SPD.
                try:
                    window_k  = model_param['k']
                except KeyError as ke:
                    error = CreateResponseWithError(6, "Key " + str(ke) + " not found.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)
                if  window_k < Constant.minWindow_K or window_k > Constant.maxWindow_K:
                    error = CreateResponseWithError('3.2.1', "Too large or too small 'window_k'.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)

                try:
                    threshold = model_param['threshold']
                except KeyError as ke:
                    error = CreateResponseWithError(6, "Key " + str(ke) + " not found.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)
                if  threshold < Constant.minThresholdSPD or threshold > Constant.maxThresholdSPD:
                    error = CreateResponseWithError('3.2.2', "Too large or too small 'threshold value'.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)

                try:
                    mode = model_param['mode']
                except KeyError as ke:
                    error = CreateResponseWithError(6, "Key " + str(ke) + " not found.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)
                if  mode < Constant.minimumMode or mode > Constant.maximumMode :
                    error = CreateResponseWithError('3.2.3', "Invalid mode.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)

                peak_detection = PeakDetection(datapoints_class, window_k, threshold, mode)
                anomalies, binary_output = peak_detection.PeakDetect()
                intervals  = apiProcess.CreateJSONResponse_ConvertPointAnomalyToInterval(anomalies)

                error = CreateResponseWithError(0, "Run successfully.")
                dict["errorResponse"] = error.GetJsonError()
                dict["anomalyResponse"] = {"intervals": intervals, "model": model_name}

            elif model_name == Constant.model_name_Zscore: #Z-score
                try:
                    threshold_Zscore = model_param['threshold']
                except KeyError as ke:
                    error = CreateResponseWithError(6, "Key " + str(ke) + " not found.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)
                if threshold_Zscore <  Constant.minThresholdZS or threshold_Zscore > Constant.maxThresholdZS:
                    error = CreateResponseWithError(3.1, "Too high or too low 'threshold value'")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)

                z_score = Z_score(datapoints_class, threshold_Zscore)
                anomalies, binary_output = z_score.outliers_modified_z_score()
                intervals = apiProcess.CreateJSONResponse_ConvertPointAnomalyToInterval(anomalies)

                error = CreateResponseWithError(0, "Run successfully.")
                dict["errorResponse"] = error.GetJsonError()
                dict["anomalyResponse"] = {"intervals": intervals, "model": model_name}

            elif model_name == Constant.model_name_DD:  #shape-based anomaly type.
                #read parameters from client's json file
                try:
                    knowledgeWindow = int(model_param['knowledgeWindow'])
                except KeyError as ke:
                    error = CreateResponseWithError(6, "Key " + str(ke) + " not found.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)
                if (knowledgeWindow < Constant.minKnowledgeWindow) or (knowledgeWindow > Constant.maxKnowledgeWindow):
                    error = CreateResponseWithError('3.3.1', "Too large or too small 'knowledgeWindow'")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)

                try:
                    step = int(model_param['step'])  # user specific
                except KeyError as ke:
                    error = CreateResponseWithError(6, "Key " + str(ke) + " not found.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)
                if step <  Constant.minStep or step > Constant.maxStep:
                    error = CreateResponseWithError('3.3.2', "Too large or too small 'step'")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)

                try:
                    sensitivity = model_param['sensitivity']  # user-specific
                except KeyError as ke:
                    error = CreateResponseWithError(6, "Key " + str(ke) + " not found.")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)
                if   sensitivity == Constant.sensitivityExtremelyHigh:
                     sensitivity  = Constant.sensitivityExtremelyHighValue
                elif sensitivity == Constant.sensitivityHigh:
                     sensitivity  = Constant.sensitivityHighValue
                elif sensitivity == Constant.sensitivityMed:
                     sensitivity  = Constant.sensitivityMedValue
                elif sensitivity == Constant.sensitivityLow:
                     sensitivity  = Constant.sensitivityLowValue
                elif sensitivity == Constant.sensitivityExtremelyLow:
                     sensitivity  = Constant.sensitivityExtremelyLowValue
                else:
                    error = CreateResponseWithError('3.3.3', "Invalid 'sensitivity'")
                    dict["errorResponse"] = error.GetJsonError()
                    return jsonify(dict)

                swin = int((float(knowledgeWindow) / 5.0)) #/ float(sensitivity))  # calculate from sensitivity

                ddParam = DiscordDiscovery.Param_gpu()
                ddParam.minSubWindowSize = swin
                ddParam.knowledgeWindowSize = knowledgeWindow
                ddParam.windowStep = 20
                ddParam.detectionFocus = 1
                try:
                    dd = DiscordDiscovery(ddParam)
                except Exception as dde:
                    print (dde)
                anomalies = []
                """############################################################################################
                for i in range(0, len(datapoints_class) - knowledgeWindow, step):
                    dataws = datapoints_class[i:i + knowledgeWindow]

                    dataw_value = []
                    for data in dataws:
                        data_value = float(data.value)
                        dataw_value.append(data_value)

                    ########## ORIGINAL IMPLEMENTATION ##########
                    #ddRange = dd.NaiveDiscovery(dataw_value, threads=8)

                    ########## SINGLE-FRAME IMPLEMENTATION ##########
                    ddRange = dd.NaiveDiscovery_SingleFrame(dataw_value, useGPU=False)

                    if (ddRange != None):
                        start = datapoints_class[ddRange.startIndex + i].epochTime
                        end   = datapoints_class[ddRange.endIndex   + i].epochTime
                        anomalies.append((start,end))

#############################################################################################"""
                dataw_value = []
                for i in range(0, len(datapoints_class)):
                    dataw_value.append(float(datapoints_class[i].value))
                ddRange = dd.NaiveDiscovery_MultiFrame(dataw_value, useGPU=False)
                if (ddRange != None):
                    for i in range(0, len(ddRange)):
                        start = datapoints_class[ddRange[i].startIndex].epochTime
                        end   = datapoints_class[ddRange[i].endIndex].epochTime
                        anomalies.append((start,end))

                intervals = apiProcess.CreateJSONReseponse_ConvertIntervalAnomalyToInterval(anomalies)
                error = CreateResponseWithError(0, "Run successfully.")
                dict["errorResponse"]   = error.GetJsonError()
                dict["anomalyResponse"] = {"intervals": intervals,"model": model_name}


            else:
                error = CreateResponseWithError(2, "Invalid Model.")
                dict["errorResponse"] = error.GetJsonError()
                return jsonify(dict)

        else:
            error = CreateResponseWithError(1 ,"Invalid data type.")
            dict["errorResponse"] = error.GetJsonError()
            return jsonify(dict)

    #Uncomment below if you wish to write the result of the request into file
    #with open('dataWithAnomalies.json','w') as js_data:
    #    json.dump(dict,js_data)

    return jsonify(dict)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0',port = 9090)
