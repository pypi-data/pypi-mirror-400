### core/sequence.py
# This module includes functions for reading FASTA files,

import re
import os
from typing import Tuple, List, Dict, Set, Optional
from multiprocessing import Pool
from functools import lru_cache
import logging

from ..config.config import APRConfig, ConfigurationError
from .exceptions import SequenceAnalysisError
from .complement import reverse_complement

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Minimum number of sequences for parallel processing
MIN_SEQUENCES_FOR_PARALLEL = 10

@lru_cache(maxsize=1024)
def normalize_sequence(raw_sequence: str) -> str:
    """
    Normalize a raw sequence by removing whitespace and converting to uppercase.

    Args:
        raw_sequence: Input sequence string.

    Returns:
        str: Normalized sequence.

    Raises:
        SequenceAnalysisError: If normalization fails.
    """
    try:
        return re.sub(r"\s+", "", raw_sequence).upper()
    except Exception as e:
        raise SequenceAnalysisError(f"Normalization failed: {str(e)}")


def process_fasta_record(record_data: Tuple[str, str, int, Set[str], Set[str]]) -> Tuple[str, str, Dict, Optional[str]]:
    """
    Process a single FASTA record in parallel.

    Args:
        record_data: Tuple of (seq_id, raw_sequence, sequence_count, allowed_bases, ambiguous_bases).

    Returns:
        Tuple[str, str, metadata, rev_sequence].

    Raises:
        SequenceAnalysisError: If sequence is invalid or processing fails.
    """
    seq_id, raw_sequence, sequence_count, allowed_bases, ambiguous_bases = record_data

    # Handle empty sequence
    if not raw_sequence.strip():
        logger.warning(f"Sequence {seq_id} is empty; skipping")
        return seq_id, "", {"processing_errors": ["Empty sequence"]}, None

    # Normalize sequence
    sequence = normalize_sequence(raw_sequence)

    # Initialize metadata
    metadata: Dict[str, any] = {
        "original_length": len(sequence),
        "n_count": sequence.count("N"),
        "removed_ambiguous": set(),
        "removed_invalid": set(),
        "final_length": 0,
        "processing_errors": []
    }

    # Process sequence based on HANDLE_AMBIGUOUS
    clean_sequence = []
    for i, char in enumerate(sequence):
        if char in allowed_bases:
            clean_sequence.append(char)
        elif char in ambiguous_bases:
            if APRConfig.HANDLE_AMBIGUOUS == "error":
                logger.error(f"Ambiguous base '{char}' at position {i} in {seq_id}")
                raise SequenceAnalysisError(f"Ambiguous base '{char}' in {seq_id}")
            elif APRConfig.HANDLE_AMBIGUOUS == "remove":
                metadata["removed_ambiguous"].add(char)
                logger.debug(f"Removed ambiguous base '{char}' at position {i} in {seq_id}")
            elif APRConfig.HANDLE_AMBIGUOUS == "keep":
                clean_sequence.append(char)
                logger.debug(f"Kept ambiguous base '{char}' at position {i} in {seq_id}")
        else:
            metadata["removed_invalid"].add(char)
            logger.warning(f"Removed invalid character '{char}' at position {i} in {seq_id}")

    clean_sequence_str = "".join(clean_sequence)
    metadata["final_length"] = len(clean_sequence_str)

    # Validate processed sequence
    if not clean_sequence_str:
        logger.error(f"Sequence {seq_id} became empty after processing")
        metadata["processing_errors"].append("Sequence became empty")
        raise SequenceAnalysisError(f"Sequence {seq_id} is empty after processing")

    # Compute reverse complement if both strands are selected
    rev_sequence = reverse_complement(clean_sequence_str) if APRConfig.STRAND_SELECTION == 2 else None

    # Log processing details
    logger.info(
        f"Processed sequence {seq_id}: "
        f"Original {metadata['original_length']:,}bp, "
        f"Final {metadata['final_length']:,}bp, "
        f"N count: {metadata['n_count']:,}"
    )
    if metadata["removed_ambiguous"]:
        logger.info(f"Removed ambiguous bases from {seq_id}: {sorted(metadata['removed_ambiguous'])}")
    if metadata["removed_invalid"]:
        logger.info(f"Removed invalid characters from {seq_id}: {sorted(metadata['removed_invalid'])}")

    return seq_id, clean_sequence_str, metadata, rev_sequence


