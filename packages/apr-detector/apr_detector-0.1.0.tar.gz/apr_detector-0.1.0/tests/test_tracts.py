from apr_detector.config.config import APRConfig
from apr_detector.core.scoring import ScoringConfig
from apr_detector.core.tract import find_a_tracts


def test_homopolymer_mixed_finds_a_and_t(chr1_prefix):
    APRConfig.DETECTION_MODE = "homopolymer_mixed"
    APRConfig.MIN_NT_IN_TRACT = 4
    APRConfig.MAX_TRACT_LENGTH = 10
    ScoringConfig.SYMMETRY_MODE = "include"
    ScoringConfig.ALLOW_TA_IN_TRACTS = True

    tracts = find_a_tracts(chr1_prefix, num_cpus=1)
    assert tracts
    has_a = any(set(t["seq"]) == {"A"} for t in tracts)
    has_t = any(set(t["seq"]) == {"T"} for t in tracts)
    assert has_a and has_t
