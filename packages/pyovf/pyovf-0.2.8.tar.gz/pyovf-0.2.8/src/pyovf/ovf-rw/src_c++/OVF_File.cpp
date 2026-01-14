// (c) 2015-2022 by Dr. Flavio ABREU ARAUJO. All rights reserved.

//#include "OVF_File.h"
#include <OVF_File.h>

//#include <stdio.h>
//#include <stdlib.h>

void OVF_File::printData(int oneD) {
    IDX fourD = this->oneToFourD(oneD);
    if(data != NULL) {
        cout << "data(" << fourD.d+1 << "," << fourD.y+1 << "," <<
                fourD.x+1 << "," << fourD.z+1 << ") = " <<
                this->getData()[oneD] << endl;
    }
}

void OVF_File::printData(IDX fourD) {
    int oneD = this->fourToOneD(fourD);
    if(data != NULL) {
        cout << "data(" << fourD.d+1 << "," << fourD.y+1 << "," <<
                fourD.x+1 << "," << fourD.z+1 << ") = " <<
                this->getData()[oneD] << endl;
    }
}

int OVF_File::fourToOneD(IDX fourD) {
    //TODO: Original: d + (x + (y + z*xnodes)*ynodes)*valuedim
    //TODO: But getXmax uses: (y + (x + z*ynodes)*xnodes)*valuedim
    //TODO: These are DIFFERENT orderings - verify which is correct for your use case. Need to check OVF specs from OOMMF.
    return fourD.d + (fourD.x + (fourD.y + fourD.z*this->xnodes)*
            this->ynodes)*this->valuedim;
}

int OVF_File::fourToOneD(int d, int x, int y, int z) {
    return d + (x + (y + z*this->xnodes)*this->ynodes)*this->valuedim;
}

IDX OVF_File::oneToFourD(int oneD) {
    IDX index;
    div_t divres;
    divres = div (oneD, this->valuedim*this->xnodes*this->ynodes);
    index.z = divres.quot;
    divres = div (divres.rem, this->valuedim*this->xnodes);
    index.y = divres.quot;
    divres = div (divres.rem, this->valuedim);
    index.x = divres.quot;
    index.d = divres.rem;
    return index;
}

int OVF_File::getmax()
{
    NumType* data = (NumType*) this->data;
    // No null check before accessing data
    if(data == nullptr) return -1;
    int idx = 0;
    for(int i = 0; i < this->elementNum; i++) {
        if(data[i] > data[idx]) { idx = i; }
    }
    return idx;
}

int OVF_File::getmin()
{
    NumType* data = (NumType*) this->data;
    // No null check before accessing data
    if(data == nullptr) return -1;
    int idx = 0;
    for(int i = 0; i < this->elementNum; i++) {
        if(data[i] < data[idx]) { idx = i; }
    }
    return idx;
}

//-------------------------------------------------------------------------

