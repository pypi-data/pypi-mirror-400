"""
Accounts
https://docs.joinmastodon.org/methods/instance/
"""
from aiohttp import ClientResponse
from tooi.http import request


async def server_information() -> ClientResponse:
    """
    Obtain general information about the server.
    https://docs.joinmastodon.org/methods/instance/#v1
    """
    return await request("GET", "/api/v1/instance")


async def server_information_v2() -> ClientResponse:
    """
    Obtain general information about the server.
    https://docs.joinmastodon.org/methods/instance/#v2
    """
    return await request("GET", "/api/v2/instance")


async def extended_description() -> ClientResponse:
    """
    Obtain an extended description of this server
    https://docs.joinmastodon.org/methods/instance/#extended_description
    """
    return await request("GET", "/api/v1/instance/extended_description")


async def user_preferences() -> ClientResponse:
    """
    Fetch the user's server-side preferences for this instance.
    https://docs.joinmastodon.org/methods/preferences/
    """
    return await request("GET", "/api/v1/preferences")
