import numpy as np
import copy

class Z_score():
    def __init__(self,data,threshold):
        self.threshold = threshold
        self.data      = data


    def outliers_modified_z_score(self):  # Robust z-score method.

        ##### we select 'med' instead of 'mean' because it will not be effect by outliers.  #####
        outputList = []
        dataValue = [self.data[i].value for i in range (len(self.data))]
        binary_output = copy.deepcopy(self.data)

        median_data = np.median(dataValue)
        median_absolute_deviation_data = np.median([np.abs(data - median_data) for data in dataValue])

        for i in range (len(self.data)):
            z_score_value = 0.6745 * (self.data[i].value - median_data) / median_absolute_deviation_data
            if z_score_value > (median_data * self.threshold):
                epochTime = self.data[i].epochTime
                value = self.data[i].value
                outputTuple = (epochTime,value)
                outputList.append(outputTuple)
                #output in binary
                binary_output[i].value = 1
            else:
                binary_output[i].value = 0

        return outputList,binary_output

