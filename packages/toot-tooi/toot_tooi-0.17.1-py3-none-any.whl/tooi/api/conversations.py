"""
Conversations
https://docs.joinmastodon.org/methods/conversations/
"""

from aiohttp import ClientResponse
from tooi.http import request


async def get_conversations() -> ClientResponse:
    """
    View all conversations
    https://docs.joinmastodon.org/methods/conversations/#get
    """
    return await request("GET", "/api/v1/conversations")
