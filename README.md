# atdf2ascii

## Abstract

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

## Requirements

Python 3.6 and above

## Installation

To install the library, clone this repository to your local machine:

```bash
git clone https://github.com/ashokverma24/atdf2ascii.git
cd atdf2ascii
```

and activate your pip/conda environment:

```bash
# source your-env/bin/activate
# conda activate your-env 
```

You can then install the library from inside the `atdf2ascii/` directory with

```bash
pip install .
```

For an editable/development install:

```bash
pip install -e .
```

## Usage

After installation, you can use the following command to process TRK-2-25 formatted DSN file from the command line:

```bash
atdf2ascii -i input_file.tdf [options ...]
```

All possible processing options are described in the help command:

```bash
atdf2ascii -h
```

To use the library programmatically, you can import the `atdf_to_ascii` function directly from `atdf2ascii`:

```python
from atdf2ascii import atdf_to_ascii

atdf_to_ascii(input_file="input_file.tdf", output_dir="./outputs", proc_count=4, count_time=None,
     doppler_one_way=True, doppler_two_way=True, doppler_three_way=True,
     range_one_way=True, range_two_way=True)
```

## Citation

A manuscript describing this code's architecture, formulation, and usability has been accepted for publication in the SoftwareX Journal.
Please cite the software as follows:

```latex
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
```
