# -*- coding: utf-8 -*-
"""

Miscellaneous functions

AUTHOR:  
        
   Dr. Ashok Kumar Verma (1,2)
   1. Department of Earth, Planetary, and Space Sciences
      University of California, Los Angeles, 90095, CA, USA.
   2. NASA Goddard Space Flight Center, Greenbelt, 20771, MD, USA.
   
   Contact: ashokkumar.verma@nasa.gov

"""
# -------------------------------------------------------------------------------------------------------------------
import binascii
import datetime as dt
import glob
import os
import sys
from inspect import currentframe, getframeinfo
from termcolor import colored, cprint

cf = currentframe()
sn = getframeinfo(cf).filename

# -------------------------------------------------------------------------------------------------------------------
# conversion factors
# -- Mega-Hz (MHz)
MHz = 1e6

# -- to convert seconds to nanoseconds
sec2nanosec = 1e9


# -------------------------------------------------------------------------------------------------------------------
def raise_error(msg: str):
    """
    
    Raise error message.
    
    Args:
        msg: A error message to print.
    """
    rm_pyc()
    raise SystemExit(colored("\nERROR:\n" + msg, color='red'))


# -------------------------------------------------------------------------------------------------------------------
def raise_warning(msg):
    """

    Raise warning message.
    
    Args:
        msg: A warning message to print.
    """
    cprint("\nWARNING:\n" + msg, 'blue')


# -------------------------------------------------------------------------------------------------------------------
def color_txt(txt: str,
              clr: str):
    """

    Print color text.

    Args:
        txt: A test to print.
        clr: Color of the text.
    """
    cprint(txt, clr)


# -------------------------------------------------------------------------------------------------------------------
def path_check(path_list):
    """

    Check input path.
    
    Args:
        path_list: A list or string of input path.
    """
    if type(path_list) is list:
        for path in path_list:
            if not os.path.exists(path):
                raise_error("'%s': No such file or directory!" % (os.path.abspath(path)))
    else:
        if not os.path.exists(path_list):
            raise_error("'%s': No such file or directory!" % (os.path.abspath(path_list)))


# -------------------------------------------------------------------------------------------------------------------
def text_to_bits(text: str,
                 encoding: str = 'utf-8',
                 errors: str = 'surrogatepass') -> str:
    """
    Convert sting to bits.
    Args:
        text: String to be encoded.
        encoding: Format of the encoding.
        errors: Error type.

    """
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


def text_from_bits(bits: bytes,
                   encoding: str = 'utf-8',
                   errors: str = 'surrogatepass') -> hex:
    """
    Converts bits to text.
    Args:
        bits: Bytes to be encoded
        encoding:  Format of the encoding.
        errors: Error type.

    """
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)


def int2bytes(i: str) -> bytes:
    """

    Args:
        i: Hexadecimal string hexstr.

    Returns:

    """
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))


# -------------------------------------------------------------------------------------------------------------------
def rm_files(des: str,
             exclude=None):
    """

    Remove files.
    
    Args:
        des: A file/directory path.
        exclude: List of files to exclude.
    """
    if exclude is None:
        exclude = []
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
    """

    Remove .pyc files.
    """
    for gin in glob.glob("./*.pyc"):
        os.remove(gin)


# -------------------------------------------------------------------------------------------------------------------
def get_date(year: int,
             doy: int,
             hr: int,
             mn: int,
             sec: int,
             ms=0) -> str:
    """

    Get formatted date.
    
    Args:
        year: Year.
        doy: Day of the year.
        hr: Hour.
        mn: Minute.
        sec: Second.
        ms: Millisecond.

    Returns: Formatted data

    """
    date = (dt.datetime(year, 1, 1) + dt.timedelta(days=doy - 1, hours=hr, minutes=mn, seconds=sec, microseconds=ms))
    date = date.strftime("%d-%b-%Y %H:%M:%S.%f")
    
    return date


# -------------------------------------------------------------------------------------------------------------------
def str2datetime(string: str):
    """

    Convert sting date into datatime object.
    
    Args:
        string: A string defines the date.

    Returns:

    """
    return dt.datetime.strptime(string, "%d-%b-%Y %H:%M:%S.%f")


# -------------------------------------------------------------------------------------------------------------------
def datetime2str(datetime):
    """

    Convert datetime object into sting format.
    
    Args:
        datetime: A date.

    Returns:

    """
    return datetime.strftime("%d-%b-%Y %H:%M:%S.%f")


# -------------------------------------------------------------------------------------------------------------------
def add_time(date: object,
             day: int = 0,
             hr: int = 0,
             mn: int = 0,
             sec: int = 0,
             ms: int = 0,
             dtType: bool = False):
    """

    Add time to the datetime object.
    
    Args:
        date: A date.
        day: Day.
        hr: Hour.
        mn: Minute.
        sec: Second.
        ms: Millisecond.
        dtType: A boolean flag to indicate if return value is a string or datetime object.

    Returns:

    """
    date = date + dt.timedelta(days=day, hours=hr, minutes=mn, seconds=sec, microseconds=ms)
    if dtType: return date
    return date.strftime("%d-%b-%Y %H:%M:%S.%f")


