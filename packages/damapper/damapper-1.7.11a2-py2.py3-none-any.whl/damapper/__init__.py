# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                           DaMapper                             %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
DaMapper is a standalone application written in C++ with an optional
python interface to extract damage pattern from US scans and export 
them as XML or IGES files.

@version: 1.7.1   
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
                           
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package DaMapper 
# DaMapper package for US damage segmentation and mapping utilities 
## @authors 
# Marc Garbade
## @date
# 19.03.2024
## @par Notes/Changes
# - Added documentation // mg 19.03.2024

try:
    from DaMapperPy import *
except ImportError:
    pass

if __name__ == '__main__':
    pass