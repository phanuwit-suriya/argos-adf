#include "dd_common.h"
#include <iostream>

using namespace std;

#ifdef DOUBLE
#define POWER pow
#else
#define POWER powf
#endif /* DOUBLE */

__device__ pdt Device_ST_Mean(pdt * data, int count) {

    pdt sum = 0.0;
    for (int idx=0;idx<count;idx++)
        sum += data[idx];

    return sum / static_cast<pdt>(count);
}

__device__ pdt Device_ST_SD(pdt * data, pdt mean, int count) {

    pdt sum = 0.0;
    for (int idx=0;idx<count;idx++)
        sum += POWER(abs(data[idx] -  mean), 2.0);

    return sqrt(sum / static_cast<pdt>(count));
}

#define DEVICE_ST(exp)      \
do {                        \
    if (threadIdx.x == 0) { \
        exp;                \
    }                       \
    __syncthreads();        \
} while (0)


__global__ void dd_DeviceProcess(
    MetricInfo * mi, AnomalyList * al, pdt * dscores) {

    __shared__ pdt iswMean;
    __shared__ pdt iswSD;
    __shared__ pdt nearestDist;
    __shared__ int lock;
#if 0
#else
    __shared__ pdt dist_s[4096];

    if (threadIdx.x == 0) {
        for (int i=0;i<mi->swPerFrameCount;i++)
            dist_s[i] = 999999999.99e+99;
    }
    __syncthreads();
#endif

    /* Frame-related info. */
    int blockId     = (blockIdx.y * gridDim.x) + blockIdx.x;
    int fIdx        = blockId / mi->swPerFrameCount;
    int fStartIndex = mi->fStartIndices[fIdx];
    //int fStopIndex  = mi->fStopIndices[fIdx];
    int fswIndex    = fIdx * mi->swPerFrameCount;
    if (blockId >= mi->fCount * mi->swPerFrameCount)
        return;

    /* Interested subwindow-related (isw) info. */
    int   iswIdx   = blockIdx.x % mi->swPerFrameCount;
    int   iswIndex = fswIndex + iswIdx;
    int   iswStartIndex = fStartIndex + mi->swStartIndices[iswIndex];
    //int   iswStopIndex  = fStartIndex + mi->swStopIndices[iswIndex];
    pdt * isw         = &(mi->data[iswStartIndex]);

    DEVICE_ST(
        iswMean = Device_ST_Mean(
            &(mi->data[iswStartIndex]), mi->options.minSubwindowSize));

    DEVICE_ST(
        iswSD = Device_ST_SD(
            &(mi->data[iswStartIndex]), iswMean, 
            mi->options.minSubwindowSize));

    DEVICE_ST(nearestDist = 999999999.99e+99);

    DEVICE_ST(lock = 0);

    __syncthreads();

    /* Comparing subwindow-related (csw) info. */
    int strides   = mi->swPerFrameCount / blockDim.x;
    strides += (mi->swPerFrameCount % blockDim.x) ? 1 : 0;

    for (int strideIdx=0;strideIdx<strides;strideIdx++) {
        int cswIdx = (strideIdx * blockDim.x) + threadIdx.x;
        if (cswIdx >= mi->swPerFrameCount)
            break;

        int cswIndex = fswIndex + cswIdx;
        int cswStartIndex = fStartIndex + mi->swStartIndices[cswIndex];
        //int cswStopIndex  = fStartIndex + mi->swStopIndices[cswIndex];

        if (abs(iswIndex - cswIndex) < mi->options.minSubwindowSize)
            continue;

        pdt cswMean = Device_ST_Mean(
            &(mi->data[cswStartIndex]), mi->options.minSubwindowSize);

        pdt cswSD = Device_ST_SD(
            &(mi->data[cswStartIndex]), 
            cswMean, mi->options.minSubwindowSize);

        pdt * csw      = &(mi->data[cswStartIndex]);
        pdt   sumSqErr = 0.0;
        for (int dIdx=0;dIdx<mi->options.minSubwindowSize;dIdx++) {
            pdt iswd = (isw[dIdx] - iswMean) / iswSD;
            pdt cswd = (csw[dIdx] - cswMean) / cswSD;
            sumSqErr += POWER(iswd - cswd, 2.0);
        }
#if 0
        pdt dist = sqrt(sumSqErr);
        while(atomicCAS(&lock, 0, 1) != 1);
        if (dist < nearestDist) {
            nearestDist = dist;
        }
        lock = 0;
#else
        dist_s[cswIdx] = sqrt(sumSqErr);
#endif
    }

    __syncthreads();

#if 0
    DEVICE_ST(
        dscores[iswIndex] = (pdt) nearestDist);
#else
    pdt nd = 999999999.99e+99;
    if (threadIdx.x == 0) {
        for (int i=0;i<mi->swPerFrameCount;i++) {
            if (dist_s[i] < nd)
                nd = dist_s[i];
        }
    }
    DEVICE_ST(
        dscores[iswIndex] = (pdt) nd);
#endif 


}

