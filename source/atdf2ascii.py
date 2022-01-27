""" 
USAGE    

    python atdf2ascii.py [-h,--help] 
    python atdf2ascii.py -i input_file [options...]
    
DESCRIPTION

    This script can be used to read and write the content of the Archival Tracking Data File (ATDF).

INPUTS:
    1.  -i     input_file     :-  Path to the input ATDF file.
    2.  -c     [count_time]   :-  The count time , in sec, to which the Doppler measurements are to be compressed.
                                  A comma-separated multiple input can be provided, for example, 10, 60.
                                  ATDF's original compression value is used by default.
    3.  -p     [proc_count]   :-  The number of available processors. Default uses half the cores available.                            
    4. [--xd1]                :-  Use this option to exclude 1-way Doppler measurements (if present).
    5. [--xd2]                :-  Use this option to exclude 2-way Doppler measurements (if present).
    6. [--xr2]                :-  Use this option to exclude 2-way Range measurements (if present).
                                
OUTPUT:
    1. ASCII files containing Doppler, range, and ramp data    
   
REQUIREMENTS:
    1. Python 3.6.5 or above

AUTHOR  
        
   Ashok Verma (ashokverma@ucla.edu)
   Department of Earth, Planetary, and Space Sciences
   University of California, Los Angeles

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
def bytes_from_file(filename, chunk_size=288):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            yield chunk


# -------------------------------------------------------------------------------------------------------------------
def print_header_info(hdr, count_time, doppler_two_way, doppler_one_way, range_two_way):
    transponder_freq = hdr['spacecraft_transponder_frequency_hp'] * 1e4 + \
                       hdr['spacecraft_transponder_frequency_lp'] * 1e-3
    start = fn.get_date(1900 + hdr['s_year'], hdr['s_doy'], hdr['s_hr'], hdr['s_mn'], hdr['s_sc'])
    end = fn.get_date(1900 + hdr['e_year'], hdr['e_doy'], hdr['e_hr'], hdr['e_mn'], hdr['e_sc'])
    sc_id = hdr['sc_id']
    
    msg = '=' * 90 + '\n'
    msg = msg + "{:>40}   :  {:<35}\n".format('Spacecraft ID',sc_id)
    msg = msg + "{:>40}   :  {:<35}\n".format('Transponder Freq [Hz]',transponder_freq)
    msg = msg + "{:>40}   :  {:<35}\n".format('Input Count time [sec]',str(count_time))
    msg = msg + "{:>40}   :  {:<35}\n".format('File Start Time',start)
    msg = msg + "{:>40}   :  {:<35}\n".format('File End Time',end)
    msg = msg + "{:>40}   :  {:<35}\n".format('1-Way Doppler',str(doppler_one_way))
    msg = msg + "{:>40}   :  {:<35}\n".format('2-Way Doppler',str(doppler_two_way))
    msg = msg + "{:>40}   :  {:<35}\n".format('2-Way Range',str(range_two_way))
    msg = msg + '=' * 90 + '\n'

    
    fn.color_txt(msg, 'magenta')
    return transponder_freq


# -------------------------------------------------------------------------------------------------------------------
# main function
def main(doppler_one_way, doppler_two_way, range_one_way, range_two_way):

    # read all options
    global options
    count_time = options.count_time
    ts = fn.time_now()
    
    # output directory
    out_dir = 'outputs/'
    if not os.path.exists(out_dir): os.mkdir(out_dir)
    # input and output files
    input_file = options.input_file.strip()
    out_file = input_file.split("/")[-1]
    out_file = out_dir + out_file.split(".")[0]
    
    # open output files
    out_obs = open(out_file + ".msr", "w")
    out_ramp = open(out_file + ".ramp", "w")
    
    # read all bytes
    all_bytes = bytes_from_file(input_file)
    
    # get list of chunks
    chunks_list = list(all_bytes)
    
    # read header
    hdr_dict = hd.header(chunks_list)
    
    # get header info
    transponder_freq = print_header_info(hdr_dict, count_time, doppler_two_way, doppler_one_way, range_two_way)
    
    # unpack rest of data
    unpacked_data = rd.get_all_items(chunks_list, options.proc_count)

    # extract and write ramp records
    Ramp(unpacked_data.ramp, out_ramp).ramp_table()
    
    # extract and write 1-Way Doppler records, if present and requested
    if doppler_one_way and len(unpacked_data.doppler1way):
        Doppler(unpacked_data.doppler1way, transponder_freq, 1, count_time, out_obs).doppler_table()
    
    # extract and write 2-Way Doppler records, if present and requested
    if doppler_two_way and len(unpacked_data.doppler2way):
        Doppler(unpacked_data.doppler2way, transponder_freq, 2, count_time, out_obs).doppler_table()
    
    # extract and write 1-Way range records
    if range_one_way and len(unpacked_data.range1way): 
       Range(unpacked_data.range1way, 1, out_obs).range_table()

    # extract and write 2-Way range records
    if range_two_way and len(unpacked_data.range2way):
       Range(unpacked_data.range2way, 2, out_obs).range_table()

    
    # close output files
    out_ramp.close()
    out_obs.close()
    
    # total time Taken
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
        parser.add_option('-c', '--count_time', action='store', default=None, help='The count time, in sec, to which '
                                                                                   'the Doppler measurements are to be'
                                                                                   "compressed. ATDF's original compression"
                                                                                   "value is used by default.")
        parser.add_option('-p', '--proc_count', action='store', default='',
                          help='The number of available processors. Default uses half the cores available.')
        parser.add_option('--xd1', '', action='store_false', default=False,
                          help="Use this option to exclude 1-way Doppler measurements (if present)")
        parser.add_option('--xd2', '', action='store_false', default=False,
                          help="Use this option to exclude 2-way Doppler measurements (if present)")
        parser.add_option('--xr1', '', action='store_false', default=False,
                          help="Use this option to exclude 1-way range measurements (if present)")
        parser.add_option('--xr2', '', action='store_false', default=False,                       
                          help="Use this option to exclude 2-way range measurements (if present)")
        
        (options, args) = parser.parse_args()

        optionKeys = ["-i", "-c", "-p", "--xd1", "--xd2", "--xr1", "--xr2"]

        if options.count_time is not None:
           count_time = []
           for i in range (len(sys.argv)):
               if "-c" == sys.argv[i]: _c = i
           for i in range (_c+1, len(sys.argv)):
                  if sys.argv[i] in optionKeys: break
                  else: count_time.append(sys.argv[i])
           count_time = ''.join(count_time).split(",")
           options.count_time = [float(c) for c in count_time]

        doppler_one_way = True
        doppler_two_way = True
        range_one_way = True
        range_two_way = True
        for key in sys.argv:
            if "--xd1" in key: doppler_one_way = False
            if "--xd2" in key: doppler_two_way = False
            if "--xr1" in key: range_one_way = False
            if "--xr2" in key: range_two_way = False
        
        if not doppler_one_way and not doppler_two_way and not range_two_way:
            fn.raise_error("None of the measurement type(s) is(are) requested. See run.py -h command for all options.")
        
        if options.input_file:
            if not os.path.exists(options.input_file):
                fn.raise_error("The path specified for the file '%s' is not valid." % options.input_file)
        else:
            fn.raise_error("The input ATDF file is missing (use -h for help)")
        
        main(doppler_one_way, doppler_two_way, 
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
