from typing import Any, Dict

from .file_logger import FileAuditLogger
from .nats_logger import NATSAuditLogger


def get_logger(logger_type: str = "nats", **kwargs: Dict[str, Any]):
    """
    Returns an audit logger for the specified backend.

    Raises:
        ValueError: if unsupported backend or missing parameters.
    """
    if logger_type == "file":
        if "file_path" not in kwargs:
            raise ValueError("Missing 'file_path' for file logger")
        return FileAuditLogger(kwargs["file_path"])

    if logger_type == "nats":
        required = {"nats_connection_url"}
        missing = required - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing args for NATS logger: {missing}")

        if "subject" not in kwargs:
            kwargs["subject"] = "audit.logs"

        return NATSAuditLogger(**kwargs)

    raise ValueError(f"Unknown logger type: {logger_type}")