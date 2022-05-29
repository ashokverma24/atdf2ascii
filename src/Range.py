""" 

Range class

Using range information from the ATDF file, this class builds and outputs One-Way-Range
and Two-Way-Range observables in Ascii format.

AUTHOR: 
        
   Dr. Ashok Kumar Verma (1,2)
   1. Department of Earth, Planetary, and Space Sciences
      University of California, Los Angeles, 90095, CA, USA.
   2. NASA Goddard Space Flight Center, Greenbelt, 20771, MD, USA.
   
   Contact: ashokkumar.verma@nasa.gov

"""

import functions as fn


# ===========================================================================
def get_ref_freq(rec: dict):
    """

    Args:
        rec: The Range record.

    Returns: Reference frequency

    """
    freq = rec['doppler_ref_freq']
    ul = rec['uplink_band']
    dl = rec['dnlink_band']
    stn = rec['station']
    rcvr_type = rec['doppler_rcvr_type']
    
    band = fn.msr_band(freq)
    if band == dl: return freq
    
    # get frequency multiplier
    fac = fn.get_mul_fac(freq)
    if fac == 0:
        msg = "\nInvalid reference frequency, %s MHz, at time %s for RANGE msr.\n Expected around 22MHz.\n" \
              + "Skipping this record.\n"
        fn.raise_warning(msg % (freq / fn.MHz, rec['time_tag']))
        return False
    freq = freq / fac
    
    # S-band uplink frequency
    if ul == "S":
        freq = 96.0 * freq
    
    # X-band frequency
    elif ul == "X":
        if stn in ['15', '45', '65'] and rcvr_type != 5:
            freq = 4.68125 * freq - 81.4125e6
        freq = 32.0 * freq + 6.5e9
    
    # for Ka band
    elif ul == "Ka":
        ref_freq = 1000.0 * freq + 1e10
    
    # for all other bands
    else:
        msg = '=' * 80 + \
              '\n~*~*~ The given reference frequency is not at the sky level ~*~*~' \
              '\nAt the moment, program is unable to compute the sky frequency at:' \
              '\nTime Tag: %s UTC' \
              '\nStation: DSS %s' \
              '\nUplink Band: %s' \
              '\nReference Freq: %s Hz\n' + '=' * 80
        fn.raise_warning(msg % (rec['time_tag'], rec['station'], ul, rec['doppler_ref_freq']))
        return False
    
    return freq


def sec_to_ru(band: str,
              freq: float,
              stn: str,
              rcvr_type: int) -> float:
    """

    Args:
        band: The band of the signal.
        freq: The frequency of the signal.
        stn: The DSN station.
        rcvr_type: Type of the DSN station.

    Returns: value in range unit

    """
    if band == 'S':
        return 0.5 * freq
    if band == 'X':
        if stn in ['15', '45', '65'] and rcvr_type != 5:
            return (11 / 75) * freq
        else:
            return (221 / (749 * 2)) * freq


