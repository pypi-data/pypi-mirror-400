#!/usr/bin/env python3
# Copyright (C) 2025 Otter Brown
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 only.

import os
from biochemHH import GBparser
from biochemHH.GBparser import reverse_complement
from biochemHH.GBparser import preferred_codon
from biochemHH.GBparser import preferred_codon_split
from biochemHH.GBparser import Read_gb
from biochemHH import Homolog
from biochemHH import StructureHH
import numpy as np


if __name__ == '__main__':

    # Set your own working directory (wd). Input and output files will be located in the working directory.

    # { ........................................ set working directory
    wd =r'C:\Users\ees26\Desktop\input'    #  Replace this with your working directory path without Chinese characters
    os.chdir(wd)
    # }


    # { ........................................ Replace this empty block with a code block from an example script
    
    # }
