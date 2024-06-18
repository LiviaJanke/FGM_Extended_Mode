# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 09:58:41 2024

@author: Livia
"""

#pip install Flask


from flask import Flask, request, render_template_string, send_file
import os
import datetime

app = Flask(__name__)

def rpad(x):
    if x < 0x1000:
        return f"{x:03X} "
    elif x == 0xFFFF:
        return f"<b><font color='#F00'>{x:04X}</font></b>"
    else:
        return f"<font color='gray'>{x:04X}</font>"

def lpad(x):
    if x < 0x1000:
        return f" {x:03X}"
    elif x == 0xFFFF:
        return f"<b><font color='#F00'>{x:04X}</font></b>"
    else:
        return f"<font color='gray'>{x:04X}</font>"

@app.route('/')
def index():
    mission = "cluster"
    
    # Generating HTML header
    html = f"<h1>{mission} Extended Mode File Listing</h1>"
    html += "<p><i>The</i> &#9711; <i>links will output and append data to /tmp/ClusterExtMode on Alsvid. This will then need to be manually edited, and deleted prior to using again.</i></p>"
    
    tmp_file_path = "/tmp/ClusterExtMode"
    tmp_file_size = os.path.getsize(tmp_file_path) if os.path.exists(tmp_file_path) else 0
    
    html += f"<p>Click <a href='/delete_tmp_file' target='_blank'><b>Here</b></a> to delete /tmp/ClusterExtMode (Current Size {tmp_file_size} bytes).</p>"
    
    # Get parameters
    sc = int(request.args.get("sc", 3))
    sc = sc if 1 <= sc <= 4 else 3
    
    current_year = datetime.datetime.now().year
    year = int(request.args.get("year", current_year))
    year = year if 2000 <= year <= current_year else current_year
    
    month = int(request.args.get("month", datetime.datetime.now().month))
    month = month if 1 <= month <= 12 else datetime.datetime.now().month
    
    day = int(request.args.get("day", datetime.datetime.now().day))
    day = day if 1 <= day <= 31 else datetime.datetime.now().day  # Simplified
    
    version = request.args.get("version", "B")
    version = version if version in ["A", "B", "C", "K", "Q"] else "B"
    
    filename = os.path.join(os.getenv("CLUSTER_RAW_DATA", "."), f"{year:04d}", f"{month:02d}", f"C{sc}_{year-2000:02d}{month:02d}{day:02d}_{version}.BS")
    html += f"<h2>{filename}</h2>"
    
    try:
        with open(filename, 'rb') as file:
            data = file.read()
    except FileNotFoundError:
        return f"<h1>File not found: {filename}</h1>"
    
    def byte(offset):
        return data[offset]
    
    pntr = 0
    newdata = b""
    originallength = len(data)
    
    while pntr < originallength:
        packetlen = (byte(pntr + 9) << 16) | (byte(pntr + 10) << 8) | byte(pntr + 11)
        tmmode = byte(pntr + 16) & 0x0F
        if tmmode == 0x0F:
            newdata += data[pntr:pntr + packetlen + 15]
        pntr += packetlen + 15
    
    data = newdata
    length = len(data)
    pntr = 0
    
    html += f"File Length: {length} (from {originallength})<br>"
    
    prevevenlastreset = 0xFFFF
    prevoddlastreset = 0xFFFF
    
    html += "<pre>"
    html += "                                                                           Even                  Odd                   Prev Now\r\n"
    html += "                                       Reset   Even            Odd         Prev This  This Next  Prev This  This Next  to   to\r\n"
    html += "Position   Packet Time                 Cnt  Cnt Min Max    Cnt Min Max     Last 1st   Last 1st   Last 1st   Last 1st   Now  Next\r\n"
    html += "========   =========================== ==== ============== ==============  ==== ====  ==== ====  ==== ====  ==== ====  ===  ===\r\n"
    
    while pntr < length:
        packetlen = (byte(pntr + 9) << 16) | (byte(pntr + 10) << 8) | byte(pntr + 11)
        tmmode = byte(pntr + 16) & 0x0F
        resetcnt = (byte(pntr + 27) << 8) | byte(pntr + 28)
        
        if tmmode == 0x0F:
            evenrangelist = [0] * 4096
            oddrangelist = [0] * 4096
            
            evenvecs = 0
            evenresetmin = 0xFFF
            evenresetmax = 0x0000
            evenvecszero = 0
            
            prevrange = ((byte(pntr + 55) << 8) | byte(pntr + 56)) & 0xFFF
            for i in range(1, 444):
                range_ = ((byte(pntr + 55 + 8 * i) << 8) | byte(pntr + 56 + 8 * i)) & 0xFFF
                if range_ > evenresetmax:
                    evenresetmax = range_
                if range_ < evenresetmin:
                    evenresetmin = range_
                diff = range_ - prevrange
                if diff in [0, 1, -4095]:
                    evenvecs += 1
                    if diff == 0:
                        evenvecszero += 1
                prevrange = range_
                evenrangelist[range_] = 1
            
            oddvecs = 0
            oddresetmin = 0xFFF
            oddresetmax = 0x0000
            oddvecszero = 0
            
            prevrange = ((byte(pntr + 51) << 8) | byte(pntr + 52)) & 0xFFF
            for i in range(1, 445):
                range_ = ((byte(pntr + 51 + 8 * i) << 8) | byte(pntr + 52 + 8 * i)) & 0xFFF
                if range_ > oddresetmax:
                    oddresetmax = range_
                if range_ < oddresetmin:
                    oddresetmin = range_
                diff = range_ - prevrange
                if diff in [0, 1, -4095]:
                    oddvecs += 1
                    if diff == 0:
                        oddvecszero += 1
                prevrange = range_
                oddrangelist[range_] = 1
            
            # Format the output similar to the PHP script
            html += f"{pntr:8d} | {resetcnt:04X} {evenvecs:3d} {evenresetmin:03X}-{evenresetmax:03X} "
            if evenvecs > oddvecs:
                html += "<font color='red'><b>E</b></font>"
                even1 = 1
            else:
                html += "<font color='grey'>e</font>"
                even1 = 0
            if (evenvecs - evenvecszero) != 0 and 15 < (evenvecs / (evenvecs - evenvecszero)) < 23:
                html += "<font color='red'><b>E</b></font>"
                even2 = 1
            else:
                html += "<font color='grey'>e</font>"
                even2 = 0
            html += " "
            html += f"{oddvecs:3d} {oddresetmin:03X}-{oddresetmax:03X} "
            if evenvecs < oddvecs:
                html += "<font color='red'><b>O</b></font>"
                odd1 = 1
            else:
                html += "<font color='grey'>o</font>"
                odd1 = 0
            if (oddvecs - oddvecszero) != 0 and 15 < (oddvecs / (oddvecs - oddvecszero)) < 23:
                html += "<font color='red'><b>O</b></font>"
                odd2 = 1
            else:
                html
