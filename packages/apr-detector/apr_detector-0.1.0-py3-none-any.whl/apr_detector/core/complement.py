## core/complement.py

import logging

from ..config.config import APRConfig
from .exceptions import SequenceAnalysisError

# Configure logging
logger = logging.getLogger(__name__)

def reverse_complement(sequence: str) -> str:
    """
    Computes the reverse complement of a DNA sequence.

    Args:
        sequence: DNA sequence (A, C, G, T, N, and ambiguous bases based on config; case-insensitive).

    Returns:
        str: Reverse complement sequence in uppercase.

    Raises:
        SequenceAnalysisError: For empty input, invalid characters, or configuration mismatches.
    """
    if not isinstance(sequence, str):
        logger.error(f"Input must be a string, got {type(sequence)}")
        raise SequenceAnalysisError(f"Input must be a string, got {type(sequence)}")
    if not sequence:
        logger.error("Cannot process empty sequence")
        raise SequenceAnalysisError("Cannot process empty sequence")

    seq_upper = sequence.upper()

    # Full IUPAC complement map
    complement_map = {
        'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C',
        'N': 'N',
        'R': 'Y', 'Y': 'R',
        'S': 'S', 'W': 'W',
        'K': 'M', 'M': 'K',
        'B': 'V', 'V': 'B',
        'D': 'H', 'H': 'D'
    }

    # Base valid characters (always allow canonical)
    valid_chars = {'A', 'C', 'G', 'T'}

    # If ambiguous handling is "keep", allow all ambiguous bases (including N)
    if APRConfig.HANDLE_AMBIGUOUS == "keep":
        valid_chars.update(APRConfig.AMBIGUOUS_BASES)

    # Validate characters against allowed set
    invalid_chars = set(seq_upper) - valid_chars
    if invalid_chars:
        logger.error(f"Invalid characters in sequence: {', '.join(sorted(invalid_chars))}")
        raise SequenceAnalysisError(
            f"Invalid characters in sequence: {', '.join(sorted(invalid_chars))}"
        )

    # If ambiguous handling is "error" and ambiguous bases present, stop
    ambiguous_present = set(seq_upper) & APRConfig.AMBIGUOUS_BASES
    if APRConfig.HANDLE_AMBIGUOUS == "error" and ambiguous_present:
        logger.error(f"Ambiguous bases found in 'error' mode: {', '.join(sorted(ambiguous_present))}")
        raise SequenceAnalysisError(
            f"Ambiguous bases not allowed in 'error' mode: {', '.join(sorted(ambiguous_present))}"
        )

    # Check for unmapped bases before attempting conversion
    unmapped = [base for base in seq_upper if base not in complement_map]
    if unmapped:
        logger.error(f"Unmapped bases in complement: {', '.join(sorted(set(unmapped)))}")
        raise SequenceAnalysisError(
            f"Unmapped bases in complement: {', '.join(sorted(set(unmapped)))}"
        )

    try:
        # Compute reverse complement
        return ''.join(complement_map[base] for base in reversed(seq_upper))
    except Exception as e:
        logger.error(f"Reverse complement failed: {str(e)}")
        raise SequenceAnalysisError(f"Reverse complement failed: {str(e)}") from e
