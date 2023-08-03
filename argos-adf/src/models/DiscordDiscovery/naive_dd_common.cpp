#include <math.h>
#include <stdlib.h>
#include <cmath>
#include "naive_dd_common.h"

int CreateSubWindows(FrameInfo * fi, int knowledgeWindowSize, int minSubWindowSize) {

    if (fi == NULL)
        return ERROR;

    dtype knowledgeWindowSize_dt = static_cast<dtype>(knowledgeWindowSize);
    dtype minSubWindowSize_dt    = static_cast<dtype>(minSubWindowSize);
    dtype subWindowSizeTemp_dt   = minSubWindowSize_dt;

    int size = 0;
    while ((knowledgeWindowSize_dt / subWindowSizeTemp_dt) >= MINIMUM_WINDOW_RATIO) {
        subWindowSizeTemp_dt += minSubWindowSize_dt;
    	size++;
    }

    fi->subWindows = new int [size];
    fi->subWindowCount = size;
  
    subWindowSizeTemp_dt = minSubWindowSize_dt; 
    int idx = 0; 
    while ((knowledgeWindowSize_dt / subWindowSizeTemp_dt) >= MINIMUM_WINDOW_RATIO) {
	fi->subWindows[idx] = static_cast<int>(subWindowSizeTemp_dt);
        subWindowSizeTemp_dt += minSubWindowSize_dt;	
    	idx++;
    }

    return SUCCESS;
}

int CreateFrameBoundaries(FrameInfo * fi, int dataLength, int knowledgeWindowSize, int windowStep) {

    if (fi == NULL)
        return ERROR;

    int lastStartIndex = dataLength - knowledgeWindowSize;
    int startIndex = 0;
    int frameCount = 0;

    do {
        if (startIndex > lastStartIndex)
	        startIndex = lastStartIndex;
	    startIndex += windowStep;
    	frameCount++;
    } while (startIndex < lastStartIndex);

    fi->startIndices = new int [frameCount];
    fi->stopIndices  = new int [frameCount];
    fi->temp         = new dtype [frameCount];
    fi->temp1        = new int [frameCount];
    fi->temp2        = new int [frameCount];
    fi->frameCount   = frameCount;

    startIndex = 0;
    int frameIdx = 0;
    do {
        if (startIndex > lastStartIndex)
            startIndex = lastStartIndex;
    	fi->startIndices[frameIdx] = startIndex;
	    fi->stopIndices[frameIdx]  = startIndex + knowledgeWindowSize;
    	startIndex += windowStep;
	    frameIdx++;
    } while (startIndex < lastStartIndex);

    return SUCCESS;
}

int CreateFrameData(FrameInfo * fi, dtype * data) {

    if (fi == NULL)
        return ERROR;

    int dataLength = 0;
    for (int idx=0;idx<fi->frameCount;idx++) {
        dataLength += fi->stopIndices[idx] - fi->startIndices[idx];
    }

    fi->stdData     = new dtype [dataLength];
    fi->stdDataSize = dataLength;
    fi->dataOffset  = new int [fi->frameCount];

    int dataOffset = 0;
    for (int idx=0;idx<fi->frameCount;idx++) {

	int startIndex = fi->startIndices[idx];
	int stopIndex  = fi->stopIndices[idx];
	int length = stopIndex - startIndex;

	fi->dataOffset[idx] = dataOffset;

	dtype sum  = 0.0;
	dtype mean = 0.0;
	dtype sd   = 0.0;
	//Calculate Mean
	for (int jIdx=startIndex;jIdx<stopIndex;jIdx++)
            sum += data[jIdx];
	mean = sum / static_cast<dtype>(length);

	//Calculate Standard Deviation
	sum = 0.0;
	for (int jIdx=startIndex;jIdx<stopIndex;jIdx++) {
            sum += pow(abs(data[jIdx] - mean), 2.0);
	}
	sd = sqrt(sum / static_cast<dtype>(length));

	//Calculate Z-score
	for (int jIdx=startIndex;jIdx<stopIndex;jIdx++) {
	    fi->stdData[dataOffset] = (data[jIdx] - mean) / sd;
	    //cout << fi->stdData[dataOffset] << endl;
	    dataOffset++;
	}
	//cout << "===============================" << endl;

        //cout << fi->startIndices[idx] << " - " << fi->stopIndices[idx] - 1 << " / " << fi->dataOffset[idx]<< endl;
    }

    return SUCCESS;
}

int CreateFrameInfo(FrameInfo * fi, dtype * data, int dataLength,
    int knowledgeWindowSize, int minSubWindowSize, int windowStep) {

    ERR_RET(CreateSubWindows(fi, knowledgeWindowSize, minSubWindowSize), SUCCESS, ERROR);
    ERR_RET(CreateFrameBoundaries(fi, dataLength, knowledgeWindowSize, windowStep), SUCCESS, ERROR);
    ERR_RET(CreateFrameData(fi, data), SUCCESS, ERROR);
  
    return SUCCESS;  
}


int CreateAnomalyMatrix(FrameInfo fi, AnomalyMatrix * am) {

    int matSize = fi.frameCount * fi.subWindowCount;
    int * startIndicesMat = new int [matSize];
    int * stopIndicesMat  = new int [matSize];

    AnomalyMatrix amTemp;
    amTemp.startIndices = new int * [fi.subWindowCount];
    amTemp.stopIndices = new int * [fi.subWindowCount];

    int offset = 0;
    for (int i=0;i<fi.subWindowCount;i++) {
        amTemp.startIndices[i] = &(startIndicesMat[offset]);
        amTemp.stopIndices[i] = &(stopIndicesMat[offset]);
        offset += fi.frameCount;
    }

    *am = amTemp;

    return 0;
}


