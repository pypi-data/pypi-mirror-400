"""
core/detector.py
APR detection module for A-phased repeat (APR) pipeline.

Responsible for grouping A-tracts into APRs, validating them based on
spacing and configuration rules, and generating annotated APR results.
"""

from typing import List, Dict, Tuple, Optional
from multiprocessing import Pool
import logging

from .complement import reverse_complement
from ..config.config import APRConfig, ConfigurationError
from .scoring import ScoringConfig, filter_tpa_in_spacers
from .exceptions import SequenceAnalysisError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Minimum number of tracts for parallel processing
MIN_TRACTS_FOR_PARALLEL = 1000


def _merge_strands(strands) -> str:
    """Merge strand strings into '+', '-', or '+-'."""
    strand_set = set()
    for st in strands:
        if not isinstance(st, str):
            continue
        strand_set.update(ch for ch in st if ch in {"+", "-"})
    if "+" in strand_set and "-" in strand_set:
        return "+-"
    if "+" in strand_set:
        return "+"
    if "-" in strand_set:
        return "-"
    return ""


def merge_apr_records(aprs: List[Dict]) -> List[Dict]:
    """
    Merge APRs that share coordinates or where one is fully contained within another.
    Rules:
      - Identical start/stop: keep the longest APR (first if tie), strand becomes '+-' if needed.
      - Containment: keep the longer APR, drop the internal one, union strands.
      - Tract sequences, num_tracts, composition, and sequence come from the longest APR.
    """
    if not aprs:
        return []

    merged_all: List[Dict] = []
    aprs_by_chr: Dict[str, List[Dict]] = {}
    for apr in aprs:
        aprs_by_chr.setdefault(apr["chr"], []).append(apr)

    for chr_id, chr_aprs in aprs_by_chr.items():
        if not chr_aprs:
            continue

        # Step 1: merge identical coordinates
        chr_sorted = sorted(
            chr_aprs,
            key=lambda a: (a["start"], a["end"], -(a["end"] - a["start"]), a["strand"])
        )
        dedup: List[Dict] = []
        i = 0
        while i < len(chr_sorted):
            same_coords = [chr_sorted[i]]
            j = i + 1
            while j < len(chr_sorted) and chr_sorted[j]["start"] == chr_sorted[i]["start"] and chr_sorted[j]["end"] == chr_sorted[i]["end"]:
                same_coords.append(chr_sorted[j])
                j += 1

            longest = max(same_coords, key=lambda a: (a["end"] - a["start"], len(a.get("sequence", ""))))
            strand = _merge_strands([a["strand"] for a in same_coords])
            base = dict(longest)
            base["strand"] = strand if strand else longest.get("strand", "+")
            dedup.append(base)
            i = j

        # Step 2: remove contained APRs, keeping the longer
        containment_merged: List[Dict] = []
        for apr in sorted(dedup, key=lambda a: (-(a["end"] - a["start"]), a["start"], a["end"])):
            merged_into_existing = False
            for existing in containment_merged:
                if existing["start"] <= apr["start"] and existing["end"] >= apr["end"]:
                    existing["strand"] = _merge_strands([existing["strand"], apr["strand"]])
                    merged_into_existing = True
                    break
            if not merged_into_existing:
                containment_merged.append(apr)

        merged_all.extend(sorted(containment_merged, key=lambda a: (a["start"], a["end"])))

    return sorted(merged_all, key=lambda a: (a["chr"], a["start"], a["end"], a.get("strand", "+")))


def process_group(args: Tuple[List[Dict[str, any]], str, Optional[str], str]) -> List[Dict]:
    tract_group, full_sequence, rev_sequence, seq_id = args
    aprs: List[Dict] = []
    current_group: List[Dict] = []
    prev_center = -float("inf")

    for tract in tract_group:
        start, end, center, strand = tract["start"], tract["end"], tract["center"], tract["strand"]

        if center <= prev_center:
            logger.warning(
                f"Non-increasing centers: {prev_center} vs {center} on strand {strand}; resetting group"
            )
            _finalize_group(current_group, aprs, full_sequence, rev_sequence, seq_id)
            current_group = [tract]
            prev_center = center
            continue
        prev_center = center

        if current_group:
            spacing = center - current_group[-1]["center"]
            if not isinstance(spacing, (int, float)) or spacing <= 0:
                logger.error(
                    f"Invalid spacing: {spacing} between {current_group[-1]['center']} and {center}"
                )
                raise SequenceAnalysisError(f"Invalid spacing: {spacing}")
            min_spacing = APRConfig.get_min_spacing()
            max_spacing = APRConfig.get_max_spacing()
            if not (min_spacing <= spacing <= max_spacing):
                _finalize_group(current_group, aprs, full_sequence, rev_sequence, seq_id)
                current_group = [tract]
                continue

        current_group.append(tract)

    if current_group:
        _finalize_group(current_group, aprs, full_sequence, rev_sequence, seq_id)

    return aprs


