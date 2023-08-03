import numpy as np
import copy

class PeakDetection:
    def __init__(self,data,window_size,threshold,mode):
        self.data        = data
        self.window_size = window_size
        self.threshold   = threshold
        self.mode        = mode

    def S_number(self):
        n_rights, n_lefts, _pfv = [], [], []
        for i in range(self.window_size, len(self.data) - self.window_size):
            ##### Only S1 and S2 #######
            if self.mode == 1 or self.mode == 2:
                for j in range(1, self.window_size + 1):
                    n_right = self.data[i].value - self.data[i + j].value
                    n_rights.append(n_right)
                    n_left = self.data[i].value - self.data[i - j].value
                    n_lefts.append(n_left)
                if self.mode == 1:
                    S = (np.amax(n_rights) + np.amax(n_lefts)) / 2
                else:
                    S = (np.sum(n_lefts) / self.window_size + np.sum(n_rights) / self.window_size) / 2

            ##### Only S3 ######
            elif self.mode == 3:
                for j in range(1, self.window_size + 1):
                    n_rights.append(self.data[i + j].value)
                    n_lefts.append(self.data[i - j].value)
                S = (2 * self.data[i].value - np.sum(n_rights) / self.window_size - np.sum(n_lefts) / self.window_size) / 2

            _pfv.append(S)  # '_pfv' is peak function values.
            n_rights, n_lefts = [], []

        return _pfv

    def PeakDetect(self):
        pre_output, output  = [], []
        binary_output =  copy.deepcopy(self.data)
        data_k = self.data[self.window_size:len(self.data) - self.window_size]

        _pfv = self.S_number()

        mean = np.mean(_pfv)  # mean of peak function values.
        SD = np.std(_pfv)  # SD of peak function values.

        for i in range(len(_pfv)):
            if (_pfv[i] > 0 and (_pfv[i] - mean) > (self.threshold * SD)):
                epochTime = data_k[i].epochTime
                value = data_k[i].value
                peak = (epochTime,value)
                pre_output.append(peak)


        #### choose maximum value in the window  ####
        for shift in range(0, len(pre_output), self.window_size):
            dataSet = pre_output[shift:shift + self.window_size]
            #select maximum peak in tuple('value')
            maximum_peak = sorted(dataSet, key=lambda x: x[1], reverse=True)[0]
            output.append(maximum_peak)

        # change output into 0 or 1.
        for i in range(len(output)):
            for j in range(len(self.data)):
                if output[i][0] == self.data[j].epochTime: # 1 in case there is peak.
                    binary_output[j].value = 1
                else:
                    binary_output[j].value = 0

        return output,binary_output