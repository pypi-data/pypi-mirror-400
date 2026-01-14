import os
import sys

# Ensure that we are testing the package installed (*not* the development) files
del sys.path[0]  # remove current directory from searching path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # add the package directory at the end

import line_racer

# Fortran extensions
import line_racer.fortran_line_calculation_molliere2015
import line_racer.fortran_line_calculation_sampling_lines

# Python modules
import line_racer.line_racer
