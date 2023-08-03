import requests
import json
import datetime
import matplotlib.pyplot as plt
import sys
from APIserver import *
import copy
import time

sys.path.append('../common')
from CommonException import  *

############### Settings ####################
url = 'http://localhost:9090/argos/api/v1.0'
#############################################

class APIClientProcess:

    def __init__(self,configData):
        self.configData = configData

    def ChangeFeederTypeToGrahite(self,feederName):
        self.configData[Constant.feeders][feederName][Constant.feeders_type] = Constant.graphite

    def ChangeFeederEndpoint(self,feederName,endpoint):
        self.configData[Constant.feeders][feederName][Constant.feeders_endpoint] = endpoint

    def ChangeFeederAddress(self,feederName,metric_addr):
        self.configData[Constant.feeders][feederName][Constant.feeders_address] = metric_addr

    def ChangeFeederHostname(self,feederName,hostname):
        self.configData[Constant.feeders][feederName][Constant.feeders_hostname] = hostname

    def ChangeFeederPath(self,feederName):
        self.configData[Constant.feeders][feederName][Constant.feeders_path] = Constant.feederPath

    def ChangeFeederStartLookBack(self,feederName,start_lookback):
        self.configData[Constant.feeders][feederName][Constant.feeders_start_lookback] = start_lookback

    def ChangeFeederPollInterval(self,feederName,poll_interval):
        self.configData[Constant.feeders][feederName][Constant.feeders_poll_interval] = poll_interval

    def ChangeFeederFile(self,feederName):
        self.configData[Constant.feeders][feederName][Constant.feeders_file] = ' '

    def AddNewFeederIntoList(self,feederName):
        self.configData[Constant.feeders][Constant.feeders_list].append(feederName)

    def AddNewFeeder(self,feederName):
        self.configData[Constant.feeders][feederName] = copy.deepcopy(configData[Constant.feeders][Constant.feeders_metric_1])

    ############################### End of feeder #####################################

    def ChangeProcessPath(self,processName,model_name):
        self.configData[Constant.processes][processName][Constant.processes_path] = Constant.processModelPath[model_name]

    def ChangeInputOfProcess(self,processName):
        self.configData[Constant.processes][processName][Constant.processes_input][Constant.processes] = []

    def ChangeProcessHostname(self,processName,hostname):
        self.configData[Constant.processes][processName][Constant.processes_hostname] = hostname

    def ChangeInputOfProcessFromFeeders(self,processName,poll_interval,feederName):
        inputProcessFromFeeders = self.configData[Constant.processes][processName][Constant.processes_input][Constant.feeders]
        for inputProcessFromFeeder in inputProcessFromFeeders:
            inputProcessFromFeeder[Constant.processes_poll_interval] = poll_interval
            inputProcessFromFeeder[Constant.processes_name]          = feederName

    def ChangeInputOfProcessFromProcesses(self,processName,poll_interval,feederName):
        inputProcessFromProcesses = self.configData[Constant.processes][processName][Constant.processes_input][Constant.processes]
        inputProcessFromProcesses = []

    def ChangeProcessModelPath(self,processName,model_name):
        self.configData[Constant.processes][processName][Constant.processes_path] = Constant.processModelPath[model_name]

    def AddNewProcessIntoList(self,processName):
        self.configData[Constant.processes][Constant.processes_list].append(processName)

    def AddNewProcess(self,processName):
        self.configData[Constant.processes][processName] = copy.deepcopy(configData[Constant.processes][Constant.processes_model_1])

    ############################### End of process ####################################

    def ChangeActionPath(self,actionName):
        self.configData[Constant.actions][actionName][Constant.actions_path] = Constant.actionPath

    def ChangeActionsHostname(self,actionName,hostname):
        self.configData[Constant.actions][actionName][Constant.actions_hostname] = hostname

    def ChangeInputOfActionFromFeeders(self,actionName,poll_interval,feederName):
        inputActionFromFeeders = configData[Constant.actions][actionName][Constant.actions_input][Constant.feeders]
        for inputActionFromFeeder in inputActionFromFeeders:
            inputActionFromFeeder[Constant.actions_poll_interval] = poll_interval
            inputActionFromFeeder[Constant.actions_name]          = feederName

    def ChangeInputOfActionFromProcesses(self, actionName, poll_interval, processName):
        inputActionFromProcesses = configData[Constant.actions][actionName][Constant.actions_input][Constant.actions_process]
        for inputActionFromProcess in inputActionFromProcesses:
            inputActionFromProcess[Constant.actions_poll_interval] = poll_interval
            inputActionFromProcess[Constant.actions_name]          = processName

    def AddNewActionIntoList(self,actionName):
        self.configData[Constant.actions][Constant.actions_list].append(actionName)

    def AddNewAction(self,actionName):
        self.configData[Constant.actions][actionName] = copy.deepcopy(configData[Constant.actions][Constant.actions_action_1])

    ############################## End of action ######################################

    #TODO: when have multiple hosts
    def ChangePyroHosts(self,hostname):
        self.configData[Constant.pyro][Constant.hosts] = [hostname]

    def ChangeNameserversHostname(self,hostname):
        nameServersLists = self.configData[Constant.pyro][Constant.nameservers]
        del nameServersLists[1]
        for nameServersList in nameServersLists:
            nameServersList[Constant.hostname] = hostname

    def ChangeDataserversHostname(self,hostname):
        dataServersLists = self.configData[Constant.pyro][Constant.dataservers]
        for dataServersList in dataServersLists:
            dataServersList[Constant.hostname] = hostname



    ############################## End of Change host name ############################

    #miscellaneous
    @staticmethod
    def DisplayErrorMessage(response):
        errorNumber = response[Constant.error_res][Constant.error_num]
        errorMessage = response[Constant.error_res][Constant.error_msg]
        print ('errorNumber  : ' + str(errorNumber))
        print ('errorMessage : ' + str(errorMessage))

    @staticmethod
    def SelectDatapointsFromDict(response):
        datapoints = response[Constant.data_res][Constant.datapoints]

        return datapoints

    @staticmethod
    def SelectIntervalFromDict(response):
        intervals = response[Constant.anomaly_res][Constant.intervals]

        return intervals