#define CHECK_ERR(exp)   \
do {                     \
    int ret = exp;       \
    if (ret) return ret; \
} while (0)

int CreateDeviceMetricInfo(MetricInfo * mi_h, MetricInfo ** mi_d) {

    MetricInfo * mi_dr, mi_hd;
    
    mi_hd = *mi_h;

    CHECK_ERR(cudaMalloc(
        (void **) &mi_dr, 
        sizeof(MetricInfo)));

    CHECK_ERR(cudaMalloc(
        (void **) &(mi_hd.data), 
        sizeof(pdt) * mi_h->dataLength));
    CHECK_ERR(cudaMemcpy(
        (void *) mi_hd.data, (void *) mi_h->data,
        sizeof(pdt) * mi_h->dataLength,
        cudaMemcpyHostToDevice));
/*
    CHECK_ERR(cudaMalloc(
        (void **) &(mi_hd.stdData), 
        sizeof(pdt) * mi_h->dataLength));
    CHECK_ERR(cudaMemcpy(
        (void *) mi_hd.stdData, (void *) mi_h->stdData,
        sizeof(pdt) * mi_h->dataLength,
        cudaMemcpyHostToDevice));
*/
    CHECK_ERR(cudaMalloc(
        (void **) &(mi_hd.fStartIndices), 
        sizeof(int) * mi_h->fCount));
    CHECK_ERR(cudaMemcpy(
        (void *) mi_hd.fStartIndices, (void *) mi_h->fStartIndices,
        sizeof(int) * mi_h->fCount,
        cudaMemcpyHostToDevice));

    CHECK_ERR(cudaMalloc(
        (void **) &(mi_hd.fStopIndices), 
        sizeof(int) * mi_h->fCount));
    CHECK_ERR(cudaMemcpy(
        (void *) mi_hd.fStopIndices, (void *) mi_h->fStopIndices,
        sizeof(int) * mi_h->fCount,
        cudaMemcpyHostToDevice));

    CHECK_ERR(cudaMalloc(
        (void **) &(mi_hd.swStartIndices),
        sizeof(int) * mi_h->fCount * mi_h->swPerFrameCount));
    CHECK_ERR(cudaMemcpy(
        (void *) mi_hd.swStartIndices, (void *) mi_h->swStartIndices,
        sizeof(int) * mi_h->fCount * mi_h->swPerFrameCount,
        cudaMemcpyHostToDevice));

    CHECK_ERR(cudaMalloc(
        (void **) &(mi_hd.swStopIndices),
        sizeof(int) * mi_h->fCount * mi_h->swPerFrameCount));
    CHECK_ERR(cudaMemcpy(
        (void *) mi_hd.swStopIndices, (void *) mi_h->swStopIndices,
        sizeof(int) * mi_h->fCount * mi_h->swPerFrameCount,
        cudaMemcpyHostToDevice));

    CHECK_ERR(cudaMalloc(
        (void **) &(mi_hd.swOwnerFrame),
        sizeof(int) * mi_h->fCount * mi_h->swPerFrameCount));
    CHECK_ERR(cudaMemcpy(
        (void *) mi_hd.swOwnerFrame, (void *) mi_h->swOwnerFrame,
        sizeof(int) * mi_h->fCount * mi_h->swPerFrameCount,
        cudaMemcpyHostToDevice));

    CHECK_ERR(cudaMemcpy(
        (void *) mi_dr, (void *) &mi_hd,
        sizeof(MetricInfo),
        cudaMemcpyHostToDevice));

    *mi_d = mi_dr;

    return 0;
}


int CreateHostDeviceDistanceScores(
    MetricInfo * mi, pdt ** dscores_h, pdt ** dscores_d) {

    *dscores_h = new pdt [mi->fCount * mi->swPerFrameCount];

    pdt * dscores_dr;
    CHECK_ERR(cudaMalloc(
        (void **) &dscores_dr,
        sizeof(pdt) * mi->fCount * mi->swPerFrameCount));

    *dscores_d = dscores_dr;

    return 0;
}

