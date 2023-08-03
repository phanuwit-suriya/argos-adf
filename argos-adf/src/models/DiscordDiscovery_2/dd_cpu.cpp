#include "dd_common.h"
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <cmath>
#include <iostream>

using namespace std;

int InitializeFrames(MetricInfo * mi) {

    if (mi == NULL)
        return -1;

    pdt * data       = mi->data;
    int   dataLength = mi->dataLength;

    int knowledgeWindowSize = mi->options.knowledgeWindowSize;
    int windowStep          = mi->options.windowStep;

    if (dataLength < knowledgeWindowSize)
        return -1;

    int lastStopIndex = knowledgeWindowSize;
    int fCount        = 0;
    do {
        fCount++;
        lastStopIndex += windowStep;
    } while (lastStopIndex < dataLength);

    mi->data          = data;
    mi->fStartIndices = new int [fCount];
    mi->fStopIndices  = new int [fCount];
    mi->fCount        = fCount;

    int fStartIndex = 0;
    for (int idx=0;idx<fCount;idx++) {
        mi->fStartIndices[idx] = fStartIndex;
        mi->fStopIndices[idx]  = fStartIndex + knowledgeWindowSize;
        fStartIndex += windowStep;
    }

    return 0;
}

int InitializeSubwindows(MetricInfo * mi) {

    if (mi == NULL)
        return -1;

    int knowledgeWindowSize = mi->options.knowledgeWindowSize;
    int minSubwindowSize    = mi->options.minSubwindowSize;

    int swCount = 0;
    int lastSwStopIndex = minSubwindowSize;
    int fCount  = mi->fCount;

    //Determine the number of sub-windows with a particular size of sub-window
    while (lastSwStopIndex < knowledgeWindowSize) {
        swCount++;
        lastSwStopIndex++;
    }
    mi->swStartIndices  = new int [mi->fCount * swCount];
    mi->swStopIndices   = new int [mi->fCount * swCount];
    mi->swOwnerFrame    = new int [mi->fCount * swCount];
    mi->swPerFrameCount = swCount;
        
    //Initialize sub-windows of all frames
    for (int fIdx=0;fIdx<fCount;fIdx++) {

        int swStartIndex = 0;
        for (int swIdx=0;swIdx<swCount;swIdx++) {
            mi->swStartIndices[(fIdx * swCount) + swIdx] = swStartIndex;
            mi->swStopIndices[(fIdx * swCount) + swIdx] = swStartIndex + minSubwindowSize;
            mi->swOwnerFrame[(fIdx * swCount) + swIdx] = fIdx;
            swStartIndex++;
        }
    }

    return 0;
}

#define CHECK_ERR(exp)     \
do {                       \
    int ret = exp;         \
    if (ret) return ret;   \
} while(0)

int CreateMetricInfo(MetricInfo * mi) {

    CHECK_ERR(InitializeFrames(mi));
    CHECK_ERR(InitializeSubwindows(mi));

    return 0;
}
#undef CHECK_ERR

#define RELEASE(var) \
if (var != NULL)     \
    delete [] var
int DestroyMetricInfo(MetricInfo * mi) {

    RELEASE(mi->stdData);
    RELEASE(mi->fStartIndices);
    RELEASE(mi->fStopIndices);
    RELEASE(mi->swStartIndices);
    RELEASE(mi->swStopIndices);
    RELEASE(mi->swOwnerFrame);

    return 0;
}
#undef RELEASE

int CreateAnomalyList(MetricInfo * mi, AnomalyList * al) {

    if (al == NULL)
        return -1;

    al->startIndices = new int [mi->fCount];
    al->stopIndices  = new int [mi->fCount];
    al->frameStartIndices = new int [mi->fCount];
    al->frameStopIndices  = new int [mi->fCount];

    return 0;

}

void StandardizeData(pdt * dataIn, pdt * dataOut, int dataLength) {

    pdt mean = 0.0;
    pdt sd   = 0.0;
    pdt sum  = 0.0;

    //Calculate Mean
    for (int idx=0;idx<dataLength;idx++)
        sum += dataIn[idx];
    mean = sum / static_cast<pdt>(dataLength);

    //Calculate Standard Deviation
    sum = 0.0;
    for (int idx=0;idx<dataLength;idx++)
        sum += pow(abs(dataIn[idx] - mean), 2.0);
    sd = sqrt(sum / static_cast<pdt>(dataLength));

    //Calculate Z-score
    for (int idx=0;idx<dataLength;idx++) {
        dataOut[idx] = (dataIn[idx] - mean) / sd;
    }
}

