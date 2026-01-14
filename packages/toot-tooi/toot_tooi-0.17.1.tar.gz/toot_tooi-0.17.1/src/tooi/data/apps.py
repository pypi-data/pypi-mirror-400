from tooi.api import apps
from tooi.entities import Application, CredentialApplication
from tooi.utils.from_dict import from_dict

async def create_app() -> CredentialApplication:
    """Create an application"""
    response = await apps.create_app()
    return from_dict(CredentialApplication, await response.json())



async def verify_credentials() -> Application:
    """Confirm that the app’s OAuth2 credentials work."""
    response = await apps.verify_credentials()
    return from_dict(Application, await response.json())
