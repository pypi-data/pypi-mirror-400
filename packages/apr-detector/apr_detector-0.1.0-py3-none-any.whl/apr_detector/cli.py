import logging
import os
import sys
import csv
from typing import List, Dict, Optional
from datetime import datetime
from statistics import mean, median
import time

from apr_detector.config.config import APRConfig, ConfigurationError
from apr_detector.core.sequence import read_fasta, validate_raw_sequence
from apr_detector.core.tract import find_a_tracts
from apr_detector.core.detector import detect_aprs
from apr_detector.core.scoring import ScoringConfig, TARestartDetector
from apr_detector.core.exceptions import SequenceAnalysisError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Project authorship metadata (used in logs and output headers)
AUTHORS = "Hamza Mohammed and Josep Comeron, PhD (University of Iowa)"
AUTHOR_CONTACTS = "mohammed-hamza@uiowa.edu; hamzamohammed1445@gmail.com; josep-comeron@uiowa.edu"


def _safe_mean(values: List[float]) -> Optional[float]:
    return mean(values) if values else None


def _safe_median(values: List[float]) -> Optional[float]:
    return median(values) if values else None


def _fmt(val) -> str:
    if val is None:
        return ""
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def log_run_settings() -> None:
    """Log a single, flag-oriented summary of the current run configuration."""
    params = [
        f"MODEL={APRConfig.MODEL_NAME}",
        f"-w (spacing window)={APRConfig.SPACING_WINDOW} [{APRConfig.get_min_spacing()}-{APRConfig.get_max_spacing()} bp]",
        f"-l (min nt in tract)={APRConfig.MIN_NT_IN_TRACT}",
        f"-t (tracts in APR)={APRConfig.MIN_NUM_TRACTS}",
        f"-p (pitch)={APRConfig.PITCH}",
        f"-n (handle ambiguous bases)={APRConfig.HANDLE_AMBIGUOUS}",
        f"-y (symmetry mode)={ScoringConfig.SYMMETRY_MODE}",
        f"-ta (allow TA in tracts)={ScoringConfig.ALLOW_TA_IN_TRACTS}",
        f"-u (max mean)={ScoringConfig.MAX_MEAN_SPACING}",
        f"-v (max variance)={ScoringConfig.MAX_SPACING_VARIANCE}",
        f"-q (min phase coherence)={ScoringConfig.MIN_PHASE_Q}",
        f"-s (strand selection)={APRConfig.STRAND_SELECTION}",
        f"-m (merge APRs)={APRConfig.MERGE_APRS}",
        f"-g (write GFF)={APRConfig.WRITE_GFF}",
        f"-b (write BED)={APRConfig.WRITE_BED}",
        f"--csv (write APR CSV)={APRConfig.WRITE_CSV}",
        f"--tracts (write tracts CSV)={APRConfig.WRITE_TRACTS_CSV}",
        f"--tracts-tsv (write tracts TSV)={APRConfig.WRITE_TRACTS_TSV}",
        f"--summary (write per-sequence summary TSV)={APRConfig.WRITE_SUMMARY}",
    ]
    logger.info("Run settings: " + " | ".join(params))


def setup_logging(output_dir: str, base_name: str, no_timestamp: bool = False) -> str:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    timestamp = "" if no_timestamp else "_" + datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(output_dir, f"{base_name}{timestamp}.log")

    if logger.hasHandlers():
        logger.handlers.clear()

    fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return log_file


