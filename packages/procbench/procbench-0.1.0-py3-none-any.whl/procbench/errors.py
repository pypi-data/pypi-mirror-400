# procmon/errors.py

class ProcMonError(Exception):
    """Base class for all procmon errors."""
    pass


class SchemaValidationError(ProcMonError):
    """Invalid or unsupported test case schema."""
    pass


class TestCaseLoadError(ProcMonError):
    """Failed to load or parse test case JSON."""
    pass


class SpawnError(ProcMonError):
    """Process failed to start."""
    pass


class MonitorRuntimeError(ProcMonError):
    """Unexpected error during monitoring."""
    pass