void InitializeMetricDataAndOptions(
    pdt        * data,
    int          dataLength,
    int          knowledgeWindowSize,
    int          windowStep,
    int          minSubwindowSize,
    int          detectionFocus,
    MetricInfo * mi) {

    //Initialize metric data
    mi->data       = data;
    mi->dataLength = dataLength;

    //Initialize options for the metric
    mi->options.knowledgeWindowSize = knowledgeWindowSize;
    mi->options.windowStep          = windowStep;
    mi->options.minSubwindowSize    = minSubwindowSize;
    mi->options.detectionFocus      = (detectionFocus == 0x00) ? 
        PatternFocused : PeakFocused;

    mi->stdData         = NULL;
    mi->fStartIndices   = NULL;
    mi->fStopIndices    = NULL;
    mi->fCount          = 0;
    mi->swStartIndices  = NULL;
    mi->swStopIndices   = NULL;
    mi->swOwnerFrame    = NULL;
    mi->swPerFrameCount = 0;

    /**
     *    Note: The peak-focusing detection standardize 
     *          the entire time series metric data.
     */
    if (mi->options.detectionFocus == PeakFocused) {
        mi->stdData = new pdt [mi->dataLength];
        StandardizeData(mi->data, mi->stdData, mi->dataLength);
    }
}

typedef struct {
    MetricInfo  * mi;
    AnomalyList * al;
    int           startFrameIndex;
    int           stopFrameIndex;
} ThreadArg;

void * dd_SingleProcess(void * arg) {

    ThreadArg   * thArg = reinterpret_cast<ThreadArg *>(arg);
    MetricInfo  * mi    = thArg->mi;
    AnomalyList * al    = thArg->al;
    int startFrameIndex = thArg->startFrameIndex;
    int stopFrameIndex  = thArg->stopFrameIndex;

    pdt * isw  = new pdt [mi->options.minSubwindowSize];
    pdt * csw = new pdt [mi->options.minSubwindowSize];

    //cout << startFrameIndex << " - " << stopFrameIndex << endl;
    for (int fIdx=startFrameIndex;fIdx<stopFrameIndex;fIdx++) {

        pdt largestDist = 0.0;
        int largestSubwindowIndex = -1;
        int fStartIndex = mi->fStartIndices[fIdx];
        int fStopIndex  = mi->fStopIndices[fIdx];
        int fswIndex    = fIdx * mi->swPerFrameCount;

        for (int iswIdx=0;iswIdx<mi->swPerFrameCount;iswIdx++) {

            pdt nearestDist = 999999999.99e+99;
            int iswIndex = fswIndex + iswIdx;
            int iswStartIndex = fStartIndex + mi->swStartIndices[iswIndex];
            int iswStopIndex  = fStartIndex + mi->swStopIndices[iswIndex];

            /* Load data chunk for ISW */
            switch (mi->options.detectionFocus) {
            case PatternFocused: 
                StandardizeData(
                    &(mi->data[iswStartIndex]), 
                    isw, 
                    mi->options.minSubwindowSize);
                break;
            case PeakFocused:
                memcpy(
                    isw, 
                    &(mi->stdData[iswStartIndex]), 
                    mi->options.minSubwindowSize * sizeof(pdt));
                break;
            default:
                cout << "WTF!" << endl;
                pthread_exit(NULL);
            }

            for (int cswIdx=0;cswIdx<mi->swPerFrameCount;cswIdx++) {

                int cswIndex = fswIndex + cswIdx;
                int cswStartIndex = fStartIndex + mi->swStartIndices[cswIndex];
                int cswStopIndex  = fStartIndex + mi->swStopIndices[cswIndex];

                /* Compare only non-self overlapping */
                if (abs(iswIndex - cswIndex) < mi->options.minSubwindowSize)
                    continue;

                /* Load data chunk for CSW */
                switch(mi->options.detectionFocus) {
                case PatternFocused:
                    StandardizeData(
                        &(mi->data[cswStartIndex]),
                        csw,
                        mi->options.minSubwindowSize);
                    break;
                case PeakFocused:
                    memcpy(
                        csw,
                        &(mi->stdData[cswStartIndex]),
                        mi->options.minSubwindowSize * sizeof(pdt));
                    break;
                default:
                    cout << "WTF!" << endl;
                    pthread_exit(NULL);
                }

                /* Calculate distance between ISW and CSW */
                pdt sumSqErr = 0.0;
                for (int i=0;i<mi->options.minSubwindowSize;i++) 
                    sumSqErr += pow(isw[i] - csw[i], 2.0);
                pdt dist = sqrt(sumSqErr);
                if (dist < nearestDist)
                    nearestDist = dist;
            } /* CSW */
            if (nearestDist > largestDist) {
                largestDist = nearestDist;
                largestSubwindowIndex = iswStartIndex;
            }
        } /* ISW */
        cout << fIdx << " / " << largestSubwindowIndex 
            << " - " << largestSubwindowIndex + mi->options.minSubwindowSize << endl;
        al->startIndices[fIdx] = largestSubwindowIndex;
        al->stopIndices[fIdx]  = largestSubwindowIndex + mi->options.minSubwindowSize;
        al->frameStartIndices[fIdx] = fStartIndex; 
        al->frameStopIndices[fIdx]  = fStopIndex;
    } /* Frame */

    delete [] csw;
    delete [] isw;

    pthread_exit(NULL);
}

