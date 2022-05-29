"""
Reference:

            DOCUMENT 820-13;  REV A
            DSN SYSTEM REQUIREMENTS
     DETAILED SUNSYSTEM INTERFACE DESIGN

                TRK-2-25

        DSN TRACKING SYSTEM INTERFACES
     ARCHIVAL TRACKING DATA FILE INTERFACE

https://pds-geosciences.wustl.edu/radiosciencedocs/urn-nasa-pds-radiosci_documentation/dsn_trk-2-25/dsn_trk-2-25.1996-07-31.pdf

AUTHOR:

   Dr. Ashok Kumar Verma (1,2)
   1. Department of Earth, Planetary, and Space Sciences
      University of California, Los Angeles, 90095, CA, USA.
   2. NASA Goddard Space Flight Center, Greenbelt, 20771, MD, USA.
   
   Contact: ashokkumar.verma@nasa.gov

"""

from functions import get_date, MHz
from decimal import Decimal as D


# Header contents of Table 3-3 of ATDF file
def update(_dict: dict,
           key: str,
           val: str):
    """
    Update dictionary value.
    Args:
        _dict: Dictionary to be updated.
        key: Name of the key.
        val: Value of the key.
    """
    _dict.update({key: val})


def get_dbl_var(hp: int = 0,
                ip: int = 0,
                lp: int = 0,
                op: int = 0,
                tp: int = 0) -> float:
    """
    Get double precision value.
    Args:
        hp: High part of the value.
        ip: Intermediate part of the value.
        lp: Low part of the value.
        op: Part4 of the value.
        tp: Type of double precision.

    Returns: Double precision value of the variable.

    """
    if tp == 0: return float(D(ip) * D(10) ** -7 + D(lp) * D(10) ** -14)
    if tp == 1: return float(D(hp) * D(10) ** 8 + D(ip) * D(10) ** 1 + D(lp) * D(10) ** -6)
    if tp == 2: return float(D(hp) * D(10) ** 3 + D(lp) * D(10) ** -6)
    if tp == 3: return float(D(hp) * D(2) ** 40 + D(ip) * D(2) ** 16 + D(lp) / D(2) ** 8 + D(op) / D(2) ** 32)