def _finalize_group(
    group: List[Dict],
    aprs: List[Dict],
    full_sequence: str,
    rev_sequence: Optional[str],
    seq_id: str,
) -> None:
    """Evaluate a tract group and append valid APRs to `aprs`."""
    if not group or len(group) < APRConfig.MIN_NUM_TRACTS:
        logger.debug(f"Group too small: {len(group)} tracts < MIN_NUM_TRACTS {APRConfig.MIN_NUM_TRACTS}")
        return

    try:
        start = group[0]["start"]
        end = group[-1]["end"]
        strand = group[0]["strand"]
        seq_to_use = full_sequence if strand == "+" else rev_sequence

        if seq_to_use is None:
            logger.error(f"No sequence provided for strand {strand}")
            raise SequenceAnalysisError(f"Missing sequence for strand {strand}")

        if not all(t["strand"] == strand for t in group):
            logger.debug(f"Mixed strands in group {start}-{end}")
            return
        if start >= end or start < 1 or end > len(seq_to_use):
            logger.debug(
                f"Invalid APR coordinates: {start}-{end} for sequence length {len(seq_to_use)}"
            )
            return

        centers = [t["center"] for t in group]
        spacings = [centers[i + 1] - centers[i] for i in range(len(centers) - 1)]
        if any(s <= 0 for s in spacings):
            logger.debug(f"Invalid spacings {spacings} in group {start}-{end}")
            return

        # Apply TpA filtering in heteropolymer spacers
        if APRConfig.DETECTION_MODE == "heteropolymer":
            for i in range(len(group) - 1):
                spacer_start = group[i]["end"]
                spacer_end = group[i + 1]["start"]
                if spacer_start >= spacer_end:
                    logger.debug(f"Invalid spacer {spacer_start}-{spacer_end}")
                    return
                spacer_seq = seq_to_use[spacer_start : spacer_end - 1].upper()
                if ScoringConfig.EXCLUDE_TPA_IN_SPACERS and not filter_tpa_in_spacers(spacer_seq):
                    logger.debug(f"APR rejected: TpA steps in spacer {spacer_seq}")
                    return

        min_spacing = APRConfig.get_min_spacing()
        if not ScoringConfig.TA_RESTART_MODE:
            min_apr_length = (len(group) - 1) * min_spacing
            if (end - start) < min_apr_length:
                logger.debug(f"APR length {end - start} < minimum {min_apr_length}")
                return

        apr_sequence = seq_to_use[start - 1 : end].upper()
        tract_seqs = [t["seq"] for t in group]

        for tract in group:
            tract_start = tract["start"]
            tract_end = tract["end"]
            tract_seq = tract["seq"]
            rel_start = tract_start - start
            rel_end = tract_end - start + 1
            if apr_sequence[rel_start:rel_end] != tract_seq:
                logger.debug(
                    f"Tract sequence {tract_seq} not found at relative {rel_start}-{rel_end} "
                    f"in APR {start}-{end} (sequence: {apr_sequence})"
                )
                return

        # Metrics: mean spacing, variance, phase coherence (Q)
        spacings = [centers[i + 1] - centers[i] for i in range(len(centers) - 1)]
        mean_spacing = sum(spacings) / len(spacings) if spacings else None
        spacing_variance = None
        if len(spacings) > 1:
            mu = mean_spacing if mean_spacing is not None else 0.0
            spacing_variance = sum((s - mu) ** 2 for s in spacings) / (len(spacings) - 1)
        phase_q = None
        if spacings:
            pitch = APRConfig.PITCH
            eps = ScoringConfig.PHASE_EPS
            residuals = []
            for s in spacings:
                k = round(s / pitch) if pitch != 0 else 0
                residuals.append(abs(s - k * pitch))
            r_bar = sum(residuals) / len(residuals)
            denom_base = ScoringConfig.PHASE_RMAX if ScoringConfig.PHASE_RMAX is not None else (pitch / 2.0)
            denom = max(denom_base, eps)
            phase_q = max(0.0, min(1.0, 1.0 - (r_bar / denom)))

        # Optional filtering
        if ScoringConfig.MAX_MEAN_SPACING is not None and mean_spacing is not None:
            if mean_spacing > ScoringConfig.MAX_MEAN_SPACING:
                logger.debug(f"APR rejected: mean spacing {mean_spacing} > max {ScoringConfig.MAX_MEAN_SPACING}")
                return
        if ScoringConfig.MAX_SPACING_VARIANCE is not None and spacing_variance is not None:
            if spacing_variance > ScoringConfig.MAX_SPACING_VARIANCE:
                logger.debug(f"APR rejected: variance {spacing_variance} > max {ScoringConfig.MAX_SPACING_VARIANCE}")
                return
        if ScoringConfig.MIN_PHASE_Q is not None and phase_q is not None:
            if phase_q < ScoringConfig.MIN_PHASE_Q:
                logger.debug(f"APR rejected: phase coherence {phase_q} < min {ScoringConfig.MIN_PHASE_Q}")
                return

        composition = (
            f"{apr_sequence.count('A')}A/"
            f"{apr_sequence.count('C')}C/"
            f"{apr_sequence.count('G')}G/"
            f"{apr_sequence.count('T')}T"
        )

        apr_entry = {
            "chr": seq_id,
            "start": start,
            "end": end,
            "strand": strand,
            "num_tracts": len(group),
            "tract_seqs": tract_seqs,
            "sequence": apr_sequence,
            "composition": composition,
            "mean_spacing": mean_spacing,
            "spacing_variance": spacing_variance,
            "phase_q": phase_q,
        }

        aprs.append(apr_entry)
        logger.debug(f"Added APR: {start}-{end}, {len(group)} tracts, strand={strand}")

    except Exception as e:
        logger.error(f"Error processing group {start}-{end}: {str(e)}")
        raise SequenceAnalysisError(f"Group processing failed: {e}")


