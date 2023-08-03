#include <math.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include "naive_dd_common.h"

using namespace std;

void * EuclideanDistance_cpu(void * arg) {

    ThreadArg * thArg = reinterpret_cast<ThreadArg *>(arg);
    FrameInfo     fi                  = thArg->fi;
    int           frameStart          = thArg->frameStart;
    int           frameCount          = thArg->frameCount;
    int           knowledgeWindowSize = thArg->knowledgeWindowSize;
    int           subWindowIndex      = thArg->subWindowIndex;

    int   subWindowSize       = fi.subWindows[subWindowIndex];
    int   frameEndExclusive   = frameStart + frameCount;
    for (int frameIdx=frameStart;frameIdx<frameEndExclusive;frameIdx++) {

        dtype largestDist         = 0.0;
        int   largestSubWindowIdx = -1;

        dtype * frameData        = &fi.stdData[fi.dataOffset[frameIdx]];
        int     frameLen         = fi.stopIndices[frameIdx] - fi.startIndices[frameIdx];
        int     lastSubWindowIdx = frameLen - subWindowSize;

        for (int curSubWindowIdx=0;curSubWindowIdx<lastSubWindowIdx;curSubWindowIdx++) {

            dtype   curNearestDist   = 999999.99e+99;

            for (int compSubWindowIdx=0;compSubWindowIdx<lastSubWindowIdx;compSubWindowIdx++) {

                if (abs(curSubWindowIdx - compSubWindowIdx) < subWindowSize)
                    continue;
            
                dtype sumSqErr = 0.0;
                for (int idx=0;idx<subWindowSize;idx++) {
                    dtype p1 = frameData[curSubWindowIdx + idx];
                    dtype p2 = frameData[compSubWindowIdx + idx];
                    sumSqErr += pow(p1 - p2, 2.0);
                }
                dtype euclideanDist = sqrt(sumSqErr);
                if (euclideanDist < curNearestDist)
                    curNearestDist = euclideanDist;
            }

            if (curNearestDist > largestDist) {
                largestDist = curNearestDist;
                largestSubWindowIdx = curSubWindowIdx;
            }
        }

        fi.temp[frameIdx] = largestDist;
        fi.temp1[frameIdx] = fi.startIndices[frameIdx] + largestSubWindowIdx;
        fi.temp2[frameIdx] = fi.temp1[frameIdx] + subWindowSize;
    }
}

void HS_NaiveDetect_cpu(
    dtype * data, int dataLength,
    int ** retIndice, int * retNum,
    int ** retIndice1, int * retNum1,
    int knowledgeWindowSize, int windowStep, int minWindowSize, int threads) {

    FrameInfo     fi; //Input  - List of data frames
    AnomalyMatrix am; //Output - Tuple of start-end indices with anomalies

    if (CreateFrameInfo(&fi, data, dataLength,
        knowledgeWindowSize, minWindowSize, windowStep) != SUCCESS) {
        cout << "Error:      Failed to initialize" << endl;
        exit(-1);
    }

    CreateAnomalyMatrix(fi, &am);

    ThreadArg * thArg = new ThreadArg[threads];

    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

    int framePerThread  = fi.frameCount / threads;
    int frameRemainders = fi.frameCount % threads;

    for (int subWinIdx=0;subWinIdx<fi.subWindowCount;subWinIdx++) {

        pthread_t * th    = new pthread_t[threads];

        int frameOffset = 0;
        for (int i=0;i<threads;i++) {
            int frameCount = (i > (frameRemainders - 1)) ?
                framePerThread : framePerThread + 1;

            thArg[i].fi = fi;
            thArg[i].frameStart = frameOffset;
            thArg[i].frameCount = frameCount;
            thArg[i].knowledgeWindowSize = knowledgeWindowSize;
            thArg[i].subWindowIndex = subWinIdx;

            int rc = pthread_create(&th[i], &attr,
                EuclideanDistance_cpu,
                reinterpret_cast<void *>(&(thArg[i])));

            frameOffset += frameCount;
        }

        void * status;
        for (int i=0;i<threads;i++) {
            pthread_join(th[i], &status);
        }

        memcpy(am.startIndices[subWinIdx], fi.temp1, fi.frameCount * sizeof(int));
        memcpy(am.stopIndices[subWinIdx], fi.temp2, fi.frameCount * sizeof(int));

        delete [] th;
    }

    //TODO: Process the result here

    int alarmCount = 0;
    for (int i=0;i<fi.frameCount;i++) {

        int left_bd = am.startIndices[fi.subWindowCount-1][i];
        int right_bd = am.stopIndices[fi.subWindowCount-1][i];
        int left_largest = am.startIndices[0][i];
        int right_largest = am.stopIndices[0][i];

        bool alarm = true;
        for (int j=fi.subWindowCount-2;j>=0;j--) {
            int left_test = am.startIndices[j][i];
            int right_test = am.startIndices[j][i];
            if ((left_bd <= right_test) && (right_bd >= left_test)) {
                if (left_bd < left_test) left_bd = left_test;
                if (right_bd > right_test) right_bd = right_test;
            }
            else
                alarm = false;
        }

        if (alarm) {
            fi.temp1[alarmCount] = left_largest;
            fi.temp2[alarmCount] = right_largest;
            alarmCount++;
        }
        else {
            cout << "Frame [" << i << "] dropped" << endl;
        }
    }

    cout << "    knowledge:     " << knowledgeWindowSize << endl;
    cout << "    windowStep:    " << windowStep << endl;
    cout << "    minWindowSize: " << minWindowSize << endl;

    *retIndice  = fi.temp1;
    *retNum     = alarmCount;
    *retIndice1 = fi.temp2;
    *retNum1    = alarmCount;

#if 1
    for (int i=0;i<alarmCount;i++)
       cout << "[eud(" << i << ")]: " << fi.temp[i] << " : " 
           << fi.startIndices[i] << " : "
	   << fi.temp1[i] << " - " << fi.temp2[i] << endl;
#endif

    delete [] thArg;
}
