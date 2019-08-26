import arrow
import warnings
from arrow.factory import ArrowParseWarning

def ignore_ArrowParseWarning():
    warnings.simplefilter("ignore", ArrowParseWarning)
