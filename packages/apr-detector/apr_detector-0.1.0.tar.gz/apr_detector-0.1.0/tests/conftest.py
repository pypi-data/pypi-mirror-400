import copy
import os
from pathlib import Path

import pytest

from apr_detector.config.config import APRConfig
from apr_detector.core.scoring import ScoringConfig
from apr_detector.core.tract import validate_sequence


APR_FIELDS = [
    "DETECTION_MODE",
    "MIN_NUM_TRACTS",
    "SPACING_WINDOW",
    "MIN_NT_IN_TRACT",
    "MAX_TRACT_LENGTH",
    "HANDLE_AMBIGUOUS",
    "AMBIGUOUS_BASES",
    "STRAND_SELECTION",
    "MERGE_APRS",
    "WRITE_GFF",
    "WRITE_BED",
    "WRITE_TRACTS_CSV",
    "WRITE_TRACTS_TSV",
    "WRITE_CSV",
    "WRITE_SUMMARY",
    "MODEL_NAME",
    "PITCH",
]

SCORE_FIELDS = [
    "ENABLE_TA_RESTART",
    "EXCLUDE_TPA_IN_SPACERS",
    "EXCLUDE_HOMOPOLYMER_IN_HETERO",
    "MAX_TPA_PER_SPACER",
    "MIN_A_MINUS_T",
    "SYMMETRY_MODE",
    "ALLOW_TA_IN_TRACTS",
    "TA_RESTART_MODE",
    "MAX_MEAN_SPACING",
    "MAX_SPACING_VARIANCE",
    "MIN_PHASE_Q",
    "PHASE_RMAX",
    "PHASE_EPS",
]


def _read_fasta_prefix(path: Path, max_bases: int) -> str:
    seq_parts = []
    total = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith(">"):
                continue
            chunk = line.strip()
            if not chunk:
                continue
            seq_parts.append(chunk)
            total += len(chunk)
            if max_bases > 0 and total >= max_bases:
                break
    sequence = "".join(seq_parts)
    if max_bases > 0:
        sequence = sequence[:max_bases]
    if not sequence:
        pytest.fail(f"Test FASTA appears empty: {path}")
    return sequence


@pytest.fixture(scope="session")
def chr1_fasta_path() -> Path:
    path = Path(__file__).resolve().parent / "data" / "S_cerevisiae_chr1.fasta"
    if not path.exists():
        pytest.fail(f"Chr1 FASTA not found at {path}")
    return path


@pytest.fixture(scope="session")
def chr1_prefix(chr1_fasta_path: Path) -> str:
    max_bases_env = os.getenv("APR_TEST_MAX_BASES", "20000")
    try:
        max_bases = int(max_bases_env)
    except ValueError:
        pytest.fail(f"APR_TEST_MAX_BASES must be an integer, got '{max_bases_env}'")
    return _read_fasta_prefix(chr1_fasta_path, max_bases)


@pytest.fixture(autouse=True)
def reset_configs():
    apr_snapshot = {name: copy.deepcopy(getattr(APRConfig, name)) for name in APR_FIELDS}
    score_snapshot = {name: copy.deepcopy(getattr(ScoringConfig, name)) for name in SCORE_FIELDS}
    validate_sequence.cache_clear()
    yield
    for name, value in apr_snapshot.items():
        setattr(APRConfig, name, value)
    for name, value in score_snapshot.items():
        setattr(ScoringConfig, name, value)
    validate_sequence.cache_clear()
