# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .run import Run
from .._models import BaseModel

__all__ = ["RunRetrieveResponse"]


class RunRetrieveResponse(BaseModel):
    """Successful response containing the run data"""

    run: Run
    """A Run represents a batch of tests triggered by a single task"""