class Range:
    """
    
    Using range information from the ATDF file, this class builds and outputs One-Way-Range
    and Two-Way-Range observables in Ascii format.

    """
    
    # -----------------------------------------------------------------------
    def __init__(self, range_recs: dict,
                 dtype: int,
                 out_file: str):
        
        """
        
        Args:
            range_recs: The range record.
            dtype: Data type.
            out_file: Path to the output file.
            
        """
        self.recs = range_recs
        self.out_file = out_file
        self.data_type = dtype
    
    # -----------------------------------------------------------------------
    def data_type_name(self):
        """
        Convert int data type to string.
        Returns: String value of the data type.

        """
        if self.data_type == 1: return '1-Way-Range'
        if self.data_type == 2: return '2-Way-Range'
    
    # -----------------------------------------------------------------------
    def create_msr(self, rec):
        """
        Write observables into ascii table.
        
        Args:
            rec: The range record.

        """
        # get uplink and downlink bands
        uplink_band = rec['uplink_band']
        dnlink_band = rec['dnlink_band']
        
        # get average delays
        sc_delay = rec['sc_delay']
        xmtr_delay = rec['exciter_stn_delay']
        rcvr_delay = rec['rcvr_stn_delay']
        
        # get station
        rcvr = fn.is_dsn_valid(rec, data_type=self.data_type_name())
        if rcvr is None:
            return
        else:
            rcvr = 'DSS %s' % (rcvr)
            xmtr = rcvr
        
        # get time
        time_tag = rec['time_tag']
        
        # get calibration delay
        C = rec['range_equp_delay']
        
        # low range component, for SRA
        rng_cm_l = rec['lwt_rng_component']
        
        # get reference frequency
        # -- get exciter band if reference freq. is given at the sky level
        rcvr_exciter_band = fn.msr_band(rec['doppler_ref_freq'])
        
        # -- get exciter band if reference freq. is not given at the sky level
        if rcvr_exciter_band is None:
            # -- get exciter band if turnaround ratio is given
            if rec["turnaround_ratio_num"] != 0 and rec["turnaround_ratio_den"] != 0:
                rcvr_exciter_band = fn.find_exciter_band(rec["turnaround_ratio_num"] / rec["turnaround_ratio_den"])
            
            # -- if turnaround ratio is not given, set exciter band to uplink band
            else:
                rcvr_exciter_band = uplink_band
            
            # -- compute reference freq. if not given at the sky level
            ref_freq = get_ref_freq(rec)
        else:
            # -- get reference freq. if given at the sky level
            ref_freq = rec['doppler_ref_freq']
        
        if ref_freq:
            # get Z-correction in RU
            Z = rec['z_correction'] * sec_to_ru(rcvr_exciter_band, ref_freq, rec['station'], rec['doppler_rcvr_type'])
            
            # get observed value
            observed = rec['range'] - C + Z - sc_delay * sec_to_ru(rcvr_exciter_band, ref_freq, rec['station'],
                                                                   rec['doppler_rcvr_type'])
            
            if self.data_type == 1:
                xmtr = "S/C"
            
            self.out_file.write(
                "%27s, %15s, %5s, %10s, %10s, %5s, %5s, %5s, %5s, %10s, %10s, %25.10f, %25.10f, %15.6f, %15.6f, "
                "%15.6f\n" \
                % (time_tag,
                   self.data_type_name(),
                   rec['sc_id'],
                   xmtr,
                   rcvr,
                   rec['channel_number'],
                   uplink_band,
                   dnlink_band,
                   rcvr_exciter_band,
                   rec['count_time'],
                   rng_cm_l,
                   observed,
                   ref_freq,
                   xmtr_delay * fn.sec2nanosec,
                   rcvr_delay * fn.sec2nanosec,
                   sc_delay * fn.sec2nanosec,
                   )
            )
    
    # -----------------------------------------------------------------------
    def range_table(self):
        """

        Converts binary Range records into ascii table.
        
        """
        # get all range records
        size = len(self.recs)
        if size > 0:
            
            # set update progress
            umsg = "Extracting %s  " % (self.data_type_name())
            prog = fn.progressBar()
            prog.start(1, umsg)

            # write a header of the output file.
            self.out_file.write(
                "%s %25s, %15s, %5s, %10s, %10s, %5s, %5s, %5s, %5s, %10s, %10s, %25s, %25s, %15s, %15s, %15s\n" \
                % ("#", "time_tag (UTC)", "Data Type", "scID", "Xmtr", "Rcvr", "Chnl", "UL", "DL", "Ex", "CT (sec)",
                   "Rng-LC", "Observed (RU)", "Ref-Freq (Hz)", "XmtrDly (nsec)", "RcvrDly (nsec)", "ScDly (nsec)"))

            # loop through every record
            i = 0
            for rec in self.recs:
                self.create_msr(rec)
                prog.setStep(i / size)
                i += 1
            prog.stop()
        
        # ===========================================================================
