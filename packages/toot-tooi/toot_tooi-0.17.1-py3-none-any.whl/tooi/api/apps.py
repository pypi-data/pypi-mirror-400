"""
Apps
https://docs.joinmastodon.org/methods/apps/
"""

from aiohttp import ClientResponse
from tooi.http import request


async def create_app() -> ClientResponse:
    """
    Create an application
    https://docs.joinmastodon.org/methods/apps/#create
    """
    return await request(
        "POST",
        "/api/v1/apps",
        json={
            "client_name": "tooi",
            "redirect_uris": "urn:ietf:wg:oauth:2.0:oob",
            "scopes": "read write follow",
            "website": "https://codeberg.org/ihabunek/tooi",
        },
    )


async def verify_credentials() -> ClientResponse:
    """
    Confirm that the app’s OAuth2 credentials work.
    https://docs.joinmastodon.org/methods/apps/#create
    """
    return await request("GET", "/api/v1/apps/verify_credentials")
