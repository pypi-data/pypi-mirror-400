# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import FileTypes
from .._utils import PropertyInfo

__all__ = ["ExtractFromFileParams"]


class ExtractFromFileParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The file to upload."""

    clean_text: Annotated[bool, PropertyInfo(alias="cleanText")]
    """Whether to clean and normalize the extracted text. When enabled (true):

    - For HTML content: Removes script, style, and other non-text elements before
      extraction
    - Normalizes whitespace (collapses multiple spaces/tabs, normalizes newlines)
    - Removes empty lines and trims leading/trailing whitespace
    - Normalizes Unicode characters (NFC)
    - For JSON content: Only minimal cleaning to preserve structure When disabled
      (false): Returns raw extracted text without any processing.
    """

    formats: List[Literal["text", "markdown"]]
    """Array of output formats to include in the response. Options: 'text', 'markdown'.

    - 'text': Extracted plain text (always available)
    - 'markdown': Markdown representation (only available for HTML content, empty
      string otherwise) Defaults to ['text'] if not specified.
    """

    max_timeout: Annotated[Union[int, str], PropertyInfo(alias="maxTimeout")]
    """Maximum time before the file extraction gives up. Accepts either:

    - Integer: milliseconds (e.g., 30000 for 30 seconds)
    - String: time format with unit (e.g., "1s", "5h", "3m", "4.4h") Supported
      units: s (seconds), m (minutes), h (hours), d (days), ms (milliseconds) Must
      be between 5 seconds and 2 minutes. Defaults to "30s" (30 seconds) if not
      specified. This controls the timeout for Tika extraction operations on
      uploaded files.
    """
