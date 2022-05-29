""" 

Doppler class

Using phase count information from the ATDF file, this class builds and outputs One-Way-Doppler,
Two-Way-Doppler, and Three-Way-Doppler observables in Ascii format.

AUTHOR:

   Dr. Ashok Kumar Verma (1,2)
   1. Department of Earth, Planetary, and Space Sciences
      University of California, Los Angeles, 90095, CA, USA.
   2. NASA Goddard Space Flight Center, Greenbelt, 20771, MD, USA.
   
   Contact: ashokkumar.verma@nasa.gov

"""

import functions as fn
import numpy as np

# ===========================================================================
from functions import dic_attrs


def store_record(rec: dict,
                 next_rec_at: str,
                 count_time: float) -> dic_attrs:
    """
    Save current record in the dictionary.
    
    Args:
        rec: The record to save.
        next_rec_at: The expected time of the next record.
        count_time: The count time.

    Returns: Data dictionary.

    """
    data = fn.dic_attrs(rec=None, next_rec_at=None, count_time=None)
    data.rec = rec
    data.next_rec_at = next_rec_at
    data.count_time = count_time
    
    return data


# ===========================================================================
class Doppler:
    """
    Using phase count information from the ATDF file, this class builds and outputs One-Way-Doppler
    and Two-Way-Doppler observables in Ascii format.
    
    """
    
    # -----------------------------------------------------------------------
    def __init__(self, doppler_recs: list,
                 transponder_freq: float,
                 dtype: int,
                 count_time: float,
                 out_file: object,
                 ramp_data: list):
        """
        
        Args:
            doppler_recs: List of Doppler records.
            transponder_freq: Transponder frequency.
            dtype: Data type.
            count_time: The count time.
            out_file: Path to the output file.
        """
        self.recs = doppler_recs
        self.data_type = dtype
        self.count_time = count_time
        self.transponder_freq = transponder_freq
        self.out_file = out_file
        self.ramp_band = None
        self.ramp_xmtr = None
        self.ramp_end = None
        self.ramp_start = None
        self.read_ramp(ramp_data)
    
    # -----------------------------------------------------------------------
    def read_ramp(self, ramp_data: str):
        """
        Read ramp data to get transmitter for 3-Way Doppler.

        Args:
            out_file: Path to the output file.

        """

        if not len(ramp_data): return 
        try:
           data = np.loadtxt(ramp_data, dtype=str, delimiter=',', ndmin=2)
           self.ramp_start = np.array([fn.str2datetime(d.strip()) for d in data[:, 0]])
           self.ramp_end = np.array([fn.str2datetime(d.strip()) for d in data[:, 1]])
           self.ramp_xmtr = np.array([d.strip() for d in data[:, 2]])
           self.ramp_band = np.array([d.strip() for d in data[:, 3]])
        except Exception as e: 
           msg = 'Unable to read data from ramp file:\nRamp file : %s\n' % ramp_file
           fn.raise_warning(msg)
    
    # -----------------------------------------------------------------------
    def get_xmtr(self, time_tag: str,
                 band: str,
                 stn: str):
        
        stn = 'DSS %s' % stn
        
        # for 1-Way
        if self.data_type == 1: return "S/C"
        
        # for 2-Way
        if self.data_type == 2: return stn
        
        # for 3-Way
        # get transmitter station, if time tag falls between start and end time,
        # and uplink band equals to the ramp band, and rcvr not equal to xmtr.
        if self.ramp_start is None or self.ramp_end is None or \
                self.ramp_band is None or self.ramp_xmtr is None: return None
        map = (time_tag >= self.ramp_start) & (time_tag < self.ramp_end) & \
              (self.ramp_band == band) & (self.ramp_xmtr != stn)
        xmtr = self.ramp_xmtr[map]
        
        if xmtr.size: return xmtr[0]
        return None
    
    # -----------------------------------------------------------------------
    def convert(self, rec: dict,
                start_doppler: dict,
                count_time: float) -> dict:
        """
        This function checks and stores new start record for each station according to
        uplink and downlink bands. If start record already exists, then it converts records
        to the observables and replace start record with the current record.
       
        Args:
            rec: The ith Doppler record.
            start_doppler: The start record of the Doppler.
            count_time: The count time.

        Returns: Updated record of Doppler

        """
        
        # getting time tag, station and band records.
        time_tag = fn.str2datetime(rec['time_tag'])
        station = fn.is_dsn_valid(rec, data_type=self.data_type_name())
        ul = rec['uplink_band']
        dl = rec['dnlink_band']
        
        # return if invalid DSN station encounters
        if station is None: return start_doppler
        
        # get transmitter
        xmtr = self.get_xmtr(time_tag, ul, station)
        if xmtr is None: return start_doppler
        
        # creating record key according to the DSN station
        # unlink- and downlink-band.
        rec_key = station + ul + dl
        
        # store start record as the former record
        former_rec = start_doppler[rec_key]
        
        # check count time units
        if count_time >= 1.0 and former_rec.rec is None:
            ms = time_tag.microsecond
            sec = time_tag.second
        
        # store record if no previous record found for the record key
        if former_rec.rec is None:
            next_rec_at = fn.add_time(time_tag, sec=count_time, dtType=True)
            former_rec = store_record(rec, next_rec_at, count_time)
            start_doppler.update({rec_key: former_rec})
            return start_doppler
        
        # convert records to observables if former record is not None
        # and all other conditions are also met.
        if time_tag == former_rec.next_rec_at and \
                station == former_rec.rec['station'] and \
                ul == former_rec.rec['uplink_band'] and \
                dl == former_rec.rec['dnlink_band'] and \
                rec['channel_number'] == former_rec.rec['channel_number']:
            self.write_msr(former_rec, rec, station, xmtr, count_time)
            next_rec_at = fn.add_time(time_tag, sec=count_time, dtType=True)
            former_rec = store_record(rec, next_rec_at, count_time)
            start_doppler.update({rec_key: former_rec})
            return start_doppler
        
        # if time tag is not as expected then reset the former records.
        if time_tag > former_rec.next_rec_at:
            former_rec = store_record(None, None, None)
            start_doppler.update({rec_key: former_rec})
            return start_doppler
        
        return start_doppler
    
    # -----------------------------------------------------------------------
    def get_ref_freq(self, rec: dict):
        """

        Args:
            rec: The Doppler record.

        Returns: Reference frequency

        """
        freq = rec['doppler_ref_freq']
        ul = rec['uplink_band']
        dl = rec['dnlink_band']
        stn = rec['station']
        rcvr_type = rec['doppler_rcvr_type']
        
        # get frequency multiplier
        fac = fn.get_mul_fac(freq)
        if fac == 0:
            msg = "\nInvalid reference frequency, %s MHz, at time %s.\n Expected around 22MHz.\n" \
                  + "Skipping this record.\n"
            fn.raise_warning(msg % (freq / fn.MHz, rec['time_tag']))
            return False
        
        freq = freq / fac
        
        # for 1-way Doppler
        if self.data_type == 1:
            
            if freq > 22e6:
                ul = 'S'
            else:
                ul = dl
        
        # S-band uplink frequency
        # Moyer, Equation 13-1, section 13.2.1)
        if ul == "S":
            ref_freq = 96.0 * freq
        
        # X-band frequency
        # Moyer, Equation 13-2/4, section 13.2.1)
        elif ul == "X":
            if stn in ['15', '45', '65'] and rcvr_type != 5:
                freq = 4.68125 * freq - 81.4125e6
            ref_freq = 32.0 * freq + 6.5e9
        
        # for Ka band
        elif ul == "Ka":
            ref_freq = 1000.0 * freq + 1e10
        
        # for all others band
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
        
        return ref_freq
    
    # -----------------------------------------------------------------------
    def data_type_name(self):
        """
        Convert int data type to string.
        Returns: String value of the data type.

        """
        if self.data_type == 1: return '1-Way-Doppler'
        if self.data_type == 2: return '2-Way-Doppler'
        if self.data_type == 3: return '3-Way-Doppler'
    
    # -----------------------------------------------------------------------
    def write_msr(self,
                  former_rec: dict,
                  rec: dict,
                  rcvr: str,
                  xmtr: str,
                  count_time: float):
        """
        Write observables into ascii table.
        Args:
            former_rec: The Doppler record.
            rec: The current Doppler record.
            rcvr: The name of the receiver.
            xmtr: The name of the transmitter.
            count_time: The count time.

        """
        # get uplink and downlink bands
        uplink_band = rec['uplink_band']
        dnlink_band = rec['dnlink_band']
        
        # get average delays
        sc_delay = 0.5 * (rec['sc_delay'] + former_rec.rec['sc_delay'])
        xmtr_delay = rec['exciter_stn_delay']
        rcvr_delay = rec['rcvr_stn_delay']
        
        # get average doppler bias (Moyer, Equation 13-22, section 13.3.1)
        C4 = rec['doppler_bias']
        
        # get doppler shift
        doppler_count_t2 = rec['doppler_count']
        doppler_count_t1 = former_rec.rec['doppler_count']
        
        # get change in the doppler cycles which accumulates during the count interval
        # (Moyer, first part of the right-hand Equation 13-26, DeltaN/Tc)
        delta_n_tc = (doppler_count_t2 - doppler_count_t1) / count_time
        
        # get middle time of two doppler counts 
        time_tag = fn.add_time(fn.str2datetime(former_rec.rec['time_tag']), sec=count_time * 0.5)
        
        # get reference frequency
        # -- get exciter band if reference freq. is given at the sky level
        rcvr_exciter_band = fn.msr_band(rec['doppler_ref_freq'])
        
        if rcvr_exciter_band is not None:
            # -- get reference freq. if given at the sky level.
            ref_freq = rec['doppler_ref_freq']
        # -- get exciter band if reference freq. is not given at the sky level.
        else:
            # -- get exciter band if turnaround ratio is given
            if rec["turnaround_ratio_num"] != 0 and rec["turnaround_ratio_den"] != 0:
                rcvr_exciter_band = fn.find_exciter_band(rec["turnaround_ratio_num"] / rec["turnaround_ratio_den"])
            
            # -- if turnaround ratio is not given, set exciter band to uplink band.
            else:
                rcvr_exciter_band = uplink_band
            
            # -- compute reference freq. if not given at the sky level.
            ref_freq = self.get_ref_freq(rec)
        
        f_bias = 0
        if ref_freq:
            # get frequency bias (Moyer, Equation 13-28, section 13.3.1)
            if self.data_type == 1:
                f_bias = 0
                C2 = fn.c_2(dnlink_band)
                M2 = fn.m_2(fn.msr_band(ref_freq), dnlink_band)
                f_bias = M2 * ref_freq - C2 * self.transponder_freq + C4
                ref_freq = self.transponder_freq
            else:
                f_bias = C4
            
            if not abs(delta_n_tc): return
            
            # get doppler observables (Moyer, Equation 13-26)
            observed = delta_n_tc - abs(f_bias)
            if C4 != 0.0: observed = C4 / abs(C4) * observed
            
            # corrections, in the case of a modulo reset
            reset = round(observed * count_time / 2 ** 32)
            if reset:
                if observed > 0:
                    observed = observed - 2 ** 32 / count_time
                else:
                    observed = observed + 2 ** 32 / count_time
            
            # write output
            rcvr = 'DSS %s' % rcvr
            if count_time == former_rec.count_time:
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
                       count_time,
                       rec['lwt_rng_component'],
                       observed,
                       ref_freq,
                       xmtr_delay * fn.sec2nanosec,
                       rcvr_delay * fn.sec2nanosec,
                       sc_delay * fn.sec2nanosec,
                       )
                )
    
    # -----------------------------------------------------------------------
    def doppler_table(self):
        """
        
        Converts binary Doppler records into ascii table.
        
        """
        
        # set empty start record
        start_doppler = fn.rec_dict(
            fn.dic_attrs(rec=None,
            next_rec_at=None,
            count_time=None,))
        
        # get all doppler records
        size = len(self.recs)
        if size > 0:
            
            # set update progress
            umsg = "Extracting %s" % (self.data_type_name())
            prog = fn.progressBar()
            prog.start(1, umsg)
            
            # write a header of the output file.
            self.out_file.write(
                "%s %25s, %15s, %5s, %10s, %10s, %5s, %5s, %5s, %5s, %10s, %10s, %25s, %25s, %15s, %15s, %15s\n" \
                % ("#", "time_tag (UTC)", "Data Type", "scID", "Xmtr", "Rcvr", "Chnl", "UL", "DL", "Ex", "CT (sec)",
                   "Rng-LC", "Observed (Hz)", "Ref-Freq (Hz)", "XmtrDly (nsec)", "RcvrDly (nsec)", "ScDly (nsec)"))
            
            # loop through every record.
            i = 0
            for rec in self.recs:
                
                # set count time.
                if self.count_time is None:
                    count_time = rec['count_time']
                else:
                    if rec['count_time'] in self.count_time:
                        count_time = rec['count_time']
                    else:
                        count_time = self.count_time[-1]
                
                start_doppler = self.convert(rec, start_doppler, count_time)
                prog.setStep(i / size)
            prog.stop()
        
        # ===========================================================================
