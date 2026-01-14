# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel
from .application import Application

__all__ = ["ApplicationResponse"]


class ApplicationResponse(BaseModel):
    """Successful response containing the application data"""

    data: Application
    """Application configuration and metadata"""
