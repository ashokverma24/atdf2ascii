""" 

Doppler class

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


def check_sky_freq(freq, band):
    flag = False
    if fn.msr_band(freq) == band: flag = True
    return flag


def store_record(rec, next_rec_at, count_time):
    """: Save a new record.

  = INPUT VARIABLES
  - rec      The record to save.
  - time     The time of the phase used from this record.  This may
             be different from rec.time() if index != 0.
  - index    The index of the phase to save.
  - mode     The computed mode for this record.

  = OUTPUT VARIABLES
  - data     On output, the fields of the data will be set with the inputs.
  """
    data = fn.dic_attrs(rec=None, next_rec_at=None, count_time=None)
    data.rec = rec
    data.next_rec_at = next_rec_at
    data.count_time = count_time
    
    return data


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


def c_2(band):
    # Moyer's Table 13-2
    if band == "S": return 1.0
    if band == "X": return 880.0 / 240.0
    if band == "Ka": return 3344.0 / 240.0


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


class Doppler:
    
    # -----------------------------------------------------------------------
    def __init__(self, doppler_recs, transponder_freq, dtype, count_time, out_file):
        self.recs = doppler_recs
        self.data_type = dtype
        self.count_time = count_time
        self.transponder_freq = transponder_freq
        self.out_file = out_file
        
        # -----------------------------------------------------------------------
    
    def convert(self, rec, start_doppler, count_time):
        
        time_tag = fn.str2datetime(rec['time_tag'])
        station = rec['station']
        ul = rec['uplink_band']
        dl = rec['dnlink_band']
        
        if ul == "Ka":
            msg = "At the moment the program is not able to process 'Ka' uplink band. \nTime Tag: %s \nStation: %s"
            fn.raise_warning(msg % (time_tag, station))
            return start_doppler
        
        xmtr = None
        if self.data_type == 1: xmtr = "S/C"
        if self.data_type == 2: xmtr = station
        
        rec_key = station + ul + dl
        former_rec = start_doppler[rec_key]
        
        if count_time >= 1.0 and former_rec.rec is None:
            ms = time_tag.microsecond
            sec = time_tag.second
        
        if former_rec.rec is None:
            next_rec_at = fn.add_time(time_tag, sec=count_time, dtType=True)
            former_rec = store_record(rec, next_rec_at, count_time)
            start_doppler.update({rec_key: former_rec})
            return start_doppler
        
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
        
        if time_tag > former_rec.next_rec_at:
            former_rec = store_record(None, None, None)
            start_doppler.update({rec_key: former_rec})
            return start_doppler
        
        return start_doppler
    
    # -----------------------------------------------------------------------
    def get_ref_freq(self, rec, band):
        
        freq = rec['doppler_ref_freq']
        ul = rec['uplink_band']
        dl = rec['dnlink_band']
        stn = rec['station']
        rcvr_type = rec['doppler_rcvr_type']

        # check sky level
        if check_sky_freq(freq, band):
            M2 = m_2(ul, dl)
            return M2, freq
        
        # get frequency multiplier
        fac = get_mul_fac(freq)
        if fac == 0:
            msg = "\nInvalid reference frequency, %s MHz, at time %s.\n Expected around 22MHz.\n" \
                  + "Skipping this record.\n"
            fn.raise_warning(msg % (freq / 1e6, rec['time_tag']))
            return False, False

        freq = freq / fac

        # for 1-way Doppler
        if self.data_type == 1:
            
            if freq > 22e6:
                ul = 'S'
            else:
                ul = dl
        
        # S-band uplink frequency
        # Moyer, Equation 13-1, section 13.2.1)
        if ul == "S": ref_freq = 96.0 * freq 
        
        # X-band frequency
        # Moyer, Equation 13-2/4, section 13.2.1)
        if ul == "X":
            if stn in ['15', '45', '65'] and rcvr_type != 5:
                freq = 4.68125 * freq - 81.4125e6
            ref_freq = 32.0 * freq + 6.5e9
        
        # get turnaround ration using up- and dn-link bands
        M2 = m_2(ul, dl)
        
        return M2, ref_freq
    
    # -----------------------------------------------------------------------
    def data_type_name(self):
        if self.data_type == 1: return '1-Way-Doppler'
        if self.data_type == 2: return '2-Way-Doppler'
    
    # -----------------------------------------------------------------------
    def write_msr(self, former_rec, rec, rcvr, xmtr, count_time):
        
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
        sc_delay = 0.5 * (rec['sc_delay'] + former_rec.rec['sc_delay']) * 1e9
        xmtr_delay = rec['exciter_stn_delay'] * 1e9
        rcvr_delay = rec['rcvr_stn_delay'] * 1e9
        
        # get average doppler bias (Moyer, Equation 13-22, section 13.3.1)
        C4 = rec['doppler_bias']
        
        # get doppler shift
        doppler_count_t2 = rec['doppler_count']
        doppler_count_t1 = former_rec.rec['doppler_count']

        # get change in the doppler cycles which accumulates during the count interval
        # (Moyer, first part of the right-hand Equation 13-26, DeltaN/Tc)
        delta_n_tc = (doppler_count_t2 - doppler_count_t1) / count_time
        
        # get average time
        time_tag = fn.add_time(fn.str2datetime(former_rec.rec['time_tag']), sec=count_time * 0.5)
        
        # get reference frequency
        M2, ref_freq = self.get_ref_freq(rec, rcvr_exciter_band)
        
        if ref_freq:
            # get frequency bias (Moyer, Equation 13-28, section 13.3.1)
            if self.data_type == 1:
                M2, ref_freq = self.get_ref_freq(rec, dnlink_band)
                C2 = c_2(dnlink_band)
                f_bias = M2 * ref_freq - C2* self.transponder_freq + C4
                ref_freq = self.transponder_freq
                uplink_band = "Ku"
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
            if xmtr != 'S/C': xmtr = 'DSS %s' % xmtr
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
                       xmtr_delay,
                       rcvr_delay,
                       sc_delay,
                       )
                )
    
    # -----------------------------------------------------------------------
    def doppler_table(self):
        
        start_doppler = fn.rec_dict(fn.dic_attrs(
            rec=None,
            next_rec_at=None,
            count_time=None, ))
        
        # get all doppler records
        size = len(self.recs)
        if size > 0:
            
            # set update progress
            umsg = "Extracting %s" % (self.data_type_name())
            stime = fn.time_now()
            prog  = fn.progressBar()
            prog.start(1, umsg)
            
            self.out_file.write(
                "%s %25s, %15s, %5s, %10s, %10s, %5s, %5s, %5s, %5s, %10s, %10s, %25s, %25s, %15s, %15s, %15s\n" \
                % ("#", "time_tag (UTC)", "Data Type", "scID", "Xmtr", "Rcvr", "Chnl", "UL", "DL", "Ex", "CT (sec)",
                   "Rng-LC", "Observed (Hz)", "Ref-Freq (Hz)", "XmtrDly (nsec)", "RcvrDly (nsec)", "ScDly (nsec)"))
            
            i = 0
            for rec in self.recs:
                
                if self.count_time is None:
                   count_time = rec['count_time']
                else:
                   if rec['count_time'] in self.count_time:
                      count_time = rec['count_time']
                   else:   
                      count_time = self.count_time[-1]
                
                start_doppler = self.convert(rec, start_doppler, count_time)
                prog.setStep(i/size)
                i += 1
            prog.stop()
        
        # ===========================================================================