def read_fasta(file_path: str, num_cpus: int = 1) -> List[Tuple[str, str, Dict, Optional[str]]]:
    """
    Read and process FASTA sequences with validation and multithreading.
    """
    # Validate file
    if not isinstance(file_path, str):
        logger.error(f"File path must be a string, got {type(file_path)}")
        raise ValueError("File path must be a string")
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"FASTA file not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        logger.error(f"No read permission for file: {file_path}")
        raise PermissionError(f"No read permission for file: {file_path}")

    # Validate configuration
    try:
        APRConfig.validate()
    except ConfigurationError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise

    allowed_bases: Set[str] = {"A", "T", "C", "G"}
    ambiguous_bases: Set[str] = APRConfig.AMBIGUOUS_BASES
    logger.debug(f"Allowed bases: {allowed_bases}, Ambiguous bases: {ambiguous_bases}")

    records = []
    sequence_count = 0
    current_id = None
    current_seq = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    if current_id and current_seq:
                        sequence_count += 1
                        seq_id = current_id or f"Unnamed_Seq_{sequence_count}"
                        records.append((seq_id, "".join(current_seq), sequence_count, allowed_bases, ambiguous_bases))
                        current_seq = []
                    current_id = line[1:].strip() or None
                elif line:
                    current_seq.append(line)
            if current_id and current_seq:
                sequence_count += 1
                seq_id = current_id or f"Unnamed_Seq_{sequence_count}"
                records.append((seq_id, "".join(current_seq), sequence_count, allowed_bases, ambiguous_bases))
            if sequence_count == 0:
                logger.warning(f"No sequences found in {file_path}")
                return []
    except Exception as e:
        logger.error(f"Unexpected error processing {file_path}: {str(e)}")
        raise SequenceAnalysisError(f"Error processing {file_path}: {str(e)}")

    if num_cpus <= 1 or sequence_count < MIN_SEQUENCES_FOR_PARALLEL:
        processed_records = []
        for record_data in records:
            try:
                result = process_fasta_record(record_data)
                processed_records.append(result)
            except SequenceAnalysisError as e:
                logger.warning(f"Skipping sequence {record_data[0]}: {str(e)}")
        return processed_records
    else:
        with Pool(processes=num_cpus) as pool:
            processed_records = pool.map(process_fasta_record, records)
        return [r for r in processed_records if not r[2]["processing_errors"]]


def validate_raw_sequence(sequence: str, num_cpus: int = 1) -> Tuple[str, Dict, Optional[str]]:
    """
    Validate and process a raw DNA sequence string.
    """
    if not isinstance(sequence, str):
        logger.error(f"Input must be a string, got {type(sequence)}")
        raise SequenceAnalysisError(f"Input must be a string, got {type(sequence)}")
    if not sequence.strip():
        logger.error("Empty sequence provided")
        raise SequenceAnalysisError("Cannot process empty sequence")

    try:
        APRConfig.validate()
    except ConfigurationError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise SequenceAnalysisError(f"Invalid configuration: {str(e)}")

    allowed_bases: Set[str] = {"A", "T", "C", "G"}
    ambiguous_bases: Set[str] = APRConfig.AMBIGUOUS_BASES

    processed_seq = normalize_sequence(sequence)

    metadata: Dict[str, any] = {
        "original_length": len(processed_seq),
        "n_count": processed_seq.count("N"),
        "removed_ambiguous": set(),
        "removed_invalid": set(),
        "final_length": 0,
        "processing_errors": []
    }

    clean_sequence = []
    for i, char in enumerate(processed_seq):
        if char in allowed_bases:
            clean_sequence.append(char)
        elif char in ambiguous_bases:
            if APRConfig.HANDLE_AMBIGUOUS == "error":
                logger.error(f"Ambiguous base '{char}' at position {i}")
                raise SequenceAnalysisError(f"Ambiguous base '{char}'")
            elif APRConfig.HANDLE_AMBIGUOUS == "remove":
                metadata["removed_ambiguous"].add(char)
            elif APRConfig.HANDLE_AMBIGUOUS == "keep":
                clean_sequence.append(char)
        else:
            metadata["removed_invalid"].add(char)
    clean_sequence_str = "".join(clean_sequence)
    metadata["final_length"] = len(clean_sequence_str)

    if not clean_sequence_str:
        logger.error("Processed sequence is empty")
        raise SequenceAnalysisError("Sequence empty after processing")

    # Compute reverse complement if both strands are selected
    rev_sequence = reverse_complement(clean_sequence_str) if APRConfig.STRAND_SELECTION == 2 else None

    logger.info(
        f"Validated raw sequence: "
        f"Original {metadata['original_length']:,}bp, "
        f"Final {metadata['final_length']:,}bp"
    )
    return clean_sequence_str, metadata, rev_sequence
