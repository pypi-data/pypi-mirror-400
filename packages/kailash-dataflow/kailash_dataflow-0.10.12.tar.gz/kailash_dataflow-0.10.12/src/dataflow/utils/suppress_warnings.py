"""
Suppress verbose Core SDK warnings and configure DataFlow logging.

This module provides utilities to:
1. Suppress console warnings from Core SDK that flood the output
2. Configure DataFlow logging levels centrally
3. Support environment variable configuration for 12-factor apps

See ADR-002 for architectural details.
"""

import logging
from typing import Dict, Optional

# Logger name to category mapping
_LOGGER_CATEGORIES: Dict[str, str] = {
    "dataflow": "core",
    "dataflow.core.nodes": "node_execution",
    "dataflow.core.engine": "core",
    "dataflow.migrations": "migration",
    "dataflow.migrations.auto_migration_system": "migration",
    "dataflow.migrations.schema_state_manager": "migration",
    "dataflow.features.bulk": "node_execution",
    "dataflow.utils": "core",
}

# Storage for original log levels (for restore functionality)
_original_levels: Dict[str, int] = {}

# Track if logging has been configured
_logging_configured: bool = False


def suppress_core_sdk_warnings():
    """
    Suppress verbose Core SDK warnings that flood console output.

    Warnings suppressed:
    - kailash.nodes.base: "Overwriting existing node registration"
    - kailash.resources.registry: "Overwriting existing factory for resource"

    These warnings are benign in DataFlow context where node registration
    overwriting is expected during model decoration.

    Usage:
        from dataflow.utils.suppress_warnings import suppress_core_sdk_warnings
        suppress_core_sdk_warnings()
    """
    # Suppress node registration warnings
    logging.getLogger("kailash.nodes.base").setLevel(logging.ERROR)

    # Suppress resource factory warnings
    logging.getLogger("kailash.resources.registry").setLevel(logging.ERROR)


def restore_core_sdk_warnings():
    """
    Restore Core SDK warning levels to default (WARNING).

    Use this to re-enable warnings for debugging if needed.

    Usage:
        from dataflow.utils.suppress_warnings import restore_core_sdk_warnings
        restore_core_sdk_warnings()
    """
    # Restore node registration warnings
    logging.getLogger("kailash.nodes.base").setLevel(logging.WARNING)

    # Restore resource factory warnings
    logging.getLogger("kailash.resources.registry").setLevel(logging.WARNING)


def configure_dataflow_logging(config: Optional["LoggingConfig"] = None) -> None:
    """Configure DataFlow logging with centralized settings.

    This function configures all DataFlow loggers according to the provided
    LoggingConfig. It supports:
    - Global log level setting
    - Category-specific log level overrides
    - Environment variable configuration (via LoggingConfig.from_env())

    Args:
        config: LoggingConfig instance. If None, uses LoggingConfig.from_env().

    Usage:
        from dataflow.core.config import LoggingConfig
        from dataflow.utils.suppress_warnings import configure_dataflow_logging

        # Use environment variables
        configure_dataflow_logging()

        # Use explicit config
        configure_dataflow_logging(LoggingConfig(level=logging.DEBUG))

        # Category-specific debugging
        configure_dataflow_logging(LoggingConfig(
            level=logging.WARNING,
            node_execution=logging.DEBUG,
        ))
    """
    global _original_levels, _logging_configured

    # Import here to avoid circular imports
    from dataflow.core.config import LoggingConfig

    if config is None:
        config = LoggingConfig.from_env()

    # Set the root dataflow logger level
    dataflow_logger = logging.getLogger("dataflow")
    if "dataflow" not in _original_levels:
        _original_levels["dataflow"] = dataflow_logger.level
    dataflow_logger.setLevel(config.level)

    # Configure category-specific loggers
    for logger_name, category in _LOGGER_CATEGORIES.items():
        logger = logging.getLogger(logger_name)

        # Store original level if not already stored
        if logger_name not in _original_levels:
            _original_levels[logger_name] = logger.level

        # Set the appropriate level
        level = config.get_level_for_category(category)
        logger.setLevel(level)

    # Also apply existing SDK warning suppression
    suppress_core_sdk_warnings()

    _logging_configured = True

    # Log configuration applied (at DEBUG to avoid noise)
    logging.getLogger("dataflow").debug(
        f"DataFlow logging configured: level={logging.getLevelName(config.level)}"
    )


def restore_dataflow_logging() -> None:
    """Restore original logging levels.

    This function restores all DataFlow loggers to their original levels
    before configure_dataflow_logging() was called. Useful for testing
    or when you need to temporarily change and restore logging levels.

    Usage:
        from dataflow.utils.suppress_warnings import (
            configure_dataflow_logging,
            restore_dataflow_logging,
        )

        # Change logging
        configure_dataflow_logging(LoggingConfig(level=logging.DEBUG))

        # ... do something ...

        # Restore original levels
        restore_dataflow_logging()
    """
    global _original_levels, _logging_configured

    for logger_name, original_level in _original_levels.items():
        logging.getLogger(logger_name).setLevel(original_level)

    _original_levels.clear()
    _logging_configured = False

    # Restore SDK warnings too
    restore_core_sdk_warnings()


def is_logging_configured() -> bool:
    """Check if DataFlow logging has been configured.

    Returns:
        True if configure_dataflow_logging() has been called.
    """
    return _logging_configured