# -------------------------------------------------------------------------------------------------------------------
def time_now():
    """

    Get current time.

    """
    return dt.datetime.now()


# -------------------------------------------------------------------------------------------------------------------
def time_dif(time_start: object,
             time_end: object) -> str:
    """

    Get time difference between two times.
    
    Args:
        time_start: A start time.
        time_end: A end time.

    Returns:

    """
    sec = (time_end - time_start).total_seconds()
    
    hr = sec / (60 * 60)
    mn = (hr - int(hr)) * 60
    sec = (mn - int(mn)) * 60
    
    return str("Time taken: %s Hr: %s Min: %s Sec \n" % (int(hr), int(mn), int(sec)))


# -----------------------------------------------------------------------
def msr_band(freq: float) -> None:
    """

     Get measurement band based on in the input frequency.
     
    Args:
        freq: Signal frequency.

    Returns: name of the signal band.

    """
    if 1.0e9 <= freq < 2.0e9: return 'L'
    if 2.0e9 <= freq < 4.0e9: return 'S'
    if 4.0e9 <= freq < 7.0e9: return 'C'
    if 7.0e9 <= freq < 12.0e9: return 'X'
    if 12.0e9 <= freq < 18.0e9: return 'Ku'
    if 26.5e9 <= freq < 40.0e9: return 'Ka'
    return None


# -----------------------------------------------------------------------
def get_mul_fac(freq: float) -> float:
    """

    Get frequency multiplier to correct the frequency.
    
    Args:
        freq: A signal frequency.

    Returns:

    """
    freq_apx = 22e6
    return 1.0 * int(round(freq / freq_apx))


# -----------------------------------------------------------------------
def check_sky_freq(freq: float,
                   band: str) -> bool:
    """

    Check if given frequency at the sky level.
    
    Args:
        freq: A signal frequency.
        band: A frequency band.

    Returns:

    """
    flag = False
    if msr_band(freq) == band: flag = True
    return flag


# -----------------------------------------------------------------------
def find_exciter_band(turnaround_ratio: float) -> str:
    """

    Find exciter band of the receiver.
    
    Args:
        turnaround_ratio: A turnaround ratio.

    Returns: A exciter frequency band.

    """
    # Moyer's Table 13-1, and
    # https://deepspace.jpl.nasa.gov/dsndocs/810-005/201/201F.pdf
    
    # S-Band
    if (1.08 < turnaround_ratio < 1.09 or  # 240.0 / 221.0
            3.90 < turnaround_ratio < 4.00 or  # 880.0 / 221.0
            15.10 < turnaround_ratio < 15.2):  # 3344.0 / 221.0
        return 'S'
    
    # X-Band
    if (0.31 < turnaround_ratio > 0.33 or  # 240.0 / 749.0
            1.17 < turnaround_ratio > 1.18 or  # 880.0 / 749.0
            4.45 < turnaround_ratio < 4.47):  # 3344.0 / 749.0
        return "X"
    
    # Ka-Band
    if (0.06 < turnaround_ratio < 0.08 or  # 240.0 / 3599.0
            0.24 < turnaround_ratio < 0.25 or  # 880.0 / 3599.0
            0.90 < turnaround_ratio < 1.0):  # 3344.0 / 3599.0
        return "Ka"
    
    return None


# -----------------------------------------------------------------------
def c_2(band: str) -> float:
    """

    A downlink multiplier.
    
    Args:
        band: A downlink band.

    Returns: C2 value based on the downlink band.

    """
    # Moyer's Table 13-2
    if band == "S": return 1.0
    if band == "X": return 880.0 / 240.0
    if band == "Ka": return 3344.0 / 240.0


def m_2(ulband: str,
        dlband: str) -> float:
    """
    
    Get turnaround ratio.
    
    Args:
        ulband: Uplink band.
        dlband: Downlink band.

    Returns: Turnaround ratio.

    """
    
    # Moyer's Table 13-1
    if ulband == "S":
        if dlband == "S": return 240.0 / 221.0
        if dlband == "X": return 880.0 / 221.0
        if dlband == "Ka": return 3344.0 / 221.0
    
    if ulband == "X":
        if dlband == "S": return 240.0 / 749.0
        if dlband == "X": return 880.0 / 749.0
        if dlband == "Ka": return 3344.0 / 749.0
    
    if ulband == "Ka":
        if dlband == "S": return 240.0 / 3599.0
        if dlband == "X": return 880.0 / 3599.0
        if dlband == "Ka": return 3344.0 / 3599.0


