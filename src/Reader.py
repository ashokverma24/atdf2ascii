"""
Purpose:
    This reads the ATDF file in accordance with DSN TRK-2-25 interface.

AUTHOR:

   Dr. Ashok Kumar Verma (1,2)
   1. Department of Earth, Planetary, and Space Sciences
      University of California, Los Angeles, 90095, CA, USA.
   2. NASA Goddard Space Flight Center, Greenbelt, 20771, MD, USA.

   Contact: ashokkumar.verma@nasa.gov

"""
import bitstring as bs
import multiprocessing as mp
import functions as fn
import atdf_reader_I as atdfRI
import atdf_reader_II as atdfRII


# Header contents of Table 3-3 of ATDF file 
def get_fields(atdf_fmt: str):
    """

    Args:
        atdf_fmt: The format of the ATDF.

    Returns:

    """
    __field_names = []
    __table_format = None
    
    if atdf_fmt == 8:
        for i in range(1, 151):  __field_names.append("Item%03d" % i)
        __table_format = \
            'uint:32, uint:8 , uint:32, uint:12, uint:16, uint:8 , uint:8 , uint:8 , uint:20, uint:10, uint:8 , ' \
            'uint:6 , uint:4 , uint:4 , uint:16, uint:8 , uint:8 , uint:8 , uint:1 , int:18, uint:1 , uint:1 , ' \
            'uint:1 , uint:1 , uint:1 , uint:6 , uint:6 , uint:4 , uint:32, uint:24, uint:24, uint:24, uint:24, ' \
            'uint:24, uint:24, uint:8 , uint:28, uint:24, uint:24, uint:24,  int:24,  int:24, uint:32, uint:32,  ' \
            'int:32, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, ' \
            'uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, uint:24, ' \
            'uint:24, uint:24, uint:24, uint:24, uint:24, uint:24,  int:4 ,  int:32,  int:4 ,  int:32, int:18,  ' \
            'int:18, uint:8 , uint:4 , uint:2 , uint:1 , uint:1 , uint:1 , uint:1 , uint:8 , uint:10,  int:18,  ' \
            'int:18, uint:24, uint:24, uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , ' \
            'uint:1 , uint:4 , uint:1 , uint:10, uint:24,  int:12,  int:4 ,  int:32,  int:4 ,  int:32, uint:4 , ' \
            'uint:32,  int:22, uint:14, uint:23, uint:1 , uint:1 , uint:1 , uint:10, uint:8 ,  int:32,  int:32, ' \
            'uint:4 , uint:32, uint:4 , uint:32, uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , ' \
            'uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , uint:1 , uint:28, uint:30, uint:32, uint:32, ' \
            'uint:32, uint:32, uint:32, uint:32, uint:32, uint:32, uint:32 '
    elif atdf_fmt == 4:
        for i in range(1, 118):  __field_names.append("Item%03d" % i)
        __table_format = \
            '2*uint:36, uint:12, uint:16, uint:8, uint:12, uint:8, uint:28, 3*uint:8, uint:4, 4*uint:8, uint:5, ' \
            '2*uint:1, int:4, 2*uint:1, 2*uint:3, 2*uint:1, uint:2, uint:3, uint:10, 5*uint:36, uint:20, uint:72, ' \
            'int:16, 3*uint:36, int:36, 18*uint:36, 2*int:36, 2*int:18, 2*uint:3, uint:2, 2*uint:1, uint:3, uint:1, ' \
            '2*uint:4, 2*uint:1, uint:30, 2*uint:18, int:18, int:36, 12*uint:1, uint:4, uint:1, 2*uint:2, 2*uint:1, ' \
            'uint:13, uint:24, int:12, 3*int:36, int:22, uint:14, uint:33, 3*uint:1, int:36, uint:5, int:31, ' \
            '2*uint:36, uint:144, uint:36, uint:144, '
    else:
        msg = "Invalid ATDF format: " \
              + "Expected:\n '8' for records defined by SFOC-NAV-2-25 (1997-04-15 and after).\n" \
              + " '4' for records defined by TRK-2-25 (1997-04-14 and before).\n" \
              + "\nFound: %s"
        fn.raise_error(msg % atdf_fmt)
    
    return __table_format, __field_names


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


