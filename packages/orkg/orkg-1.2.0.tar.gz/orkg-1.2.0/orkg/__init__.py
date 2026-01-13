import logging

from orkg import errors
from orkg.client import ORKG
from orkg.common import OID, ComparisonType, ExportFormat, Hosts, ThingType
from orkg.graph import subgraph
from orkg.version import __version__

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logger = logging.getLogger("ORKG")
logger.addHandler(logging.NullHandler())
