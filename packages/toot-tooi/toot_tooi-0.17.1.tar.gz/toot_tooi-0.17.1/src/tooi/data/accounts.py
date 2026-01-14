from tooi.api import accounts
from tooi.entities import Account, Relationship
from tooi.utils.from_dict import from_dict, from_dict_list


async def lookup(acct: str) -> Account:
    """Look up an account by name and return its info."""
    response = await accounts.lookup(acct)
    return from_dict(Account, await response.json())


async def relationships(
    account_ids: list[str],
    *,
    with_suspended: bool = False,
) -> list[Relationship]:
    """Look up an account by name and return its info."""
    response = await accounts.relationships(account_ids, with_suspended=with_suspended)
    return from_dict_list(Relationship, await response.json())


async def relationship(account_id: str, *, with_suspended: bool = False) -> Relationship | None:
    """Look up an account by name and return its info."""
    rels = await relationships([account_id], with_suspended=with_suspended)
    return rels[0] if rels else None


async def verify_credentials() -> Account:
    """Test to make sure that the user token works."""
    response = await accounts.verify_credentials()
    return from_dict(Account, await response.json())


async def follow(
    account_id: str,
    *,
    reblogs: bool | None = None,
    notify: bool | None = None,
) -> Relationship:
    """Follow the given account."""
    response = await accounts.follow(account_id, reblogs=reblogs, notify=notify)
    return from_dict(Relationship, await response.json())


async def unfollow(account_id: str) -> Relationship:
    """Unfollow the given account."""
    response = await accounts.unfollow(account_id)
    return from_dict(Relationship, await response.json())


async def block(account_id: str) -> Relationship:
    """Block the given account."""
    response = await accounts.block(account_id)
    return from_dict(Relationship, await response.json())


async def unblock(account_id: str) -> Relationship:
    """Unblock the given account."""
    response = await accounts.unblock(account_id)
    return from_dict(Relationship, await response.json())


async def mute(account_id: str) -> Relationship:
    """Mute the given account."""
    response = await accounts.mute(account_id)
    return from_dict(Relationship, await response.json())


async def unmute(account_id: str) -> Relationship:
    """Unmute the given account."""
    response = await accounts.unmute(account_id)
    return from_dict(Relationship, await response.json())
