from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from functools import cache
from pathlib import Path
from typing import AsyncGenerator, NamedTuple
from urllib.parse import urlencode, urlparse

import click
from platformdirs import user_data_path
from pydantic import BaseModel, Field

from tooi import APP_NAME, APP_WEBSITE, http
from tooi.entities import Account as AccountEntity
from tooi.entities import CredentialApplication, Instance, Token
from tooi.http import anon_request
from tooi.utils.from_dict import from_response

logger = logging.getLogger(__name__)


SCOPES = "read write"


class Credentials(BaseModel):
    active_acct: str | None = None
    accounts: dict[str, Account] = Field(default_factory=dict)
    apps: dict[str, Application] = Field(default_factory=dict)

    @property
    def active_account(self) -> Account | None:
        return self.accounts.get(self.active_acct) if self.active_acct else None

    @property
    def active_application(self) -> Application | None:
        return self.apps[self.active_account.instance] if self.active_account else None


class Account(BaseModel):
    acct: str
    """Qualified account name, e.g. Gargron@mastodon.social"""
    username: str
    """Account username, e.g. Gargron"""
    instance: str
    """Instance domain, e.g. mastodon.social"""
    access_token: str
    """Obtained OAuth token, used for authorizing HTTP requests."""


class Application(BaseModel):
    title: str
    """Instance title, e.g. Mastodon"""
    domain: str
    """Instance domain, e.g. mastodon.social"""
    base_url: str
    """Base URL without the trailing dash, e.g. https://mastodon.social"""
    client_id: str
    """Client ID key, used for obtaining OAuth tokens."""
    client_secret: str
    """Client secret key, used for obtaining OAuth tokens."""


class ActiveCredentials(NamedTuple):
    applicaton: Application
    account: Account


@cache
def get_active_credentials() -> ActiveCredentials:
    credentials = load_credentials()
    account =  credentials.active_account
    application =  credentials.active_application

    if account is None or application is None:
        raise ValueError("Not logged in")  # TODO: handle gracefully

    return ActiveCredentials(application, account)



def get_data_path() -> Path:
    return user_data_path(APP_NAME, ensure_exists=True)


def get_credentials_path() -> Path:
    return get_data_path() / "credentials.json"


def get_application(name: str) -> Application | None:
    return load_credentials().apps.get(name)


async def create_application(instance: Instance, base_url: str) -> Application:
    payload = {
        "client_name": APP_NAME,
        "redirect_uris": "urn:ietf:wg:oauth:2.0:oob",
        "scopes": SCOPES,
        "website": APP_WEBSITE,
    }

    response = await anon_request("POST", f"{base_url}/api/v1/apps", json=payload)
    data = await from_response(CredentialApplication, response)

    application = Application(
        title=instance.title,
        domain=_get_instance_domain(instance),
        base_url=base_url,
        client_id=data.client_id,
        client_secret=data.client_secret,
    )

    logger.info(f"Application {application.domain} created, storing credentials")
    async with _edit_credentials() as credentials:
        credentials.apps[application.domain] = application

    return application


def _get_instance_domain(instance: Instance) -> str:
    """Extracts the instance domain name.

    Pleroma and its forks return an actual URI here, rather than a domain name
    like Mastodon. This is contrary to the spec. In this case, parse out the
    domain and return it.

    Not using v2 instance endpoint, which shouldn't have this problem, because
    many servers still don't support it.
    """
    if instance.uri.startswith("http"):
        return urlparse(instance.uri).netloc
    return instance.uri


def get_browser_login_url(app: Application) -> str:
    """Returns the URL for manual log in via browser"""
    query = {
        "response_type": "code",
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "scope": SCOPES,
        "client_id": app.client_id,
    }

    return "{}/oauth/authorize/?{}".format(app.base_url, urlencode(query))


async def login(application: Application, authorization_code: str) -> Account:
    token = await _request_token(application, authorization_code)
    account_entity = await _verify_credentials(application, token.access_token)

    username = account_entity.acct
    instance = application.domain

    account = Account(
        acct=f"{username}@{instance}",
        username=username,
        instance=instance,
        access_token=token.access_token,
    )

    logger.info(f"Account {account.acct} logged in, storing credentials")
    async with _edit_credentials() as credentials:
        credentials.accounts[account.acct] = account
        if not credentials.active_acct:
            credentials.active_acct = account.acct

    return account


async def _request_token(application: Application, authorization_code: str) -> Token:
    """
    https://docs.joinmastodon.org/methods/oauth/#token
    """
    url = f"{application.base_url}/oauth/token"

    data = {
        "grant_type": "authorization_code",
        "client_id": application.client_id,
        "client_secret": application.client_secret,
        "code": authorization_code,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    }

    response = await anon_request("POST", url, json=data, allow_redirects=False)
    return await from_response(Token, response)


async def _verify_credentials(application: Application, access_token: str) -> AccountEntity:
    """
    https://docs.joinmastodon.org/methods/accounts/#verify_credentials
    """
    url = f"{application.base_url}/api/v1/accounts/verify_credentials"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await anon_request("GET", url, headers=headers)
    return await from_response(AccountEntity, response)


def load_credentials() -> Credentials:
    path = get_credentials_path()

    if not path.exists():
        click.echo(f"Initializing credentials file: {path}")
        with path.open("w") as f:
            f.write("{}")

    with path.open("r") as f:
        data = f.read()

    return Credentials.model_validate_json(data)


async def activate_account(acct: str):
    async with _edit_credentials() as credentials:
        assert acct in credentials.accounts
        credentials.active_acct = acct


def _save_credentials(creds: Credentials):
    path = get_credentials_path()

    with path.open("w") as f:
        f.write(creds.model_dump_json(indent=4))


@asynccontextmanager
async def _edit_credentials() -> AsyncGenerator[Credentials, None]:
    creds = load_credentials()
    yield creds
    _save_credentials(creds)
    # Clear places where active account data is cached
    await http.close_session()
    get_active_credentials.cache_clear()
