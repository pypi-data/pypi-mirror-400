import logging
from typing import List, Optional

from ..config.config import APRConfig
from .complement import reverse_complement
from .exceptions import SequenceAnalysisError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ScoringConfig:
    """Configuration for scoring-related parameters."""
    ENABLE_TA_RESTART: bool = False  # Drives TA-restart detection mode
    EXCLUDE_TPA_IN_SPACERS: bool = False
    EXCLUDE_HOMOPOLYMER_IN_HETERO: bool = False  # When true, drop pure A or pure T tracts in heteropolymer mode
    MAX_TPA_PER_SPACER: int = 100
    MIN_A_MINUS_T: int = 4
    SYMMETRY_MODE: str = "include"  # include, exclude, only
    ALLOW_TA_IN_TRACTS: bool = True  # Allow TA dinucleotide inside tract sequences
    TA_RESTART_MODE: bool = False  # Set when TA-restart is active; routes to Model3 detection path
    MAX_MEAN_SPACING: Optional[float] = None  # Optional filter on mean spacing
    MAX_SPACING_VARIANCE: Optional[float] = None  # Optional filter on spacing variance
    MIN_PHASE_Q: Optional[float] = None  # Optional filter on phase coherence
    PHASE_RMAX: Optional[float] = None  # Optional override for phase coherence denominator; defaults to pitch/2
    PHASE_EPS: float = 1e-9  # Protect division in Q

    @classmethod
    def validate(cls) -> None:
        """Validate scoring configuration parameters."""
        if not isinstance(cls.ENABLE_TA_RESTART, bool):
            raise SequenceAnalysisError("ENABLE_TA_RESTART must be boolean")
        if not isinstance(cls.EXCLUDE_TPA_IN_SPACERS, bool):
            raise SequenceAnalysisError("EXCLUDE_TPA_IN_SPACERS must be boolean")
        if not isinstance(cls.EXCLUDE_HOMOPOLYMER_IN_HETERO, bool):
            raise SequenceAnalysisError("EXCLUDE_HOMOPOLYMER_IN_HETERO must be boolean")
        if not isinstance(cls.MAX_TPA_PER_SPACER, int) or cls.MAX_TPA_PER_SPACER < 0:
            raise SequenceAnalysisError("MAX_TPA_PER_SPACER must be non-negative integer")
        if not isinstance(cls.MIN_A_MINUS_T, int) or cls.MIN_A_MINUS_T < 0:
            raise SequenceAnalysisError("MIN_A_MINUS_T must be non-negative integer")
        if not isinstance(cls.SYMMETRY_MODE, str) or cls.SYMMETRY_MODE not in {"include", "exclude", "only"}:
            raise SequenceAnalysisError("SYMMETRY_MODE must be one of: include, exclude, only")
        if not isinstance(cls.ALLOW_TA_IN_TRACTS, bool):
            raise SequenceAnalysisError("ALLOW_TA_IN_TRACTS must be boolean")
        for fld in ("MAX_MEAN_SPACING", "MAX_SPACING_VARIANCE", "MIN_PHASE_Q", "PHASE_EPS", "PHASE_RMAX"):
            val = getattr(cls, fld, None)
            if fld == "PHASE_EPS":
                if not isinstance(val, (int, float)) or val <= 0:
                    raise SequenceAnalysisError("PHASE_EPS must be positive")
            elif val is not None and not isinstance(val, (int, float)):
                raise SequenceAnalysisError(f"{fld} must be numeric or None")


#Model 3APR detection implementation

class TARestartTract:
    __slots__ = ("center", "start", "end")

    def __init__(self, center: float, start: int, end: int) -> None:
        self.center = center
        self.start = start
        self.end = end


class REP:
    __slots__ = ("start", "loop", "len", "num", "end", "sub", "strand", "special")

    def __init__(
        self, start: int, loop: int, length: int, num: int, end: int, sub: int, strand: int, special: int
    ) -> None:
        self.start = start
        self.loop = loop
        self.len = length
        self.num = num
        self.end = end
        self.sub = sub
        self.strand = strand
        self.special = special


def _rc_lower(seq: str) -> str:
    comp = str.maketrans("atcg", "tagc")
    return seq.translate(comp)[::-1]


