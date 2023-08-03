#ifndef _DD_COMMON_H
#define _DD_COMMON_H

#ifdef _DOUBLE
typedef double pdt;
#else
typedef float pdt;
#endif

#ifndef _SWIG_PARSE
typedef enum {
    PatternFocused = 0x00,
    PeakFocused    = 0x01
} DetectionFocus;

typedef struct {
    int            knowledgeWindowSize;
    int            windowStep;
    int            minSubwindowSize;
    DetectionFocus detectionFocus;
} MetricOptions;

typedef struct {
    /* Metric time series data */
    pdt          *  data;
    pdt          *  stdData; /* Used only when DetectionFocus::PeakFocused */
    int             dataLength;

    /* Frames (Window) */
    int          *  fStartIndices; /* Absolute to data */
    int          *  fStopIndices;  /* Absolute to data */
    int             fCount;

    /* Sub-windows */
    int          *  swStartIndices; /* Relative to fStartIndices */
    int          *  swStopIndices;  /* Relative to fStartIndices */
    int          *  swOwnerFrame;
    int             swPerFrameCount;
    MetricOptions   options;
} MetricInfo;

typedef struct {
    int * startIndices;
    int * stopIndices;
    int * frameStartIndices;
    int * frameStopIndices;
} AnomalyList;

/**
 * Commonly used functions (both CPU and GPU versions.
 * See the implementation on dd_cpu.cpp
 */

int InitializeFrames(MetricInfo * mi);

int InitializeSubwindows(MetricInfo * mi);

int CreateMetricInfo(MetricInfo * mi);

int DestroyMetricInfo(MetricInfo * mi);

int CreateAnomalyList(MetricInfo * mi, AnomalyList * al);

void StandardizeData(pdt * dataIn, pdt * dataOut, int dataLength);

void InitializeMetricDataAndOptions(
    pdt        * data,
    int          dataLength,
    int          knowledgeWindowSize,
    int          windowStep,
    int          minSubwindowSize,
    int          detectionFocus,
    MetricInfo * mi);

#endif /* _SWIG_PARSE */
#endif /* _DD_COMMON_H */

