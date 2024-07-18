/******************************************************************************\
*                                                                              *
* ext2tvec                                                                     *
* ========                                                                     *
*                                                                              *
* Convert space-seperated raw Extended Mode data into the fgmtvec used with    *
* FGM DP pipeline stages.                                                      *
*                                                                              *
* Compile with "gcc -std=gnu99 ext2tvec.c -lm -o ext2tvec                      *
* (Do not use c99, as that will break getopt),                                 *
*                                                                              *
* Version History                                                              *
* ---------------                                                              *
* 0.1 | 2024-04-29 | Initial Working version, but parameter order can be       *
*                    significant, which might be problematic.                  *
* 0.2 | 2024-04-29 | Parameter ordering should be irrelevant now. Error values *
*                    also tidied up, and some Verbose information added.       *
*                                                                              *
* Version 0.2                                                                  *
* 2024-04-29                                                                   *
* TMO                                                                          *
*                                                                              *
* (C) Space Magnetometer Laboratory, Imperial College London, 2024             *
*                                                                              *
\******************************************************************************/

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <inttypes.h>
#include <math.h>
#include <time.h>

// The Extended Mode data should not exceed 23 hours (or maybe 28 hours in a very worst
// case scenario). 28 hours of Extended Mode Data, with one vector per four second spin,
// is around 28*3600/4 vectors, which is 25000 vectors. If we allow for 50000 vectors,
// that's more than allowance.

#define SIZE 50000

float b[SIZE][3];
uint16_t year[SIZE];
uint32_t micro[SIZE];
uint8_t month[SIZE],day[SIZE],hour[SIZE],min[SIZE],sec[SIZE];

struct timesp
{
    uint32_t tv_sec;
    uint32_t tv_nsec;
}; 

struct fgmtvec
{
    uint32_t stat;     // Satellite Status Word
    struct timesp tv;  // Time
    float b[3];        // Magnetic Field
    float phavar;      // Spin Phase or Total Variance
    float magvar;      // Magnitude Variance
};

int32_t microconvert(char asciimicros[256])
{
	uint8_t convdigit(char digit)
	{
		if ((digit>='0') && (digit<='9'))
		{
			return(digit-'0');
		}
		else
		{
			return(-1);
		}
		
	}
	
	if (asciimicros[strlen(asciimicros)-1]!='Z')
	{
		fprintf(stderr,"Error - ISO Time has to finish with a Z, \"%s\" doesn't\r\n",asciimicros);
		exit(-10);
	}
	
	if (strlen(asciimicros)>6)
	{
		fprintf(stderr,"Microsecond value too large, can't be more than 6 digits : \"%s\"\r\n)",asciimicros);
		exit(-11);
	}
	
	int32_t returnvalue=0;
	
	// 012345678901234_012345678901234_012345678901234_012345678901234_012345678901234_
	// 123.456Z        123.4Z          123.4567Z       123.456789Z
	//
	// 4*100000+5*10000+6*1000 = 456000                 10^5 = 100000
	// 4*100000+5*10000+6*1000+7*100+8*10+9 = 456789
	//
	// strlen("456Z")= 4, need to loop from 0 to 2 = strlen()-2
	
	
	for(uint16_t n=0;n<(strlen(asciimicros)-1);n++)
	{
		returnvalue+=pow(10,(double)(5-n))*convdigit(asciimicros[n]);
	}
	
	return(returnvalue);
}