def write_apr_output(aprs: List[Dict], output_file: str, source: str = "APR_Detector") -> None:
    if not aprs:
        logger.warning(f"No APRs to write to {output_file}")
        return

    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

        with open(output_file, 'w', encoding='utf-8') as f:
            params = [
                f"MODEL={APRConfig.MODEL_NAME}",
                f"-t (tracts in APR)={APRConfig.MIN_NUM_TRACTS}",
                f"-w (spacing window)={APRConfig.SPACING_WINDOW} [{APRConfig.get_min_spacing()}-{APRConfig.get_max_spacing()} bp]",
                f"-l (min nt in tract)={APRConfig.MIN_NT_IN_TRACT}",
                f"-p (pitch)={APRConfig.PITCH}",
                f"-n (handle ambiguous bases)={APRConfig.HANDLE_AMBIGUOUS}",
                f"-y (symmetry mode)={ScoringConfig.SYMMETRY_MODE}",
                f"-ta (allow TA in tracts)={ScoringConfig.ALLOW_TA_IN_TRACTS}",
                f"-u (max mean)={ScoringConfig.MAX_MEAN_SPACING}",
                f"-v (max variance)={ScoringConfig.MAX_SPACING_VARIANCE}",
                f"-q (min phase coherence)={ScoringConfig.MIN_PHASE_Q}",
                f"-s (strand selection)={APRConfig.STRAND_SELECTION}",
                f"-m (merge APRs)={APRConfig.MERGE_APRS}",
                f"-g (write GFF)={APRConfig.WRITE_GFF}",
                f"-b (write BED)={APRConfig.WRITE_BED}",
                f"--csv (write APR CSV)={APRConfig.WRITE_CSV}",
                f"-tracts (write tracts CSV)={APRConfig.WRITE_TRACTS_CSV}",
                f"-tracts-tsv (write tracts TSV)={APRConfig.WRITE_TRACTS_TSV}",
            ]
            f.write("# " + " | ".join(params) + "\n")

            header = [
                "Sequence_name", "Source", "Start", "Stop", "Length", "Strand",
                "Tract_count", "Tracts", "Composition", "Sequence",
                "Mean_spacing", "Spacing_variance", "Phase_Coherence"
            ]
            f.write("\t".join(header) + "\n")

            for apr in aprs:
                tracts = ";".join(apr['tract_seqs'])
                mean_spacing = "" if apr.get("mean_spacing") is None else str(apr.get("mean_spacing"))
                spacing_variance = "" if apr.get("spacing_variance") is None else str(apr.get("spacing_variance"))
                phase_q = "" if apr.get("phase_q") is None else str(apr.get("phase_q"))
                line = [
                    str(apr['chr']),
                    source,
                    str(apr['start']),
                    str(apr['end']),
                    str(apr['end'] - apr['start'] + 1),
                    apr['strand'],
                    str(apr['num_tracts']),
                    tracts,
                    apr['composition'],
                    apr['sequence'],
                    mean_spacing,
                    spacing_variance,
                    phase_q,
                ]
                f.write("\t".join(line) + "\n")

        logger.info(f"Wrote {len(aprs)} APRs to {output_file}")
    except IOError as e:
        logger.error(f"Failed to write output to {output_file}: {str(e)}")
        raise SequenceAnalysisError(f"Output writing failed: {e}")


def write_apr_csv(aprs: List[Dict], output_file: str, source: str = "APR_Detector") -> None:
    if not aprs:
        logger.warning(f"No APRs to write to {output_file}")
        return
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        header = [
            "Sequence_name", "Source", "Start", "Stop", "Length", "Strand",
            "Tract_count", "Tracts", "Composition", "Sequence",
            "Mean_spacing", "Spacing_variance", "Phase_Coherence"
        ]
        with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            params = [
                f"MODEL={APRConfig.MODEL_NAME}",
                f"-t (tracts in APR)={APRConfig.MIN_NUM_TRACTS}",
                f"-w (spacing window)={APRConfig.SPACING_WINDOW} [{APRConfig.get_min_spacing()}-{APRConfig.get_max_spacing()} bp]",
                f"-l (min nt in tract)={APRConfig.MIN_NT_IN_TRACT}",
                f"-p (pitch)={APRConfig.PITCH}",
                f"-n (handle ambiguous bases)={APRConfig.HANDLE_AMBIGUOUS}",
                f"-ta (allow TA in tracts)={ScoringConfig.ALLOW_TA_IN_TRACTS}",
                f"-u (max mean)={ScoringConfig.MAX_MEAN_SPACING}",
                f"-v (max variance)={ScoringConfig.MAX_SPACING_VARIANCE}",
                f"-q (min phase coherence)={ScoringConfig.MIN_PHASE_Q}",
                f"-s (strand selection)={APRConfig.STRAND_SELECTION}",
                f"-m (merge APRs)={APRConfig.MERGE_APRS}",
                f"-g (write GFF)={APRConfig.WRITE_GFF}",
                f"-b (write BED)={APRConfig.WRITE_BED}",
            ]
            writer.writerow(["# " + " | ".join(params)])
            writer.writerow(header)
            for apr in aprs:
                tracts = ";".join(apr['tract_seqs'])
                writer.writerow([
                    str(apr['chr']),
                    source,
                    str(apr['start']),
                    str(apr['end']),
                    str(apr['end'] - apr['start'] + 1),
                    apr['strand'],
                    str(apr['num_tracts']),
                    tracts,
                    apr['composition'],
                    apr['sequence'],
                    "" if apr.get("mean_spacing") is None else apr.get("mean_spacing"),
                    "" if apr.get("spacing_variance") is None else apr.get("spacing_variance"),
                    "" if apr.get("phase_q") is None else apr.get("phase_q"),
                ])
        logger.info(f"Wrote {len(aprs)} APRs to {output_file}")
    except IOError as e:
        logger.error(f"Failed to write APR CSV to {output_file}: {str(e)}")
        raise SequenceAnalysisError(f"APR CSV writing failed: {e}")


