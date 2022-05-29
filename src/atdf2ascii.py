# coding=utf-8
"""
USAGE    

    python atdf2ascii.py [-h,--help] 
    python atdf2ascii.py -i input_file [options...]
    
DESCRIPTION

    This script constructs an ASCII table of Doppler and Range observables from the Deep Space Network's closed-loop
    Archival Tracking Data Files (ATDF) structured according to DSN's TRK-2-25 interface. To meet the evolution of
    the radio science subsystem, the DSN deprecated the ATDF format in the early 2000s and replaced it with the
    TNF TRK-2-34 format. All ATDF formatted files archived since 1986 can be preprocessed with this script.

INPUTS:
    1.  -i     input_file     :-  Path to the input ATDF file.
    2.  -o     output_dir     :-  Path to the output directory.
    3.  -c     [count_time]   :-  The count time , in sec, to which the Doppler measurements are to be compressed.
                                  A comma-separated multiple input can be provided, for example, 10, 60.
                                  ATDF's original compression value will be used by default.
    4.  -p     [proc_count]   :-  The number of available processors. Default uses half the cores available.                            
    5. [--xd1]                :-  Use this option to exclude 1-way Doppler measurements (if present).
    6. [--xd2]                :-  Use this option to exclude 2-way Doppler measurements (if present).
    7. [--xd3]                :-  Use this option to exclude 2-way Doppler measurements (if present).
    8. [--xr1]                :-  Use this option to exclude 1-way Range measurements (if present).
    9. [--xr2]                :-  Use this option to exclude 2-way Range measurements (if present).
                                
OUTPUT:
    1. Two ASCII files containing Doppler, range, ramp, and ancillary data
   
REQUIREMENTS:
    1. Python 3.6.5 or above

AUTHOR  
        
   Dr. Ashok Kumar Verma (1,2)
   1. Department of Earth, Planetary, and Space Sciences
      University of California, Los Angeles, 90095, CA, USA.
   2. NASA Goddard Space Flight Center, Greenbelt, 20771, MD, USA.
   
   Contact: ashokkumar.verma@nasa.gov

"""
import optparse
import os
import sys
import traceback
from io import StringIO

import Header as hd
import Reader as rd
import functions as fn
from Doppler import Doppler
from Ramp import Ramp
from Range import Range


# -------------------------------------------------------------------------------------------------------------------
# read all bytes
def bytes_from_file(filename: str,
                    chunk_size: int = 288):
    """
    Reads all bytes from the file and split them according to the chuck size.
    Args:
        filename: Path to the input ATDF file.
        chunk_size (optional): Size of the chunk.
    """
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            yield chunk


# -------------------------------------------------------------------------------------------------------------------
def print_header_info(chunks_list: list,
                      count_time: list,
                      doppler_two_way: bool,
                      doppler_one_way: bool,
                      doppler_three_way: bool,
                      range_two_way: bool,
                      range_one_way: bool):
    """
    Print brief overview of the ATDF file.
    Args:
        chunks_list: The list of bytes where each element is 288 bytes long.
        count_time : The count time.
        doppler_two_way: Boolean flag to indicate include or exclude 2-Way Doppler measurements.
        doppler_one_way: Boolean flag to indicate include or exclude 1-Way Doppler measurements.
        range_two_way: Boolean flag to indicate include or exclude 2-Way Range measurements.
        range_one_way: Boolean flag to indicate include or exclude 1-Way Range measurements.

    Returns:

    """
    # read all options
    global options
    
    # read header
    hdr = hd.header(chunks_list)
    
    # transponder frequency
    transponder_freq = hdr['spacecraft_transponder_frequency_hp'] * 1e4 + \
                       hdr['spacecraft_transponder_frequency_lp'] * 1e-3
    
    # start time in header
    start_time_hdr = fn.get_date(1900 + hdr['s_year'], hdr['s_doy'], hdr['s_hr'], hdr['s_mn'], hdr['s_sc'])
    
    # end time in header
    end_time_hdr = fn.get_date(1900 + hdr['e_year'], hdr['e_doy'], hdr['e_hr'], hdr['e_mn'], hdr['e_sc'])
    
    # sc id
    sc_id = hdr['sc_id']
    
    # time of the last observation
    start_time_obs, end_time_obs = rd.get_all_items(chunks_list, options.proc_count, True)
    if start_time_obs is None: start_time_obs = start_time_hdr
    if end_time_obs is None: end_time_obs = end_time_hdr
    
    msg = '=' * 90 + '\n'
    msg = msg + "{:>40}   :  {:<35}\n".format('Spacecraft ID', sc_id)
    msg = msg + "{:>40}   :  {:<35}\n".format('Transponder Freq [Hz]', transponder_freq)
    msg = msg + "{:>40}   :  {:<35}\n".format('Input Count time [sec]', str(count_time))
    msg = msg + "{:>40}   :  {:<35}\n".format('File Start Time', start_time_obs)
    msg = msg + "{:>40}   :  {:<35}\n".format('File End Time', end_time_obs)
    msg = msg + "{:>40}   :  {:<35}\n".format('1-Way Doppler', str(doppler_one_way))
    msg = msg + "{:>40}   :  {:<35}\n".format('2-Way Doppler', str(doppler_two_way))
    msg = msg + "{:>40}   :  {:<35}\n".format('3-Way Doppler', str(doppler_three_way))
    msg = msg + "{:>40}   :  {:<35}\n".format('1-Way Range', str(range_one_way))
    msg = msg + "{:>40}   :  {:<35}\n".format('2-Way Range', str(range_two_way))
    msg = msg + '=' * 90 + '\n'
    
    fn.color_txt(msg, 'magenta')
    return transponder_freq, end_time_obs


