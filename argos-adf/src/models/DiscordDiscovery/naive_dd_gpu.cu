#include <cuda.h>
#include <unistd.h>
#include <iostream>
#include "naive_dd_common.h"

using namespace std;

#define CUDAERR_RET(str) if (str != cudaSuccess) return ERROR

int CopyFrameInfoToDevice(FrameInfo fi, FrameInfo * fi_device) {

    //Allocate device memory
    CUDAERR_RET(cudaMalloc(
        reinterpret_cast<void **>(&(fi_device->stdData)), fi.stdDataSize * sizeof(dtype)));
    fi_device->stdDataSize = fi.stdDataSize;

    CUDAERR_RET(cudaMalloc(
	reinterpret_cast<void **>(&(fi_device->startIndices)), fi.frameCount * sizeof(int)));
    CUDAERR_RET(cudaMalloc(
	reinterpret_cast<void **>(&(fi_device->stopIndices)), fi.frameCount * sizeof(int)));
    CUDAERR_RET(cudaMalloc(
	reinterpret_cast<void **>(&(fi_device->dataOffset)), fi.frameCount * sizeof(int)));
    fi_device->frameCount = fi.frameCount;

    CUDAERR_RET(cudaMalloc(
        reinterpret_cast<void **>(&(fi_device->subWindows)), fi.subWindowCount * sizeof(int)));
    fi_device->subWindowCount = fi.subWindowCount;

    CUDAERR_RET(cudaMalloc(
        reinterpret_cast<void **>(&(fi_device->temp)), fi.frameCount * sizeof(dtype)));
    CUDAERR_RET(cudaMalloc(
        reinterpret_cast<void **>(&(fi_device->temp1)), fi.frameCount * sizeof(int)));
    CUDAERR_RET(cudaMalloc(
        reinterpret_cast<void **>(&(fi_device->temp2)), fi.frameCount * sizeof(int)));

    //Memory content transfer to device
    CUDAERR_RET(cudaMemcpy(
        fi_device->stdData, fi.stdData, 
	fi.stdDataSize * sizeof(dtype), cudaMemcpyHostToDevice));

    CUDAERR_RET(cudaMemcpy(
        fi_device->startIndices, fi.startIndices,
	fi.frameCount * sizeof(int), cudaMemcpyHostToDevice));
    CUDAERR_RET(cudaMemcpy(
        fi_device->stopIndices, fi.stopIndices,
	fi.frameCount * sizeof(int), cudaMemcpyHostToDevice));
    CUDAERR_RET(cudaMemcpy(
        fi_device->dataOffset, fi.dataOffset,
	fi.frameCount * sizeof(int), cudaMemcpyHostToDevice));

    CUDAERR_RET(cudaMemcpy(
	fi_device->subWindows, fi.subWindows,
	fi.subWindowCount * sizeof(int), cudaMemcpyHostToDevice));

    return SUCCESS;
}

