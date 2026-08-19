class GenomepipeError(Exception):
    """Base exception for controlled Genomepipe failures."""


class ConfigurationError(GenomepipeError):
    """Invalid project configuration."""


class InputValidationError(GenomepipeError):
    """Invalid or unusable pipeline input."""


class ModuleExecutionError(GenomepipeError):
    """A pipeline module failed during execution."""


class ExternalToolError(ModuleExecutionError):
    """An external bioinformatics tool failed."""


class UnsafeOperationError(GenomepipeError):
    """An operation violates the current execution policy."""