def write_gff_output(aprs: List[Dict], output_file: str, source: str = "APR_Detector") -> None:
    """Write APRs in GFF3 format (1-based inclusive)."""
    if not aprs:
        logger.warning(f"No APRs to write to {output_file}")
        return

    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("##gff-version 3\n")
            for idx, apr in enumerate(aprs, start=1):
                attributes = [
                    f"ID=APR_{idx}",
                    f"NumTracts={apr['num_tracts']}",
                    f"Tracts={','.join(apr['tract_seqs'])}",
                    f"Composition={apr['composition']}",
                ]
                if apr.get("mean_spacing") is not None:
                    attributes.append(f"MeanSpacing={apr['mean_spacing']}")
                if apr.get("spacing_variance") is not None:
                    attributes.append(f"SpacingVariance={apr['spacing_variance']}")
                if apr.get("phase_q") is not None:
                    attributes.append(f"PhaseCoherence={apr['phase_q']}")
                fields = [
                    str(apr["chr"]),
                    source,
                    "APR",
                    str(apr["start"]),
                    str(apr["end"]),
                    ".",
                    apr["strand"] if apr["strand"] else ".",
                    ".",
                    ";".join(attributes)
                ]
                f.write("\t".join(fields) + "\n")
        logger.info(f"Wrote {len(aprs)} APRs to {output_file}")
    except IOError as e:
        logger.error(f"Failed to write GFF output to {output_file}: {str(e)}")
        raise SequenceAnalysisError(f"GFF output writing failed: {e}")


def write_bed_output(aprs: List[Dict], output_file: str, source: str = "APR_Detector") -> None:
    """Write APRs in BED6 format (0-based start, end-exclusive)."""
    if not aprs:
        logger.warning(f"No APRs to write to {output_file}")
        return

    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'w', encoding='utf-8') as f:
            for idx, apr in enumerate(aprs, start=1):
                chrom_start = max(0, apr["start"] - 1)
                chrom_end = apr["end"]
                name = f"APR_{idx}"
                score = str(apr["num_tracts"])
                strand = apr["strand"] if apr["strand"] else "."
                fields = [str(apr["chr"]), str(chrom_start), str(chrom_end), name, score, strand]
                f.write("\t".join(fields) + "\n")
        logger.info(f"Wrote {len(aprs)} APRs to {output_file}")
    except IOError as e:
        logger.error(f"Failed to write BED output to {output_file}: {str(e)}")
        raise SequenceAnalysisError(f"BED output writing failed: {e}")


