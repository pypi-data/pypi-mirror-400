"""Miscellaneous code."""

from dataclasses import dataclass
from typing import ClassVar, Optional


@dataclass
class ThumbNodeRequest:
    """Request data to be attached to an image node's attribute list.

    Designed for messages to be passed from the image directives to the resizing class.
    """

    width: Optional[int]
    height: Optional[int]

    KEY: ClassVar[str] = "thumb-request"