int OVF_File::getXmax()
{
    assert(this->valuedim == 1 || this->valuedim == 2 || this->valuedim == 3);
    NumType* data = (NumType*) this->data;
    int idx = 0; // x-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            for(int z = 0; z < this->znodes; z++) {
                int i = (y + (x + z*this->ynodes)*
                        this->xnodes)*this->valuedim;
                if(data[i] > data[idx]) { idx = i; }
            }
        }
    }
    /*cout << "getXmax = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

int OVF_File::getYmax()
{
    assert(this->valuedim == 2 || this->valuedim == 3);
    NumType* data = (NumType*) this->data;
    int idx = 1; // y-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            for(int z = 0; z < this->znodes; z++) {
                int i = 1 + (y + (x + z*this->ynodes)*
                        this->xnodes)*this->valuedim;
                if(data[i] > data[idx]) { idx = i; }
            }
        }
    }
    /*cout << "getYmax = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

int OVF_File::getZmax()
{
    assert(this->valuedim == 3);
    NumType* data = (NumType*) this->data;
    int idx = 2; // z-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            for(int z = 0; z < this->znodes; z++) {
                int i = 2 + (y + (x + z*this->ynodes)*
                        this->xnodes)*this->valuedim;
                if(data[i] > data[idx]) { idx = i; }
            }
        }
    }
    /*cout << "getZmax = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

//-------------------------------------------------------------------------

int OVF_File::getXmax(int layer)
{
    assert(this->valuedim == 1 || this->valuedim == 2 || this->valuedim == 3);
    assert(layer >= 0 && layer < this->znodes);
    NumType* data = (NumType*) this->data;
    int idx = 0; // x-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            int i = (y + (x + layer*this->ynodes)*
                    this->xnodes)*this->valuedim;
            if(data[i] > data[idx]) { idx = i; }
        }
    }
    /*cout << "getXmax = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

int OVF_File::getYmax(int layer)
{
    assert(this->valuedim == 2 || this->valuedim == 3);
    assert(layer >= 0 && layer < this->znodes);
    NumType* data = (NumType*) this->data;
    int idx = 1; // y-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            int i = 1 + (y + (x + layer*this->ynodes)*
                    this->xnodes)*this->valuedim;
            if(data[i] > data[idx]) { idx = i; }
        }
    }
    /*cout << "getYmax = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

int OVF_File::getZmax(int layer)
{
    assert(this->valuedim == 3);
    assert(layer >= 0 && layer < this->znodes);
    NumType* data = (NumType*) this->data;
    int idx = 2; // z-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            int i = 2 + (y + (x + layer*this->ynodes)*
                    this->xnodes)*this->valuedim;
            if(data[i] > data[idx]) { idx = i; }
        }
    }
    /*cout << "getZmax = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

//-------------------------------------------------------------------------

int OVF_File::getXmin()
{
    assert(this->valuedim == 1 || this->valuedim == 2 || this->valuedim == 3);
    NumType* data = (NumType*) this->data;
    int idx = 0; // x-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            for(int z = 0; z < this->znodes; z++) {
                int i = (y + (x + z*this->ynodes)*
                        this->xnodes)*this->valuedim;
                if(data[i] < data[idx]) { idx = i; }
            }
        }
    }
    cout << "getXmin = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;
    return idx;
}

int OVF_File::getYmin()
{
    assert(this->valuedim == 2 || this->valuedim == 3);
    NumType* data = (NumType*) this->data;
    int idx = 1; // y-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            for(int z = 0; z < this->znodes; z++) {
                int i = 1 + (y + (x + z*this->ynodes)*
                        this->xnodes)*this->valuedim;
                if(data[i] < data[idx]) { idx = i; }
            }
        }
    }
    cout << "getYmin = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;
    return idx;
}

int OVF_File::getZmin()
{
    assert(this->valuedim == 3);
    NumType* data = (NumType*) this->data;
    int idx = 2; // z-component
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            for(int z = 0; z < this->znodes; z++) {
                int i = 2 + (y + (x + z*this->ynodes)*
                        this->xnodes)*this->valuedim;
                if(data[i] < data[idx]) { idx = i; }
            }
        }
    }
    /*cout << "getZmin = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

//-------------------------------------------------------------------------

int OVF_File::getXmin(int layer)
{
    assert(this->valuedim == 1 || this->valuedim == 2 || this->valuedim == 3);
    assert(layer >= 0 && layer < this->znodes);
    NumType* data = (NumType*) this->data;
    int idx = 0;
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            int i = (y + (x + layer*this->ynodes)*
                    this->xnodes)*this->valuedim;
            if(data[i] < data[idx]) { idx = i; }
        }
    }
    /*cout << "getXmin = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

int OVF_File::getYmin(int layer)
{
    assert(this->valuedim == 2 || this->valuedim == 3);
    assert(layer >= 0 && layer < this->znodes);
    NumType* data = (NumType*) this->data;
    int idx = 1;
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            int i = 1 + (y + (x + layer*this->ynodes)*
                    this->xnodes)*this->valuedim;
            if(data[i] < data[idx]) { idx = i; }
        }
    }
    /*cout << "getYmin = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

int OVF_File::getZmin(int layer)
{
    assert(this->valuedim == 3);
    assert(layer >= 0 && layer < this->znodes);
    NumType* data = (NumType*) this->data;
    int idx = 2;
    for(int x = 0; x < this->xnodes; x++) {
        for(int y = 0; y < this->ynodes; y++) {
            int i = 2 + (y + (x + layer*this->ynodes)*
                    this->xnodes)*this->valuedim;
            if(data[i] < data[idx]) { idx = i; }
        }
    }
    /*cout << "getZmin = " << data[idx] << " ("
                << "idx_max = " << idx << ")" << endl;*/
    return idx;
}

