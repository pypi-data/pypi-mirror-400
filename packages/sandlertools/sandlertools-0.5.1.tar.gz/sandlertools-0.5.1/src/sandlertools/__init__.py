"""
Sandler Tools

A metapackage combining several computational tools based on
Chemical, Biochemical, and Engineering Thermodynamics (5th edition)
by Stan Sandler
https://www.pearson.com/us/higher-education/program/Sandler-Chemical-Biochemical-and-Engineering-Thermodynamics-5th-Edition/PGM332005.html

Copyright (c) 2025 Cameron F Abrams
"""

from sandlerprops.properties import Compound, PropertiesDatabase, get_database
from sandlersteam.state import State as SandlerSteamState
from sandlersteam.state import SteamTables
from sandlersteam.request import Request as SteamRequest
from sandlercubics.eos import IdealGasEOS, GeneralizedVDWEOS, PengRobinsonEOS
from sandlercorrespondingstates.charts import CorrespondingStatesChartReader
from sandlermisc.gas_constant import GasConstant
from sandlermisc.thermals import DeltaH_IG, DeltaS_IG
from sandlerchemeq.component import Component
from sandlerchemeq.reaction import Reaction
from sandlerchemeq.chemeqsystem import ChemEqSystem

from importlib.metadata import version

versions = {
    'sandlerprops': version('sandlerprops'),
    'sandlersteam': version('sandlersteam'),
    'sandlercubics': version('sandlercubics'),
    'sandlercorrespondingstates': version('sandlercorrespondingstates'),
    'sandlermisc': version('sandlermisc'),
    'sandlerchemeq': version('sandlerchemeq'),
}

__all__ = [ 'Compound',
            'PropertiesDatabase',
            'get_database',
            'SandlerSteamState', 
            'SteamTables', 
            'SteamRequest',
            'IdealGasEOS', 
            'GeneralizedVDWEOS', 
            'PengRobinsonEOS', 
            'CorrespondingStatesChartReader', 
            'GasConstant', 
            'DeltaH_IG', 
            'DeltaS_IG',
            'Component',
            'Reaction',
            'ChemEqSystem' ]