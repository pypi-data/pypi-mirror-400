"""Attachment wrapper class for AAS HTTP Client."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Attachment:
    """Represents an attachment with its content and metadata."""

    content: bytes
    content_type: str
    filename: str | None = None
