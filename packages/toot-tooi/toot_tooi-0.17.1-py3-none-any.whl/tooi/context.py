from tooi.credentials import get_active_credentials
from tooi.entities import Status


def account_name(acct: str) -> str:
    """
    Mastodon does not include the instance name for local account, this
    functions adds the current instance name to the account name if it's
    missing.
    """
    if "@" in acct:
        return acct

    application, _ = get_active_credentials()
    return f"{acct}@{application.domain}"


def is_mine(status: Status):
    return is_me(status.account.acct)


def is_me(acct: str):
    _, active_account = get_active_credentials()
    return account_name(acct) == active_account.acct
