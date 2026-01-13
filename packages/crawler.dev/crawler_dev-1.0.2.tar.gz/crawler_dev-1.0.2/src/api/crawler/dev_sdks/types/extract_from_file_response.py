# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ExtractFromFileResponse"]


class ExtractFromFileResponse(BaseModel):
    content_type: Optional[str] = FieldInfo(alias="contentType", default=None)

    filename: Optional[str] = None

    markdown: Optional[str] = None
    """
    Markdown representation (included when 'markdown' is in formats array, empty
    string for non-HTML content)
    """

    size: Optional[int] = None
    """The size of the entity in bytes"""

    text: Optional[str] = None
    """Extracted plain text (included when 'text' is in formats array)"""
