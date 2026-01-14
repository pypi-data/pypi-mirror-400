"""
APR Detector Core Module

Provides:
- sequence: FASTA sequence reading and validation
- complement: DNA reverse complement generation
- tract: Identification of A/T-rich regions
- detector: Detection of A-Phased Repeats (APRs)
- scoring: TA-restart and TpA filtering for APR detection
- exceptions: Custom exception for error handling

Version: 2.0.0
"""

from .sequence import read_fasta, validate_raw_sequence
from .complement import reverse_complement
from .tract import find_a_tracts
from .detector import detect_aprs
from .scoring import ScoringConfig
from .exceptions import SequenceAnalysisError

__all__ = [
    "read_fasta",
    "validate_raw_sequence",
    "reverse_complement",
    "find_a_tracts",
    "detect_aprs",
    "ScoringConfig",
    "SequenceAnalysisError"
]

__version__ = "2.0.0"
