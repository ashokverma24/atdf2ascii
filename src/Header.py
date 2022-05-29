"""
Header:

    Reads the header of the ATDF file.

AUTHOR:

   Dr. Ashok Kumar Verma (1,2)
   1. Department of Earth, Planetary, and Space Sciences
      University of California, Los Angeles, 90095, CA, USA.
   2. NASA Goddard Space Flight Center, Greenbelt, 20771, MD, USA.
   
   Contact: ashokkumar.verma@nasa.gov

"""
import bitstring as bs
import functions as fn

# Header contents of Table 3-1 of ATDF file

__table1_field_names = [
    'record_format1',
    'reserved1',
    'record_type1',
    'not_in_used',
    'a', 't', 'd', 'f',
    'not_in_used']
__table1_format = 'uint:32, uint:8, uint:32, uint:120, bin:16, bin:8, bin:12, bin:8, uint:2068,'

# Header contents of Table 3-2 of ATDF file
__table2_field_names = [
    'record_format2',
    'reserved2',
    'record_type2',
    's_year',
    's_doy',
    's_hr',
    's_mn',
    's_sc',
    'not_in_used',
    'sc_id',
    'not_in_used',
    'e_year',
    'e_doy',
    'e_hr',
    'e_mn',
    'e_sc',
    'not_in_used',
    'spacecraft_transponder_frequency_hp',
    'spacecraft_transponder_frequency_lp',
    'not_in_used']
__table2_format = 'uint:32, uint:8, uint:32, uint:12, uint:16, uint:8, uint:12, uint:8, uint:12, \
                   uint:16, uint:24, uint:12, uint:16, uint:8, uint:12, uint:8, uint:16, 2*uint:36, uint:1980'

__field_names = (__table1_field_names + __table2_field_names)


# -------------------------------------------------------------------------------------------------------------------
def check_table1_data(obj: dict):
    """

    Check validity of the ATDF format.
   
    Args:
        obj: A dictionary of Table 1 items.
    """
    if obj["record_type1"] != 10:
        msg = "Item #3 (Record Type), in Table 3-1 (ATDF File Identification Logical Record Format): \n" \
              "Expected value: 10\n" \
              "Obtained value: %s \n"
        fn.raise_error(msg % (obj["record_type1"]))
    
    atdf = obj["a"] + obj["t"] + obj["d"] + obj["f"]
    if atdf != "ATDF":
        msg = "Item #15-18, in Table 3-1 (ATDF File Identification Logical Record Format): \n" \
              "Expected value: ATDF\n" \
              "Obtained value: %s \n"
        fn.raise_error(msg % atdf)


# -------------------------------------------------------------------------------------------------------------------
def check_table2_data(obj):
    """
    
    Check validity of the ATDF format.
    
    Args:
        obj: A dictionary of Table 2 items.
    """
    if obj["record_type2"] != 30:
        msg = "Item #3 (Record Type), in Table 3-2 (ATDF Transponder Logical Record Format): \n" \
              "Expected value: 30\n" \
              "Obtained value: %s \n"
        fn.raise_error(msg % (obj["record_type2"]))


# -------------------------------------------------------------------------------------------------------------------
def header(hdr_raw):
    """
    Purpose:
    Read header of ATDF file.

    args:
        hdr_raw (list):
           list of bytes, where each element size is 288 bytes.
    """
    
    # extract header chunk
    hdr_raw = hdr_raw[0] + hdr_raw[1]
    
    # header format
    hdr_fmt = (__table1_format + __table2_format)
    
    # Unpack SFDU header
    bitarray = bs.BitArray(hdr_raw)
    unpack = bitarray.unpack(hdr_fmt)
    
    out_dict = {}
    for i, val in enumerate(unpack):
        if 'not_in_used' not in __field_names[i]:
            if isinstance(val, str): val = fn.text_from_bits(val)
            out_dict.update({__field_names[i]: val})
    
    check_table1_data(out_dict)
    check_table2_data(out_dict)
    
    return out_dict
