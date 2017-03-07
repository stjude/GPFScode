#!/usr/bin/env python
##########################################################################
#    cWs: Convolved waiters for load balancing of Spectrum Scale systems
#    Copyright (C) 2016 J. Robert Michael, PhD
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
import math
import datetime

### NOTE: This program uses 'subprocess.Popen()' with 'shell=True' to call 'mmpmon'. Please use at your own risk.
### For warnings regarding this (often frowned upon) formalism, see https://docs.python.org/2/library/subprocess.html#frequently-used-arguments
def bashexec( cmd ):
    import subprocess
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    outlines = out.splitlines()
    errlines = err.splitlines()
    return outlines, errlines

### TODO: Should we differentiate between different kinds of waiters?
def get_tot_wait_time():
    cmd = '/usr/lpp/mmfs/bin/mmdiag --waiters'
    (outlines, errlines) = bashexec(cmd)
    tot_wait_time = 0 
    for line in outlines:
        if( 'waiting' in line ):
            tline = line.split('waiting')[1]
            if( 'seconds' in line ):
                t = float(tline.split('seconds')[0])
            elif( 'minutes' in line):
                t = 60.0*float(tline.split('minutes')[0])
            elif( 'hours' in line):
                t = 60.0*60.0*float(tline.split('hours')[0])

            tot_wait_time += t

    return tot_wait_time

### main routine
if __name__=="__main__":
    import socket
    import sys

    ### define variables (TODO: Allow for these to be commandline variables)
    sleep_time = 15 ### time in seconds to sleep. 
    nmins_keep = 10 ### how long (in minutes)back to look for convolution

    nitems = int(math.ceil(nmins_keep*60/sleep_time)) ### how many items to keep in record

    ws = [ 1.0/float(abs(nitems-i)) for i in reversed(range(nitems)) ] ### weight vector for convolution
    Ws = []
    print "%10s %10s %10s"%( 'hostname', 'epochTime', 'cWs')
    while( True ):
        if( len(Ws) > nitems ):
            del Ws[-1]
        Ws.insert(0, get_tot_wait_time())
        den = sum(ws[:len(Ws)])
        cWs = float( sum( [w*W for (w,W) in zip(ws, Ws)] ))/den

        epochTime = datetime.datetime.now().strftime('%s')
        hostname = socket.gethostname()

        print "%10s %10s %10.2f"%( hostname, epochTime, cWs)

        sys.stdout.flush()
        time.sleep(sleep_time)
