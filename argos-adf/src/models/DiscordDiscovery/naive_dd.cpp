#include <math.h>
#include <string.h>
#include <cmath>
#include <iostream>
#include "naive_dd.h"

//Unnecessary
using namespace std;

int GetWindowList(darr data, wdarr * retWindowList, int windowLength, int windowStep) {
    wdarr windowList;

    //Assuming that the remaining data points will not be included in the calculation
    int stpLastWindow = data.length - windowLength;
    int numWindows = 0;
    int stpIndex = 0;
    while (stpIndex < stpLastWindow) {
        stpIndex += windowStep;
        numWindows++;
    }

    windowList.data   = new darr [numWindows];
    windowList.length = numWindows;
    int stepOffset = 0;
    for (int i=0;i<numWindows;i++) {
        windowList.data[i].data   = new dtype [windowLength];
        windowList.data[i].length = windowLength;
        dtype * ptr = windowList.data[i].data;

#if 0 //Which is faster? Whether to use the CPU or DMA to copy content of memory locations
        for (int j=0;j<windowLength;j++) {
            ptr[j] = data.data[stepOffset + j];
        }
#else
        memcpy(
                reinterpret_cast<void *>(ptr),
                reinterpret_cast<void *>(&(data.data[stepOffset])),
                windowLength * sizeof(dtype));
#endif
        stepOffset += windowStep;
    }

    *retWindowList = windowList;
}

void FreeWindowList(wdarr windowList) {

    int numWindows = windowList.length;
    for (int i=0;i<numWindows;i++) {

        darr arr = windowList.data[i];
        delete [] arr.data;
    }
    delete [] windowList.data;
}

int ConvertWindowList_ZScore(wdarr windowList) {

    int numWindows = windowList.length;
    for (int i=0;i<numWindows;i++) {

        dtype * ptr       = windowList.data[i].data;
        int     numPoints = windowList.data[i].length;
        dtype   sum       = 0.0;
        dtype   mean      = 0.0;
        dtype   sd        = 0.0;

        //Calculate Mean
        for (int j=0;j<numPoints;j++)
            sum += ptr[j];
        mean = sum / static_cast<dtype>(numPoints);

        //Calculate Standard Deviation
        sum = 0.0;
        for (int j=0;j<numPoints;j++) {
            sum += pow(abs(ptr[j] - mean), 2.0);
        }
        sd = sqrt(sum / static_cast<dtype>(numPoints));

        //Calculate Z-score
        for (int j=0;j<numPoints;j++) {
            dtype temp = (ptr[j] - mean) / sd;
            ptr[j] = temp;
        }
    }

    return 0;
}

int GetPAA(wdarr windowList, int windowLength, int saxLength, wdarr * paa) {

    int numWindows = windowList.length;

    wdarr paaTemp;
    paaTemp.data   = new darr [numWindows];
    paaTemp.length = numWindows;

    for (int i=0;i<numWindows;i++) {

        dtype * ptr         = windowList.data[i].data;
        int     numPoints   = windowList.data[i].length;
        int     numWords    = windowLength / saxLength;
        int     numSections = windowLength / numWords;

        paaTemp.data[i].data   = new dtype [numSections];
        paaTemp.data[i].length = numSections;

        dtype sum = 0.0;
        int   sectionIndex = 0;
        for (int j=0;j<numPoints;j++) {
            sum += ptr[j];
            if (((j + 1) % numWords) == 0) {
                paaTemp.data[i].data[sectionIndex] = sum / static_cast<dtype>(numWords);
                sectionIndex += 1;
                sum = 0.0;
            }
        }
    }

    *paa = paaTemp;

    return 0;
}

int GetSAX(wdarr paa, int saxLength, wsaxarr * sax) {

    int numWindows = paa.length;

    wsaxarr saxTemp;
    saxTemp.data   = new saxarr [numWindows];
    saxTemp.length = numWindows;

    for (int i=0;i<numWindows;i++) {

        dtype * ptr       = paa.data[i].data;
        int     numPoints = paa.data[i].length;

        saxTemp.data[i].data   = new saxtype [numPoints];
        saxTemp.data[i].length = numPoints;
        saxtype * ptrSax       = saxTemp.data[i].data;

        for (int j=0;j<numPoints;j++) {
            if (ptr[j] <= -0.67)
                ptrSax[j] = 0;
            else if ((ptr[j] > -0.67) && (ptr[j] <= 0))
                ptrSax[j] = 1;
            else if ((ptr[j] > 0) && (ptr[j] <= 0.67))
                ptrSax[j] = 2;
            else if (ptr[j] > 0.67)
                ptrSax[j] = 3;
        }
    }

    *sax = saxTemp;

    return 0;
}

dtype GetEuclideanDist(darr seq1, darr seq2, int windowLength) {

    dtype sumsq = 0.0;
    for (int i=0;i<windowLength;i++) {
        sumsq += pow(seq1.data[i] - seq2.data[i], 2.0);
    }

    return sqrt(sumsq);
}

dtype GetDistance(darr seq1, darr seq2, int windowLength) {

    return GetEuclideanDist(seq1, seq2, windowLength);
}

void HS_NaiveDetect(dtype * data, int dataLength, dtype ** retIndice, int * retNum,
    int windowLength, int windowStep, int saxLength) {

    int _windowLength = windowLength;
    int _windowStep = windowStep;

    int _saxLength = saxLength;
    if ((saxLength > MAX_SAX_LENGTH) || (saxLength < MIN_SAX_LENGTH))
        _saxLength = DEFAULT_SAX_LENGTH;

    //Verify if length of window is divisible by length of SAX word
    //if ((_windowLength % _saxLength) != 0)
    //    return;

    darr    _data;
    wdarr   _windowList;
    wdarr   _paaList;
    wsaxarr _saxList;
    _data.data = data;
    _data.length = dataLength;
    GetWindowList(_data, &_windowList, _windowLength, _windowStep);
    ConvertWindowList_ZScore(_windowList);
    //GetPAA(_windowList, _windowLength, _saxLength, &_paaList);
    //GetSAX(_paaList, _saxLength, &_saxList);

    //========================================================================

    int   numWindows = _windowList.length;
    dtype best_so_far_dist = 0;
    int   best_so_far_window = -1;

    dtype dist_sum = 0.0;
    int   dist_count = 0;

    for (int i=0;i<numWindows;i++) {
    //for (int i=numWindows-1;i>=0;i--) {
        dtype nearest_neighbor_dist = 999999.99e+99;
        for (int j=0;j<numWindows;j++) {
            int i_start_index = i * _windowStep;
            int j_start_index = j * _windowStep;
            if ((abs(j_start_index - i_start_index)) < _windowLength) {
                continue;
            }
            dtype dist = GetDistance(_windowList.data[i], _windowList.data[j], _windowLength);
            if (dist < nearest_neighbor_dist)
                nearest_neighbor_dist = dist;
        }
        if (nearest_neighbor_dist > best_so_far_dist) {
            best_so_far_dist = nearest_neighbor_dist;
            best_so_far_window = i;
        }

        dist_sum += nearest_neighbor_dist;
        dist_count += 1;
    }
    dtype dist_mean = (dist_sum - best_so_far_dist) / (dist_count-1);

    //========================================================================

    dtype * retIndiceTemp = new dtype [2];
    retIndiceTemp[0] = static_cast<dtype>(best_so_far_window * _windowStep);
    retIndiceTemp[1] = static_cast<dtype>((best_so_far_window * _windowStep) + _windowLength);

    *retIndice = retIndiceTemp;
    *retNum = dataLength;

    //Deallocate temporary data structures
    FreeWindowList(_windowList);
}