//-------------------------------------------------------------------------

NumType* OVF_File::getData() {
    return (NumType*) this->data;
}

void OVF_File::setData(void* dataPtr) {
    this->data = dataPtr;
}

OVF_File::OVF_File() {
    this->elementNum = 0;
    
    this->xmin = 0, this->ymin = 0, this->zmin = 0;
    this->xmax = 0, this->ymax = 0, this->zmax = 0;
    this->valuedim = 0;
    this->xbase = 0, this->ybase = 0, this->zbase = 0;
    this->xnodes = 0, this->ynodes = 0, this->znodes = 0;
    this->xstepsize = 0, this->ystepsize = 0, this->zstepsize = 0;
    this->StageSimTime = 0;
    this->TotalSimTime = 0;
    this->AppliedField = 0;
    
    this->data = NULL;
    
    this->Title = "";
    this->meshtype = "";
    this->meshunit = "";
    this->StageSimTimeUnit = "";
    this->TotalSimTimeUnit = "";
    this->AppliedFieldUnit = "";
}

OVF_File::~OVF_File() {
    if(this->data != NULL) {
//! MATLAB or numpy take over the cleanup of data
#if !defined(BINDING)
        delete[] (NumType*) this->data;
#endif
        this->data = NULL;
    }
}

void OVF_File::readOVF (const char* fileName) {
#if defined(TIMINGS)
    HR_time start = chrono::high_resolution_clock::now();
#endif
    
    string line;
    ifstream myfile (fileName, ios::binary);
    if (myfile.is_open())
    {
        while ( getline (myfile, line) )
        {
            vector<string> vs = string_tochenizer(line);
            
            if(!vs[0].compare("#")) {
                if(vs.size() > 1) {
                    #if defined(DEBUG)
                        // printDebugMsg((line + '\n').c_str());
                        printDebugMsg(line.c_str());
                    #endif
                    
                    if(!vs[1].compare("OOMMF")) {
                        if(vs.size() == 4) {
                            //TODO
                        } else {
                            //TODO error
                        }
                    }
                    else if(!vs[1].compare("Segment")) {
                        if(vs.size() == 4) {
                            //TODO deal with "count:"
                        } else {
                            //TODO error
                        }
                    }
                    else if(!vs[1].compare("Title:")) {
                        if(vs.size() == 3) {
                            this->Title = vs[2];
                        } else {
                            this->Title = "";
                        }
                    }
                    else if(!vs[1].compare("meshtype:")) {
                        if(vs.size() == 3) {
                            this->meshtype = vs[2];
                        } else {
                            this->meshtype = "";
                        }
                    }
                    else if(!vs[1].compare("meshunit:")) {
                        if(vs.size() == 3) {
                            this->meshunit = vs[2];
                        } else {
                            this->meshunit = "";
                        }
                    }
                    else if(!vs[1].compare("xmin:")) {
                        if(vs.size() == 3) {
                            this->xmin = atof (vs[2].c_str());
                        } else {
                            this->xmin = 0;
                        }
                    }
                    else if(!vs[1].compare("ymin:")) {
                        if(vs.size() == 3) {
                            this->ymin = atof (vs[2].c_str());
                        } else {
                            this->ymin = 0;
                        }
                    }
                    else if(!vs[1].compare("zmin:")) {
                        if(vs.size() == 3) {
                            this->zmin = atof (vs[2].c_str());
                        } else {
                            this->zmin = 0;
                        }
                    }
                    else if(!vs[1].compare("xmax:")) {
                        if(vs.size() == 3) {
                            this->xmax = atof (vs[2].c_str());
                        } else {
                            this->xmax = 0;
                        }
                    }
                    else if(!vs[1].compare("ymax:")) {
                        if(vs.size() == 3) {
                            this->ymax = atof (vs[2].c_str());
                        } else {
                            this->ymax = 0;
                        }
                    }
                    else if(!vs[1].compare("zmax:")) {
                        if(vs.size() == 3) {
                            this->zmax = atof (vs[2].c_str());
                        } else {
                            this->zmax = 0;
                        }
                    }
                    else if(!vs[1].compare("Begin:")) {
                        if(!vs[2].compare("Data")) {
                            if(this->valuedim == 0 || this->xnodes == 0 ||
                                    this->ynodes == 0 ||
                                    this->znodes == 0) {
                                string str = "Header error: ";
                                printErrMsg((str + "one or more " +
                                        "parameters are not set!"
                                        ).c_str());
                            } else {
                                if(vs.size() == 5) {
                                    if(!vs[3].compare("Binary") && !vs[4].compare("4")) {

                                        myfile.seekg (sizeof(NumType), ios::cur);
                                        //TODO: maybe read this elements from file
                                        
                                        this->elementNum = this->valuedim*this->xnodes*
                                                this->ynodes*this->znodes;
                                        
                                        // deallocate data if it exists
                                        if(this->data != NULL) {
                                            delete[] (NumType*) this->data;
                                            this->data = NULL;
                                        }
                                        
                                        this->data = new NumType [this->elementNum];
                                        myfile.read ((char*) this->data,
                                                sizeof(NumType)*this->elementNum);

                                        #if defined(DEBUG)
                                            std::streamsize bytes = myfile.gcount();
                                            printDebugMsg(("\nNumber of bytes in data: " +
                                                    to_string((int)bytes) + "\n").c_str());
                                        #endif

                                        //! OOMMF adds an end-of-line character after the data
                                        //! but mumax3 doesn't!
                                        char c;
                                        myfile.get(c);
                                        if(c=='\n') {
                                            #if defined(DEBUG)
                                                printDebugMsg("End-of-line detected after data!");
                                            #endif
                                        } else {
                                            myfile.seekg (-sizeof(char), ios::cur);
                                            #if defined(DEBUG)
                                                printDebugMsg(("Char after data: [" +
                                                to_string(c) + "]").c_str());
                                            #endif
                                        }
                                    } else {
                                        printErrMsg("(OVF file) This connector has been compiled for 'Binary 4' data format!");
                                        
                                        //! START fake read
                                        myfile.seekg (sizeof(NumType)*2, ios::cur);
                                        //TODO: maybe read this elements from file
                                        
                                        this->elementNum = this->valuedim*this->xnodes*
                                                this->ynodes*this->znodes;
                                        
                                        // deallocate data if it exists
                                        if(this->data != NULL) {
                                            delete[] (NumType*) this->data;
                                            this->data = NULL;
                                        }
                                        
                                        this->data = new NumType [this->elementNum*2];
                                        myfile.read ((char*) this->data,
                                                sizeof(NumType)*this->elementNum*2);

                                        #if defined(DEBUG)
                                            std::streamsize bytes = myfile.gcount();
                                            printDebugMsg(("\nNumber of bytes in data: " +
                                                    to_string((int)bytes) + "\n").c_str());
                                        #endif

                                        //! OOMMF adds an end-of-line character after the data
                                        //! but mumax3 doesn't!
                                        char c;
                                        myfile.get(c);
                                        if(c=='\n') {
                                            #if defined(DEBUG)
                                                printDebugMsg("End-of-line detected after data!");
                                            #endif
                                        } else {
                                            myfile.seekg (-sizeof(char), ios::cur);
                                            #if defined(DEBUG)
                                                printDebugMsg(("Char after data: [" +
                                                to_string(c) + "]").c_str());
                                            #endif
                                        }
                                        //! END fake read

                                        this->Title = "ERROR!";
                                        this->elementNum = 0;
                                        this->valuedim = 0;
                                        this->xnodes = 0;
                                        this->ynodes = 0;
                                        this->znodes = 0;
                                        // deallocate data if it exists
                                        if(this->data != NULL) {
                                            delete[] (NumType*) this->data;
                                            this->data = NULL;
                                        }
                                        //TODO
                                    }
                                } else {
                                    if(vs.size() == 4) {
                                        if(!vs[3].compare("Text")) {
                                            printErrMsg("(OVF file) This connector has not yet been adapted to 'Text' data format!");
                                            this->Title = "ERROR!";
                                            this->elementNum = 0;
                                            this->valuedim = 0;
                                            this->xnodes = 0;
                                            this->ynodes = 0;
                                            this->znodes = 0;
                                            // deallocate data if it exists
                                            if(this->data != NULL) {
                                                delete[] (NumType*) this->data;
                                                this->data = NULL;
                                            }
                                            //TODO
                                        } else {
                                            printErrMsg(("(OVF file) Unknown data format: " +
                                                        vs[3]).c_str());
                                        }
                                    }
                                }
                            }
                        }
                        else if(!vs[2].compare("Segment")) {
                            //TODO: check
                        }
                        else if(!vs[2].compare("Header")) {
                            //TODO: check
                        }
                    }
                    else if(!vs[1].compare("End:")) {
                        if(!vs[2].compare("Data")) {
                            //TODO: check
                        }
                        else if(!vs[2].compare("Segment")) {
                            //TODO: check
                        }
                        else if(!vs[2].compare("Header")) {
                            //TODO: check
                        }
                    }
                    else if(!vs[1].compare("valuedim:")) {
                        if(vs.size() == 3) {
                            this->valuedim = atoi (vs[2].c_str());
                        } else {
                            this->valuedim = 0;
                        }
                    }
                    else if(!vs[1].compare("valuelabels:")) {
                        // printWarnMsg("valuelabels: not yet implemented");
                        //TODO: implement
                    }
                    else if(!vs[1].compare("valueunits:")) {
                        // printWarnMsg("valueunits: not yet implemented");
                        //TODO: implement
                    }
                    else if(!vs[1].compare("Desc:")) {
                        if(vs.size() == 7) {
                            //? # Desc: Oxs vector field output
                            //TODO: implement

                            //? # Desc:  MIF source file: .../vortex_dynamics_STT_Jdc.mif
                            //TODO: implement
                        }

                        if(vs.size() == 7) {
                            //? # Desc:  Iteration: 5188, State id: 40568
                            //TODO: implement

                            //? # Desc:  Stage: 199, Stage iteration: 20
                            //TODO: implement

                            //? # Desc:  Stage simulation time: 1e-11 s
                            if(!vs[2].compare("Stage")) {
                                this->StageSimTime = atof (vs[5].c_str());
                                this->StageSimTimeUnit = vs[6];
                            }

                            //? # Desc:  Total simulation time: 2e-09 s
                            if(!vs[2].compare("Total")) {
                                this->TotalSimTime = atof (vs[5].c_str());
                                this->TotalSimTimeUnit = vs[6];
                            }
                        }
                    }
                    else if(!vs[1].compare("xbase:")) {
                        if(vs.size() == 3) {
                            this->xbase = atof (vs[2].c_str());
                        } else {
                            this->xbase = 0;
                        }
                    }
                    else if(!vs[1].compare("ybase:")) {
                        if(vs.size() == 3) {
                            this->ybase = atof (vs[2].c_str());
                        } else {
                            this->ybase = 0;
                        }
                    }
                    else if(!vs[1].compare("zbase:")) {
                        if(vs.size() == 3) {
                            this->zbase = atof (vs[2].c_str());
                        } else {
                            this->zbase = 0;
                        }
                    }
                    else if(!vs[1].compare("xnodes:")) {
                        if(vs.size() == 3) {
                            this->xnodes = atoi (vs[2].c_str());
                        } else {
                            this->xnodes = 0;
                        }
                    }
                    else if(!vs[1].compare("ynodes:")) {
                        if(vs.size() == 3) {
                            this->ynodes = atoi (vs[2].c_str());
                        } else {
                            this->ynodes = 0;
                        }
                    }
                    else if(!vs[1].compare("znodes:")) {
                        if(vs.size() == 3) {
                            this->znodes = atoi (vs[2].c_str());
                        } else {
                            this->znodes = 0;
                        }
                    }
                    else if(!vs[1].compare("xstepsize:")) {
                        if(vs.size() == 3) {
                            this->xstepsize = atof (vs[2].c_str());
                        } else {
                            this->xstepsize = 0;
                        }
                    }
                    else if(!vs[1].compare("ystepsize:")) {
                        if(vs.size() == 3) {
                            this->ystepsize = atof (vs[2].c_str());
                        } else {
                            this->ystepsize = 0;
                        }
                    }
                    else if(!vs[1].compare("zstepsize:")) {
                        if(vs.size() == 3) {
                            this->zstepsize = atof (vs[2].c_str());
                        } else {
                            this->zstepsize = 0;
                        }
                    } else {
                        string str = "Parameter ";
                        printWarnMsg((str + vs[1] +
                                " not recognized yet!").c_str());
                    }
                } else {
                    // #if defined(DEBUG)
                    //     printDebugMsg("Empty header line found!");
                    // #endif
                }
            }
        }
        myfile.close();
    } else {
        string str = "Unable to open file ";
        printErrMsg((str + fileName + ".").c_str()); 
    }

#if defined(TIMINGS)
    HR_time finish = chrono::high_resolution_clock::now();
    printDuration(start, finish, "OVF_File::readOVF");
#endif
}