def process_fasta_file(
    fasta_file: str,
    output_dir: str,
    num_cpus: int = 1,
    output_prefix: Optional[str] = None,
    no_timestamp: bool = False,
    tracts_csv_override: Optional[str] = None,
    tracts_tsv_override: Optional[str] = None,
    apr_csv_override: Optional[str] = None,
) -> None:
    if not os.path.exists(fasta_file):
        logger.error(f"FASTA file does not exist: {fasta_file}")
        raise SequenceAnalysisError(f"FASTA file not found: {fasta_file}")

    base_name = output_prefix or os.path.splitext(os.path.basename(fasta_file))[0]
    log_file = setup_logging(output_dir, base_name, no_timestamp)
    logger.info(f"Log file: {log_file}")
    logger.info(f"Processing FASTA file: {fasta_file} with {num_cpus} CPUs")

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') if not no_timestamp else None
        APRConfig.validate()
        ScoringConfig.validate()
        log_run_settings()
        write_apr_csv = bool(APRConfig.WRITE_CSV or apr_csv_override)
        write_tracts_csv = bool(APRConfig.WRITE_TRACTS_CSV or tracts_csv_override)
        write_tracts_tsv = bool(APRConfig.WRITE_TRACTS_TSV or tracts_tsv_override)
        sequences = read_fasta(fasta_file, num_cpus)
        logger.info(f"Number of sequences: {len(sequences)}")
        declared_sequences = len(sequences)
        processed_sequences = 0
        # Prepare tract writers (streaming, no buffering)
        tract_csv_writer = None
        tract_csv_handle = None
        tract_tsv_handle = None
        if write_tracts_csv:
            tracts_name = tracts_csv_override if tracts_csv_override else f"{base_name}_tracts.csv"
            if timestamp and not tracts_csv_override:
                tracts_name = f"{base_name}_{timestamp}_tracts.csv"
            tracts_path = tracts_name if os.path.isabs(tracts_name) else os.path.join(output_dir, tracts_name)
            header = [
                "sequence",
                "start",
                "end",
                "length",
                "center",
                "strand",
                "sequence_bases",
                "is_symmetrical",
                "detection_mode",
                "symmetry_mode",
                "allow_ta_in_tracts",
            ]
            try:
                os.makedirs(os.path.dirname(tracts_path), exist_ok=True) if os.path.dirname(tracts_path) else None
                tract_csv_handle = open(tracts_path, "w", encoding="utf-8", newline="")
                tract_csv_writer = csv.writer(tract_csv_handle)
                tract_csv_writer.writerow(header)
            except IOError as e:
                logger.error(f"Failed to open tracts CSV for writing: {e}")
                tract_csv_handle = None
                tract_csv_writer = None
        if write_tracts_tsv:
            tracts_name_tsv = tracts_tsv_override if tracts_tsv_override else f"{base_name}_tracts.tsv"
            if timestamp and not tracts_tsv_override:
                tracts_name_tsv = f"{base_name}_{timestamp}_tracts.tsv"
            tracts_path_tsv = tracts_name_tsv if os.path.isabs(tracts_name_tsv) else os.path.join(output_dir, tracts_name_tsv)
            header_tsv = [
                "sequence",
                "start",
                "end",
                "length",
                "center",
                "strand",
                "sequence_bases",
                "is_symmetrical",
                "detection_mode",
                "symmetry_mode",
                "allow_ta_in_tracts",
            ]
            try:
                os.makedirs(os.path.dirname(tracts_path_tsv), exist_ok=True) if os.path.dirname(tracts_path_tsv) else None
                tract_tsv_handle = open(tracts_path_tsv, "w", encoding="utf-8", newline="")
                tract_tsv_handle.write("\t".join(header_tsv) + "\n")
            except IOError as e:
                logger.error(f"Failed to open tracts TSV for writing: {e}")
                tract_tsv_handle = None
        summary_columns = [
            "species",
            "sequence_bp_total",
            "at_bp_total",
            "gc_bp_total",
            "ambiguous_bp_total",
            "aprs_total",
            "apr_bp_total",
            "avg_apr_len",
            "median_apr_len",
            "max_apr_len",
            "mean_spacing_mean",
            "mean_spacing_median",
            "mean_spacing_min",
            "mean_spacing_max",
            "spacing_variance_mean",
            "spacing_variance_median",
            "spacing_variance_min",
            "spacing_variance_max",
            "phase_coherence_mean",
            "phase_coherence_median",
            "phase_coherence_pass",
            "tracts_total",
            "avg_tract_len",
            "median_tract_len",
            "max_tract_len",
            "tract_a_percent",
            "tract_t_percent",
            "runtime_seconds",
            "runtime_per_Mb",
            "declared_sequences",
            "processed_sequences",
            "APRs_per_Mb",
            "tracts_per_Mb",
            "at_percent",
            "gc_percent",
            "ambiguous_percent",
            "apr_per_ATMb",
            "tracts_per_ATMb",
        ]
        summary_header_logged = False
        summary_rows: List[List[str]] = []

        all_aprs = []
        for seq_id, sequence, metadata, rev_sequence in sequences:
            logger.info(f"Processing sequence: {seq_id}")
            seq_start_time = time.perf_counter()

            processed_sequence, seq_metadata, rev_seq = validate_raw_sequence(sequence, num_cpus)
            logger.info(f"Validated sequence: Original {seq_metadata['original_length']:,}bp, "
                        f"Final {seq_metadata['final_length']:,}bp, N count: {seq_metadata['n_count']:,}")

            try:
                a_tracts = find_a_tracts(processed_sequence, num_cpus, rev_seq)
            except SequenceAnalysisError as e:
                logger.error(f"Failed to find A-tracts for {seq_id}: {str(e)}")
                continue

            if tract_csv_writer or tract_tsv_handle:
                for t in a_tracts:
                    length = t["end"] - t["start"] + 1
                    row = [
                        seq_id,
                        t["start"],
                        t["end"],
                        length,
                        t.get("center", ""),
                        t["strand"],
                        t["seq"],
                        t.get("is_symmetrical", ""),
                        APRConfig.DETECTION_MODE,
                        ScoringConfig.SYMMETRY_MODE,
                        ScoringConfig.ALLOW_TA_IN_TRACTS,
                    ]
                    if tract_csv_writer:
                        try:
                            tract_csv_writer.writerow(row)
                        except IOError as e:
                            logger.error(f"Failed to write tracts CSV row: {e}")
                            tract_csv_writer = None
                    if tract_tsv_handle:
                        try:
                            tract_tsv_handle.write("\t".join(str(x) for x in row) + "\n")
                        except IOError as e:
                            logger.error(f"Failed to write tracts TSV row: {e}")
                            tract_tsv_handle = None

            try:
                aprs = detect_aprs(a_tracts, seq_id, processed_sequence, rev_seq, num_cpus)
                all_aprs.extend(aprs)
            except SequenceAnalysisError as e:
                logger.error(f"Failed to detect APRs for {seq_id}: {str(e)}")
                continue
            processed_sequences += 1

            # --- Per-sequence summary metrics ---
            elapsed = time.perf_counter() - seq_start_time
            species = (seq_id.split()[0] if seq_id else "NA")
            sequence_bp_total = len(processed_sequence)
            at_bp_total = processed_sequence.count("A") + processed_sequence.count("T")
            gc_bp_total = processed_sequence.count("G") + processed_sequence.count("C")
            ambiguous_bp_total = sequence_bp_total - (at_bp_total + gc_bp_total)

            apr_lengths = [apr["end"] - apr["start"] + 1 for apr in aprs]
            apr_bp_total = sum(apr_lengths)
            mean_spacings = [apr["mean_spacing"] for apr in aprs if apr.get("mean_spacing") is not None]
            spacing_vars = [apr["spacing_variance"] for apr in aprs if apr.get("spacing_variance") is not None]
            phase_qs = [apr["phase_q"] for apr in aprs if apr.get("phase_q") is not None]
            phase_threshold = ScoringConfig.MIN_PHASE_Q
            phase_q_pass = sum(1 for q in phase_qs if phase_threshold is None or q >= phase_threshold)

            tracts_total = len(a_tracts)
            tract_lengths = [len(t["seq"]) for t in a_tracts]
            tract_a_bases = sum(t["seq"].count("A") for t in a_tracts)
            tract_t_bases = sum(t["seq"].count("T") for t in a_tracts)
            tract_base_total = tract_a_bases + tract_t_bases

            aprs_per_mb = (aprs_total := len(aprs)) * 1_000_000 / sequence_bp_total if sequence_bp_total else 0.0
            tracts_per_mb = tracts_total * 1_000_000 / sequence_bp_total if sequence_bp_total else 0.0
            apr_per_atmb = aprs_total * 1_000_000 / at_bp_total if at_bp_total else 0.0
            tracts_per_atmb = tracts_total * 1_000_000 / at_bp_total if at_bp_total else 0.0

            at_percent = (at_bp_total / sequence_bp_total * 100) if sequence_bp_total else 0.0
            gc_percent = (gc_bp_total / sequence_bp_total * 100) if sequence_bp_total else 0.0
            ambig_percent = (ambiguous_bp_total / sequence_bp_total * 100) if sequence_bp_total else 0.0

            runtime_per_mb = elapsed / (sequence_bp_total / 1_000_000) if sequence_bp_total else None

            row = [
                species,
                sequence_bp_total,
                at_bp_total,
                gc_bp_total,
                ambiguous_bp_total,
                aprs_total,
                apr_bp_total,
                _safe_mean(apr_lengths),
                _safe_median(apr_lengths),
                max(apr_lengths) if apr_lengths else None,
                _safe_mean(mean_spacings),
                _safe_median(mean_spacings),
                min(mean_spacings) if mean_spacings else None,
                max(mean_spacings) if mean_spacings else None,
                _safe_mean(spacing_vars),
                _safe_median(spacing_vars),
                min(spacing_vars) if spacing_vars else None,
                max(spacing_vars) if spacing_vars else None,
                _safe_mean(phase_qs),
                _safe_median(phase_qs),
                phase_q_pass,
                tracts_total,
                _safe_mean(tract_lengths),
                _safe_median(tract_lengths),
                max(tract_lengths) if tract_lengths else None,
                (tract_a_bases / tract_base_total * 100) if tract_base_total else None,
                (tract_t_bases / tract_base_total * 100) if tract_base_total else None,
                elapsed,
                runtime_per_mb,
                declared_sequences,
                processed_sequences,
                aprs_per_mb,
                tracts_per_mb,
                at_percent,
                gc_percent,
                ambig_percent,
                apr_per_atmb,
                tracts_per_atmb,
            ]
            if not summary_header_logged:
                logger.info("SUMMARY\t" + "\t".join(summary_columns))
                summary_header_logged = True
            logger.info("SUMMARY\t" + "\t".join(_fmt(v) for v in row))
            summary_rows.append([_fmt(v) for v in row])

        output_filename = f"{base_name}_APRs.tsv"
        if timestamp:
            output_filename = f"{base_name}_{timestamp}_APRs.tsv"
        output_file = os.path.join(output_dir, output_filename)

        write_apr_output(all_aprs, output_file)
        base_no_ext, _ = os.path.splitext(output_file)
        if APRConfig.WRITE_GFF:
            write_gff_output(all_aprs, base_no_ext + ".gff")
        if APRConfig.WRITE_BED:
            write_bed_output(all_aprs, base_no_ext + ".bed")
        if write_apr_csv:
            apr_csv_name = apr_csv_override if apr_csv_override else f"{base_name}_APRs.csv"
            if timestamp and not apr_csv_override:
                apr_csv_name = f"{base_name}_{timestamp}_APRs.csv"
            apr_csv_path = apr_csv_name if os.path.isabs(apr_csv_name) else os.path.join(output_dir, apr_csv_name)
            write_apr_csv(all_aprs, apr_csv_path)
        if tract_csv_handle:
            try:
                tract_csv_handle.close()
            except IOError as e:
                logger.error(f"Failed to close tracts CSV: {e}")
        if tract_tsv_handle:
            try:
                tract_tsv_handle.close()
            except IOError as e:
                logger.error(f"Failed to close tracts TSV: {e}")
        # Write per-sequence summary TSV
        try:
            summary_name = f"{base_name}_summary.tsv"
            if timestamp:
                summary_name = f"{base_name}_{timestamp}_summary.tsv"
            summary_path = summary_name if os.path.isabs(summary_name) else os.path.join(output_dir, summary_name)
            with open(summary_path, "w", encoding="utf-8", newline="") as summary_file:
                summary_file.write("\t".join(summary_columns) + "\n")
                for row in summary_rows:
                    summary_file.write("\t".join(str(v) for v in row) + "\n")
            logger.info(f"Wrote summary statistics to {summary_path}")
        except IOError as e:
            logger.error(f"Failed to write summary TSV: {e}")
        logger.info(f"Finished processing. Total APRs detected: {len(all_aprs)}")
        logger.info(f"Authors: {AUTHORS} | Contacts: {AUTHOR_CONTACTS}")
    except SequenceAnalysisError as e:
        logger.error(f"Processing failed: {str(e)}")
        raise

