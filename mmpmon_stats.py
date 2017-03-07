#!/usr/bin/env python
##########################################################################
#    mmpmon_stats: Applications of time averaging to GPFS metrics
#    Copyright (C) 2016 J. Robert Michael, PhD
#    (with contributions from Keith Solademi)
##########################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import time
import sys
import datetime
import socket

### NOTE: This program uses 'subprocess.Popen()' with 'shell=True' to call 'mmpmon'. Please use at your own risk.
### For warnings regarding this (often frowned upon) formalism, see https://docs.python.org/2/library/subprocess.html#frequently-used-arguments
def bashexec(cmd):
    import subprocess
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    outlines = out.splitlines()
    errlines = err.splitlines()
    return outlines, errlines

def mmget_state():
    mmcmd = "echo io_s | /usr/lpp/mmfs/bin/mmpmon -s -p "

    (outlines, errlines) = bashexec(mmcmd)
    toks = outlines[0].split()

    v = []
    v.append( float(toks[12]) ) # Bytes read
    v.append( float(toks[14]) ) # Bytes written
    v.append( float(toks[16]) ) # Files opened
    v.append( float(toks[18]) ) # Files closed
    v.append( float(toks[20]) ) # Reads
    v.append( float(toks[22]) ) # Writes
    v.append( float(toks[24]) ) # Directory reads
    v.append( float(toks[26]) ) # Inodes changed

    v[0] = v[0]/(1000.0*1000.0) # Bytes -> MB
    v[1] = v[1]/(1000.0*1000.0) # Bytes -> MB

    return v

if __name__=="__main__":
    epoch0 = datetime.datetime(1970,1,1)

    print "*****************************************"
    print "* MBRps .... MB read per second         *"
    print "* MBWps .... MB written per second      *"
    print "* FOps ..... Files opened per second    *"
    print "* FCps ..... Files closed per second    *"
    print "* Rps ...... Reads per second           *"
    print "* kRps ..... kilo-Reads per second      *"
    print "* Wps ...... Writes per second          *"
    print "* kWps ..... kilo-Writes per second     *"
    print "* RDps ..... Directory reads per second *"
    print "* INDps .... Inode changes per second   *"
    print "*****************************************"
    metrics = ['Hostname', 'EpochTime', 'MBRps', 'MBWps', 'FOps', 'FCps', 'Rps', 'kRps', 'Wps', 'kWps', 'RDps', 'INDps']
    for m in metrics:
        print "%10s"%( m ),
    print ""

    # Averaged values will take place over a 'time_gap' interval.
    time_gap = 30
    # Reports will be made every 'tsleep' seconds
    tsleep = 5

    ts = []
    vs = []

    while( True ):

        v = mmget_state()

        now = time.time()
        ts.append( now )
        vs.append( v )
        then = ts[0]
        dt = now - then
        if( dt == 0.0 ): 
            continue
        while( dt > time_gap ):
            del ts[0]
            del vs[0]
            then = ts[0]
            dt = now - then

        v1 = vs[0]
        v2 = vs[-1]

        MBRps = ( v2[0] - v1[0] )/dt
        MBWps = ( v2[1] - v1[1] )/dt
        FOps = ( v2[2] - v1[2] )/dt
        FCps = ( v2[3] - v1[3] )/dt
        Rps = ( v2[4] - v1[4] )/dt
        kRps = Rps/1000.0
        Wps = ( v2[5] - v1[5] )/dt
        kWps = Wps/1000.0
        RDps = ( v2[6] - v1[6] )/dt
        INDps = ( v2[7] - v1[7] )/dt

        values = [MBRps, MBWps, FOps, FCps, Rps, kRps, Wps, kWps, RDps, INDps]
        epochTime = 0.0
        #epochTime = (datetime.datetime.now() - epoch0).total_seconds()
        epochTime = datetime.datetime.now().strftime('%s')
        hostname = socket.gethostname()
        print "%10s %10s"%( hostname, epochTime ),
        for v in values:
            print "%10.2f"%( v ),
        print ""

        #print "MBRps %.2f MBWps %.2f FOps %.2f FCps %.2f Rps %.2f kRps %.2f Wps %.2f kWps %.2f RDps %.2f INDps %.2f"%( MBRps, MBWps, FOps, FCps, Rps, kRps, Wps, kWps, RDps, INDps)

        sys.stdout.flush()
        time.sleep(tsleep)