void OVF_File::writeOVF(const char* fileName) {
    ofstream myfile (fileName, ios::binary);
    
#if defined(TIMINGS)
    HR_time start = chrono::high_resolution_clock::now();
#endif
    
    myfile << "# OOMMF OVF 2.0" << endl;
    myfile << "# Segment count: 1" << endl;
    myfile << "# Begin: Segment" << endl;
    myfile << "# Begin: Header" << endl;
    myfile << "# Title: " << this->Title << endl;
    myfile << "# meshtype: " << this->meshtype << endl;
    myfile << "# meshunit: " << this->meshunit << endl;
    myfile << setprecision(15);
    myfile << "# xmin: " << this->xmin << endl;
    myfile << "# ymin: " << this->ymin << endl;
    myfile << "# zmin: " << this->zmin << endl;
    myfile << "# xmax: " << this->xmax << endl;
    myfile << "# ymax: " << this->ymax << endl;
    myfile << "# zmax: " << this->zmax << endl;
    myfile << "# valuedim: " << this->valuedim << endl;

    if (this->valuedim == 3)
    {
        if (this->Title.compare("m") == 0) {
            myfile << "# valuelabels: m_x m_y m_z" << endl;
            myfile << "# valueunits: 1 1 1" << endl;
        } else if (this->Title.compare("B_ext") == 0) {
            myfile << "# valuelabels: B_ext_x B_ext_y B_ext_z" << endl;
            myfile << "# valueunits: T T T" << endl;
        } else if (this->Title.compare("J") == 0) {
            myfile << "# valuelabels: J_x J_y J_z" << endl;
            myfile << "# valueunits: A/m^2 A/m^2 A/m^2" << endl;
        } else {
            myfile << "# valuelabels: m_x m_y m_z" << endl;
            myfile << "# valueunits: 1 1 1" << endl;
        }
    } else if (this->valuedim == 1) {
        myfile << "# valuelabels: " << this->Title << endl;
        myfile << "# valueunits: 1" << endl;
    } else {
        myfile << "# valuelabels: unknown" << endl;
        myfile << "# valueunits: 1" << endl;
    }

    myfile << "# Desc: Total simulation time:  " << this->StageSimTime <<
            "  " << this->StageSimTimeUnit << endl;
    myfile << "# Desc: Total simulation time:  " << this->TotalSimTime <<
            "  " << this->TotalSimTimeUnit << endl;
    myfile << "# xbase: " << this->xbase << endl;
    myfile << "# ybase: " << this->ybase << endl;
    myfile << "# zbase: " << this->zbase << endl;
    myfile << "# xnodes: " << this->xnodes << endl;
    myfile << "# ynodes: " << this->ynodes << endl;
    myfile << "# znodes: " << this->znodes << endl;
    myfile << "# xstepsize: " << this->xstepsize << endl;
    myfile << "# ystepsize: " << this->ystepsize << endl;
    myfile << "# zstepsize: " << this->zstepsize << endl;
    myfile << "# End: Header" << endl;
    myfile << "# Begin: Data Binary " << sizeof(NumType) << endl;
    
    NumType* skip = new NumType[1]; skip[0] = 1234567.0;
    myfile.write((char*) skip, sizeof(NumType));
    
    int elementCount = this->valuedim*this->xnodes*
            this->ynodes*this->znodes;
    
    myfile.write((char*) this->data, sizeof(NumType)*elementCount);
    
    myfile << "# End: Data Binary " << sizeof(NumType) << endl;
    myfile << "# End: Segment" << endl;
    
    myfile.close();
    delete[] skip;
    
#if defined(TIMINGS)
    HR_time finish = chrono::high_resolution_clock::now();
    printDuration(start, finish, "OVF_File::writeOVF");
#endif
}

