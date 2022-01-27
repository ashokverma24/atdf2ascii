""" 

Range class

AUTHOR: 
        
   Ashok Verma (ashokverma@ucla.edu)
   Department of Earth, Planetary, and Space Sciences
   University of California, Los Angeles

"""

import functions as fn


# ===========================================================================
def get_mul_fac(freq):
    freq_apx = 22e6
    return 1.0 * int(round(freq / freq_apx))
    
# -----------------------------------------------------------------------


def get_ref_freq(rec):
    freq = rec['doppler_ref_freq']
    ul = rec['uplink_band']
    dl = rec['dnlink_band']
    stn = rec['station']
    rcvr_type = rec['doppler_rcvr_type']
    
    band = fn.msr_band(freq)
    if band == dl: return freq
    
    # get frequency multiplier
    fac = get_mul_fac(freq)
    if fac == 0:
        msg = "\nInvalid reference frequency, %s MHz, at time %s for RANGE msr.\n Expected around 22MHz.\n" \
              + "Skipping this record.\n"
        fn.raise_warning(msg % (freq / 1e6, rec['time_tag']))
        return False
    freq = freq / fac
    
    # S-band uplink frequency
    if ul == "S": freq = 96.0 * freq
    
    # X-band frequency
    if ul == "X":
        if stn in ['15', '45', '65'] and rcvr_type != 5:
            freq = 4.68125 * freq - 81.4125e6
        freq = 32.0 * freq + 6.5e9
    
    return freq


def c_2(band):
    # Moyer's Table 13-2
    if band == "S": return 1.0
    if band == "X": return 880.0 / 240.0
    if band == "Ka": return 3344.0 / 240.0


# -----------------------------------------------------------------------


def m_2(ulband, dlband):
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
def find_exciter_band(turnaround_ratio):
    # Moyer's Table 13-1
    if turnaround_ratio == 240.0 / 221.0 or \
            turnaround_ratio == 880.0 / 221.0 or \
            turnaround_ratio == 3344.0 / 221.0:
        return "S"
    
    if turnaround_ratio == 240.0 / 749.0 or \
            turnaround_ratio == 880.0 / 749.0 or \
            turnaround_ratio == 3344.0 / 749.0:
        return "X"
    
    if turnaround_ratio == 240.0 / 3599.0 or \
            turnaround_ratio == 880.0 / 3599.0 or \
            turnaround_ratio == 3344.0 / 3599.0:
        return "Ka"
    
    return None


def sec_to_ru(band, freq):
    if band == 'S':
        return 0.5 * freq
    if band == 'X':
        # return (11/75)*freq
        return (221 / (749 * 2)) * freq


class Range:
    
    # -----------------------------------------------------------------------
    def __init__(self, range_recs, dtype, out_file):
        self.recs = range_recs
        self.out_file = out_file
        self.data_type = dtype

    # -----------------------------------------------------------------------
    def data_type_name(self):
        if self.data_type == 1: return '1-Way-Range'
        if self.data_type == 2: return '2-Way-Range'

    # -----------------------------------------------------------------------
    def create_msr(self, rec):
        
        # get uplink and downlink bands
        uplink_band = rec['uplink_band']
        dnlink_band = rec['dnlink_band']
        
        # get turnaround ratio
        if rec["turnaround_ratio_num"] == 0 or rec["turnaround_ratio_den"] == 0:
            turnaround_ratio = m_2(uplink_band, dnlink_band)
        else:
            turnaround_ratio = rec["turnaround_ratio_num"] / rec["turnaround_ratio_den"]
        
        # get exciter band
        rcvr_exciter_band = find_exciter_band(turnaround_ratio)
        
        # get average delays
        sc_delay = rec['sc_delay'] * 1e9
        xmtr_delay = rec['exciter_stn_delay'] * 1e9
        rcvr_delay = rec['rcvr_stn_delay'] * 1e9
        
        # get time
        time_tag = rec['time_tag']
        
        # get calibration delay
        C = rec['range_equp_delay']
        
        # low range component, for SRA
        rng_cm_l = rec['lwt_rng_component']
        
        # get reference frequency
        ref_freq = get_ref_freq(rec)
        
        if ref_freq:
            # get Z-correction in RU
            Z = rec['z_correction'] * sec_to_ru(dnlink_band, ref_freq)
            
            # get observed value
            observed = rec['range'] - C + Z - sc_delay*sec_to_ru(dnlink_band, ref_freq)
            
            # write output
            rcvr = 'DSS %s' % rec['station']
            xmtr = rcvr

            if self.data_type == 1:
                xmtr = "S/C"
                uplink_band = "Ku"

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
                   xmtr_delay,
                   rcvr_delay,
                   sc_delay,
                   )
            )
    
    # -----------------------------------------------------------------------
    def range_table(self):
        
        # get all range records
        size = len(self.recs)
        if size > 0:
            
            # set update progress
            umsg = "Extracting %s"%(self.data_type_name())
            prog  = fn.progressBar()
            prog.start(1, umsg)
            self.out_file.write(
                "%s %25s, %15s, %5s, %10s, %10s, %5s, %5s, %5s, %5s, %10s, %10s, %25s, %25s, %15s, %15s, %15s\n" \
                % ("#", "time_tag (UTC)", "Data Type", "scID", "Xmtr", "Rcvr", "Chnl", "UL", "DL", "Ex", "CT (sec)",
                   "Rng-LC", "Observed (RU)", "Ref-Freq (Hz)", "XmtrDly (nsec)", "RcvrDly (nsec)", "ScDly (nsec)"))
            i = 0
            for rec in self.recs:
                self.create_msr(rec)
                prog.setStep(i/size)
                i += 1
            prog.stop()
        
        # ===========================================================================