class TARestartDetector:


    def __init__(self, dna_string: str) -> None:
        self.seq_forward = dna_string.lower()
        self.total_bases = len(self.seq_forward)
        self.seq_reverse = _rc_lower(self.seq_forward)
        self.tract_candidates: list[TARestartTract] = []

    def get_at_tracts(self, min_len: int, max_len: int) -> int:
        tracts: list[TARestartTract] = []
        seq_fwd = self.seq_forward
        seq_rev = self.seq_reverse
        total_bases = self.total_bases

        run_len = 0
        i = 0
        while i < total_bases:
            if seq_fwd[i] in ("a", "t"):
                run_len += 1
            else:
                if min_len <= run_len <= max_len:
                    start_1b = i - run_len + 1  # 1-based start
                    run_end_1b = start_1b + run_len  # one past end (1-based)

                    a_len = t_len = at_len = ta_len = max_at_len = max_t_len = 0
                    a_len_rc = t_len_rc = at_len_rc = ta_len_rc = max_at_len_rc = max_t_len_rc = 0
                    max_at_end = max_at_end_rc = 0

                    n_rc = total_bases - run_end_1b
                    n = start_1b - 1  # 0-based into seq
                    while n < run_end_1b - 1:
                        n_rc += 1
                        if seq_fwd[n] == "a":
                            t_len = 0
                            ta_len = 0
                            if seq_fwd[n - 1] == "t":
                                a_len = 0
                                at_len = 0
                            else:
                                a_len += 1
                                at_len += 1
                        if seq_fwd[n] == "t":
                            if ta_len < a_len:
                                ta_len += 1
                                at_len += 1
                            else:
                                t_len += 1
                                ta_len = 0
                                at_len = 0
                                a_len = 0
                        if max_at_len < at_len:
                            max_at_len = at_len
                            max_at_end = n
                        if max_t_len < t_len:
                            max_t_len = t_len

                        if seq_rev[n_rc] == "a":
                            t_len_rc = 0
                            ta_len_rc = 0
                            if seq_rev[n_rc - 1] == "t":
                                a_len_rc = 0
                                at_len_rc = 0
                            else:
                                a_len_rc += 1
                                at_len_rc += 1
                        if seq_rev[n_rc] == "t":
                            if ta_len_rc < a_len_rc:
                                ta_len_rc += 1
                                at_len_rc += 1
                            else:
                                t_len_rc += 1
                                ta_len_rc = 0
                                at_len_rc = 0
                                a_len_rc = 0
                        if max_at_len_rc < at_len_rc:
                            max_at_len_rc = at_len_rc
                            max_at_end_rc = n_rc
                        if max_t_len_rc < t_len_rc:
                            max_t_len_rc = t_len_rc

                        n += 1

                    if (max_at_len - max_t_len) >= min_len or (max_at_len_rc - max_t_len_rc) >= min_len:
                        end_pos = start_1b + run_len  # 1-based end (inclusive) +1
                        if (max_at_len - max_t_len) >= (max_at_len_rc - max_t_len_rc):
                            center = (max_at_end - ((max_at_len - 1) / 2.0)) + 1.0
                        else:
                            center = total_bases - (max_at_end_rc - ((max_at_len_rc - 1) / 2.0))
                        tracts.append(TARestartTract(center=center, start=start_1b, end=end_pos))
                run_len = 0
            i += 1

        self.tract_candidates = tracts
        return len(tracts)

    def getAtracts(self, minAT: int, maxAT: int) -> int:

        return self.get_at_tracts(minAT, maxAT)

    def find_aprs(self, min_tract_len: int, max_tract_len: int, min_tract_count: int) -> list[REP]:
        areps: list[REP] = []
        n_processed = self.get_at_tracts(min_tract_len, max_tract_len)
        chain_len = 1
        i = 0
        while i < n_processed - (min_tract_count + 1):
            dist_to_next = self.tract_candidates[i + 1].center - self.tract_candidates[i].center
            if 9.9 <= dist_to_next <= 11.1:
                chain_len += 1
            else:
                if chain_len >= min_tract_count:
                    start = self.tract_candidates[(i - chain_len) + 1].start
                    end = self.tract_candidates[i].end - 1
                    areps.append(
                        REP(
                            start=start,
                            loop=0,
                            length=chain_len,
                            num=chain_len,
                            end=end,
                            sub=0,
                            strand=0,
                            special=0,
                        )
                    )
                chain_len = 1
            i += 1
        # Note: No final flush (matches original behavior)
        return areps

    def findAPR(self, minAPR: int, maxAPR: int, minATracts: int) -> list[REP]:

        return self.find_aprs(minAPR, maxAPR, minATracts)

def is_symmetrical_tract(seq: str) -> bool:

    seq = seq.upper()
    if len(seq) % 2 != 0:
        return False  # must be even length

    mid = len(seq) // 2
    left, right = seq[:mid], seq[mid:]

    if not set(left) <= {"A"} or not set(right) <= {"T"}:
        return False

    # Check reverse complement symmetry
    rev_seq = reverse_complement(seq)
    return seq == rev_seq


def filter_tpa_in_spacers(spacer_seq: str) -> bool:
    """
    Filter spacers based on TpA step count.

    Args:
        spacer_seq: Spacer sequence.

    Returns:
        bool: True if spacer passes filter, False otherwise.
    """
    if not isinstance(spacer_seq, str):
        logger.error(f"Spacer sequence must be a string, got {type(spacer_seq)}")
        raise SequenceAnalysisError(f"Invalid spacer sequence type: {type(spacer_seq)}")

    seq = spacer_seq.upper()
    if not seq:
        logger.debug("Empty spacer sequence; passes TpA filter")
        return True

    # Simplified: Check presence if exclusion enabled (no count, as per removal of TPA steps count)
    if ScoringConfig.EXCLUDE_TPA_IN_SPACERS:
        result = 'TA' not in seq
    else:
        result = True  # Allow if not excluding

    logger.debug(f"TpA filter: seq={seq}, exclude={ScoringConfig.EXCLUDE_TPA_IN_SPACERS}, pass={result}")
    return result
