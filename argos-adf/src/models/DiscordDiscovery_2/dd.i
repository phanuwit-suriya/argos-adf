%module dd 
#ifdef _GPU
%{
#define SWIG_FILE_WITH_INIT
#define _SWIG_PARSE
#include "dd_common.h"
extern void dd_gpu(
    pdt*   data,          int  dataLength, 
    int**  aStartIndices, int* aStartIndicesCount,
    int**  aStopIndices,  int* aStopIndicesCount,
    int**  fStartIndices, int* fStartIndicesCount,
    int**  fStopIndices,  int* fStopIndicesCount,
    int knowledgeWindowSize, 
    int windowStep, 
    int minSubwindowSize, 
    int detectionFocus);
extern void dd_cpu(
    pdt*   data,          int  dataLength, 
    int**  aStartIndices, int* aStartIndicesCount,
    int**  aStopIndices,  int* aStopIndicesCount,
    int**  fStartIndices, int* fStartIndicesCount,
    int**  fStopIndices,  int* fStopIndicesCount,
    int knowledgeWindowSize, 
    int windowStep, 
    int minSubwindowSize, 
    int detectionFocus,
    int threads);
%}
#else
%{
#define SWIG_FILE_WITH_INIT
#define _SWIG_PARSE
#include "dd_common.h"
extern void dd_cpu(
    pdt*   data,          int  dataLength, 
    int**  aStartIndices, int* aStartIndicesCount,
    int**  aStopIndices,  int* aStopIndicesCount,
    int**  fStartIndices, int* fStartIndicesCount,
    int**  fStopIndices,  int* fStopIndicesCount,
    int knowledgeWindowSize, 
    int windowStep, 
    int minSubwindowSize, 
    int detectionFocus,
    int threads);
%}
#endif

%include "numpy.i"

%init %{
    import_array();
%}

#ifdef _DOUBLE
#ifdef _GPU
%apply (double* IN_ARRAY1, int DIM1) {(double* data, int dataLength)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** aStartIndices, int* aStartIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** aStopIndices,  int* aStopIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** fStartIndices, int* fStartIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** fStopIndices,  int* fStopIndicesCount)}
extern void dd_gpu(
    double*   data,          int  dataLength, 
    int**  aStartIndices, int* aStartIndicesCount,
    int**  aStopIndices,  int* aStopIndicesCount,
    int**  fStartIndices, int* fStartIndicesCount,
    int**  fStopIndices,  int* fStopIndicesCount,
    int knowledgeWindowSize, 
    int windowStep, 
    int minSubwindowSize, 
    int detectionFocus);
#endif

%apply (double* IN_ARRAY1, int DIM1) {(double* data, int dataLength)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** aStartIndices, int* aStartIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** aStopIndices,  int* aStopIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** fStartIndices, int* fStartIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** fStopIndices,  int* fStopIndicesCount)}
extern void dd_cpu(
    double*   data,          int  dataLength, 
    int**  aStartIndices, int* aStartIndicesCount,
    int**  aStopIndices,  int* aStopIndicesCount,
    int**  fStartIndices, int* fStartIndicesCount,
    int**  fStopIndices,  int* fStopIndicesCount,
    int knowledgeWindowSize, 
    int windowStep, 
    int minSubwindowSize, 
    int detectionFocus,
    int threads);
#else
#ifdef _GPU
%apply (float* IN_ARRAY1, int DIM1) {(float* data, int dataLength)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** aStartIndices, int* aStartIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** aStopIndices,  int* aStopIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** fStartIndices, int* fStartIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** fStopIndices,  int* fStopIndicesCount)}
extern void dd_gpu(
    float*   data,          int  dataLength, 
    int**  aStartIndices, int* aStartIndicesCount,
    int**  aStopIndices,  int* aStopIndicesCount,
    int**  fStartIndices, int* fStartIndicesCount,
    int**  fStopIndices,  int* fStopIndicesCount,
    int knowledgeWindowSize, 
    int windowStep, 
    int minSubwindowSize, 
    int detectionFocus);
#endif

%apply (float* IN_ARRAY1, int DIM1) {(float* data, int dataLength)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** aStartIndices, int* aStartIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** aStopIndices,  int* aStopIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** fStartIndices, int* fStartIndicesCount)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** fStopIndices,  int* fStopIndicesCount)}
extern void dd_cpu(
    float*   data,          int  dataLength, 
    int**  aStartIndices, int* aStartIndicesCount,
    int**  aStopIndices,  int* aStopIndicesCount,
    int**  fStartIndices, int* fStartIndicesCount,
    int**  fStopIndices,  int* fStopIndicesCount,
    int knowledgeWindowSize, 
    int windowStep, 
    int minSubwindowSize, 
    int detectionFocus,
    int threads);
#endif

