# -*- coding: utf-8 -*-
"""

Miscellaneous functions

AUTHOR:  
        
   Ashok Verma (ashokverma@ucla.edu)
   Department of Earth, Planetary, and Space Sciences
   University of California, Los Angeles

"""

# -------------------------------------------------------------------------------------------------------------------
import os, glob, sys
import datetime as dt
from termcolor import colored, cprint
from inspect import currentframe, getframeinfo

cf = currentframe()
sn = getframeinfo(cf).filename


# -------------------------------------------------------------------------------------------------------------------
def raise_error(msg):
    rm_pyc()
    raise SystemExit(colored("ERROR:\n" + msg, color='red'))


# -------------------------------------------------------------------------------------------------------------------
def raise_warning(msg):
    cprint("WARNING:\n" + msg, 'blue')


# -------------------------------------------------------------------------------------------------------------------
def color_txt(txt, clr):
    cprint(txt, clr)


# -------------------------------------------------------------------------------------------------------------------
def check_run_status(run_flag, cmd, line_number, sn=""):
    if not "None" in str(run_flag) and len(str(run_flag)):
        rm_pyc()
        msg = "%s \n Error while '%s' \n Script Name: %s \n Line Number: %s" % (run_flag, cmd, sn, line_number)
        raise_error(msg)


# -------------------------------------------------------------------------------------------------------------------
def path_check(path_list):
    if type(path_list) is list:
        for path in path_list:
            if not os.path.exists(path):
                check_run_status("No such file or directory", "path check: '%s'" % path, cf.f_lineno)
    else:
        if not os.path.exists(path_list):
            check_run_status("No such file or directory", "path check: '%s'" % path_list, cf.f_lineno)


# -------------------------------------------------------------------------------------------------------------------
def rm_files(des, exclude=[]):
    get_all = glob.glob(des)
    
    if len(exclude) > 0:
        get_all = []
        for excl in exclude:
            files = []
            for trash in glob.glob(des):
                if excl not in trash:
                    files.append(trash)
            
            get_all.append(files)
        get_all = list(set.intersection(*map(set, get_all)))
    
    for trash in get_all:
        if os.path.exists(trash): os.remove(trash)


# -------------------------------------------------------------------------------------------------------------------
def rm_pyc():
    for gin in glob.glob("./*.pyc"):
        os.remove(gin)


# -------------------------------------------------------------------------------------------------------------------
def get_date(year, doy, hr, mn, sec, ms=0):
    date = (dt.datetime(year, 1, 1) + dt.timedelta(days=doy - 1, hours=hr, minutes=mn, seconds=sec, microseconds=ms))
    date = date.strftime("%d-%b-%Y %H:%M:%S.%f")
    
    return date


# -------------------------------------------------------------------------------------------------------------------
def str2datetime(string):
    return dt.datetime.strptime(string, "%d-%b-%Y %H:%M:%S.%f")


# -------------------------------------------------------------------------------------------------------------------
def datetime2str(datetime):
    return datetime.strftime("%d-%b-%Y %H:%M:%S.%f")


# -------------------------------------------------------------------------------------------------------------------
def add_time(date, day=0, hr=0, mn=0, sec=0, ms=0, dtType=False):
    date = date + dt.timedelta(days=day, hours=hr, minutes=mn, seconds=sec, microseconds=ms)
    if dtType: return date
    return date.strftime("%d-%b-%Y %H:%M:%S.%f")


# -------------------------------------------------------------------------------------------------------------------
def time_now():
    return dt.datetime.now()


# -------------------------------------------------------------------------------------------------------------------
def time_dif(time_start, time_end):
    sec = (time_end - time_start).total_seconds()
    
    hr = sec / (60 * 60)
    mn = (hr - int(hr)) * 60
    sec = (mn - int(mn)) * 60
    
    return str("Time taken: %s Hr: %s Min: %s Sec \n" % (int(hr), int(mn), int(sec)))


# -----------------------------------------------------------------------
def msr_band(freq):
    if 1.0e9 <= freq < 2.0e9: return 'L'
    if 2.0e9 <= freq < 4.0e9: return 'S'
    if 4.0e9 <= freq < 7.0e9: return 'C'
    if 7.0e9 <= freq < 12.0e9: return 'X'
    if 12.0e9 <= freq < 18.0e9: return 'Ku'
    if 26.5e9 <= freq < 40.0e9: return 'Ka'
    return None


# -----------------------------------------------------------------------
def rec_dict(rec):
    stations = [12, 14, 15, 24, 25, 26, 34, 35, 36, 42, 43, 45, 54, 55, 61, 63, 64, 65, 66]
    up = ['S', 'X', 'Ku']
    dw = ['S', 'X', 'Ku']
    
    data = {}
    for stn in stations:
        sn = str(stn)
        for u in up:
            for d in dw:
                data.update({sn + u + d: rec})
    return data


# -------------------------------------------------------------------------------------------------------------------
class progressBar:

      '''

      Track progress for the running operations.

      '''

      def __init__( self, maxLabelLen=36, blockSize=20 ):

         '''

         INPUTS:

         --maxLabelLen  Length of the longest job label.
         --blockSize  The size of the progress bar.

         '''
         self.colLen = maxLabelLen
         self.step = None
         self.totalSteps = None
         self.lastOutputPct = None
         self.blockSize = blockSize
         self.st = time_now() 

      def start( self, numStep=100, label=""):

         '''
         Start a job.

         This will print a job label and start the counter.

         INPUTS:

         --numStep  The number of steps in the job.
         --label  The label for the job. If this is longer than maxLabelLen, it will be truncated.

         '''

         self.step = 0
         self.label = "%40s" %label.replace("Postfit measurements","Filter Solution").title()
         self.totalSteps = numStep
         self.lastOutputPct = 0
         self.localStep = 0

         lbl = label
         if len( lbl ) > self.colLen:
            lbl = label[:self.colLen]

         status = ""
         text = "\r"+self.label+"   :  [{0}] {1}% {2}".format(colored ("█"*self.localStep + \
                "-"*(self.blockSize-self.localStep), 'red') , 0, status)

         sys.stdout.write(text)
         sys.stdout.flush()

      def setLabel( self, label ):
          self.label = label

      def increment( self ):

         '''

         Increment the current step by 1.

         '''

         self.step += 1
         self.setStep( self.step )

      def setStep( self, step ):

         '''

         Set the current step to the input value.

         INPUTS:

         --step  The current step to the input value.

         '''
         self.step = step

         x = float( self.step ) / float( self.totalSteps )
         pct = float( self.step ) / float( self.totalSteps ) * 100
         delta = pct - self.lastOutputPct

         status = ""
         chrSize = 100/self.blockSize
         while delta >= chrSize:
            self.localStep += 1
            text = "\r"+self.label+"   :  [{0}] {1}% {2}".format( colored("█"*self.localStep + \
                   "-"*(self.blockSize-self.localStep), 'red'), int(pct), status)
            sys.stdout.write(text)

            self.lastOutputPct += chrSize
            delta -= chrSize

         sys.stdout.flush()

      def stop( self ):

         '''

         Stop the job.

         '''

         status = time_dif(self.st, time_now())
         text = "\r"+self.label+"   :  [{0}] {1}% {2}\n".format( colored("█"*self.blockSize, 'green'), \
                100, status)
         sys.stdout.write( text )
         sys.stdout.flush()

# -------------------------------------------------------------------------------------------------------------------
class dic_attrs():
    def __init__(self, **kw):
        self.__dict__ = kw

# -------------------------------------------------------------------------------------------------------------------