def check_for_high_rate(data_dict):
    """
    Check for the high rate data.
    
    Args:
        data_dict: The data dictionary.

    Returns: A list of dictionary.

    """
    _dict = {}
    time_tag = fn.str2datetime(data_dict['time_tag'])
    
    # update count and time tag.
    for key, val in data_dict.items():
        if 'count' not in key and 'time_tag' not in key:
            update(_dict, key, val)
    
    out_list = []
    
    # append to list if high data rate exists.
    if data_dict["high_rate"] and data_dict["data_type"] == 1:
        for i in range(10):
            out_dict = {}
            time = fn.add_time(time_tag, sec=i / 10)
            dop_cycle = data_dict['doppler_count%s' % (i + 1)]
            count = 0.1
            update(out_dict, 'time_tag', time)
            update(out_dict, 'doppler_count', dop_cycle)
            update(out_dict, 'count_time', count)
            out_dict.update(_dict)
            out_list.append(out_dict)
    else:
        out_dict = {}
        update(out_dict, 'time_tag', fn.datetime2str(time_tag))
        update(out_dict, 'doppler_count', data_dict['doppler_count1'])
        update(out_dict, 'count_time', data_dict['count_time'])
        out_dict.update(_dict)
        out_list = [out_dict]
    
    return out_list


def reader(raw: bytes,
           atdf_fmt: int,
           __format_type: str,
           __field_names: dict):
    """
    Unpack data in accordance with TRK-2-25 format.
    Args:
        raw: A raw data record.
        atdf_fmt: A integer indicates the TRK-2-25 format.
        __format_type: A string defines the structure of the format.
        __field_names: Name of the fields.

    Returns:

    """
    # Unpack SFDU header
    bitarray = bs.BitArray(raw)
    unpack = bitarray.unpack(__format_type)
    
    # update dictionary values.
    out_dict = {}
    for i, val in enumerate(unpack):
        if isinstance(val, str): val = fn.text_from_bits(val)
        out_dict.update({__field_names[i]: val})
    
    if atdf_fmt == 8: return atdfRII.get_table3_data(out_dict)
    if atdf_fmt == 4: return atdfRI.get_table3_data(out_dict)


def loop(i_start: int,
         i_end: int,
         prog: object,
         list_chunks: list,
         atdf_fmt: int,
         __format_type: str,
         __field_names: dict,
         queue: object):
    """
    Loop through all records with in the set
    Args:
        i_start: Start index of the record.
        i_end: End index of the record.
        prog: A progress bar object.
        list_chunks: A list of all records.
        atdf_fmt: A integer indicates the TRK-2-25 format.
        __format_type: A string defines the structure of the format.
        __field_names: Name of the fields.
        queue: A queue object.
    """
    dtypes = [[], [], [], [], [], []]
    for i in range(i_start, i_end):
        _dict = reader(list_chunks[i], atdf_fmt, __format_type, __field_names)
        data_list = check_for_high_rate(_dict)

        for j in range(len(data_list)):
            data_dict = data_list[j]

            # Ramp
            if data_dict['data_type'] == 6 and data_dict['ground_mode'] == 0: dtypes[0].append(data_dict)
            
            # 1-way Doppler
            if (data_dict['data_type'] == 1 or data_dict['data_type'] == 2) and data_dict['doppler_valid'] and \
                    data_dict['ground_mode'] == 1:
                dtypes[1].append(data_dict)
            
            # 2-way Doppler
            if (data_dict['data_type'] == 1 or data_dict['data_type'] == 2) and data_dict['doppler_valid'] and \
                    data_dict['ground_mode'] == 2:
                dtypes[2].append(data_dict)
            
            # 3-way Doppler
            if (data_dict['data_type'] == 1 or data_dict['data_type'] == 2) and data_dict['doppler_valid'] and \
                    data_dict['ground_mode'] == 3:
                dtypes[3].append(data_dict)

            # 1-way Range
            if data_dict['data_type'] == 5 and data_dict['ground_mode'] == 5 and data_dict['range_valid']:
                dtypes[4].append(data_dict)
            
            # 2-way Range
            if data_dict['data_type'] == 5 and data_dict['ground_mode'] == 6 and data_dict['range_valid']:
                dtypes[5].append(data_dict)
            
            if i_start == 0: prog.setStep(0.05 + 0.85 * i / (i_end - i_start))
    
    queue.put(dtypes)


