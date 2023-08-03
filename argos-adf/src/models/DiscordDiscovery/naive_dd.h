#ifndef _NAIVE_DD_H
#define _NAIVE_DD_H

//Definitions required in all naive Discord-discovery implementations
#define MIN_SAX_LENGTH 4
#define DEFAULT_SAX_LENGTH 8
#define MAX_SAX_LENGTH 16

typedef float dtype;
typedef char  saxtype;
template <typename T> struct st_arr {
    T   * data;
    int   length;
};
typedef st_arr<dtype>   darr;
typedef st_arr<darr>    wdarr;
typedef st_arr<saxtype> saxarr;
typedef st_arr<saxarr>  wsaxarr;

//Prototypes (See implementation in naive_dd.cpp)
int   GetWindowList(darr data, wdarr * retWindowList, int windowLength, int windowStep);
void  FreeWindowList(wdarr windowList);
int   ConvertWindowList_ZScore(wdarr windowList);
int   GetPAA(wdarr windowList, int windowLength, int saxLength, wdarr * paa);
int   GetSAX(wdarr paa, int saxLength, wsaxarr * sax);
dtype GetEuclideanDist(darr seq1, darr seq2, int windowLength);
dtype GetDistance(darr seq1, darr seq2, int windowLength);


#endif /* _NAIVE_DD_H */