def get_table3_data(out_dict):
    """
    Extract values in accordance with the Table 3 of TRK-2-25 interface document.
    Args:
        out_dict: Output dictionary.

    Returns: Dictionary with ascii values.

    """
    data_dict = {}
    
    # Record Format
    update(data_dict, 'record_format', out_dict['Item001'])
    
    # Time Tag
    time_tag = get_date(1900 + out_dict['Item004'], out_dict['Item005'],
                        out_dict['Item006'], out_dict['Item007'], out_dict['Item008'])
    update(data_dict, "time_tag", time_tag)
    
    # Data Rate
    record_type = out_dict['Item003']
    high_rate = False
    if record_type == 91: high_rate = True
    update(data_dict, "high_rate", high_rate)
    
    # Receiving/Transmitter Station ID Number
    update(data_dict, "station", str(out_dict['Item010']))
    
    # Receiver/Downlink Frequency Band
    if out_dict['Item011'] == 0: band = "NA"  # Not in use
    if out_dict['Item011'] == 1: band = "S"
    if out_dict['Item011'] == 2: band = "X"
    if out_dict['Item011'] == 3: band = "Ka"
    update(data_dict, "dnlink_band", band)
    
    # Sample Data Type
    update(data_dict, "data_type", out_dict['Item012'])
    
    # Doppler/Phase Channel Number
    update(data_dict, 'channel_number', out_dict['Item013'])
    
    # Ground Mode
    update(data_dict, "ground_mode", out_dict['Item014'])
    
    # Spacecraft ID
    update(data_dict, "sc_id", out_dict['Item015'])
    
    # Range Type
    update(data_dict, "range_type", out_dict['Item016'])
    
    # Doppler Good/Bad Indicator
    doppler_good = False
    if out_dict['Item019'] == 0: doppler_good = True
    update(data_dict, "doppler_valid", doppler_good)
    
    # Doppler Bias, Hz
    update(data_dict, "doppler_bias", out_dict['Item020'] * 1e3)
    
    # Frequency Level Indicator
    sky_level = False
    if out_dict['Item022'] == 1: sky_level = True
    update(data_dict, "sky_level", sky_level)
    
    # Doppler Reference Receiver Type
    update(data_dict, "doppler_rcvr_type", out_dict['Item026'])
    
    # Source Designation/Exciter Type
    update(data_dict, "exciter_type", out_dict['Item027'])
    
    # Sample Interval, seconds
    update(data_dict, "count_time", out_dict['Item029'] * 1e-2)
    
    # No. 1 Doppler Count or Downlink Phase, cycles
    dop_count1 = get_dbl_var(hp=out_dict['Item030'],
                             ip=out_dict['Item031'],
                             lp=out_dict['Item032'], tp=1)
    update(data_dict, "doppler_count1", dop_count1)
    
    # Range data, RU or ns
    rnge = get_dbl_var(hp=out_dict['Item033'],
                       ip=out_dict['Item034'],
                       lp=out_dict['Item035'], tp=1)
    update(data_dict, "range", rnge)
    
    # Lowest (Last) Ranging Component
    update(data_dict, "lwt_rng_component", out_dict['Item036'])
    
    # Uplink Phase, cycles
    uplink_phase = get_dbl_var(hp=out_dict['Item037'],
                               ip=out_dict['Item038'],
                               lp=out_dict['Item039'],
                               op=out_dict['Item040'], tp=3)
    update(data_dict, "uplink_phase", uplink_phase)
    
    # Doppler Reference/Receiver Frequency, Hz
    dop_ref_freq = get_dbl_var(hp=out_dict['Item043'],
                               lp=out_dict['Item044'], tp=2)
    update(data_dict, "doppler_ref_freq", dop_ref_freq)
    
    # No. 2 Doppler Count or Downlink Phase, cycles
    dop_count2 = get_dbl_var(hp=out_dict['Item046'],
                             ip=out_dict['Item047'],
                             lp=out_dict['Item048'], tp=1)
    update(data_dict, "doppler_count2", dop_count2)
    
    # light time
    update(data_dict, "light_time", out_dict['Item048'])
    
    # No. 3 Doppler Count or Downlink Phase, cycles
    dop_count3 = get_dbl_var(hp=out_dict['Item049'],
                             ip=out_dict['Item050'],
                             lp=out_dict['Item051'], tp=1)
    update(data_dict, "doppler_count3", dop_count3)
    
    # No. 4 Doppler Count or Downlink Phase, cycles
    dop_count4 = get_dbl_var(hp=out_dict['Item052'],
                             ip=out_dict['Item053'],
                             lp=out_dict['Item054'], tp=1)
    update(data_dict, "doppler_count4", dop_count4)
    
    # T1 Integration Time Constant
    update(data_dict, "t1_time_const", out_dict['Item054'])
    
    # No. 5 Doppler Count or Downlink Phase, cycles
    dop_count5 = get_dbl_var(hp=out_dict['Item055'],
                             ip=out_dict['Item056'],
                             lp=out_dict['Item057'], tp=1)
    update(data_dict, "doppler_count5", dop_count5)
    
    # T2 Integration Time Constant
    update(data_dict, "t2_time_const", out_dict['Item057'])
    
    # No. 6 Doppler Count or Downlink Phase, cycles
    dop_count6 = get_dbl_var(hp=out_dict['Item058'],
                             ip=out_dict['Item059'],
                             lp=out_dict['Item060'], tp=1)
    update(data_dict, "doppler_count6", dop_count6)
    
    # T3 Integration Time Constant
    update(data_dict, "t3_time_const", out_dict['Item060'])
    
    # No. 7 Doppler Count or Downlink Phase, cycles
    dop_count7 = get_dbl_var(hp=out_dict['Item061'],
                             ip=out_dict['Item062'],
                             lp=out_dict['Item063'], tp=1)
    update(data_dict, "doppler_count7", dop_count7)
    
    # No. 8 Doppler Count or Downlink Phase, cycles
    dop_count8 = get_dbl_var(hp=out_dict['Item064'],
                             ip=out_dict['Item065'],
                             lp=out_dict['Item066'], tp=1)
    update(data_dict, "doppler_count8", dop_count8)
    
    # No. 9 Doppler Count or Downlink Phase, cycles
    dop_count9 = get_dbl_var(hp=out_dict['Item067'],
                             ip=out_dict['Item068'],
                             lp=out_dict['Item069'], tp=1)
    update(data_dict, "doppler_count9", dop_count9)
    
    # No. 10 Doppler Count or Downlink Phase, cycles
    dop_count10 = get_dbl_var(hp=out_dict['Item070'],
                              ip=out_dict['Item071'],
                              lp=out_dict['Item072'], tp=1)
    update(data_dict, "doppler_count10", dop_count10)
    
    # Doppler or Downlink Phase Pseudo-Residual, Hz
    update(data_dict, "doppler_residual", out_dict['Item074'] * 1e-3)
    
    # Range Pseudo-Residual, RU
    update(data_dict, "range_residual", out_dict['Item076'] * 1e-3)
    
    # Exciter/Uplink Frequency Band and Input Network/Source ID
    if out_dict['Item079'] == 0: band = "S1"  # Not in use
    if out_dict['Item079'] == 1: band = "S"
    if out_dict['Item079'] == 2: band = "X"
    if out_dict['Item079'] == 3: band = "Ka"
    if out_dict['Item079'] == 7: band = "S2"  # Not in use
    update(data_dict, "uplink_band", band)
    
    # Numerator for Spacecraft Turnaround Ratio
    update(data_dict, "turnaround_ratio_num", out_dict['Item077'])
    
    # Denominator for Spacecraft Turnaround Ratio
    update(data_dict, "turnaround_ratio_den", out_dict['Item078'])
    
    # Conscan Mode
    update(data_dict, "conscan_mode", out_dict['Item081'])
    
    # Total Slipped Cycles During Count, cycles
    update(data_dict, "slipped_cycles", out_dict['Item087'])
    
    # Doppler Noise, Hz
    update(data_dict, "doppler_noise", out_dict['Item088'] * 1e-3)
    
    # Exciter Station Delay, second
    update(data_dict, "exciter_stn_delay", out_dict['Item090'] * 1e-9)
    
    # Receiver Station Delay, second
    update(data_dict, "rcvr_stn_delay", out_dict['Item091'] * 1e-9)
    
    # Range Good/Bad Indicator
    range_good = False
    if out_dict['Item096'] == 0: range_good = True
    update(data_dict, "range_valid", range_good)
    
    # Ranging Equipment Delay, RU
    update(data_dict, "range_equp_delay", out_dict['Item104'] * 1e-2)
    
    # Z-Correction, second
    update(data_dict, "z_correction", out_dict['Item112'] * 1e-11)
    
    # Spacecraft Delay, second
    update(data_dict, "sc_delay", out_dict['Item113'] * 1e-9)
    
    # Range Noise, RU
    update(data_dict, "range_noise", out_dict['Item114'] * 1e-2)
    
    # Ramp Controller Indicator
    update(data_dict, "ramp_controller_indicator", out_dict['Item119'])
    
    # Programmed Frequency Ramp Rate, Hz/sec
    ramp_rate = get_dbl_var(hp=out_dict['Item120'],
                            lp=out_dict['Item121'], tp=2)
    update(data_dict, "ramp_rate", ramp_rate)
    
    # Programmed Ramp Start Frequency, Hz
    ramp_start = get_dbl_var(hp=out_dict['Item123'],
                             lp=out_dict['Item125'], tp=2)
    update(data_dict, "ramp_start_freq", ramp_start)
    
    # Transmitter/Exciter Reference Frequency, Hz
    tran_freq = get_dbl_var(hp=out_dict['Item140'],
                            lp=out_dict['Item141'], tp=2)
    update(data_dict, "xmtr_ref_freq", tran_freq)
    
    return data_dict
