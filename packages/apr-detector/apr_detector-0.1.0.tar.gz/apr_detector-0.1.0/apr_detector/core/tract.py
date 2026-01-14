import re
from typing import List, Dict, Tuple, Optional
from multiprocessing import Pool
import logging
from functools import lru_cache

from ..config.config import APRConfig, ConfigurationError
from .complement import reverse_complement
from .exceptions import SequenceAnalysisError
from .scoring import ScoringConfig, is_symmetrical_tract

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _ta_restart_center(seq: str, tract_start: int) -> float:
    """
    Compute center of longest A/AnTn run with TA-restart logic (Model 3 mode).
    Returns 1-based center coordinate (fractional for even-length runs).
    """
    max_atlen = 0
    max_atend = 0
    alen = tlen = atlen = talen = 0
    prev_b = None
    for idx, b in enumerate(seq.upper()):
        if b == "A":
            tlen = 0
            talen = 0
            if prev_b == "T":
                alen = 0
                atlen = 0
            else:
                alen += 1
                atlen += 1
        elif b == "T":
            if talen < alen:
                talen += 1
                atlen += 1
            else:
                tlen += 1
                talen = 0
                atlen = 0
                alen = 0
        else:
            alen = tlen = atlen = talen = 0

        if atlen > max_atlen:
            max_atlen = atlen
            max_atend = idx
        prev_b = b

    if max_atlen == 0:
        return tract_start + (len(seq) - 1) / 2.0
    center_idx = max_atend - (max_atlen - 1) / 2.0
    return tract_start + center_idx
@lru_cache(maxsize=1024)
def validate_sequence(sequence: str) -> bool:
    """Validate sequence characters based on HANDLE_AMBIGUOUS policy."""
    logger.debug("Validating sequence in validate_sequence")
    if APRConfig.HANDLE_AMBIGUOUS == "error":
        allowed = "ATCG"
    else:
        allowed = "".join(sorted({"A", "T", "C", "G"} | APRConfig.AMBIGUOUS_BASES))
    valid_pattern = rf'^[{allowed}]*$'
    return bool(re.match(valid_pattern, sequence.upper()))


def merge_overlapping_tracts(tracts: List[Dict]) -> List[Dict]:
    """Merge overlapping A-tracts, taking union of positions and longest sequence."""
    if not tracts:
        return []
    tracts = sorted(tracts, key=lambda x: (x["start"], x["end"], x["strand"]))
    merged = []
    current = tracts[0].copy()

    for next_tract in tracts[1:]:
        if next_tract["start"] <= current["end"] and next_tract["strand"] == current["strand"]:
            current["end"] = max(current["end"], next_tract["end"])
            if len(next_tract["seq"]) > len(current["seq"]):
                current["seq"] = next_tract["seq"]
            current["center"] = (current["start"] + current["end"] - 1) / 2.0 + 1
        else:
            merged.append(current)
            current = next_tract.copy()
    merged.append(current)

    for i in range(1, len(merged)):
        if merged[i]["center"] <= merged[i - 1]["center"] and merged[i]["strand"] == merged[i - 1]["strand"]:
            logger.error(f"Non-increasing centers: {merged[i - 1]} -> {merged[i]}")
            raise SequenceAnalysisError(
                f"Non-increasing centers in merged tracts: {merged[i - 1]['center']} vs {merged[i]['center']}"
            )

    return merged


