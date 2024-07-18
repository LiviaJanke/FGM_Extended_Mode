/********************************************************************\
*                                                                    *
*  generate_tvec.c                                                   *
*  ===============                                                   *
*                                                                    *
* Generates some test data formatted using the fgmtvec data          *
* structure. The data is sent to stdout                              *
*                                                                    *
* This is used to generate test data for the fgm DP software         *
*                                                                    *
* The date in this data is set to 2024-04-19, so STOF,STEF and SATT  *
* files for this period will need to be processed and used to add    *
* data to stof.cl1, satt.cl1 and stef.cl1, as well as setting the    *
* Environment variables appropriately.                               *
*                                                                    *
*   gcc generate_tvec.c -lm -o generate_tvec                         *
*                                                                    *
*   generate_tvec > testfile.data                                    *
*                                                                    *
*   cat testfile.data | fgmls                                        *
*   cat testfile.data | fgmhrt -s gse | fgmvec | more                *
*   cat testfile.data | fgmhrt -s gse | fgmpos | igmvec | more       *
*   cat testfile.data | fgmhrt -s gse | fgmpos | caavec | more       *
*                                                                    *
* Version 1.                                                         *
* Tim Oddy                                                           *
* 2024-04-25                                                         *
*                                                                    *
\********************************************************************/

#include <stdio.h>
#include <stdint.h>
#include <math.h>

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

struct fgmtrec
{
    uint32_t id;       // Mission Status Word
    uint32_t stat;     // Satellite Status Word
    struct timesp tv;  // Time
    float b[3];        // Magnetic Field Vector
    float phavar;      // Spin Phase or Total Variance
    float magvar;      // Magnitude Variance
    float r[3];        // Spacecraft Position Vector
};

int main()
{
	// Satellite Status Word
	//
	// (SC-1)<<30	30-31	2		Spacecraft									Byte 0	MS-Nybble
	//				29		1		Unused
	// 0<<28		28		1		1ry Sensor
	//
	// 0<<27		27		1		No Eclipse											LS-Nybble
	// 0<<26		26		1		No Range Change
	// 3<<24		24-25	2		Special Calibration
	//																			--------------------
	// 1<<23		23		1		Averaged									Byte 1	Both Nybbles
	// 15<<19		19-22	4		Averaging quality better than 90%
	// 1<<16		16-18	3		FSR Ref Frame
	//																			--------------------
	// 0<<15		15		1		Do not filter out vectors due to Eclipse	Byte 2	MS-Nybble
	// 0<<14		14		1		or due to Calibration Mode
	// 0<<13		13		1		or due to Range Change
	// 1<<12		12		1		Filtered Science Data
	//
	// 0<<11		11		1		Not filtered as MSA Data							LS-Nybble
	// 0<<9			9-10	2		No calibration on OB or IB
	// 0<<8			8		1		ADC 1 in use
	//																			--------------------
	// 0<<7			7		1		Sensor is OB								Byte 3	MS-Nybble
	// range<<4		6-4		3		Range is <range>
	//
	// 0xC<<0		3-0		4		Let's call the TM Mode C !							LS-Nybble
	//
	// 0000 0011   1111 1001   0001 0000   0rrr 1100  =  0x03F910rC


	uint8_t		range=2;
	uint8_t		sc=1;
	struct 		fgmtvec temp;

	temp.stat=0x03F9100C+(range<<4)+((sc-1)<<30);

	for(uint8_t x=0;x<100;x++)
	{
		temp.tv.tv_sec=1713484800+(x/10);
		temp.tv.tv_nsec=(x%10)*100000000;
		temp.b[0]=80*sinf((float)x/100);
		temp.b[1]=80*cosf((float)x/100);
		temp.b[2]=80*sinf((float)x/13);
		temp.phavar=0;	// This doesn't seem to change fgmhrt's behaviour, so is probably ignored
		temp.magvar=1;	// Some software complains if this is zero
		
		fwrite(&temp,sizeof(temp),1,stdout);
	}
}
