# -*- coding: utf-8 -*-
"""
Created on Thu Okt 7 13:44:32 2025

This module is a collector for all mantle implementations. And provides the SIR3S_Model_Mantle() class that contains the functions from all other classes defined in the mantle.

@author: Jablonski

"""

from sir3stoolkit.mantle.alternative_models import SIR3S_Model_Alternative_Models
from sir3stoolkit.mantle.dataframes import SIR3S_Model_Dataframes
from sir3stoolkit.mantle.plotting import SIR3S_Model_Plotting

class SIR3S_Model_Mantle(SIR3S_Model_Alternative_Models, SIR3S_Model_Dataframes, SIR3S_Model_Plotting):

    pass