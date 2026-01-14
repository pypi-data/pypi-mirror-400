# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .topic import Topic
from .._models import BaseModel

__all__ = ["TopicResponse"]


class TopicResponse(BaseModel):
    """Successful response containing the topic data"""

    data: Topic
    """Details about a single Topic"""
