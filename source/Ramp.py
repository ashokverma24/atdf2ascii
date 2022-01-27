""" 

Ramp class

AUTHOR:  
        
   Ashok Verma (ashokverma@ucla.edu)
   Department of Earth, Planetary, and Space Sciences
   University of California, Los Angeles

"""

# ===========================================================================

import functions as fn


# ===========================================================================
def check_sky_freq(freq, band):
    flag = False
    if fn.msr_band(freq) == band: flag = True
    return flag


def get_rate(rate, band, sky_level):
    if sky_level:
        return rate
    else:
        if "S" == band: return rate * 96.0
        if "X" == band: return 32.0 * rate
        return rate


# -----------------------------------------------------------------------
def get_mul_fac(freq):
    freq_apx = 22e6
    return 1.0 * int(round(freq / freq_apx))


def get_ref_freq(rec):
    freq = rec['ramp_start_freq']
    ul = rec['uplink_band']
    sky_level = check_sky_freq(freq, ul)
    
    if sky_level: return freq, 1.0
    
    # get frequency multiplier
    fac = get_mul_fac(freq)
    if fac == 0:
        msg = "\nInvalid start ramp frequency, %s MHz, at time %s.\n Expected around 22MHz.\n" \
              + "Returning previous record.\n"
        fn.raise_warning(msg % (freq / 1e6, rec['time_tag']))
        return freq, fac
    
    freq = freq / fac
    
    # S-band uplink frequency
    if ul == "S": ref_freq = 96.0 * freq
    
    # X-band frequency
    if ul == "X":
        ref_freq = 32.0 * freq + 6.5e9
    
    return ref_freq, fac


def store_record(rec):
    """: Save a new record.

  """
    data = fn.dic_attrs(
        rec=None,
        time=None,
        ramp_rate=None,
        ramp_start_freq=None,
        band=None,
        station=None)
    
    data.rec = rec
    data.time = rec['time_tag']
    data.band = rec['uplink_band']
    data.station = rec['station']
    
    freq = rec['ramp_start_freq']
    freq_rate = rec['ramp_rate']
    sky_level = check_sky_freq(freq, data.band)
    
    data.ramp_start_freq, fac = get_ref_freq(rec)
    data.ramp_rate = get_rate(freq_rate / fac, data.band, sky_level)
    
    return data


class Ramp:
    
    # -----------------------------------------------------------------------
    def __init__(self, ramp_recs, out_file):
        self.recs = ramp_recs
        self.out_file = out_file
    
    # -----------------------------------------------------------------------
    def _freq(self, rec):
        
        time = rec['time_tag']
        station = rec['station']
        ul = rec['uplink_band']
        dl = rec['dnlink_band']
        freq = rec['ramp_start_freq']
        
        if ul == "Ka":
            fac = 0
            msg = "At the moment the program is not able to process 'Ka' uplink band.\nTime Tag: %s \nStation: %s"
            fn.raise_warning(msg % (time, station))
        
        else:
            freq, fac = get_ref_freq(rec)
        
        return time, ul, dl, station, freq, fac
    
    # -----------------------------------------------------------------------
    def convert(self, rec, start_ramp):
        
        # Get the count time from the user configuration input.
        time, ul, dl, station, freq, fac = self._freq(rec)
        if fac == 0: return start_ramp
        
        rec_key = station + ul + dl
        
        ramp_rec = start_ramp[rec_key]
        if ramp_rec.rec is None:
            ramp_rec = store_record(rec)
            start_ramp.update({rec_key: ramp_rec})
            return start_ramp
        
        self.write_ramp(ramp_rec, rec)
        ramp_rec = store_record(rec)
        start_ramp.update({rec_key: ramp_rec})
        
        return start_ramp
    
    # -----------------------------------------------------------------------
    def write_ramp(self, start, rec):
        
        end_time, band, dl, xmtr, freq, fac = self._freq(rec)
        
        self.out_file.write(
            "%27s, %30s, %10s, %5s, %25.10f, %15.6f\n" \
            % (start.time,
               end_time,
               'DSS %s' % xmtr,
               band,
               start.ramp_start_freq,
               start.ramp_rate
               )
        )
    
    # -----------------------------------------------------------------------
    def ramp_table(self):
        
        start_ramp = fn.rec_dict(fn.dic_attrs(
            rec=None,
            time=None,
            ramp_rate=None,
            ramp_start_freq=None,
            band=None,
            station=None))
        
        # get all ramp records
        size = len(self.recs)
        if size > 0:
            
            self.out_file.write("%s %25s, %30s, %10s, %5s, %25s, %15s\n" \
                                % ("#", "Start-Time", "End-Time", "Station", "Band", "Frequency (Hz)", "Rate (Hz/sec)"))
            
            # set update progress
            umsg = "Extracting Ramp records"
            prog  = fn.progressBar()
            prog.start(1, umsg)
            
            i = 0
            for rec in self.recs:
                start_ramp = self.convert(rec, start_ramp)
                prog.setStep(i / size)
                i += 1
            prog.stop()
        # ===========================================================================
