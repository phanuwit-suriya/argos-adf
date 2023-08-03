%module naive_dd
#ifdef _GPU
%{
#define SWIG_FILE_WITH_INIT
extern void HS_NaiveDetect(float* data, int dataLength, float** retIndice, int* retNum,
    int windowLength, int windowStep, int saxLength);
extern void HS_NaiveDetect_mt(float* data, int dataLength, float** retIndice, int* retNum,
    int windowLength, int windowStep, int saxLength, int numThreads);
extern void HS_NaiveDetect_gpu(float* data, int dataLength, int** retIndice, int* retNum,
    int** retIndice1, int* retNum1,
    int knowledgeWindowSize, int windowStep, int minWindowSize);
extern void HS_NaiveDetect_cpu(float* data, int dataLength, int** retIndice, int* retNum,
    int** retIndice1, int* retNum1,
    int knowledgeWindowSize, int windowStep, int minWindowSize, int threads);
%}
#else
%{
#define SWIG_FILE_WITH_INIT
extern void HS_NaiveDetect(float* data, int dataLength, float** retIndice, int* retNum,
    int windowLength, int windowStep, int saxLength);
extern void HS_NaiveDetect_mt(float* data, int dataLength, float** retIndice, int* retNum,
    int windowLength, int windowStep, int saxLength, int numThreads);
extern void HS_NaiveDetect_cpu(float* data, int dataLength, int** retIndice, int* retNum,
    int** retIndice1, int* retNum1,
    int knowledgeWindowSize, int windowStep, int minWindowSize, int threads);
%}
#endif

%include "numpy.i"

%init %{
    import_array();
%}

%apply (float* IN_ARRAY1, int DIM1) {(float* data, int dataLength)}
%apply (float** ARGOUTVIEW_ARRAY1, int* DIM1) {(float** retIndice, int* retNum)}
extern void HS_NaiveDetect(float* data, int dataLength, float** retIndice, int* retNum,
    int windowLength, int windowStep, int saxLength);

%apply (float* IN_ARRAY1, int DIM1) {(float* data, int dataLength)}
%apply (float** ARGOUTVIEW_ARRAY1, int* DIM1) {(float** retIndice, int* retNum)}
extern void HS_NaiveDetect_mt(float* data, int dataLength, float** retIndice, int* retNum,
    int windowLength, int windowStep, int saxLength, int numThreads);

#ifdef _GPU
%apply (float* IN_ARRAY1, int DIM1) {(float* data, int dataLength)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** retIndice, int* retNum)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** retIndice1, int* retNum1)}
extern void HS_NaiveDetect_gpu(float* data, int dataLength, int** retIndice, int* retNum,
    int** retIndice1, int* retNum1,
    int knowledgeWindowSize, int windowStep, int minWindowSize);
#endif

%apply (float* IN_ARRAY1, int DIM1) {(float* data, int dataLength)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** retIndice, int* retNum)}
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1) {(int** retIndice1, int* retNum1)}
extern void HS_NaiveDetect_cpu(float* data, int dataLength, int** retIndice, int* retNum,
    int** retIndice1, int* retNum1,
    int knowledgeWindowSize, int windowStep, int minWindowSize, int threads);