# -------------------------------------------------------------------------------------------------------------------
# main function
def main(doppler_one_way: bool,
         doppler_two_way: bool,
         doppler_three_way : bool,
         range_one_way: bool,
         range_two_way: bool):
    """

    Args:
        doppler_one_way: Boolean flag to indicate include or exclude 1-Way Doppler measurements.
        doppler_two_way: Boolean flag to indicate include or exclude 2-Way Doppler measurements.
        range_one_way: Boolean flag to indicate include or exclude 1-Way Range measurements.
        range_two_way: Boolean flag to indicate include or exclude 2-Way Range measurements.
    """
    # read all options
    global options
    count_time = options.count_time
    ts = fn.time_now()
    
    # output directory
    out_dir = os.path.abspath(options.output_dir)
    if not os.path.exists(out_dir):
        try:
            os.mkdir(out_dir)
        except Exception:
            raise OSError("\n\nCan't create output directory (%s)!" % out_dir)
    
    # input and output files
    input_file = options.input_file.strip()
    out_file = input_file.split("/")[-1]
    out_file = out_dir + "/" + out_file.split(".")[0]
    
    # open output files
    out_obs = open(out_file + ".msr", "w")
    out_ramp = open(out_file + ".ramp", "w")
    
    # read all bytes
    all_bytes = bytes_from_file(input_file)
    
    # get list of chunks
    chunks_list = list(all_bytes)
    
    # get header info
    transponder_freq, end_date = print_header_info(chunks_list, count_time, doppler_two_way,
                                                   doppler_one_way, doppler_three_way,
                                                   range_two_way, range_one_way)
    
    # unpack rest of data
    unpacked_data = rd.get_all_items(chunks_list, options.proc_count)
    
    # extract and write ramp records
    last_ramps = Ramp(unpacked_data.ramp, out_ramp, end_date).ramp_table()
    out_ramp.close()
    
    # read ramp data
    ramp_data = open(out_file + ".ramp",'rt').readlines()[:-1*last_ramps]

    # extract and write 1-Way Doppler records, if present and requested
    if doppler_one_way and len(unpacked_data.doppler1way):
        Doppler(unpacked_data.doppler1way, transponder_freq, 1, count_time, out_obs, ramp_data).doppler_table()
    
    # extract and write 2-Way Doppler records, if present and requested
    if doppler_two_way and len(unpacked_data.doppler2way):
        Doppler(unpacked_data.doppler2way, transponder_freq, 2, count_time, out_obs, ramp_data).doppler_table()

    # extract and write 3-Way Doppler records, if present and requested
    if doppler_three_way and len(unpacked_data.doppler3way):
        Doppler(unpacked_data.doppler3way, transponder_freq, 3, count_time, out_obs, ramp_data).doppler_table()
    
    # extract and write 1-Way range records
    if range_one_way and len(unpacked_data.range1way):
        Range(unpacked_data.range1way, 1, out_obs).range_table()
    
    # extract and write 2-Way range records
    if range_two_way and len(unpacked_data.range2way):
        Range(unpacked_data.range2way, 2, out_obs).range_table()
    
    # close output files
    out_obs.close()
    
    # print output file location and total time Taken
    fn.color_txt('=' * 90, 'magenta')
    fn.color_txt("\n\t\t\tOutput files:"
                 "\n\t\t\t\t Measurement File: %s.msr"
                 "\n\t\t\t\t Ramp File: %s.ramp" % (out_file, out_file), 'magenta')
    fn.color_txt("\n\t\t\tTotal %s" % fn.time_dif(ts, fn.time_now()), 'magenta')
    fn.color_txt('=' * 90 + '\n', 'magenta')


