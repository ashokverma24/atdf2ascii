# atdf2ascii

#######################################################################################################
Abstract:

Radio science data collected from NASA’s Deep Space Networks (DSNs) are made available 
in various formats through NASA’s Planetary Data System (PDS). The majority of these data are 
packed in complex formats, making them inaccessible to users without specialized knowledge. In 
this paper, we present a Python-based tool that can preprocess the closed-loop archival tracking 
data files (ATDFs), produce Doppler and range observables, and write them in an ASCII table along 
with ancillary information. ATDFs are the earliest closed-loop radio science products with limited 
available documentation. Most data processing software (e.g., orbit determination software) cannot 
use them directly, thus limiting the utilization of these data. As such, the vast majority of historical 
closed-loop radio science data have not yet been processed with modern software and with our 
improved understanding of the solar system. The preprocessing tool presented in this paper makes it 
possible to revisit such historical data using modern techniques and software to conduct crucial radio 
science experiments.


#######################################################################################################
Requriemnts:

Python 3.6 and above

#######################################################################################################
Installation:

pip install .

For an editable/development install:

pip install -e .

#######################################################################################################
Help Command:

atdf2ascii -h

#######################################################################################################
Command to process TRK-2-25 formatted DSN file:

atdf2ascii -i input_file.tdf [options ...]

#######################################################################################################
Programmatic use:

from atdf2ascii import main

main(input_file="input_file.tdf", output_dir="./outputs", proc_count=4, count_time=None,
     doppler_one_way=True, doppler_two_way=True, doppler_three_way=True,
     range_one_way=True, range_two_way=True)

#######################################################################################################

NOTE:

A manuscript describing this code's architecture, formulation, and usability has been accepected for publication in the SoftwareX Journal. 

Please cite the software as follows:

@article{VERMA2022101190,
title = {A Python-based tool for constructing observables from the DSN’s closed-loop archival tracking data files},
journal = {SoftwareX},
volume = {19},
pages = {101190},
year = {2022},
issn = {2352-7110},
doi = {https://doi.org/10.1016/j.softx.2022.101190},
url = {https://www.sciencedirect.com/science/article/pii/S2352711022001145},
author = {Ashok Kumar Verma},
keywords = {Radio science, ATDF, Closed-loop, DSN},
}
