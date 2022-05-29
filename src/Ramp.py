""" 

Ramp class

Using ramp record information from the ATDF file, this class builds and outputs time history of the ramp
frequency.

AUTHOR:
        
   Dr. Ashok Kumar Verma (1,2)
   1. Department of Earth, Planetary, and Space Sciences
      University of California, Los Angeles, 90095, CA, USA.
   2. NASA Goddard Space Flight Center, Greenbelt, 20771, MD, USA.
   
   Contact: ashokkumar.verma@nasa.gov

"""

# ===========================================================================

import functions as fn


# ===========================================================================
def get_rate(rate: float,
             band: str,
             sky_level: bool) -> float:
    """
    Get ramp frequency rate.
    Args:
        rate: The rate of change of frequency.
        band: The band of the signal.
        sky_level: A boolean indicator of the sky level frequency.

    Returns: The rate of change of frequency.

    """
    if sky_level:
        return rate
    else:
        if "S" == band: return rate * 96.0
        if "X" == band: return 32.0 * rate
        if "Ka" == band: return 1000.0 * rate
        return rate


def get_ref_freq(rec):
    """

    Args:
        rec: The ramp record.

    Returns: The reference frequency.

    """
    freq = rec['ramp_start_freq']
    ul = fn.msr_band(freq)
    if ul is not None: return freq, 1.0
    
    # get frequency multiplier
    ul = rec['uplink_band']
    fac = fn.get_mul_fac(freq)
    if fac == 0:
        msg = "\nInvalid start ramp frequency, %s MHz, at time %s.\n Expected around 22MHz.\n" \
              + "Returning previous record.\n"
        fn.raise_warning(msg % (freq / fn.MHz, rec['time_tag']))
        return freq, fac
    
    freq = freq / fac
    
    # S-band uplink frequency
    if ul == "S":
        ref_freq = 96.0 * freq
    
    # X-band frequency
    elif ul == "X":
        ref_freq = 32.0 * freq + 6.5e9
    
    # Ka-Band frequency
    elif ul == 'Ka':
        ref_freq = 1000.0 * freq + 1e10
    
    # for all others band
    else:
        msg = '=' * 80 + \
              '\n~*~*~ The given reference frequency is not at the sky level ~*~*~' \
              '\nAt the moment, program is not able to compute the sky frequency at:' \
              '\nTime Tag: %s UTC' \
              '\nStation: DSS %s' \
              '\nUplink Band: %s' \
              '\nReference Freq: %s Hz\n' + '=' * 80
        fn.raise_warning(msg % (rec['time_tag'], rec['station'], ul, rec['ramp_start_freq']))
        fac = 0
        ref_freq = rec['ramp_start_freq']
    return ref_freq, fac


def store_record(rec):
    """
    Save current record in the dictionary.
    
    Args:
        rec: The ramp record.

    Returns: Saved record dictionary.

    """
    
    # create an empty data dictionary.
    data = fn.dic_attrs(
        rec=None,
        time=None,
        ramp_rate=None,
        ramp_start_freq=None,
        band=None,
        station=None)
    
    # set values to the dictionary keys.
    data.rec = rec
    data.time = rec['time_tag']
    data.band = rec['uplink_band']
    data.station = rec['station']
    
    # get frequency and rate from the record.
    freq = rec['ramp_start_freq']
    freq_rate = rec['ramp_rate']
    sky_level = fn.check_sky_freq(freq, data.band)
    
    # set values to the dictionary keys.
    data.ramp_start_freq, fac = get_ref_freq(rec)
    data.ramp_rate = get_rate(freq_rate / fac, data.band, sky_level)
    
    return data


class Ramp:
    """
    
    Using ramp record information from the ATDF file, this class builds and outputs time history of the ramp
    frequency.

    """
    
    # -----------------------------------------------------------------------
    def __init__(self, ramp_recs: dict,
                 out_file: str,
                 end_date: str):
        """
        
        Args:
            ramp_recs: The ramp record.
            out_file: Path to the output file.
            end_date: The last epoch of the measurement.
            
        """
        self.recs = ramp_recs
        self.out_file = out_file
        self.end_date = end_date
    
    # -----------------------------------------------------------------------
    def _freq(self,
              rec: dict):
        
        """
        
        Args:
            rec: The ramp record.

        Returns: Time tag, uplink, downlink, DSN station, frequency, correction factor

        """
        
        time = rec['time_tag']
        station = fn.is_dsn_valid(rec, data_type='Ramp')
        ul = rec['uplink_band']
        dl = rec['dnlink_band']
        freq, fac = get_ref_freq(rec)
        return time, ul, dl, station, freq, fac
    
    # -----------------------------------------------------------------------
    def convert(self, rec: dict,
                start_ramp: dict):
        """

        Args:
            rec: The current ramp record.
            start_ramp: The former ramp record.

        """
        # Get the count time from the user configuration input.
        time, ul, dl, station, freq, fac = self._freq(rec)
        if fac == 0 or station is None: return start_ramp
        
        # set ramp key
        rec_key = station + ul
        
        # update former ramp record.
        ramp_rec = start_ramp[rec_key]
        if ramp_rec.rec is None:
            ramp_rec = store_record(rec)
            start_ramp.update({rec_key: ramp_rec})
            return start_ramp
        
        # write ramp into the table.
        self.write_ramp(ramp_rec, rec)
        ramp_rec = store_record(rec)
        start_ramp.update({rec_key: ramp_rec})
        
        return start_ramp
    
    # -----------------------------------------------------------------------
    def write_ramp(self, start: dict,
                   rec: dict,
                   end_date=False):
        """
        Write ramp record into the output file.
        Args:
            start: The start ramp record.
            rec: The current ramp record.
            end_date: The last epoch of the measurement..
        """
        end_time, band, dl, xmtr, freq, fac = self._freq(rec)
        if end_date: end_time = end_date
        
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
        """

        Converts binary ramp records into ascii table.
        
        """

        # set empty start record
        start_ramp = fn.rec_dict(fn.dic_attrs(
            rec=None,
            time=None,
            ramp_rate=None,
            ramp_start_freq=None,
            band=None,
            station=None), True)
        
        # get all ramp records
        size = len(self.recs)
        if size > 0:
    
            # write a header of the output file.
            self.out_file.write("%s %25s, %30s, %10s, %5s, %25s, %15s\n" \
                                % ("#", "Start-Time", "End-Time", "Station", "Band", "Frequency (Hz)", "Rate (Hz/sec)"))
            
            # set update progress
            umsg = "Extracting Ramp records "
            prog = fn.progressBar()
            prog.start(1, umsg)

            # loop through every record.
            i = 0
            for rec in self.recs:
                start_ramp = self.convert(rec, start_ramp)
                prog.setStep(i / size)
                i += 1
            
            # write last ramp.
            lr = 0
            for key, value in start_ramp.items():
                items = start_ramp[key].rec
                if items is not None:
                    time_tag = items['time_tag']
                    if fn.str2datetime(time_tag) < fn.str2datetime(self.end_date):
                        self.write_ramp(store_record(items), items, end_date=self.end_date)
                        lr += 1
            prog.stop()
            return lr
        # ===========================================================================
