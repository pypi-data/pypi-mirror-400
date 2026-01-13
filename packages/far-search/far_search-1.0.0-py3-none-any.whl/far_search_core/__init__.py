"""
FAR Search Core SDK - Lightweight Federal Acquisition Regulations search.

No LangChain dependency - works in any Python project.
"""

from far_search_core.client import FARSearchClient, search_far
from far_search_core.exceptions import FARSearchError, FARAPIError, FARRateLimitError

__version__ = "1.0.0"
__all__ = [
    "FARSearchClient",
    "search_far",
    "FARSearchError",
    "FARAPIError",
    "FARRateLimitError",
]

