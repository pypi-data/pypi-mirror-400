"""Utility functions for fw-meta."""

import re
import string


def sanitize_label(value: str) -> str:
    """Sanitize and truncate labels for filesystem dir/filename compatibility."""
    # replace '*' with 'star' (to retain eg. DICOM MR T2* domain context)
    value = re.sub(r"\*", r"star", value)
    # replace any occurrences of (one or more) invalid chars w/ an underscore
    unprintable = [chr(c) for c in range(128) if chr(c) not in string.printable]
    invalid_chars = "*/:<>?\\|\t\n\r\x0b\x0c" + "".join(unprintable)
    value = re.sub(rf"[{re.escape(invalid_chars):s}]+", "_", value)
    # truncate to 255 chars
    value = value[:255]
    # drop ending dots (azure limitation)
    value = value.rstrip(".")
    return value


def sanitize_path_fields(value: dict) -> dict:
    """Sanitize container label and file name fields to be filesystem-safe."""
    value = value.copy()
    conts = ["project", "subject", "session", "acquisition"]
    for key in [f"{cont}.label" for cont in conts] + ["file.name"]:
        if val := value.get(key):
            value[key] = sanitize_label(val)
    return value
