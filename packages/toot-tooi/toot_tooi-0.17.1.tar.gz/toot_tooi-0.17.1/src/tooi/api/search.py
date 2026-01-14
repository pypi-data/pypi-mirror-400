"""
Search endpoints
https://docs.joinmastodon.org/methods/search/
"""

from aiohttp import ClientResponse
from tooi.http import request


async def search(query: str) -> ClientResponse:
    """
    Perform a search
    https://docs.joinmastodon.org/methods/search/#v2
    """
    return await request("GET", "/api/v2/search", params={
        "q": query,
        # "type": "hashtags"
    })
