#include <math.h>
#include <string.h>
#include <cmath>
#include <iostream>
#include "naive_dd.h"

//Unnecessary
using namespace std;

typedef struct {
    int   index;
    int   startIndex;
    int   endIndex;
    dtype nearestDistance;
} DiscordWindow;

typedef struct {
    int   numThreads;
    int * syncFlags;
} BusyBarrier;

typedef struct {
    darr            data;
    wdarr           windowList;
    int             offsetWindowList;
    int             countWindowList;
    int             windowLength;
    int             windowStep;
    DiscordWindow * pDiscordWindow;

    int             threadNum;
    BusyBarrier     bar;
} ThreadArg;

int GetNumWindows(int dataLength, int windowLength, int windowStep) {
    //Assuming that the remaining data points will not be included in the calculation
    int stpLastWindow = dataLength - windowLength;
    int numWindows = 0;
    int stpIndex = 0;
    while (stpIndex < stpLastWindow) {
        stpIndex += windowStep;
        numWindows++;
    }
}

int GetWindowList_mt(darr data, wdarr windowList,
    int windowLength, int windowStep, int offsetWindowList, int countWindowList) {

    int startIdx   = offsetWindowList;
    int endIdx     = startIdx + countWindowList;
    int stepOffset = startIdx * windowStep;
    for (int i=startIdx;i<endIdx;i++) {

        windowList.data[i].data   = new dtype [windowLength];
        windowList.data[i].length = windowLength;
        dtype * ptr               = windowList.data[i].data;

        for (int j=0;j<windowLength;j++)
            ptr[j] = data.data[stepOffset + j];
        stepOffset += windowStep;
    }
}