# -----------------------------------------------------------------------
def is_dsn_valid(rec: dict,
                 getAll: bool = False,
                 data_type: str = None):
    """
    Check if given station is the valid DSN station
    
    Args:
        rec: A data record.
        getAll: A boolean flag to return all valid DSN stations.
        data_type: A type of data.

    Returns:

    """
    # list of all DSN numbers
    all_dsn = [
        # Goldstone stations
        12, 13, 14, 15, 16, 17, 23, 24, 25, 26, 27, 28,
        
        # Canberra stations
        33, 34, 35, 36, 42, 43, 45, 46,
        
        # Madrid stations
        53, 54, 55, 61, 63, 65, 66,
    ]
    
    # return all, if asked
    if getAll: return all_dsn
    
    # raise warning if station is not valid.
    if int(rec['station']) not in all_dsn:
        msg = '"%s" is not a valid DSN station.\n' \
              'If you think otherwise, then \n' \
              'please add this station at:\n\n' \
              'functions.py ---> is_dsn_valid ---> all_dsn\n\n' \
              'Time tag: %s\n' \
              'Station: DSS %s\n' \
              'Data type: %s\n'
        raise_warning(msg % (rec['station'], rec['time_tag'], rec['station'], data_type))
        return None
    else:
        return rec['station']


# -----------------------------------------------------------------------
def rec_dict(rec: dict,
             ramp: bool = False) -> dict:
    """

    Creates a dictionary of the records according to the DSN station, unlink
    downlink bands.
    
    Args:
        rec: A dictionary of records.
        ramp: A boolean flag to indicate if the data ramped.

    """
    # get list of all DSNs
    stations = is_dsn_valid(rec, True)
    
    up = ['S', 'X', 'Ka']
    dw = ['S', 'X', 'Ka']
    
    data = {}
    for stn in stations:
        for u in up:
            if ramp:
                data.update({str(stn) + u: rec})
            else:
                for d in dw:
                    data.update({str(stn) + u + d: rec})
    return data


# -------------------------------------------------------------------------------------------------------------------
class progressBar:
    """

      Track progress for the running operations.

      """
    
    def __init__(self, maxLabelLen: int = 40,
                 blockSize: int = 20):
        """
        
        Args:
            maxLabelLen: Length of the longest job label.
            blockSize: The size of the progress bar.
         
        """
        self.colLen = maxLabelLen
        self.step = None
        self.totalSteps = None
        self.lastOutputPct = None
        self.blockSize = blockSize
        self.st = time_now()
    
    def start(self, numStep: int = 100,
              label: str = ""):
        """
        
        Start a job. This will print a job label and start the counter.
        
        Args:
            numStep: The number of steps in the job.
            label: The label for the job.

        """
        
        self.step = 0
        self.label = label
        self.totalSteps = numStep
        self.lastOutputPct = 0
        self.localStep = 0
        
        status = ""
        text = "\r" + self.label + "   :  [{0}] {1}% {2}".format(colored("█" * self.localStep + \
                                                                         "-" * (self.blockSize - self.localStep),
                                                                         'red'), 0, status)
        
        sys.stdout.write(text)
        sys.stdout.flush()
    
    def setLabel(self, label: str):
        """
        
        Set label.
        
        Args:
            label: The label for the job.

        """
        self.label = label
    
    def increment(self):
        """

        Increment the current step by 1.
        
        """
        self.step += 1
        self.setStep(self.step)
    
    def setStep(self, step: int):
        """
        Set the current step to the input value.
        
        Args:
            step: The current step to the input value.


        """
        
        self.step = step
        
        x = float(self.step) / float(self.totalSteps)
        pct = float(self.step) / float(self.totalSteps) * 100
        delta = pct - self.lastOutputPct
        
        status = ""
        chrSize = 100 / self.blockSize
        while delta >= chrSize:
            self.localStep += 1
            text = "\r" + self.label + "   :  [{0}] {1}% {2}".format(colored("█" * self.localStep + \
                                                                             "-" * (self.blockSize - self.localStep),
                                                                             'red'), int(pct), status)
            sys.stdout.write(text)
            
            self.lastOutputPct += chrSize
            delta -= chrSize
        
        sys.stdout.flush()
    
    def stop(self):
        """
        
        Stop the job.

        """
        
        status = time_dif(self.st, time_now())
        text = "\r" + self.label + "   :  [{0}] {1}% {2}\n".format(colored("█" * self.blockSize, 'green'), 100, status)
        sys.stdout.write(text)
        sys.stdout.flush()


# -------------------------------------------------------------------------------------------------------------------
class dic_attrs():
    """

    Set dictionary attributes.
    
    """
    
    # def __init__(self, **kw):
    def __init__(self, **kw) -> None:
        self.__dict__ = kw

# -------------------------------------------------------------------------------------------------------------------
