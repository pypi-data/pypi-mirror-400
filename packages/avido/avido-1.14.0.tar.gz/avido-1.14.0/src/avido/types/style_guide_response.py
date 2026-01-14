# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel
from .style_guide import StyleGuide

__all__ = ["StyleGuideResponse"]


class StyleGuideResponse(BaseModel):
    """Successful response containing the style guide data"""

    data: StyleGuide
    """A style guide for a specific application"""
