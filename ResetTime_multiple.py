#!/usr/bin/python3 

from datetime import datetime,timedelta
#from scipy.stats import linregress
import sys

validphid=(0x1F,0x47,0x6F,0x97,0x26,0x4E,0x76,0x9E,0x2D,0x55,0x7D,0xA5)
sciphid=(0x1F,0x47,0x6F,0x97,0x26,0x4E,0x76,0x9E)
fgmhkphid=(0x2D,0x55,0x7D,0xA5)

#rewrite interpolation func

class packet():

    counter=0

    # .cdds is the CDDS packet header bytes (15)
    # .size is the packet size from that CDDS header
    # .payload are the bytes of the payload packet, so everything that isn't the CDDS header
    # .reset is the packet reset count, from the appropriate part of the FGM header
    # .micros are the total microseconds from a combination of the days, milliseconds and microseconds
    # .scet is the time, in Python format, from the .micros
    # .pktcnt is a one-up count of each packet (ie order by presence in file)
    # counter is a count of all the packets ever initialised
    

    def __init__(self,d):
        self.cdds=d[0:15]
        self.size=int.from_bytes(d[9:12],"big")
        self.payload=d[15:15+self.size]
        
        if self.cdds[8] in sciphid:
            self.reset=int.from_bytes(self.payload[12:14],"big")
        elif self.cdds[8] in fgmhkphid:
            self.reset=(int.from_bytes(self.payload[8:10],"big")+65537)%65536
        else:
            self.reset=-1
        self.micros= int.from_bytes(self.cdds[0:2],"big")*86400*1000000+int.from_bytes(self.cdds[2:6],"big")*1000+int.from_bytes(self.cdds[6:8],"big")
        self.scet=timedelta(microseconds=self.micros)+datetime(1958,1,1)
        
        self.pktcnt=packet.counter
        packet.counter+=1
    
    def __str__(self):
        return("{:7s}".format("#"+str(self.pktcnt))+" | "+" ".join('{:02X}'.format(n) for n in self.cdds)+" | "+" ".join('{:02X}'.format(n) for n in self.payload[0:30]))

# Just check that a filename has been passed as the one and only argument

if len(sys.argv)!=2:
    print("A single filename should be passed as an argument",file=sys.stderr)
    quit()

# Read that file in, as a bytearray called data
# datalen is the byte size

file=open(sys.argv[1],"rb")
if file==0:
    print("Could not open file \""+file+"\"")
    quit()
data=bytearray(file.read())
file.close()
datalen=len(data)

# Import all that bytearray 'data', into a list called 'packets'
# Use 'offset' to track the position in 'data'

# The CDDS header of 15 bytes, makes each chunk of data 15 bytes + the size in that CDDS header

# If the packet Telementry Status (in bytes 0 & 1) is 0x000E, then the
# instrument is in Extended Mode. There's nothing useful in any science packet
# that is marked like this, so throw it away
# This is effectively a While-Do loop, so when offset is greater or equal ot datalen
# we've got to the end, so exit the loop

packets=[]
offset=0

while True:
    packets.append(packet(data[offset:]))
    offset+=15+len(packets[-1].payload)
    if packets[-1].payload[0]==0 and packets[-1].payload[1]==0x0E:
        packets=packets[:-1]
    if offset>=datalen:
        break

# Go through the entire set of packes, and try to spot where the reset
# doesn't increase, implying either a roll-over or a power-on. Regardless
# of why, a regression fit will be buggered by this, so do it on what
# we alrady have, and reinitialise start

i=0
start=0
while i<(len(packets)-1):
    if (packets[i+1].reset)<(packets[i].reset):
        resets=[p.reset for p in packets[start:i+1]]
        listmicros=[p.micros for p in packets[start:i+1]]
        slope,intercept,rvalue, pvalue,stderr=linregress(resets,listmicros)
        regressionvalues=[p.reset*slope+intercept for p in packets[start:i+1]]

        print(min(p.scet for p in packets[start:i+1]).strftime("%Y-%m-%dT%H:%M:%SZ"),max(p.scet for p in packets[start:i+1]).strftime("%Y-%m-%dT%H:%M:%SZ"),sep=" ",end=" ")
        print("{:04X}".format(min(p.reset for p in packets[start:i+1])),"{:04X}".format(max(p.reset for p in packets[start:i+1])),end=" ")
        print("{:23.15f}".format(slope),"{:19.2f}".format(intercept))
        start=i+1
    i+=1

# At this point, we've still got some packets left, so we also have to
# do a regression fit on these, and output that too
# This should be almost the same as the regression above

resets=[p.reset for p in packets[start:i+1]]
listmicros=[p.micros for p in packets[start:i+1]]
slope,intercept,rvalue, pvalue,stderr=linregress(resets,listmicros)
regressionvalues=[p.reset*slope+intercept for p in packets[start:i+1]]

print(min(p.scet for p in packets[start:i+1]).strftime("%Y-%m-%dT%H:%M:%SZ"),max(p.scet for p in packets[start:i+1]).strftime("%Y-%m-%dT%H:%M:%SZ"),sep=" ",end=" ")
print("{:04X}".format(min(p.reset for p in packets[start:i+1])),"{:04X}".format(max(p.reset for p in packets[start:i+1])),end=" ")
print("{:23.15f}".format(slope),"{:19.2f}".format(intercept))

# The output from the program is formatted as:
#   The start SCET - ISO formatted to nearest second
#   The end SCET
#   The start reset value - Hex 4-digits, left-zero-padded
#   The end reset value
#   The regression fit slope
#   The regression fit intercept