if __name__ == "__main__":
    for j in range(len(sys.argv)):
        if sys.argv[j].startswith(Constant.prefix):
            val = sys.argv[j][1:]
            if val == Constant.generate:
                ref_pos_g  = j
                Constant.generate_config = True
            elif val == Constant.read:
                ref_pos_r = j
            else:
                raise CommonException(None,"Function '-"+str(val)+"' do not exist.")

    #To check when don't put '-r'
    try:
        ref_pos_r
    except NameError as ne:
        raise CommonException(ne,'Sorry, please insert "-r" before clients_format.json ')

    #get client_format name
    if Constant.generate_config == True:# if user want to generate a config file.
        #when -g and -r are changed position.
        try:
            configName = sys.argv[ref_pos_g + 1]
        except IndexError as ie:
            raise  CommonException(ie, 'Sorry, please specify generated config file name.')

        if configName.endswith(Constant.json_suffix) == False:
            raise CommonException(None, 'Generated config file is not json format.')
        elif configName.startswith(Constant.prefix)  == True:
            raise CommonException(None, 'Sorry, please specify generated config file name.')

        if ref_pos_g > ref_pos_r:
            clientConfigNameLists = sys.argv[ref_pos_r+1:ref_pos_g]
        elif ref_pos_g < ref_pos_r:
            clientConfigNameLists = sys.argv[ref_pos_r + 1:]
            if sys.argv[ref_pos_g+1] == sys.argv[ref_pos_r]:
                raise CommonException(None,'Sorry, please specify generated config file name.')

    else: # if user only want to read client_format.
        if not sys.argv[ref_pos_r+1:]:
            raise CommonException(None,"Sorry, please specify client's config file name.")
        clientConfigNameLists = sys.argv[ref_pos_r+1:]

    for clientConfigNameList in clientConfigNameLists:
        # To check the clients_format's suffix.
        if clientConfigNameList.endswith(Constant.json_suffix,0,len(clientConfigNameList)) == False:
            raise CommonException(None, 'Client config file is not json format.')

        filename = clientConfigNameList
        operationFlag = 0

        #########################################################
        #              Receive data from APIserver              #
        #########################################################

        #read data from clients_format.json
        with open(filename) as json_data:
            data = json.load(json_data)

        #send json data to APIserver.py
        try:
            response = requests.post(url, json=data)
            response = response.json()
        except Exception as e:
            print(e)

        #Display error message from server.
        APIClientProcess.DisplayErrorMessage(response)

        data_types     = data[Constant.dataTypes]
        model_name     = str(data[Constant.model_name])
        metric_addr    = data[Constant.metric_addr]
        #read from user's config file.
        start_lookback = data[Constant.config_gen][Constant.start_lookback]
        poll_interval  = data[Constant.config_gen][Constant.poll_interval]

        for data_type in data_types:
            if data_type == Constant.dataTypesDatapoints:  # plot datapoints.
                plot_data = []
                try:
                    datapoints = APIClientProcess.SelectDatapointsFromDict(response)
                except KeyError as ke:
                    raise KeyError
                for datapoint in datapoints:
                    epochTime = datetime.datetime.utcfromtimestamp(float(datapoint[Constant.epochTime]))
                    value     = datapoint[Constant.value]
                    plot_data.append((epochTime, value))
                print (len(plot_data))
                operationFlag += 1

            elif data_type == Constant.dataTypesAnomalies: #print only anomalies.
                plot_anomalies = []
                try:
                    intervals = APIClientProcess.SelectIntervalFromDict(response)
                except KeyError as ke:
                    raise KeyError

                for interval in intervals:
                    start = datetime.datetime.utcfromtimestamp(float(interval[Constant.start]))
                    stop = datetime.datetime.utcfromtimestamp(float(interval[Constant.stop]))
                    plot_anomalies.append((start,stop))
                operationFlag += 2

        #########################################################
        #                 Start showing results.                #
        #########################################################

        start_localtime = str(plot_data[0][0])
        end_localtime   = str(plot_data[len(plot_data)-1][0])
        titleStr = "From: " + start_localtime + " | to: " + end_localtime
        picname =str(model_name)+"_total_users.png"

        #plot only datapoints.
        if operationFlag   == 1:
            plt.figure(figsize=(12, 10), dpi=80)
            plt.title(titleStr)
            plt.plot(*zip(*plot_data), color='black')

        #print only anomalies.
        elif operationFlag == 2:
            print("====================")
            print(plot_anomalies)

        #plot both anomalies and datapoints.
        else:
            plt.figure(figsize=(12, 10), dpi=80)
            plt.title(titleStr)
            plt.plot(*zip(*plot_data),color = 'black')

            print("====================")
            print(plot_anomalies)
            for plot_anomaly in plot_anomalies:
                if (model_name == Constant.model_name_SPD) or (model_name == Constant.model_name_Zscore):
                    plt.axvline(x=plot_anomaly[0], linewidth=0.5, color='red')
                else:
                    plt.axvspan(plot_anomaly[0],plot_anomaly[1], color='#FF0000', alpha=0.5)
        plt.savefig(picname)
        plt.show()

        #####################################################
        #                Generate config file               #
        #####################################################

        if Constant.generate_config == True:
            if Constant.generate_config_count == 0: # The first generation of config.json ( after -g )which copies format from 'config_timplate.json'
                with open(Constant.configTemplate) as json_data:
                    configData = json.load(json_data)
                # read Graphite endpoint.
                with open("APIserver.json", "r") as jsonFile:
                    endpoint = json.load(jsonFile)[Constant.graphite_endpoint]

                #Initialize
                apiClientProcess = APIClientProcess(configData)

                feederName  = 'Metric_'+ str(Constant.generate_config_count+1)
                processName = 'Model_' + str(Constant.generate_config_count+1)
                actionName  = 'Action_'+ str(Constant.generate_config_count+1)

                #Change 'Pyro' host name
                apiClientProcess.ChangePyroHosts(Constant.localhost)
                apiClientProcess.ChangeNameserversHostname(Constant.localhost)
                apiClientProcess.ChangeDataserversHostname(Constant.localhost)

                #change 'feeder' as clients_format.json
                apiClientProcess.ChangeFeederTypeToGrahite(feederName)
                apiClientProcess.ChangeFeederEndpoint(feederName,endpoint)
                apiClientProcess.ChangeFeederAddress(feederName, metric_addr)
                apiClientProcess.ChangeFeederHostname(feederName,Constant.feeders_localhost)
                apiClientProcess.ChangeFeederPath(feederName)
                apiClientProcess.ChangeFeederStartLookBack(feederName,start_lookback)
                apiClientProcess.ChangeFeederPollInterval(feederName,poll_interval)
                apiClientProcess.ChangeFeederFile(feederName)

                #modify 'process' as clients_format.json
                apiClientProcess.ChangeProcessPath(processName,model_name)
                apiClientProcess.ChangeProcessHostname(processName,Constant.processes_localhost)
                apiClientProcess.ChangeInputOfProcess(processName)
                apiClientProcess.ChangeInputOfProcessFromFeeders(processName,poll_interval,feederName)

                #modify 'action' as clients_format.json
                apiClientProcess.ChangeActionPath(actionName)
                apiClientProcess.ChangeActionsHostname(actionName,Constant.actions_localhost)
                apiClientProcess.ChangeInputOfActionFromFeeders(actionName, poll_interval, feederName)
                apiClientProcess.ChangeInputOfActionFromProcesses(actionName, poll_interval, processName)

                Constant.generate_config_count += 1

            elif Constant.generate_config_count > 0: # Add a new feeder, process and action due to multiple 'client_format.json'.

                feederName  = 'Metric_'+ str(Constant.generate_config_count+1)
                processName = 'Model_' + str(Constant.generate_config_count+1)
                actionName  = 'Action_'+ str(Constant.generate_config_count+1)

                # create a new feeder.
                apiClientProcess.AddNewFeederIntoList(feederName)
                apiClientProcess.AddNewFeeder(feederName)
                apiClientProcess.ChangeFeederEndpoint(feederName, endpoint)
                apiClientProcess.ChangeFeederAddress(feederName,metric_addr)
                apiClientProcess.ChangeFeederStartLookBack(feederName,start_lookback)
                apiClientProcess.ChangeFeederPollInterval(feederName,poll_interval)

                # create a new process.
                apiClientProcess.AddNewProcessIntoList(processName)
                apiClientProcess.AddNewProcess(processName)
                apiClientProcess.ChangeProcessModelPath(processName,model_name)
                apiClientProcess.ChangeInputOfProcessFromFeeders(processName,poll_interval,feederName)

                # create a new action.
                apiClientProcess.AddNewActionIntoList(actionName)
                apiClientProcess.AddNewAction(actionName)
                apiClientProcess.ChangeInputOfActionFromFeeders(actionName,poll_interval,feederName)
                apiClientProcess.ChangeInputOfActionFromProcesses(actionName, poll_interval, processName)

                Constant.generate_config_count += 1

            elif Constant.multiple_node == True:# TODO : Will revise this part dueto multiple connected-node.
                # create a new feeder.
                configData[Constant.feeders]['List'].append("Metric_2")
                configData[Constant.feeders]['Metric_2']  = copy.deepcopy(configData[Constant.feeders]['Metric_1'])
                # create a new process.
                configData['Processes']['List'].append("Model_2")
                configData['Processes']['Model_2'] = copy.deepcopy(configData['Processes']['Model_1'])
                configData['Processes']['Model_1'][Constant.processes_input][Constant.feeders].append(inputProcessFromFeeders[0])
                configData['Processes']['Model_1'][Constant.processes_input][Constant.feeders][1]['Name']  = 'Metric_2'

                # create a new action.
                configData[Constant.actions]['List'].append("Action_2")
                configData[Constant.actions]['Action_2']  = copy.deepcopy(configData[Constant.actions]['Action_1'])
                configData[Constant.actions]['Action_1']['Input'][Constant.feeders].append(inputActionFromFeeders[0])
                configData[Constant.actions]['Action_1']['Input'][Constant.feeders][1]['Name'] = 'Metric_2'

    if Constant.generate_config == True:
        #generate config file.
        with open(configName,'w') as js_data:
            json.dump(configData,js_data, indent=4, sort_keys=True,separators=(',', ': '))
        print ('==================')
        print ('saved ')
