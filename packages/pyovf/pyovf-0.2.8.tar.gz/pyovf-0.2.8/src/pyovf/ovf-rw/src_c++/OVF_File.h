// (c) 2015-2022 by Dr. Flavio ABREU ARAUJO. All rights reserved.

#ifndef OVF_FILE_H
#define OVF_FILE_H

#if defined(MEX)
#include "mex.h"
#endif

#include <iostream>
#include <fstream>
#include <string>
#include <cstring> // strtok, strcpy
#include <vector>
#include <stdlib.h> // atoi, atof, ...
#include <iomanip> // setprecision
#include <sstream> // needed by my to_string function
#include <cassert>

//! WARNING: For MuMax "Data Binary 4" (float)
typedef float NumType;
#define NumTypeClass mxSINGLE_CLASS

//! WARNING: For MuMax "Data Binary 8" (double)
// typedef double NumType;
// #define NumTypeClass mxDOUBLE_CLASS

using namespace std;

template <typename T> string to_string(T value);
vector<string> string_tochenizer(string line);
void printErrMsg(const char* MSG);
void printWarnMsg(const char* MSG);
void printDebugMsg(const char* MSG);
void printMsg(const char* MSG);
bool exists(const char* fileName);

#if defined(TIMINGS)
#include <chrono> // Nanosecond timings (-std=c++11)
typedef chrono::time_point<chrono::high_resolution_clock> HR_time;
void printDuration(HR_time start, HR_time finish);
void printDuration(HR_time start, HR_time finish, string msg);
#endif

struct IDX {
    int d;
    int x;
    int y;
    int z;
};

//-------------------------------------------------------------------------

class OVF_File
{
private:
    //NumType* data;
    void* data;
    
public:
    int elementNum;
    
public:
    string Title;
    string meshtype;
    string meshunit;
    
    double xmin, ymin, zmin;
    double xmax, ymax, zmax;
    
    int valuedim;
    
    double xbase, ybase, zbase;
    int xnodes, ynodes, znodes;
    double xstepsize, ystepsize, zstepsize;

    double StageSimTime;
    string StageSimTimeUnit;
    
    double TotalSimTime;
    string TotalSimTimeUnit;
    
    double AppliedField;
    string AppliedFieldUnit;

public:
    OVF_File();
    ~OVF_File();
    
    void readOVF (const char* fileName);
    void writeOVF (const char* fileName);
    
    NumType* getData();
    void setData(void* data);
    
public:
    int getmax();
    int getmin();
    
    int getXmax();
    int getYmax();
    int getZmax();
    
    int getXmax(int layer);
    int getYmax(int layer);
    int getZmax(int layer);
    
    int getXmin();
    int getYmin();
    int getZmin();
    
    int getXmin(int layer);
    int getYmin(int layer);
    int getZmin(int layer);
    
    void printData(int oneD);
    void printData(IDX fourD);
    int fourToOneD(IDX fourD);
    int fourToOneD(int d, int x, int y, int z);
    IDX oneToFourD(int oneD);
};

#endif