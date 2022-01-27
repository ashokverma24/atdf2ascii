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
Help Command:

Python atdf2ascii.py -h

#######################################################################################################
Command to process TRK-2-25 formatted DSN file:

Python atdf2ascii.py -i input_file.tdf [options ...]

#######################################################################################################

NOTE:

A manuscript describing this code's architecture, formulation, and usability has been submitted for publication in the MDPI Journal. 
The citation information will be updated here once it has been accepted.  