def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Detect A-phased repeats (APRs) in a FASTA file.")
    parser.add_argument("model", nargs='?', default="Model2", help="Model prefix (default: Model2)")
    parser.add_argument("fasta", nargs='?', help="Input FASTA file (can be overridden with -i)")
    parser.add_argument("output_dir", nargs='?', help="Output directory (can be overridden with -o)")
    parser.add_argument("-i", "--input", help="Input FASTA file (alternative to positional argument)")
    parser.add_argument("-o", "--output", help="Output directory (alternative to positional argument)")
    parser.add_argument("-l", "--min_nt_in_tract", type=int, default=4)
    parser.add_argument("-t", "--min_num_tracts", type=int, default=3)
    parser.add_argument("-w", "--spacing_window", type=float, default=0.5)
    parser.add_argument("-p", "--pitch", type=float, default=10.5, help="Helical pitch in bp for phase coherence (default 10.5)")
    parser.add_argument(
        "-n", "-N", "--handle_ambiguous",
        type=int,
        default=None,
        help="Ambiguous base handling: 0=remove/exclude, 1=keep/include (default), 2=error; if omitted or flag-only, use default"
    )
    parser.add_argument(
        "-y", "--enable_symmetrical_tracts",
        nargs="?",
        const=None,
        type=int,
        default=None,
        help="Symmetry: 1=include, 0=exclude, 2=only symmetrical (ignored for Model3)"
    )
    parser.add_argument(
        "-m", "--merge_aprs",
        nargs="?",
        const=None,
        type=int,
        default=None,
        help="Merge APRs with identical/contained coords: 1=merge (default), 0=do not merge"
    )
    parser.add_argument(
        "-ta", "--ta",
        type=int,
        choices=[0, 1],
        default=1,
        help="Allow TA dinucleotide inside tract sequences: 1=allow (default), 0=disallow"
    )
    parser.add_argument("-u", "--max_mean", type=float, default=None, help="Max mean spacing (bp) for APR retention")
    parser.add_argument("-v", "--max_var", type=float, default=None, help="Max spacing variance (bp^2) for APR retention")
    parser.add_argument("-q", "--min_phase_q", type=float, default=None, help="Min phase coherence (0-1) for APR retention")
    parser.add_argument("-s", "--strand_selection", type=int, choices=[1, 2], default=1)
    parser.add_argument("-nt", "--no_timestamp", action="store_true")
    parser.add_argument("-c", "--num_cpus", type=int, default=1)
    parser.add_argument("-g", "--gff", action="store_true", help="Also write GFF3 output")
    parser.add_argument("-b", "--bed", action="store_true", help="Also write BED output")
    parser.add_argument(
        "--csv",
        nargs="?",
        const=True,
        default=False,
        help="Also write APRs to CSV (optional path override for filename)"
    )
    parser.add_argument(
        "--tracts",
        nargs="?",
        const=True,
        default=False,
        help="Write candidate tracts to CSV (optional path override for filename)"
    )
    parser.add_argument(
        "--tracts-tsv",
        nargs="?",
        const=True,
        default=False,
        help="Write candidate tracts to TSV (optional path override for filename)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Write per-sequence summary TSV"
    )
    args = parser.parse_args(argv)

    fasta_file = args.input or args.fasta
    output_dir = args.output or args.output_dir

    if not fasta_file or not output_dir:
        parser.print_help()
        sys.exit(1)

    APRConfig.MIN_NT_IN_TRACT = args.min_nt_in_tract
    APRConfig.MIN_NUM_TRACTS = args.min_num_tracts
    APRConfig.SPACING_WINDOW = args.spacing_window
    APRConfig.PITCH = args.pitch

    if args.handle_ambiguous is None:
        APRConfig.HANDLE_AMBIGUOUS = getattr(APRConfig, "HANDLE_AMBIGUOUS", "keep")
    else:
        amb_map = {0: "remove", 1: "keep", 2: "error"}
        if args.handle_ambiguous not in amb_map:
            parser.error("Invalid --handle_ambiguous value; use 0 (remove/exclude), 1 (keep/include), or 2 (error)")
        APRConfig.HANDLE_AMBIGUOUS = amb_map[args.handle_ambiguous]

    # Symmetry handling: 1/include, 0/exclude, 2/only (ignored in Model3)
    if args.enable_symmetrical_tracts is None:
        ScoringConfig.SYMMETRY_MODE = getattr(ScoringConfig, "SYMMETRY_MODE", "include")
    else:
        sym_map = {0: "exclude", 1: "include", 2: "only"}
        if args.enable_symmetrical_tracts not in sym_map:
            parser.error("Invalid -y/--enable_symmetrical_tracts value; use 0, 1, or 2")
        ScoringConfig.SYMMETRY_MODE = sym_map[args.enable_symmetrical_tracts]

    # Merge control
    if args.merge_aprs is None:
        APRConfig.MERGE_APRS = getattr(APRConfig, "MERGE_APRS", True)
    else:
        if args.merge_aprs not in (0, 1):
            parser.error("Invalid -m/--merge_aprs value; use 0 or 1")
        APRConfig.MERGE_APRS = bool(args.merge_aprs)

    ScoringConfig.ALLOW_TA_IN_TRACTS = bool(args.ta)
    ScoringConfig.MAX_MEAN_SPACING = args.max_mean
    ScoringConfig.MAX_SPACING_VARIANCE = args.max_var
    ScoringConfig.MIN_PHASE_Q = args.min_phase_q

    APRConfig.STRAND_SELECTION = args.strand_selection
    APRConfig.WRITE_GFF = args.gff or APRConfig.WRITE_GFF
    APRConfig.WRITE_BED = args.bed or APRConfig.WRITE_BED
    if args.csv is True:
        APRConfig.WRITE_CSV = True
        apr_csv_override = None
    elif isinstance(args.csv, str):
        APRConfig.WRITE_CSV = True
        apr_csv_override = args.csv
    else:
        APRConfig.WRITE_CSV = getattr(APRConfig, "WRITE_CSV", False)
        apr_csv_override = None
    if args.tracts is True:
        APRConfig.WRITE_TRACTS_CSV = True
        tracts_csv_override = None
    elif isinstance(args.tracts, str):
        APRConfig.WRITE_TRACTS_CSV = True
        tracts_csv_override = args.tracts
    else:
        APRConfig.WRITE_TRACTS_CSV = getattr(APRConfig, "WRITE_TRACTS_CSV", False)
        tracts_csv_override = None
    if args.tracts_tsv is True:
        APRConfig.WRITE_TRACTS_TSV = True
        tracts_tsv_override = None
    elif isinstance(args.tracts_tsv, str):
        APRConfig.WRITE_TRACTS_TSV = True
        tracts_tsv_override = args.tracts_tsv
    else:
        APRConfig.WRITE_TRACTS_TSV = getattr(APRConfig, "WRITE_TRACTS_TSV", False)
        tracts_tsv_override = None
    APRConfig.WRITE_SUMMARY = bool(args.summary or getattr(APRConfig, "WRITE_SUMMARY", False))

    from apr_detector.core.tract import validate_sequence
    validate_sequence.cache_clear()

    model_input = args.model or "Model2"
    model_str = model_input.strip()
    model_norm = model_str.lower()
    model_label = model_str if model_str else "Model2"

    # Reset model-specific toggles each run
    ScoringConfig.ENABLE_TA_RESTART = False
    ScoringConfig.TA_RESTART_MODE = False
    ScoringConfig.EXCLUDE_HOMOPOLYMER_IN_HETERO = False

    if model_norm.startswith("model"):
        if model_norm.startswith("model1"):
            has_a = 'a' in model_norm
            has_b = 'b' in model_norm
            if has_a and has_b:
                logger.info("Model1 with both 'a' and 'b' suffixes detected; defaulting to T-only tracts (b).")

            if has_b:
                APRConfig.DETECTION_MODE = "homopolymer_t"
                model_label = "Model1b"
            elif has_a:
                APRConfig.DETECTION_MODE = "homopolymer"
                model_label = "Model1a"
            else:
                APRConfig.DETECTION_MODE = "homopolymer_mixed"  # pure A or pure T tracts; APRs can mix
                model_label = "Model1"

            if has_a and not has_b:
                ScoringConfig.EXCLUDE_TPA_IN_SPACERS = True
        elif model_norm.startswith("model2"):
            APRConfig.DETECTION_MODE = "heteropolymer"
            model_label = "Model2"
            if 'a' in model_norm:
                ScoringConfig.EXCLUDE_TPA_IN_SPACERS = False
                ScoringConfig.EXCLUDE_HOMOPOLYMER_IN_HETERO = True  # skip pure A/T tracts
                model_label = "Model2a"
                logger.info("Model2a selected: heteropolymer-only tracts (pure A/T dropped).")
            if 'b' in model_norm:
                ScoringConfig.SYMMETRY_MODE = "only"
                model_label = "Model2b"
                logger.info("Model2b selected: symmetry mode forced to 'only' for heteropolymer tracts.")
        elif model_norm.startswith("model3"):
            APRConfig.DETECTION_MODE = "heteropolymer"
            model_label = "Model3"
            ScoringConfig.ENABLE_TA_RESTART = True
        else:
            logger.error(f"Invalid model prefix: {model_str}")
            sys.exit(1)

    APRConfig.MODEL_NAME = model_label
    logger.info(f"Selected model: {APRConfig.MODEL_NAME}")

    # TA-restart mode trigger
    ScoringConfig.TA_RESTART_MODE = bool(ScoringConfig.ENABLE_TA_RESTART)

    try:
        if ScoringConfig.TA_RESTART_MODE:
            # TA-restart detector path
            seq_id = None
            seq_parts = []
            APRConfig.validate()
            ScoringConfig.validate()
            with open(fasta_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(">"):
                        if seq_id is None:
                            seq_id = line[1:].split()[0]
                        continue
                    seq_parts.append(line)
            if seq_id is None:
                logger.error("FASTA missing header")
                sys.exit(1)
            sequence = "".join(seq_parts)
            det = TARestartDetector(sequence)
            reps = det.find_aprs(APRConfig.MIN_NT_IN_TRACT, APRConfig.MAX_TRACT_LENGTH, APRConfig.MIN_NUM_TRACTS)
            base_name = os.path.splitext(os.path.basename(fasta_file))[0]
            log_file = setup_logging(output_dir, base_name, args.no_timestamp)
            log_run_settings()
            aprs = []
            for rep in reps:
                start = rep.start
                end = rep.end
                seq_slice = sequence[start - 1 : end]
                composition = (
                    f"{seq_slice.count('A')}A/"
                    f"{seq_slice.count('C')}C/"
                    f"{seq_slice.count('G')}G/"
                    f"{seq_slice.count('T')}T"
                )
                aprs.append(
                    {
                        "chr": seq_id,
                        "start": start,
                        "end": end,
                        "strand": ".",
                        "num_tracts": rep.num,
                        "tract_seqs": [],
                        "composition": composition,
                        "sequence": seq_slice,
                    }
                )
            output_filename = f"{base_name}_APRs.tsv"
            output_file = os.path.join(output_dir, output_filename)
            write_apr_output(aprs, output_file)
            base_no_ext, _ = os.path.splitext(output_file)
            if APRConfig.WRITE_GFF:
                write_gff_output(aprs, base_no_ext + ".gff")
            if APRConfig.WRITE_BED:
                write_bed_output(aprs, base_no_ext + ".bed")
            if APRConfig.WRITE_CSV:
                apr_csv_name = apr_csv_override if apr_csv_override else f"{base_name}_APRs.csv"
                if not args.no_timestamp and apr_csv_override is None:
                    apr_csv_name = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_APRs.csv"
                apr_csv_path = apr_csv_name if os.path.isabs(apr_csv_name) else os.path.join(output_dir, apr_csv_name)
                write_apr_csv(aprs, apr_csv_path)
            logger.info(f"Finished processing. Total APRs detected: {len(aprs)}")
            logger.info(f"Authors: {AUTHORS} | Contacts: {AUTHOR_CONTACTS}")
        else:
            process_fasta_file(
                fasta_file=fasta_file,
                output_dir=output_dir,
                num_cpus=args.num_cpus,
                no_timestamp=args.no_timestamp,
                tracts_csv_override=tracts_csv_override,
                tracts_tsv_override=tracts_tsv_override,
                apr_csv_override=apr_csv_override,
            )
    except SequenceAnalysisError as e:
        logger.error(f"APR detection failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    raise SystemExit(main())