def find_tracts_in_chunk(args: Tuple[str, int, int, str, Optional[str]]) -> List[Dict]:
    sequence, start, chunk_size, strand, rev_sequence = args
    end = min(start + chunk_size, len(sequence))
    chunk = sequence[start:end]
    tracts = []
    i = 0

    while i < len(chunk) - APRConfig.MIN_NT_IN_TRACT + 1:
        base = chunk[i]
        mode = APRConfig.DETECTION_MODE
        if mode == "homopolymer":
            if base != "A":
                i += 1
                continue
            valid_bases = {"A"}
        elif mode == "homopolymer_t":
            if base != "T":
                i += 1
                continue
            valid_bases = {"T"}
        elif mode == "homopolymer_mixed":
            if base not in {"A", "T"}:
                i += 1
                continue
            # For mixed homopolymer mode, each tract must still be a pure run of its starting base.
            valid_bases = {base}
        elif mode == "heteropolymer":
            if base not in {"A", "T"}:
                i += 1
                continue
            valid_bases = {"A", "T"}
        else:
            i += 1
            continue
        j = i
        tract_seq = []
        length = 0

        while j < len(chunk) and chunk[j] in valid_bases and length < APRConfig.MAX_TRACT_LENGTH:
            tract_seq.append(chunk[j])
            j += 1
            length += 1

        if APRConfig.MIN_NT_IN_TRACT <= length <= APRConfig.MAX_TRACT_LENGTH:
            tract_str = "".join(tract_seq)
            tract_start = start + i + 1
            tract_end = start + i + length

            # In heteropolymer mode with strict heteropolymer filtering, skip pure A or pure T tracts
            if mode == "heteropolymer" and ScoringConfig.EXCLUDE_HOMOPOLYMER_IN_HETERO:
                if set(tract_str) == {"A"} or set(tract_str) == {"T"}:
                    logger.debug(f"Skipping homopolymer tract in heteropolymer-only mode: {tract_str} at {tract_start}-{tract_end}")
                    i += max(1, length)
                    continue

            tract_candidates = [(tract_str, tract_start, tract_end)]
            if not ScoringConfig.ALLOW_TA_IN_TRACTS and "TA" in tract_str:
                tract_candidates = []
                last_cut = 0
                for match in re.finditer("TA", tract_str):
                    cut = match.start() + 1  # split between the T and following A
                    if cut - last_cut >= APRConfig.MIN_NT_IN_TRACT:
                        sub_seq = tract_str[last_cut:cut]
                        sub_start = tract_start + last_cut
                        sub_end = sub_start + len(sub_seq) - 1
                        tract_candidates.append((sub_seq, sub_start, sub_end))
                    last_cut = cut
                remaining_len = len(tract_str) - last_cut
                if remaining_len >= APRConfig.MIN_NT_IN_TRACT:
                    sub_seq = tract_str[last_cut:]
                    sub_start = tract_start + last_cut
                    sub_end = sub_start + len(sub_seq) - 1
                    tract_candidates.append((sub_seq, sub_start, sub_end))
                if not tract_candidates:
                    logger.debug(f"Tract rejected due to TA motif (flag --ta 0): seq={tract_str}, start={tract_start}, strand={strand}")

            for seq_str, t_start, t_end in tract_candidates:
                symmetrical = is_symmetrical_tract(seq_str)
                if ScoringConfig.TA_RESTART_MODE:
                    center = _ta_restart_center(seq_str, t_start)
                else:
                    center = (t_start + t_end - 1) / 2.0 + 1
                tracts.append({
                    "start": t_start,
                    "end": t_end,
                    "seq": seq_str,
                    "center": center,
                    "strand": strand,
                    "is_symmetrical": symmetrical
                })
                logger.debug(f"Tract found: start={t_start}, seq={seq_str}, strand={strand}, symmetrical={symmetrical}")

        i += max(1, length)

    return tracts


