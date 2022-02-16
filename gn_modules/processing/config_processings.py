"""
This config file defines the processings array.
At the processing step, only the processings present in this array will be computed.
"""

from gn_modules.processing.processings.masculinity_rate_and_names import MasculinityRateAndNames
from gn_modules.processing.processings.homogenous_category import HomogenousCategory
from gn_modules.processing.processings.quotes import Quotes

processings = [
    MasculinityRateAndNames,
    HomogenousCategory,
    Quotes,
]
