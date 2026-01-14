"""
Custom exception for APR Detector error handling.
"""

class SequenceAnalysisError(Exception):
    """
    Exception raised for errors during sequence analysis in the APR Detector.

    Args:
        message: Error message describing the issue.
    """
    def __init__(self, message: str = "Sequence analysis failed"):
        super().__init__(message)
        self.message = message