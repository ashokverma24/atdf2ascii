"""
Reference:

            DOCUMENT 820-13;  REV A
            DSN SYSTEM REQUIREMENTS
           DETAILED INTERFACE DESIGN

                    TRK-2-25

        DSN TRACKING SYSTEM INTERFACES
     ARCHIVAL TRACKING DATA FILE INTERFACE

AUTHOR:

   Ashok Verma (ashokverma@ucla.edu)
   Department of Earth, Planetary, and Space Sciences
   University of California, Los Angeles

"""
import binascii
from functions import get_date
from decimal import Decimal


# Header contents of Table 3-3 of ATDF file
def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)


def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))


def update(_dict, key, val): _dict.update({key: val})


def get_phase_count(val1, val2):
    return float(Decimal(val1) * Decimal(10) ** 4 + Decimal(val2) * Decimal(10) ** -3)


def ramp_freq(hp, lp):
    if hp == 0.0: return hp
    dp = float(Decimal(hp) * Decimal(10) ** 1 + Decimal(lp) * Decimal(10) ** -6)
    return dp


def get_table3_data(out_dict):
    data_dict = {}
    
    # Record Format
    record_format = out_dict['Item001']
    if record_format == 64: record_format = 4
    update(data_dict, 'record_format', record_format)
    
    # Time Tag
    time_tag = get_date(1900 + out_dict['Item003'], out_dict['Item004'],
                        out_dict['Item005'], out_dict['Item006'], out_dict['Item007'])
    update(data_dict, "time_tag", time_tag)
    
    # Data Rate
    record_type = out_dict['Item002']
    high_rate = False
    if record_type == 91: high_rate = True
    update(data_dict, "high_rate", high_rate)
    
    # Receiving/Transmitter Station ID Number
    update(data_dict, "station", str(out_dict['Item010']))
    
    # Receiver/Downlink Frequency Band
    if out_dict['Item011'] == 0: band = "Ku"
    if out_dict['Item011'] == 1: band = "S"
    if out_dict['Item011'] == 2: band = "X"
    if out_dict['Item011'] == 3: band = "Ka"
    update(data_dict, "dnlink_band", band)
    
    # Sample Data Type
    update(data_dict, "data_type", out_dict['Item012'])
    
    # Doppler/Phase Channel Number
    update(data_dict, 'channel_number', out_dict['Item069'])
    
    # Ground Mode
    update(data_dict, "ground_mode", out_dict['Item013'])
    
    # Spacecraft ID
    update(data_dict, "sc_id", out_dict['Item008'])
    
    # Range Type
    update(data_dict, "range_type", out_dict['Item014'])
    
    # Doppler Good/Bad Indicator
    doppler_good = False
    if out_dict['Item017'] == 0: doppler_good = True
    update(data_dict, "doppler_valid", doppler_good)
    
    # Doppler Bias, Hz
    update(data_dict, "doppler_bias", out_dict['Item020'] * 1e6)
    
    # Frequency Level Indicator
    sky_level = False
    update(data_dict, "sky_level", sky_level)
    
    # Doppler Reference Receiver Type
    update(data_dict, "doppler_rcvr_type", out_dict['Item071'])
    
    # Source Designation/Exciter Type
    update(data_dict, "exciter_type", out_dict['Item028'])
    
    # Sample Interval, seconds
    update(data_dict, "count_time", out_dict['Item030'] * 1e-2)
    
    # No. 1 Doppler Count or Downlink Phase, cycles
    dop_count1 = get_phase_count(out_dict['Item031'],
                                 out_dict['Item032'], )
    update(data_dict, "doppler_count1", dop_count1)
    
    # Range data, RU or ns
    dsn_range = get_phase_count(out_dict['Item033'],
                                out_dict['Item034'])
    update(data_dict, "range", dsn_range)
    
    # Lowest (Last) Ranging Component
    update(data_dict, "lwt_rng_component", out_dict['Item035'])
    
    # Uplink Phase, cycles
    update(data_dict, "uplink_phase", 0.0)
    
    # Doppler Reference/Receiver Frequency, Hz
    update(data_dict, "doppler_ref_freq", out_dict['Item040'] / 1e1)
    
    # No. 2 Doppler Count or Downlink Phase, cycles
    dop_count2 = get_phase_count(out_dict['Item042'],
                                 out_dict['Item043'], )
    update(data_dict, "doppler_count2", dop_count2)
    
    # light time
    update(data_dict, "light_time", out_dict['Item043'])
    
    # No. 3 Doppler Count or Downlink Phase, cycles
    dop_count3 = get_phase_count(out_dict['Item044'],
                                 out_dict['Item045'], )
    update(data_dict, "doppler_count3", dop_count3)
    
    # No. 4 Doppler Count or Downlink Phase, cycles
    dop_count4 = get_phase_count(out_dict['Item046'],
                                 out_dict['Item047'])
    update(data_dict, "doppler_count4", dop_count4)
    
    # T1 Integration Time Constant
    update(data_dict, "t1_time_const", out_dict['Item047'])
    
    # No. 5 Doppler Count or Downlink Phase, cycles
    dop_count5 = get_phase_count(out_dict['Item048'],
                                 out_dict['Item049'])
    update(data_dict, "doppler_count5", dop_count5)
    
    # T2 Integration Time Constant
    update(data_dict, "t2_time_const", out_dict['Item049'])
    
    # No. 6 Doppler Count or Downlink Phase, cycles
    dop_count6 = get_phase_count(out_dict['Item050'],
                                 out_dict['Item051'])
    update(data_dict, "doppler_count6", dop_count6)
    
    # T3 Integration Time Constant
    update(data_dict, "t3_time_const", out_dict['Item051'])
    
    # No. 7 Doppler Count or Downlink Phase, cycles
    dop_count7 = get_phase_count(out_dict['Item052'],
                                 out_dict['Item053'])
    update(data_dict, "doppler_count7", dop_count7)
    
    # No. 8 Doppler Count or Downlink Phase, cycles
    dop_count8 = get_phase_count(out_dict['Item054'],
                                 out_dict['Item055'])
    update(data_dict, "doppler_count8", dop_count8)
    
    # No. 9 Doppler Count or Downlink Phase, cycles
    dop_count9 = get_phase_count(out_dict['Item056'],
                                 out_dict['Item057'])
    update(data_dict, "doppler_count9", dop_count9)
    
    # No. 10 Doppler Count or Downlink Phase, cycles
    dop_count10 = get_phase_count(out_dict['Item058'],
                                  out_dict['Item059'])
    update(data_dict, "doppler_count10", dop_count10)
    
    # Lowest (Last) Ranging Component
    update(data_dict, "hgt_rng_component", out_dict['Item059'])
    
    # Doppler or Downlink Phase Pseudo-Residual, Hz
    update(data_dict, "doppler_residual", out_dict['Item060'] * 1e-3)
    
    # Range Pseudo-Residual, RU
    update(data_dict, "range_residual", out_dict['Item061'])
    
    # Exciter/Uplink Frequency Band and Input Network/Source ID
    if out_dict['Item064'] == 0: band = "Ku"
    if out_dict['Item064'] == 1: band = "S"
    if out_dict['Item064'] == 2: band = "X"
    if out_dict['Item064'] == 3: band = "Ka"
    if out_dict['Item064'] == 7: band = "S2"
    update(data_dict, "uplink_band", band)
    
    # Numerator for Spacecraft Turnaround Ratio
    update(data_dict, "turnaround_ratio_num", out_dict['Item062'])
    
    # Denominator for Spacecraft Turnaround Ratio
    update(data_dict, "turnaround_ratio_den", out_dict['Item063'])
    
    # Conscan Mode
    update(data_dict, "conscan_mode", out_dict['Item066'])
    
    # Total Slipped Cycles During Count, cycles
    update(data_dict, "slipped_cycles", out_dict['Item076'])
    
    # Doppler Noise, Hz
    update(data_dict, "doppler_noise", out_dict['Item077'] * 1e-3)
    
    # Exciter Station Delay, second
    update(data_dict, "exciter_stn_delay", 0.0 * 1e-9)
    
    # Receiver Station Delay, second
    update(data_dict, "rcvr_stn_delay", 0.0 * 1e-9)
    
    # Range Good/Bad Indicator
    range_good = False
    if out_dict['Item085'] == 0: range_good = True
    update(data_dict, "range_valid", range_good)
    
    # Ranging Equipment Delay, RU
    update(data_dict, "range_equp_delay", 0.0 * 1e-2)
    
    # Z-Correction, second
    update(data_dict, "z_correction", out_dict['Item104'] * 1e-11)
    
    # Spacecraft Delay, second
    update(data_dict, "sc_delay", out_dict['Item105'] * 1e-9)
    
    # Range Noise, RU
    update(data_dict, "range_noise", out_dict['Item106'] * 1e-2)
    
    # Ramp Controller Indicator
    update(data_dict, "ramp_controller_indicator", out_dict['Item111'])
    
    # Programmed Frequency Ramp Rate, Hz/sec
    update(data_dict, "ramp_rate", out_dict["Item112"] * 1e-6)
    
    # Programmed Ramp Start Frequency, Hz
    ramp_start = ramp_freq(out_dict["Item113"],
                           out_dict["Item114"])
    update(data_dict, "ramp_start_freq", ramp_start)
    
    # Transmitter/Exciter Reference Frequency, Hz
    update(data_dict, "xmtr_ref_freq", out_dict["Item116"] / 1e1)
    
    return data_dict