__global__ void EuclideanDistance(FrameInfo fi, int knowledgeWindowSize, int subWindowIdx) {

    extern __shared__ dtype frameData[];

    int frameId     = (blockIdx.y * gridDim.x) + blockIdx.x;
    int locThreadId = (threadIdx.y * blockDim.x) + threadIdx.x;
    int tpb         = blockDim.y * blockDim.x;
    int stride      = knowledgeWindowSize / tpb;
    stride += ((knowledgeWindowSize % tpb) != 0) ? 1 : 0;

    int     frameLen   = fi.stopIndices[frameId] - fi.startIndices[frameId];
    dtype * frameStart = &fi.stdData[fi.dataOffset[frameId]];

    //Results
    dtype * atomicDist     = &(frameData[frameLen]);
    int   * atomicLock     = reinterpret_cast<int *>(&(frameData[frameLen + 1]));
    int   * atomicStartIdx = reinterpret_cast<int *>(&(frameData[frameLen + 2]));
    int   * atomicEndIdx   = reinterpret_cast<int *>(&(frameData[frameLen + 3]));

    int subWindowSize    = fi.subWindows[subWindowIdx];
    int lastSubWindowIdx = frameLen - subWindowSize;

    //Load data into shared memory
    for (int iStrd=0;iStrd<stride;iStrd++) {
        int threadId = (iStrd * tpb) + locThreadId;

        if (threadId > knowledgeWindowSize)
            continue;

        if (threadId == 0) {
            *atomicDist = 0.0;
            *atomicLock = 0;
        }
        frameData[threadId] = frameStart[threadId];
    }
    __syncthreads();

    //Start looking for anomalies
    for (int iStrd=0;iStrd<stride;iStrd++) {
        int threadId = (iStrd * tpb) + locThreadId;
        int curSubWindowIdx = threadId;
        if (threadId > lastSubWindowIdx)
            return;

        dtype curNearestDist = 999999.99e+99;
        for (int compSubWindowIdx=0;compSubWindowIdx<lastSubWindowIdx;compSubWindowIdx++) {
            if (abs(curSubWindowIdx - compSubWindowIdx) < subWindowSize)
	        continue;

            dtype sumSqErr = 0.0;
            for (int idx=0;idx<subWindowSize;idx++) {
                sumSqErr += powf(frameStart[curSubWindowIdx + idx] - 
                    frameStart[compSubWindowIdx + idx], 2.0);
            }
            dtype euclideanDist = sqrtf(sumSqErr);
            if (euclideanDist < curNearestDist)
                curNearestDist = euclideanDist;
        }
        atomicCAS(atomicLock, 0, 1);
        if (curNearestDist > *atomicDist) {
            *atomicDist     = curNearestDist;
            *atomicStartIdx = threadId;
            *atomicEndIdx   = threadId + subWindowSize;
        }
        atomicCAS(atomicLock, 1, 0);

    }
    __syncthreads();

    if (locThreadId == 0) {
        fi.temp[frameId] = *atomicDist;
        fi.temp1[frameId] = fi.startIndices[frameId] + *atomicStartIdx;
        fi.temp2[frameId] = fi.startIndices[frameId] + *atomicEndIdx;
    }
}

void HS_NaiveDetect_gpu(
    dtype * data, int dataLength,
    int ** retIndice, int * retNum,
    int ** retIndice1, int * retNum1,
    int knowledgeWindowSize, int windowStep, int minWindowSize) {

    FrameInfo fi, fi_device;

    if (CreateFrameInfo(&fi, data, dataLength,
        knowledgeWindowSize, minWindowSize, windowStep) != SUCCESS) {
        cout << "Error:      Failed to initialize" << endl;
	cout << "CUDA error: " << cudaGetErrorString(cudaGetLastError()) << endl;
        exit(-1);
    }
    if (CopyFrameInfoToDevice(fi, &fi_device) != SUCCESS) {
        cout << "Error:      Failed to allocate device memory" << endl;
	cout << "CUDA error: " << cudaGetErrorString(cudaGetLastError()) << endl;
	exit(-1);
    }

    AnomalyMatrix am;
    CreateAnomalyMatrix(fi, &am);


    cudaError_t ce;
    for (int i=0;i<fi.subWindowCount;i++) {
        //Launch with: Blocks=Frames, Threads=Sub-windows
        //TODO: There is something wrong with threads=256
        dim3 blocks(fi.frameCount, 1, 1);
        EuclideanDistance<<<blocks, 1024, 
            (knowledgeWindowSize + 4) * sizeof(dtype)>>>(fi_device, knowledgeWindowSize, i);
        cudaThreadSynchronize();
        ce = cudaGetLastError();

        ce = cudaMemcpy(fi.temp, fi_device.temp,
            fi.frameCount * sizeof(dtype), cudaMemcpyDeviceToHost);
        if (ce != cudaSuccess)
            cout << "Err: " << cudaGetErrorString(ce) << endl;
        ce = cudaMemcpy(am.startIndices[i], fi_device.temp1, 
            fi.frameCount * sizeof(int), cudaMemcpyDeviceToHost);
        if (ce != cudaSuccess)
            cout << "Err: " << cudaGetErrorString(ce) << endl;
        ce = cudaMemcpy(am.stopIndices[i], fi_device.temp2, 
            fi.frameCount * sizeof(int), cudaMemcpyDeviceToHost);
        if (ce != cudaSuccess)
            cout << "Err: " << cudaGetErrorString(ce) << endl;
    }

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
    cout << "    Execution:     " << cudaGetErrorString(ce) << endl;

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
}