int ConvertWindowList_ZScore_mt(wdarr windowList, int offsetWindowList, int countWindowList) {

    int startIdx = offsetWindowList;
    int endIdx = offsetWindowList + countWindowList;
    for (int i=startIdx;i<endIdx;i++) {

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

void InitBusyBarrier(BusyBarrier * bar, int numThreads) {

    bar->numThreads = numThreads;
    bar->syncFlags  = new int [bar->numThreads];
    memset(bar->syncFlags, 0, bar->numThreads * sizeof(int));
}

void WaitAtBarrier(BusyBarrier bar, int threadNum) {

    bar.syncFlags[threadNum] = 1;

    int numThreads = bar.numThreads;
    bool proceed = true;
    do {
        proceed = true;
        for (int i=0;i<numThreads;i++) {
            proceed &= (bar.syncFlags[i] == 1);
        }
    } while(!proceed);
}

void FreeBusyBarrier(BusyBarrier bar) {
    delete [] bar.syncFlags;
}

void * HS_NaiveDetect_th(void * arg) {

    ThreadArg     * tharg = reinterpret_cast<ThreadArg *>(arg);
    darr            data              = tharg->data;
    wdarr           windowList       = tharg->windowList;
    int             offsetWindowList = tharg->offsetWindowList;
    int             countWindowList  = tharg->countWindowList;
    int             windowLength     = tharg->windowLength;
    int             windowStep       = tharg->windowStep;
    DiscordWindow * pDiscordWindow   = tharg->pDiscordWindow;
    int             threadNum        = tharg->threadNum;
    BusyBarrier     bar              = tharg->bar;

    GetWindowList_mt(data, windowList, windowLength, windowStep, offsetWindowList, countWindowList);
    ConvertWindowList_ZScore_mt(windowList, offsetWindowList, countWindowList);
    WaitAtBarrier(bar, threadNum);

    int startIdx   = offsetWindowList;
    int endIdx     = startIdx + countWindowList;
    int numWindows = windowList.length;
    for (int i=startIdx;i<endIdx;i++) {
        dtype nearest_neighbor_dist = 999999.99e+99;
        int i_start_index = i * windowStep;
        for (int j=0;j<numWindows;j++) {
            int j_start_index = j * windowStep;
            if ((abs(j_start_index - i_start_index)) < windowLength) {
                continue;
            }
            dtype dist = GetDistance(windowList.data[i], windowList.data[j], windowLength);
            if (dist < nearest_neighbor_dist)
                nearest_neighbor_dist = dist;
        }

        pDiscordWindow[i].index           = i;
        pDiscordWindow[i].startIndex      = i_start_index;
        pDiscordWindow[i].endIndex        = i_start_index + windowLength;
        pDiscordWindow[i].nearestDistance = nearest_neighbor_dist;
    }

    pthread_exit(0);
}

void HS_NaiveDetect_mt(dtype * data, int dataLength, dtype ** retIndice, int * retNum,
    int windowLength, int windowStep, int saxLength, int numThreads) {

    int _windowLength = windowLength;
    int _windowStep = windowStep;
    int _numThreads = numThreads;

    int _saxLength = saxLength;
    if ((saxLength > MAX_SAX_LENGTH) || (saxLength < MIN_SAX_LENGTH))
        _saxLength = DEFAULT_SAX_LENGTH;

    darr            _data;
    wdarr           _windowList;
    wdarr           _paaList;
    wsaxarr         _saxList;
    DiscordWindow * _pDiscordWindow;

    _data.data = data;
    _data.length = dataLength;

    //Initialize bare window list
    int numWindows     = GetNumWindows(_data.length, _windowLength, _windowStep);
    _windowList.data   = new darr [numWindows];
    _windowList.length = numWindows;
    _pDiscordWindow    = new DiscordWindow [numWindows];

    //========================================================================

    //Create threads
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

    BusyBarrier bar;
    InitBusyBarrier(&bar, numThreads);

    ThreadArg * thArg = new ThreadArg [numThreads];
    pthread_t * threads = new pthread_t [numThreads];

    int numWindowsTh     = numWindows / _numThreads;
    int numWindowsRem    = numWindows % _numThreads;
    int offsetWindowList = 0;

    for (int i=0;i<numThreads;i++) {
        int windowCount = (i > numWindowsRem - 1) ? numWindowsTh : numWindowsTh + 1;

        thArg[i].data             = _data;
        thArg[i].windowList       = _windowList;
        thArg[i].offsetWindowList = offsetWindowList;
        thArg[i].countWindowList  = windowCount;
        thArg[i].windowLength     = _windowLength;
        thArg[i].windowStep       = _windowStep;
        thArg[i].pDiscordWindow   = _pDiscordWindow;
        thArg[i].threadNum        = i;
        thArg[i].bar              = bar;

        int rc = pthread_create(&threads[i], &attr, HS_NaiveDetect_th, reinterpret_cast<void *>(&thArg[i]));
        if (rc)
            cout << "Error: cannot create threads (" << rc << ")." << endl;
        offsetWindowList += windowCount;
    }

    pthread_attr_destroy(&attr);

     //Join threads here
    for (int i=0;i<numThreads;i++) {
        void * status;
        int rc = pthread_join(threads[i], &status);
        if (rc)
            cout << "Error: cannot join threads (" << rc << ")." << endl;
    }

    dtype maxDistance = 0;
    int   maxIndex = -1;
    for (int i=0;i<numWindows;i++) {
        if (_pDiscordWindow[i].nearestDistance > maxDistance) {
            maxIndex = i;
            maxDistance = _pDiscordWindow[i].nearestDistance;
        }
    }

    //========================================================================

    dtype * retIndiceTemp = new dtype [2];
    retIndiceTemp[0] = static_cast<dtype>(_pDiscordWindow[maxIndex].startIndex);
    retIndiceTemp[1] = static_cast<dtype>(_pDiscordWindow[maxIndex].endIndex);

    FreeWindowList(_windowList);
    delete [] _pDiscordWindow;

    FreeBusyBarrier(bar);
    delete [] thArg;
    delete [] threads;

    *retIndice = retIndiceTemp;
    *retNum = dataLength;

}