def detect_aprs(
    a_tracts: List[Dict[str, any]],
    seq_id: str,
    full_sequence: str,
    rev_sequence: Optional[str] = None,
    num_cpus: int = 1,
) -> List[Dict]:
    """Detect A-phased repeats (APRs) from a list of A-tracts."""
    if not isinstance(a_tracts, list):
        raise TypeError(f"a_tracts must be a list, got {type(a_tracts)}")
    if not a_tracts:
        logger.info("No A-tracts provided; returning empty APR list")
        return []

    required_keys = {"start", "end", "center", "strand", "seq"}
    for tract in a_tracts:
        if not isinstance(tract, dict) or not required_keys.issubset(tract.keys()):
            raise SequenceAnalysisError(f"Each A-tract must include keys: {required_keys}")
        if tract["strand"] not in {"+", "-"}:
            raise SequenceAnalysisError(f"Invalid strand: {tract['strand']}; must be '+' or '-'")
        logger.debug(f"Tract: {tract}")

    if not isinstance(seq_id, str):
        raise TypeError(f"seq_id must be a string, got {type(seq_id)}")
    if not isinstance(full_sequence, str):
        raise TypeError(f"full_sequence must be a string, got {type(full_sequence)}")
    if not full_sequence:
        logger.warning("Empty full_sequence provided; returning empty APR list")
        return []

    try:
        APRConfig.validate()
        ScoringConfig.validate()
    except ConfigurationError as e:
        raise SequenceAnalysisError(f"Configuration error: {str(e)}")

    if APRConfig.DETECTION_MODE in {"heteropolymer", "homopolymer_mixed"}:
        valid_bases = {"A", "T"}
    elif APRConfig.DETECTION_MODE == "homopolymer":
        valid_bases = {"A"}
    else:
        valid_bases = {"T"}
    if APRConfig.HANDLE_AMBIGUOUS == "keep":
        valid_bases.update(APRConfig.AMBIGUOUS_BASES)

    rev_full_sequence = reverse_complement(full_sequence) if rev_sequence is None else rev_sequence

    for tract in a_tracts:
        start, end, center, seq = tract["start"], tract["end"], tract["center"], tract["seq"]
        ref_seq = full_sequence if tract["strand"] == "+" else rev_full_sequence
        if not (1 <= start <= end <= len(ref_seq) + 1):
            raise SequenceAnalysisError(
                f"Tract coordinates {start}-{end} out of bounds for {len(ref_seq)} bp sequence on strand {tract['strand']}"
            )
        if not isinstance(center, (int, float)) or center < 0:
            raise SequenceAnalysisError(f"Invalid center value: {center}")
        if not seq or not set(seq.upper()).issubset(valid_bases):
            raise SequenceAnalysisError(f"Tract sequence '{seq}' invalid for mode {APRConfig.DETECTION_MODE}")

    logger.info(f"Processing {len(a_tracts)} tracts for sequence {seq_id}")

    forward_tracts = [t for t in a_tracts if t["strand"] == "+"]
    reverse_tracts = [t for t in a_tracts if t["strand"] == "-"]
    aprs: List[Dict] = []

    def process_chunks(chunks):
        try:
            with Pool(processes=min(num_cpus, len(chunks))) as pool:
                results = pool.map(process_group, chunks)
            return [apr for chunk_aprs in results for apr in chunk_aprs]
        except MemoryError:
            logger.warning("MemoryError in parallel processing; falling back to sequential")
            return [apr for chunk in chunks for apr in process_group(chunk)]

    # --- Forward strand processing ---
    if forward_tracts:
        if num_cpus <= 1 or len(forward_tracts) < MIN_TRACTS_FOR_PARALLEL:
            aprs.extend(process_group((forward_tracts, full_sequence, rev_full_sequence, seq_id)))
        else:
            chunk_size = max(100, len(forward_tracts) // num_cpus)
            chunks = [
                (forward_tracts[i : i + chunk_size], full_sequence, rev_full_sequence, seq_id)
                for i in range(0, len(forward_tracts), chunk_size)
            ]
            logger.info(f"Processing {len(chunks)} forward chunks with {min(num_cpus, len(chunks))} CPUs")
            aprs.extend(process_chunks(chunks))

    # --- Reverse strand processing ---
    if APRConfig.STRAND_SELECTION == 2 and reverse_tracts:
        if num_cpus <= 1 or len(reverse_tracts) < MIN_TRACTS_FOR_PARALLEL:
            aprs.extend(process_group((reverse_tracts, full_sequence, rev_full_sequence, seq_id)))
        else:
            chunk_size = max(100, len(reverse_tracts) // num_cpus)
            chunks = [
                (reverse_tracts[i : i + chunk_size], full_sequence, rev_full_sequence, seq_id)
                for i in range(0, len(reverse_tracts), chunk_size)
            ]
            logger.info(f"Processing {len(chunks)} reverse chunks with {min(num_cpus, len(chunks))} CPUs")
            aprs.extend(process_chunks(chunks))

    # --- Transform reverse strand APRs to positive-strand coordinates ---
    seq_len = len(full_sequence)
    for apr in aprs:
        if apr["strand"] == "-":
            orig_start = apr["start"]
            orig_end = apr["end"]
            apr["start"] = seq_len - orig_end + 1
            apr["end"] = seq_len - orig_start + 1
            apr["sequence"] = reverse_complement(apr["sequence"])
            apr["tract_seqs"] = [reverse_complement(seq) for seq in apr["tract_seqs"]]
            apr["composition"] = (
                f"{apr['sequence'].count('A')}A/"
                f"{apr['sequence'].count('C')}C/"
                f"{apr['sequence'].count('G')}G/"
                f"{apr['sequence'].count('T')}T"
            )
            logger.debug(
                f"Transformed reverse APR to positive coordinates: {apr['start']}-{apr['end']} (len={seq_len})"
            )

    # --- Final sanity check: remove APRs containing ambiguous bases (N) ---
    if APRConfig.HANDLE_AMBIGUOUS != "keep":
        before_count = len(aprs)
        aprs = [apr for apr in aprs if not (set(apr["sequence"]) & APRConfig.AMBIGUOUS_BASES)]
        removed = before_count - len(aprs)
        if removed > 0:
            logger.info(f"Filtered {removed} APRs with ambiguous bases due to HANDLE_AMBIGUOUS={APRConfig.HANDLE_AMBIGUOUS}")

    if APRConfig.MERGE_APRS:
        before_merge = len(aprs)
        aprs = merge_apr_records(aprs)
        logger.info(f"Merged APRs for {seq_id}: {before_merge} -> {len(aprs)}")
    else:
        logger.info(f"Merging disabled; returning {len(aprs)} APRs for sequence {seq_id}")

    return sorted(aprs, key=lambda x: (x["start"], x["end"], x["strand"]))