def find_a_tracts(sequence: str, num_cpus: int = 1, rev_sequence: Optional[str] = None) -> List[Dict]:
    if not isinstance(sequence, str):
        raise SequenceAnalysisError(f"Input must be a string, got {type(sequence)}")
    if not sequence:
        logger.info("Empty sequence provided; returning empty tract list")
        return []

    sequence = sequence.upper()
    if not validate_sequence(sequence):
        raise SequenceAnalysisError(f"Invalid characters in sequence: {set(sequence) - {'A', 'T', 'C', 'G'} - APRConfig.AMBIGUOUS_BASES}")

    seq_len = len(sequence)
    logger.info(f"Finding A-tracts in sequence of length {seq_len:,} with {num_cpus} CPUs")

    try:
        APRConfig.validate()
        ScoringConfig.validate()
    except ConfigurationError as e:
        raise SequenceAnalysisError(f"Invalid configuration: {str(e)}")

    if APRConfig.HANDLE_AMBIGUOUS == "error" and any(c in APRConfig.AMBIGUOUS_BASES for c in sequence):
        raise SequenceAnalysisError(f"Ambiguous bases found: {set(sequence) & APRConfig.AMBIGUOUS_BASES}")
    elif APRConfig.HANDLE_AMBIGUOUS == "remove":
        for base in APRConfig.AMBIGUOUS_BASES:
            sequence = sequence.replace(base, "")
        # After removal, ensure resulting sequence is still valid
        if not validate_sequence(sequence):
            raise SequenceAnalysisError(f"Invalid characters remain after ambiguous removal")

    compute_rev = APRConfig.STRAND_SELECTION == 2
    rev_sequence = reverse_complement(sequence) if compute_rev else None

    def process_chunks(chunks, strand, seq):
        try:
            with Pool(processes=min(num_cpus, len(chunks))) as pool:
                results = pool.map(find_tracts_in_chunk, chunks)
            return [tract for chunk_tracts in results for tract in chunk_tracts]
        except MemoryError:
            logger.warning(f"MemoryError in parallel processing for {strand} strand; falling back to sequential")
            return [tract for chunk in chunks for tract in find_tracts_in_chunk(chunk)]

    if num_cpus <= 1 or seq_len < 1000:
        forward_tracts = find_tracts_in_chunk((sequence, 0, seq_len, "+", rev_sequence))
        reverse_tracts = find_tracts_in_chunk((rev_sequence, 0, seq_len, "-", sequence)) if APRConfig.STRAND_SELECTION == 2 and rev_sequence else []
    else:
        chunk_size = max(1, seq_len // (num_cpus * 4))
        chunks = [(sequence, i, chunk_size, "+", rev_sequence) for i in range(0, seq_len, chunk_size)]
        logger.info(f"Processing {len(chunks)} chunks with {min(num_cpus, len(chunks))} CPUs")
        forward_tracts = process_chunks(chunks, "+", sequence)
        reverse_tracts = []
        if APRConfig.STRAND_SELECTION == 2 and rev_sequence:
            rev_chunks = [(rev_sequence, i, chunk_size, "-", sequence) for i in range(0, seq_len, chunk_size)]
            reverse_tracts = process_chunks(rev_chunks, "-", rev_sequence)

    tracts = forward_tracts + reverse_tracts
    tracts.sort(key=lambda x: x["start"])
    logger.info(f"Found {len(tracts)} tracts before symmetry filtering and merging")

    # Symmetry filtering based on mode
    if ScoringConfig.SYMMETRY_MODE == "exclude":
        before = len(tracts)
        tracts = [t for t in tracts if not t.get("is_symmetrical", False)]
        removed = before - len(tracts)
        if removed > 0:
            logger.info(f"Removed {removed} symmetrical tracts (symmetry mode: exclude)")
    elif ScoringConfig.SYMMETRY_MODE == "only":
        before = len(tracts)
        tracts = [t for t in tracts if t.get("is_symmetrical", False)]
        removed = before - len(tracts)
        if removed > 0:
            logger.info(f"Kept only symmetrical tracts (symmetry mode: only); removed {removed} others")

    try:
        merged_tracts = merge_overlapping_tracts(tracts)
        logger.info(f"Merged tracts: {len(tracts)} -> {len(merged_tracts)} tracts")
    except SequenceAnalysisError as e:
        logger.error(f"Merging failed: {str(e)}")
        raise

    logger.info(f"Returning {len(merged_tracts)} candidate tracts")
    return sorted(merged_tracts, key=lambda x: (x["start"], x["end"], x["strand"]))
