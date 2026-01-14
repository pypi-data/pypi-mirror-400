__all__ = ["__version__", "MeasureSummary", "center", "spread", "utils"]

from importlib import metadata

from statmeasures import center, spread, utils
from statmeasures.summary import MeasureSummary

__version__ = metadata.version(__name__)
