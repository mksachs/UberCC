#include <stdio.h>

/* A converter for the binary format used by DataGraph. Intended to extract
 the data from a binary file in case DataGraph is not available.
 This is a cross platform routine, that only requires a C compiler.
 
 To use, first compile
 cc converter.c
 Then run the executable on the file
 ./a.out "Column 1.dtbin"
 
 This prints the column on the screen, but you can easily incorporate this
 code into your own program for free.  Note this source code is bare bones
 and has minimal error testing.  For a more flexible implementation
 look for DTSource, which is a free C++ class library
 */

#include <stdlib.h>

char RunningOnBigEndian(void)
{
    int fourBytes[1];
    fourBytes[0] = 128912422;
    short int *asTwoShorts = (short int *)fourBytes;
    return (asTwoShorts[0]==1967);
}

void Swap4Bytes(char *bytes)
{
    char t;
    t = bytes[0];   bytes[0] = bytes[3];   bytes[3] = t;
    t = bytes[1];   bytes[1] = bytes[2];   bytes[2] = t;
}

void Swap8Bytes(char *bytes)
{
    char t;
    t = bytes[0];   bytes[0] = bytes[7];   bytes[7] = t;
    t = bytes[1];   bytes[1] = bytes[6];   bytes[6] = t;
    t = bytes[2];   bytes[2] = bytes[5];   bytes[5] = t;
    t = bytes[3];   bytes[3] = bytes[4];   bytes[4] = t;
}

int main (int argc, const char * argv[])
{
    int i,typeNumber, m, n, o, nameLength;
    char variableName[256];
    int length = 0;
    double *theNumbers = 0;
    char *theMask = 0;
    int blockSizes[21] = {0,8,4,0,0,0,0,0,2,2,2,1,1,0,0,0,0,0,0,0,1};
    char LEBE[3];
    
    if (argc!=2) {
        fprintf(stderr,"Run with only one argument, the file name\n");
        return -1;
    }
    FILE *theFile = fopen(argv[1],"rb");
    if (theFile==0) {
        fprintf(stderr,"Could not open the file\n");
        return -1;
    }
    
    // Check the format to see if it is Little or Big endian
    fseek(theFile,21,SEEK_SET);
    fread(LEBE,1,3,theFile);
    if (LEBE[0]!='B' && LEBE[0]!='L') return -1; // Obviously wrong.
    char swapBytes = (RunningOnBigEndian() ? (LEBE[0]=='L') : (LEBE[0]=='B'));
    
    // The format is pretty simple.
    // Header block, name of variable, content of variable
    while (theNumbers==0 || theMask==0) {
        fseek(theFile,8,SEEK_CUR); // Not needed
        fread(&typeNumber,1,4,theFile);
        fread(&m,1,4,theFile);
        fread(&n,1,4,theFile);
        fread(&o,1,4,theFile);
        fread(&nameLength,1,4,theFile);
        if (swapBytes) {
            Swap4Bytes((char *)&typeNumber);
            Swap4Bytes((char *)&m);
            Swap4Bytes((char *)&n);
            Swap4Bytes((char *)&o);
            Swap4Bytes((char *)&nameLength);
        }
        if (fread(variableName,1,nameLength,theFile)!=nameLength) break;
        if (nameLength==8 && strncmp(variableName,"Numbers",7)==0) {
            length = m;
            theNumbers = (double *)malloc(length*sizeof(double));
            fread(theNumbers,8,length,theFile);
            if (swapBytes) {
                for (i=0;i<length;i++) Swap8Bytes((char *)(theNumbers+i));
            }
        }
        else if (nameLength==5 && strncmp(variableName,"Mask",4)==0 && length==m) {
            theMask = (char *)malloc(length);
            fread(theMask,1,length,theFile);
        }
        else {
            // Skip over this data block
            fseek(theFile,blockSizes[typeNumber]*m*n*o,SEEK_CUR);
        }
    }
    if (length==0) return -1;
    
    // Now print the content
    for (i=0;i<length;i++) {
        if (theMask==0 || theMask[i])
            fprintf(stdout,"%.15lg\n",theNumbers[i]);
        else
            fprintf(stdout,"\n");
    }
    
    return 0;
}
