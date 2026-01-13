# src/ptcal/__init__.py

# Version des Pakets
__version__ = "0.1.0"

# Exponiere die Hauptklassen direkt im Top-Level Namespace
from .calibrator import PtCalibrator
from .sensor import PtSensor

# Exponiere Core-Funktionen, falls jemand "Low-Level" Mathe braucht
# (Optional, aber nützlich für Power-User)
from .core import (
    its90_w_ref_calc,
    cvd_r,
    solve_temp_from_r_cvd_iterative
)

# Definiere, was bei "from ptcal import *" importiert wird
__all__ = [
    "PtCalibrator",
    "PtSensor",
    "its90_w_ref_calc",
    "cvd_r"
]
