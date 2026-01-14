# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .trace import Trace
from .._models import BaseModel

__all__ = ["TraceRetrieveResponse"]


class TraceRetrieveResponse(BaseModel):
    """Successful response containing a single trace object"""

    data: Trace
    """A trace grouping related steps (e.g. a user-agent interaction or conversation)."""