int dd_ProcessParallel(MetricInfo & mi, AnomalyList & al, int threads) {

    pthread_t      * th    = new pthread_t [threads];
    ThreadArg      * thArg = new ThreadArg [threads];
    pthread_attr_t   attr;

    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

    /* Divide the work and create threads */
    int framePerThread = mi.fCount / threads;
    int remFrames      = mi.fCount % threads;
    int frameOffset    = 0;
    for (int idx=0;idx<threads;idx++) {
        int startFrameIndex = frameOffset;
        frameOffset += (idx < remFrames) ? framePerThread + 1 : framePerThread;
        thArg[idx].mi = &mi;
        thArg[idx].al = &al;
        thArg[idx].startFrameIndex = startFrameIndex;
        thArg[idx].stopFrameIndex  = frameOffset;

        int ret = pthread_create(&(th[idx]), &attr,
            dd_SingleProcess, reinterpret_cast<void *>(&thArg[idx]));
        //TODO: Error handling here
    }

    /* Join threads */
    void * status;
    for (int idx=0;idx<threads;idx++) {
        pthread_join(th[idx], &status);
    }

    delete [] thArg;
    delete [] th;

    return 0;
}

void dd_cpu(
    pdt *  data,                int   dataLength,
    int ** aStartIndices,       int * aStartIndicesCount,
    int ** aStopIndices,        int * aStopIndicesCount,
    int ** fStartIndices,       int * fStartIndicesCount,
    int ** fStopIndices,        int * fStopIndicesCount,
    int    knowledgeWindowSize,
    int    windowStep,
    int    minSubwindowSize,
    int    detectionFocus,
    int    threads) {

    MetricInfo mi; 

    InitializeMetricDataAndOptions(
        data,
        dataLength,
        knowledgeWindowSize,
        windowStep,
        minSubwindowSize,
        detectionFocus,
        &mi);

    //TODO: Define error code and handling here
    int ret = CreateMetricInfo(&mi);
    if (ret)
        cout << "ERROR CREATE" << endl;
    cout << "dd_cpu" << endl;
    cout << "\tknowledgeWindowSize: " << mi.options.knowledgeWindowSize << endl;
    cout << "\twindowStep:          " << mi.options.windowStep << endl;
    cout << "\tminSubwindowSize:    " << mi.options.minSubwindowSize << endl;
    cout << "\tdetectionFocus:      " << mi.options.detectionFocus << endl;

    AnomalyList al;
    CreateAnomalyList(&mi, &al);
/*
    for (int fIdx=0;fIdx<mi.fCount;fIdx++) {
        cout << "===== F " << mi.fStartIndices[fIdx] << " - " << mi.fStopIndices[fIdx] 
            << " =====" << endl;

        for (int swIdx=0;swIdx<mi.swPerFrameCount;swIdx++) {
            cout << "\t" << mi.swOwnerFrame[(fIdx * mi.swPerFrameCount) + swIdx] << " : " 
                << mi.swStartIndices[(fIdx * mi.swPerFrameCount) + swIdx] << " - "
                << mi.swStopIndices[(fIdx * mi.swPerFrameCount) + swIdx] << endl;
        }
    }
*/

    ret = dd_ProcessParallel(mi, al, threads);

    ret = DestroyMetricInfo(&mi);
    if (ret)
        cout << "ERROR RELEASE" << endl;

    *aStartIndices = al.startIndices;
    *aStopIndices  = al.stopIndices;
    *aStartIndicesCount = mi.fCount;
    *aStopIndicesCount  = mi.fCount;
    *fStartIndices = al.frameStartIndices;
    *fStopIndices  = al.frameStopIndices;
    *fStartIndicesCount = mi.fCount;
    *fStopIndicesCount  = mi.fCount;
}
