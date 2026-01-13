"""
Documents module - PDF generation, RIB, statements
"""

from .statement import StatementGenerator
from .rib import RIBGenerator

__all__ = [
    "StatementGenerator",
    "RIBGenerator",
]