int CreateDeviceAnomalyList(
    MetricInfo  *  mi_h,
    AnomalyList *  al_h, 
    AnomalyList ** al_d) {

    AnomalyList * al_dr, al_hd;

    CHECK_ERR(cudaMalloc(
        (void **) &al_dr, sizeof(AnomalyList)));

    CHECK_ERR(cudaMalloc(
        (void **) &(al_hd.startIndices),
        sizeof(int) * mi_h->fCount));

    CHECK_ERR(cudaMalloc(
        (void **) &(al_hd.stopIndices),
        sizeof(int) * mi_h->fCount));

    CHECK_ERR(cudaMalloc(
        (void **) &(al_hd.frameStartIndices),
        sizeof(int) * mi_h->fCount));

    CHECK_ERR(cudaMalloc(
        (void **) &(al_hd.frameStopIndices),
        sizeof(int) * mi_h->fCount));

    CHECK_ERR(cudaMemcpy(
        (void *) al_dr, (void *) &al_hd,
        sizeof(AnomalyList),
        cudaMemcpyHostToDevice));

    *al_d = al_dr;

    return 0;
}

#undef CHECK_ERR

void dd_gpu(
    pdt *  data,                int   dataLength,
    int ** aStartIndices,       int * aStartIndicesCount,
    int ** aStopIndices,        int * aStopIndicesCount,
    int ** fStartIndices,       int * fStartIndicesCount,
    int ** fStopIndices,        int * fStopIndicesCount,
    int    knowledgeWindowSize,
    int    windowStep,
    int    minSubwindowSize,
    int    detectionFocus) {

    MetricInfo mi, * mi_d; 

    InitializeMetricDataAndOptions(
        data,
        dataLength,
        knowledgeWindowSize,
        windowStep,
        minSubwindowSize,
        detectionFocus,
        &mi);

    /* Create host and device metric list */
    //TODO: Define error code and handling here
    int ret = CreateMetricInfo(&mi);
    if (ret)
        cout << "ERROR CREATE" << endl;
    cout << "dd_gpu" << endl;
    cout << "\tknowledgeWindowSize: " << mi.options.knowledgeWindowSize << endl;
    cout << "\twindowStep:          " << mi.options.windowStep << endl;
    cout << "\tminSubwindowSize:    " << mi.options.minSubwindowSize << endl;
    cout << "\tdetectionFocus:      " << mi.options.detectionFocus << endl;

    ret = CreateDeviceMetricInfo(&mi, &mi_d);
    if (ret) {
        cout << "ERROR CREATE DEVICE METRIC INFO" << endl;
        cout << "\t" << cudaGetErrorString(cudaGetLastError()) << endl;
    }

    /* Create host and device anomaly list */
    AnomalyList al, * al_d;
    CreateAnomalyList(&mi, &al);
    CreateDeviceAnomalyList(&mi, &al, &al_d);

    /* Create host and device distance score arrays */
    pdt * dscores, * dscores_d;
    CreateHostDeviceDistanceScores(&mi, &dscores, &dscores_d);

    /* Launch DD kernel */
    int blockCount = mi.fCount * mi.swPerFrameCount;
    int threadCount = (mi.swPerFrameCount / 32) * 32;
    cout << "Lanching DD kernel: " << blockCount << " : "
        << threadCount << endl;

    int blockCountX = 1;
    int blockCountY = 1;
    if (blockCount > 65535) {
        blockCountY = blockCount / 65535;
        blockCountY += (blockCount % 65535) ? 1 : 0;
        blockCountX = 65535;
    }
    else {
        blockCountY = 1;
        blockCountX = blockCount;
    }
    dim3 grid(blockCountX, blockCountY, 1);
    dd_DeviceProcess<<<grid, 512>>>(mi_d, al_d, dscores_d);
    cudaError_t ce = cudaDeviceSynchronize();
    if (ce != cudaSuccess) {
        cout << "DD Kernel Execution failed: "
            << cudaGetErrorString(ce) << endl;
    }


    /* Show Distance Scores */
#if 1
    ce = cudaMemcpy(dscores, dscores_d, 
        sizeof(pdt) * mi.fCount * mi.swPerFrameCount, 
        cudaMemcpyDeviceToHost);
    if (ce != cudaSuccess) {
        cout << "DD Transfer failed: "
            << cudaGetErrorString(ce) << endl;
    }
    int count = mi.fCount * mi.swPerFrameCount;
    for (int i=0;i<count;i++)
        cout << dscores[i] << endl;
#endif

    ret = DestroyMetricInfo(&mi);
    if (ret)
        cout << "ERROR RELEASE" << endl;

    *aStartIndices = al.startIndices;
    *aStopIndices  = al.stopIndices;
    *aStartIndicesCount = 0;//mi.fCount;
    *aStopIndicesCount  = 0;//mi.fCount;
    *fStartIndices = al.frameStartIndices;
    *fStopIndices  = al.frameStopIndices;
    *fStartIndicesCount = 0;//mi.fCount;
    *fStopIndicesCount  = 0;//mi.fCount;
}