int main(int argc, char **argv)
{
	int help=0;
	int verbose=0;
	int c;
	FILE *outh,*inh;

	extern char *optarg;
	extern int optind;
	
	char micros[256];
	uint8_t forceoverwrite;
	uint8_t doit;
	char *retval;
	char inputline[256];
	uint8_t sc=0;

	inh=stdin;
	outh=stdout;
	forceoverwrite=0;
	doit=0;
	uint8_t inputfile,outputfile;
	char inputname[256]="";
	char outputname[256]="";


	inputfile=0;
	outputfile=0;

	while ((c=getopt(argc,argv,"vhyi:o:s:")) != -1)
	{
		switch(c)
		{
			case 'h':
				printf("\r\n ext2tvec - Extended mode to fgmtvec pipeline conversion stage\r\n");
				printf(" ========\r\n\r\n");
				printf(" This program takes space or comma seperated data from Extended Mode processing,\r\n");
				printf(" and outputs it in an fgmtvec format that most FGM DP pipeline stages can\r\n");
				printf(" accept.\r\n\r\n");
				printf("   -i <filename>  Select Input File, otherwise use STDIN (a file \"Cx...\" with x \r\n");
				printf("                  between 1 & 4, then x will be used as the spacecraft number)\r\n");
				printf("   -o <filename>  Select Output File, otherwise use STDOUT\r\n");
				printf("   -y             Force overwriting of the output file (ie Yes)\r\n");
				printf("   -s <sc>        Spacecraft number, which must be 1 to 4\r\n");
				printf("\r\n");
				printf(" Version 0.1, 2024-04-26, (C) Space Magnetometer Laboratory\r\n\r\n");
				exit(0);
			case 'v':
				verbose=1;
				break;
			case 'y':
				forceoverwrite=1;
				break;
			case 'i':
				strcpy(inputname,optarg);
				inputfile=1;
				break;
			case 'o':
				strcpy(outputname,optarg);
				outputfile=1;
				break;
			case 's':
				if (strlen(optarg)!=1)
				{
					fprintf(stderr,"Error - Spacecraft number \"%s\" must be a single digit\r\n",optarg);
					exit(-12);
				}
				if ((optarg[0]<'1') || (optarg[1]>'4'))
				{
					fprintf(stderr,"Error - Spacecraft number \"%s\" must be between 1 and 4\r\n",optarg);
					exit(-14);
				}
				sc=optarg[0]-'0';
				break;
			default:
				exit(-99);
				break;
		}
	}

	if (inputfile && outputfile && (strcmp(inputname,outputname)==0))
	{
		fprintf(stderr,"Error - Input and Output filenames cannot be the same.\r\n");
		exit(-1);
	}

	if (inputfile)
	{
		inh=fopen(inputname,"rb");
		if (!inh)
		{
			fprintf(stderr,"Error - Cannot open \"%s\" as input file.\r\n",optarg);
			exit(-2);
		}
		if (sc==0)
		{
			if ((inputname[0]=='C') && (inputname[1]>='1') && (inputname[1]<='4'))
				sc=inputname[1]-'0';
		}
	}
	else
		inh=stdin;

	if (outputfile)
	{
		if (fopen(outputname,"r"))
		{
			if (!forceoverwrite)
			{
				fprintf(stderr,"Error - The output file already exists. Delete it or use -y to force overwriting.\r\n");
				exit(-3);
			}
		}
		outh=fopen(outputname,"wb");
		if (!outh)
		{
			fprintf(stderr,"Error - Cannot open \"%s\" as output file.\r\n",outputname);
			exit(-4);
		}
	}
	else
		outh=stdout;

	if (optind<argc)
	{
		fprintf(stderr,"Error - Unknown parameter(s).\r\n");
		exit(-5);
	}

	if (sc==0)
	{
		fprintf(stderr,"Error - The spacecraft must be defined.\r\n");
		exit(-6);
	}

	if (verbose)
	{
		fprintf(stderr,"Input Filename   : \"%s\"\r\n",inputname);
		fprintf(stderr,"Output Filename  : \"%s\"\r\n",outputname);
		fprintf(stderr,"Force Over-write : %s\r\n",forceoverwrite?"Yes":"No");
		fprintf(stderr,"Spacecraft       : %d\r\n",sc);
	}

	
	uint32_t veccnt=0;
	int cnt;

	while (1)
	{
		// 1111 22 33 44 55 66 777     8888888    9999999   10101010
		// 2002-02-27T23:34:54.000Z     5.4782    -6.1114    -2.2926
		// 2002-02-27T23:34:58.010Z    -2.6404    -3.4165    15.5850
		// 2002-02-27T23:35:02.030Z    -0.5316    -2.1936     2.8673
		
		cnt=fscanf(inh,"%"SCNuLEAST16"-%"SCNu8"-%"SCNu8"T%"SCNu8":%"SCNu8":%"SCNu8".%6s %f %f %f",&year[veccnt],&month[veccnt],&day[veccnt],&hour[veccnt],&min[veccnt],&sec[veccnt],(char*)&micros,&b[veccnt][0],&b[veccnt][1],&b[veccnt][2]);
		
		if (microconvert(micros)>=0)
		{
			micro[veccnt]=microconvert(micros);
		}
		else
		{
			fprintf(stderr,"Error - Bad microseconds (%s) in line \"%d\".\r\n",micros,veccnt);
			exit(-7);
		}
		if (cnt==EOF)
			break;
		if (cnt<0)
		{
			fprintf(stderr,"Error - Error with scanf; %d, at line %d.\r\n",cnt,veccnt);
			exit(-8);
		}
		if (cnt!=10)
		{
			fprintf(stderr,"Error - Unexpected number of parameters (%d) at line %d.\r\n",cnt,veccnt);
			exit(-9);
		}
		veccnt++;
	}
	while(cnt!=EOF);

	struct fgmtvec temp;
	struct tm segmentedtime;
	time_t unixtime;
	
	uint8_t range=2; // Just pretend it's always this! (I don't think anything downstream needs this).
	
	temp.stat=0x03F9100C+(range<<4)+((sc-1)<<30);
	
	for(int i=0;i<veccnt;i++)
	{
		segmentedtime.tm_year=year[i]-1900;
		segmentedtime.tm_mon=month[i]-1;
		segmentedtime.tm_mday=day[i];
		segmentedtime.tm_hour=hour[i];
		segmentedtime.tm_min=min[i];
		segmentedtime.tm_sec=min[i];
		segmentedtime.tm_isdst=0;
		unixtime=mktime(&segmentedtime);
			
		temp.tv.tv_sec=unixtime;
		temp.tv.tv_nsec=micro[i]*1000;
		temp.b[0]=b[i][0];
		temp.b[1]=b[i][1];
		temp.b[2]=b[i][2];
		temp.phavar=0;
		temp.magvar=0;
		fwrite(&temp,sizeof(temp),1,outh);
	}
	
	fclose(inh);
}	