# -------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'])
        parser.add_option('-i', '--input_file', action='store', default='', help='Path to the ATDF data file.')
        parser.add_option('-o', '--output_dir', action='store', default='./outputs',
                          help='Path to the output directory.')
        parser.add_option('-c', '--count_time', action='store', default=None, help='The count time, in sec, to which '
                                                                                   'the Doppler measurements are to be'
                                                                                   "compressed. ATDF's original "
                                                                                   "compression "
                                                                                   "value is used by default.")
        parser.add_option('-p', '--proc_count', action='store', default='',
                          help='The number of available processors. Default uses half the cores available.')
        parser.add_option('--xd1', '', action='store_false', default=False,
                          help="Use this option to exclude 1-way Doppler measurements (if present)")
        parser.add_option('--xd2', '', action='store_false', default=False,
                          help="Use this option to exclude 2-way Doppler measurements (if present)")
        parser.add_option('--xd3', '', action='store_false', default=False,
                          help="Use this option to exclude 3-way Doppler measurements (if present)")
        parser.add_option('--xr1', '', action='store_false', default=False,
                          help="Use this option to exclude 1-way range measurements (if present)")
        parser.add_option('--xr2', '', action='store_false', default=False,
                          help="Use this option to exclude 2-way range measurements (if present)")
        
        (options, args) = parser.parse_args()
        
        optionKeys = ["-i", "-o", "-c", "-p", "--xd1", "--xd2", "--xd3", "--xr1", "--xr2"]
        
        if options.count_time is not None:
            count_time = []
            for i in range(len(sys.argv)):
                if "-c" == sys.argv[i]:
                    for j in range(i + 1, len(sys.argv)):
                        if sys.argv[j] in optionKeys:
                            break
                        else:
                            count_time.append(sys.argv[j])
            count_time = ''.join(count_time).split(",")
            options.count_time = [float(c) for c in count_time]
        
        doppler_one_way = True
        doppler_two_way = True
        doppler_three_way = True
        range_one_way = True
        range_two_way = True
        for key in sys.argv:
            if "--xd1" in key: doppler_one_way = False
            if "--xd2" in key: doppler_two_way = False
            if "--xd3" in key: doppler_three_way = False
            if "--xr1" in key: range_one_way = False
            if "--xr2" in key: range_two_way = False
        
        if not doppler_one_way and not doppler_two_way and not \
                doppler_three_way and not range_two_way and not \
                range_one_way:
            fn.raise_error("None of the measurement type(s) is(are) requested. See run.py -h command for all options.")
        
        if options.input_file:
            if not os.path.exists(options.input_file):
                fn.raise_error("The path specified for the file '%s' is not valid." % options.input_file)
        else:
            fn.raise_error("The input ATDF file is missing (use -h for help)")
        
        main(doppler_one_way, doppler_two_way, doppler_three_way,
             range_one_way, range_two_way)
        sys.exit()
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:  # sys.exit()
        raise e
    except Exception as e:
        fn.color_txt('\nERROR, UNEXPECTED EXCEPTION\n', 'red')
        error = StringIO()
        sys.stderr = error
        traceback.print_exc()
        fn.color_txt(str(error.getvalue()), 'red')
        sys.modules[__name__].__dict__.clear()
        raise SystemExit()
