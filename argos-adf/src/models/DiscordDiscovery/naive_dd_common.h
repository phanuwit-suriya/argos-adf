#ifndef _NAIVE_DD_COMMON_H
#define _NAIVE_DD_COMMON_H

typedef float dtype;

typedef struct {
    dtype * stdData;
    int   * startIndices;
    int   * stopIndices;
    int   * dataOffset;
    int   * subWindows;
    dtype * temp;
    int   * temp1;
    int   * temp2;
    int     stdDataSize;
    int     frameCount;
    int     subWindowCount;
} FrameInfo;

typedef struct {
    int ** startIndices;
    int ** stopIndices;
} AnomalyMatrix;

typedef struct {
    FrameInfo fi;
    int       frameStart;
    int       frameCount;
    int       knowledgeWindowSize;
    int       subWindowIndex;
} ThreadArg;

#define SUCCESS 0
#define ERROR -1
#define MINIMUM_WINDOW_RATIO 10.0
#define ERR_RET(str, exp, ret) if (str != exp) return ret

int CreateSubWindows(FrameInfo * fi, int knowledgeWindowSize, int minSubWindowSize);


int CreateFrameBoundaries(FrameInfo * fi, int dataLength, int knowledgeWindowSize, int windowStep);


int CreateFrameData(FrameInfo * fi, dtype * data);

int CreateFrameInfo(FrameInfo * fi, dtype * data, int dataLength,
    int knowledgeWindowSize, int minSubWindowSize, int windowStep);

int CreateAnomalyMatrix(FrameInfo fi, AnomalyMatrix * am);
#endif /* _NAIVE_DD_COMMON_H */

