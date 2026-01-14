from apr_detector.config.config import APRConfig
from apr_detector.core.sequence import normalize_sequence, validate_raw_sequence


def test_normalize_sequence_strips_and_uppercases(chr1_prefix):
    raw = f"{chr1_prefix.lower()}\n"
    assert normalize_sequence(raw) == chr1_prefix.upper()


def test_validate_raw_sequence_removes_ambiguous(chr1_prefix):
    APRConfig.HANDLE_AMBIGUOUS = "remove"
    sequence, metadata, _ = validate_raw_sequence(f"{chr1_prefix} N R")
    assert sequence == chr1_prefix
    assert metadata["n_count"] == 1
    assert "R" in metadata["removed_ambiguous"]