// to_string existe dans #include <string> sur mon mac
// mais pas sur mon linux ubuntu
template <typename T> string to_string(T value)
{
    //create an output string stream
    ostringstream os;
    //throw the value into the string stream
    os << value;
    //convert the string stream into a string and return
    return os.str();
}

vector<string> string_tochenizer(string line) {
    // SAFER: Use std::string methods instead of C-style string manipulation
    vector<string> vs;
    istringstream iss(line);
    string token;
    while (iss >> token) {
        vs.push_back(token);
    }
    return vs;
}

void printErrMsg(const char* MSG) {
#if defined(MEX) 
    mexErrMsgTxt(MSG);
#else
    // cout << MSG << endl;
    cout << "\033[1;31m" << MSG << "\033[0m" << endl;
#endif
}

void printWarnMsg(const char* MSG) {
#if defined(MEX) 
    mexWarnMsgTxt(MSG);
#else
    // cout << MSG << endl;
    cout << "\033[1;33m" << MSG << "\033[0m" << endl;
#endif
}

void printDebugMsg(const char* MSG) {
#if defined(MEX) 
    mexWarnMsgTxt(MSG);
#else
    // cout << MSG << endl;
    cout << "\033[0;34m" << MSG << "\033[0m" << endl;
#endif
}

void printMsg(const char* MSG) {
#if defined(MEX) 
    mexPrintf(MSG); mexPrintf("\n");
#else
    cout << MSG << endl;
#endif
}

bool exists(const char* fileName) {
    return ifstream(fileName).good();
}

#if defined(TIMINGS)
void printDuration(HR_time start, HR_time finish) {
    string MSG = "Duration: ";
    //printMsg((MSG + to_string(chrono::duration_cast<chrono::nanoseconds>
    //        (finish-start).count()) + " ns").c_str());
    printMsg((MSG + to_string(chrono::duration_cast<chrono::nanoseconds>
            (finish-start).count()/(1000.0*1000.0)) + " ms").c_str());
}
void printDuration(HR_time start, HR_time finish, string msg) {
    string MSG = "Duration: ";
    //printMsg((MSG + to_string(chrono::duration_cast<chrono::nanoseconds>
    //        (finish-start).count()) + " ns (" + msg + ")").c_str());
    printMsg((MSG + to_string(chrono::duration_cast<chrono::nanoseconds>
            (finish-start).count()/(1000.0*1000.0)) + " ms (" + msg + ")").c_str());
}
#endif
