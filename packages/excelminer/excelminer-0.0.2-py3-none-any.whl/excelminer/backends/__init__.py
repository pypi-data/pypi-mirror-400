"""Backend implementations and shared contracts."""

from .base import AnalysisContext, AnalysisOptions, Backend, BackendReport
from .calamine_backend import CalamineBackend
from .com_backend import ComBackend
from .ooxml_zip import OOXMLZipBackend
from .openpyxl_backend import OpenpyxlBackend
from .pivot_zip import PivotZipBackend
from .powerquery_zip import PowerQueryZipBackend
from .vba_zip import VbaZipBackend

__all__ = [
    "AnalysisContext",
    "AnalysisOptions",
    "Backend",
    "BackendReport",
    "OOXMLZipBackend",
    "PowerQueryZipBackend",
    "PivotZipBackend",
    "VbaZipBackend",
    "OpenpyxlBackend",
    "CalamineBackend",
    "ComBackend",
]