def get_all_items(list_chunks: list,
                  pro_count: int,
                  get_obs_span=False):
    """
    Unpack all items and sort them according to the data type.
    
    Args:
        list_chunks: A list contain all records.
        pro_count: A number of available processors.
        get_obs_span:A boolean flag to return start and final epoch of the measurement.

    """
    # set update progress
    umsg = "Unpacking raw ATDF data "
    if not get_obs_span:
        prog = fn.progressBar()
        prog.start(1, umsg)
    
    # remove header from the chunks    
    list_chunks = list_chunks[2:]
    
    # get appropriate format
    fmt = 'uint:32'
    bitarray = bs.BitArray(list_chunks[0])
    atdf_fmt = bitarray.unpack(fmt)[0]
    __format_type, __field_names = get_fields(atdf_fmt)
    
    # remove padded data that used to fill the remaining bytes 
    for i in range(1, len(list_chunks)):
        obj = reader(list_chunks[-1 * i], atdf_fmt, __format_type, __field_names)
        if obj["record_format"] == atdf_fmt: break
    if i != 1: list_chunks = list_chunks[:1 - i]
    if not get_obs_span: prog.setStep(0.05)
    
    # return start and final epoch of the measurement, if requested.
    if get_obs_span:
        dict_start = reader(list_chunks[0], atdf_fmt, __format_type, __field_names)
        dict_end = reader(list_chunks[-1], atdf_fmt, __format_type, __field_names)
        start_time = None
        end_time = None
        try:
            start_time = dict_start['time_tag']
        except Exception:
            pass
        
        try:
            end_time = dict_end['time_tag']
        except Exception:
            pass
        
        return start_time, end_time
    
    # get all available cpus
    if not pro_count:
        __cpu_count = mp.cpu_count() // 2
    else:
        __cpu_count = int(pro_count)
    
    # read data using multi-processors
    queues = [mp.Queue() for _ in range(__cpu_count)]
    
    m = len(list_chunks) % __cpu_count
    pp = len(list_chunks) // __cpu_count
    
    s = 0
    x = 0
    loop_args = []
    while s < len(list_chunks):
        x = x + 1
        s_index = s
        e_index = s + pp
        if x <= m: e_index = e_index + 1
        loop_args += [(s_index, e_index, prog, list_chunks, atdf_fmt, __format_type, __field_names, queues[x - 1])]
        s = e_index
    jobs = [mp.Process(target=loop, args=a) for a in loop_args]
    
    # start multi-processors
    for j in jobs:
        j.start()
    pppp = 0
    
    # combine results from all processors.
    results = [[]] * 6
    for q in queues:
        pppp = pppp + 1
        out = q.get()
        for k in range(len(out)):
            results[k] = results[k] + out[k]
        prog.setStep(0.9 + 0.099 * pppp / __cpu_count)
    
    for j in jobs:
        j.join()
    
    # sort data according to the data type.
    dtype = fn.dic_attrs(ramp=results[0], doppler1way=results[1], doppler2way=results[2],
                         doppler3way=results[3], range1way=results[4], range2way=results[5], )
    
    prog.stop()
    
    return dtype
