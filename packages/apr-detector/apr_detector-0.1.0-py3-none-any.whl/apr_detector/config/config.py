### config/config.py# Configuration module for A-phased repeat (APR) detection pipeline.
# This module defines configuration settings,
# including, spacing settings, and sequence handling options.

import json
from typing import Set, List, Tuple
import logging

# Configure logging with timestamp and level
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Exception for invalid configuration settings."""
    def __init__(self, message: str):
        super().__init__(f"Invalid Configuration: {message}")
        self.message = message

class APRConfig:
    """
    Configuration for A-phased repeat (APR) detection pipeline.
    Defines settings for A-tract detection, spacing, detection modes, and sequence handling.
    Penalty and scoring settings are managed in ScoringConfig (scoring.py).
    """

    # --- Core APR Detection Settings ---
    DETECTION_MODE: str = 'heteropolymer'  # heteropolymer, homopolymer, homopolymer_t, homopolymer_mixed
    MIN_NUM_TRACTS: int = 3  # Minimum number of A-tracts to form an APR (for -t)
    SPACING_WINDOW: float = 0.5  # Window around 10.5 nt distance (for -w)

    # --- A-Tract Length Parameters ---
    MIN_NT_IN_TRACT: int = 4  # Minimum A-tract length (for -l)
    MAX_TRACT_LENGTH: int = 9  # Maximum A-tract length

    # --- Sequence Handling ---
    HANDLE_AMBIGUOUS: str = "keep"  # remove, error, keep
    AMBIGUOUS_BASES: Set[str] = {'R', 'Y', 'S', 'W', 'K', 'M', 'B', 'D', 'H', 'V', 'N'}
    STRAND_SELECTION: int = 1  # 1: single strand (+), 2: both strands
    MERGE_APRS: bool = True  # Merge identical/contained APRs by default
    WRITE_GFF: bool = False  # Emit GFF output alongside TSV
    WRITE_BED: bool = False  # Emit BED output alongside TSV
    WRITE_TRACTS_CSV: bool = False  # Emit candidate tracts CSV alongside APR outputs
    WRITE_TRACTS_TSV: bool = False  # Emit candidate tracts TSV alongside APR outputs
    WRITE_CSV: bool = False  # Emit APRs as CSV alongside TSV
    WRITE_SUMMARY: bool = False  # Emit per-sequence summary TSV
    MODEL_NAME: str = "Model2"  # track selected model for reporting
    PITCH: float = 10.5  # Helical pitch in bp for phase coherence

    @classmethod
    def get_min_spacing(cls) -> float:
        """Compute minimum spacing from SPACING_WINDOW around PITCH."""
        return cls.PITCH - cls.SPACING_WINDOW

    @classmethod
    def get_max_spacing(cls) -> float:
        """Compute maximum spacing from SPACING_WINDOW around PITCH."""
        return cls.PITCH + cls.SPACING_WINDOW

    @classmethod
    def get_min_max_tract_length(cls) -> Tuple[int, int]:
        """Return the minimum and maximum A-tract lengths."""
        return cls.MIN_NT_IN_TRACT, cls.MAX_TRACT_LENGTH

    @classmethod
    def validate(cls) -> None:
        """Validate configuration parameters, raising ConfigurationError if invalid."""
        errors: List[str] = []

        # Validate detection mode
        valid_modes = {'heteropolymer', 'homopolymer', 'homopolymer_t', 'homopolymer_mixed'}
        if cls.DETECTION_MODE not in valid_modes:
            errors.append(f"Invalid DETECTION_MODE: '{cls.DETECTION_MODE}'. Valid: {valid_modes}")
        if not isinstance(cls.PITCH, (int, float)) or cls.PITCH <= 0:
            errors.append(f"PITCH must be positive (is {cls.PITCH})")

        # Validate tract lengths
        if not isinstance(cls.MIN_NT_IN_TRACT, int) or cls.MIN_NT_IN_TRACT < 1:
            errors.append(f"MIN_NT_IN_TRACT must be int >= 1 (is {cls.MIN_NT_IN_TRACT})")
        if not isinstance(cls.MAX_TRACT_LENGTH, int) or cls.MAX_TRACT_LENGTH < cls.MIN_NT_IN_TRACT:
            errors.append(f"MAX_TRACT_LENGTH ({cls.MAX_TRACT_LENGTH}) < MIN_NT_IN_TRACT ({cls.MIN_NT_IN_TRACT})")

        # Validate MIN_NUM_TRACTS
        if not isinstance(cls.MIN_NUM_TRACTS, int) or cls.MIN_NUM_TRACTS < 2:
            errors.append(f"MIN_NUM_TRACTS ({cls.MIN_NUM_TRACTS}) must be int >= 2")

        # Validate spacing window
        if not isinstance(cls.SPACING_WINDOW, float) or cls.SPACING_WINDOW < 0:
            errors.append(f"SPACING_WINDOW ({cls.SPACING_WINDOW}) must be >= 0")
        min_spacing = cls.get_min_spacing()
        max_spacing = cls.get_max_spacing()
        if max_spacing < min_spacing:
            errors.append(f"Computed MAX_SPACING ({max_spacing}) < MIN_SPACING ({min_spacing})")

        # Validate sequence handling
        if cls.HANDLE_AMBIGUOUS not in {"remove", "error", "keep"}:
            errors.append(f"HANDLE_AMBIGUOUS must be 'remove', 'error', or 'keep' (is '{cls.HANDLE_AMBIGUOUS}')")
        if cls.STRAND_SELECTION not in {1, 2}:
            errors.append(f"STRAND_SELECTION must be 1 or 2 (is {cls.STRAND_SELECTION})")
        if not isinstance(cls.MERGE_APRS, bool):
            errors.append(f"MERGE_APRS must be boolean (is {cls.MERGE_APRS})")
        if not isinstance(cls.WRITE_GFF, bool):
            errors.append(f"WRITE_GFF must be boolean (is {cls.WRITE_GFF})")
        if not isinstance(cls.WRITE_BED, bool):
            errors.append(f"WRITE_BED must be boolean (is {cls.WRITE_BED})")
        if not isinstance(cls.WRITE_TRACTS_CSV, bool):
            errors.append(f"WRITE_TRACTS_CSV must be boolean (is {cls.WRITE_TRACTS_CSV})")
        if not isinstance(cls.WRITE_TRACTS_TSV, bool):
            errors.append(f"WRITE_TRACTS_TSV must be boolean (is {cls.WRITE_TRACTS_TSV})")
        if not isinstance(cls.WRITE_CSV, bool):
            errors.append(f"WRITE_CSV must be boolean (is {cls.WRITE_CSV})")
        if not isinstance(cls.WRITE_SUMMARY, bool):
            errors.append(f"WRITE_SUMMARY must be boolean (is {cls.WRITE_SUMMARY})")

        if errors:
            error_msg = "Configuration errors:\n- " + "\n- ".join(errors)
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

    @classmethod
    def load_defaults(cls) -> None:
        """Reset configuration to default values."""
        logger.info("Loading default configuration")
        cls.DETECTION_MODE = 'heteropolymer'
        cls.MIN_NUM_TRACTS = 3
        cls.SPACING_WINDOW = 0.5
        cls.MIN_NT_IN_TRACT = 4
        cls.MAX_TRACT_LENGTH = 9
        cls.HANDLE_AMBIGUOUS = "remove"
        cls.AMBIGUOUS_BASES = {'R', 'Y', 'S', 'W', 'K', 'M', 'B', 'D', 'H', 'V', 'N'}
        cls.STRAND_SELECTION = 1
        cls.MERGE_APRS = True
        cls.WRITE_GFF = False
        cls.WRITE_BED = False
        cls.WRITE_TRACTS_CSV = False
        cls.WRITE_TRACTS_TSV = False
        cls.WRITE_CSV = False
        cls.WRITE_SUMMARY = False
        cls.MODEL_NAME = "Model2"
        cls.PITCH = 10.5
        logger.info("Default configuration loaded")

    @classmethod
    def load_from_file(cls, config_file: str) -> None:
        """Load configuration from a JSON file."""
        logger.info(f"Loading configuration from {config_file}")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            for key, value in config_data.items():
                if hasattr(cls, key):
                    if key == "AMBIGUOUS_BASES" and isinstance(value, list):
                        setattr(cls, key, set(value))
                    else:
                        setattr(cls, key, value)
                else:
                    logger.warning(f"Ignoring unknown configuration key '{key}'")
            cls.validate()
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
            raise ConfigurationError(f"Failed to load config file: {e}")

    @classmethod
    def save_to_file(cls, config_file: str) -> None:
        """Save configuration to a JSON file."""
        logger.info(f"Saving configuration to {config_file}")
        try:
            config_data = {
                'DETECTION_MODE': cls.DETECTION_MODE,
                'MIN_NUM_TRACTS': cls.MIN_NUM_TRACTS,
                'SPACING_WINDOW': cls.SPACING_WINDOW,
                'MIN_NT_IN_TRACT': cls.MIN_NT_IN_TRACT,
                'MAX_TRACT_LENGTH': cls.MAX_TRACT_LENGTH,
                'HANDLE_AMBIGUOUS': cls.HANDLE_AMBIGUOUS,
                'AMBIGUOUS_BASES': list(cls.AMBIGUOUS_BASES),
                'STRAND_SELECTION': cls.STRAND_SELECTION,
                'MERGE_APRS': cls.MERGE_APRS,
                'WRITE_GFF': cls.WRITE_GFF,
                'WRITE_BED': cls.WRITE_BED,
                'WRITE_TRACTS_CSV': cls.WRITE_TRACTS_CSV,
                'WRITE_TRACTS_TSV': cls.WRITE_TRACTS_TSV,
                'WRITE_CSV': cls.WRITE_CSV,
                'WRITE_SUMMARY': cls.WRITE_SUMMARY,
                'PITCH': cls.PITCH,
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Error saving config file {config_file}: {e}")
            raise ConfigurationError(f"Failed to save config file: {e}")
