from __future__ import annotations

import asyncio
from typing import NamedTuple

from textual import getters, on, work
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input, Label, Link, Rule

from tooi.app import TooiApp
from tooi.credentials import (
    Account,
    Application,
    Credentials,
    create_application,
    get_browser_login_url,
    load_credentials,
    login,
)
from tooi.entities import Instance
from tooi.http import ResponseError, anon_request
from tooi.messages import LoggedIn
from tooi.screens.modal import ModalScreen, ModalTitle
from tooi.utils.from_dict import from_response
from tooi.widgets.menu import Menu, MenuItem
from tooi.widgets.status_bar import StatusBar


class InstanceInfo(NamedTuple):
    instance: Instance
    base_url: str


class AccountsScreen(Screen[str | None]):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    AccountsScreen {
        #add-instance {
            margin-left: 1;
        }
        .connected-instances {
            margin-top: 1;
        }
        StatusBar {
            height: 2; /* prevent overlap with Footer */
        }
    }
    """

    BINDINGS = [
        Binding("left,up,h,k", "focus_previous"),
        Binding("down,right,j,l", "focus_next"),
    ]

    credentials: reactive[Credentials] = reactive(load_credentials(), recompose=True)

    def compose(self):
        yield Header()

        yield Label("Select Account", classes="text-header")
        if not self.credentials.accounts:
            yield Label("You are not logged into any accounts")

        for account in self.credentials.accounts.values():
            is_active = account.acct == self.credentials.active_acct
            variant = "success" if is_active else "primary"
            yield Button(
                account.acct,
                action=f"select('{account.acct}')",
                flat=True,
                variant=variant,
            )

        yield Label("Connected Instances", classes="connected-instances text-header")
        if self.credentials.apps:
            for app in self.credentials.apps.values():
                yield ConnectedInstance(app)
        else:
            yield Label("You have no connected instances")

        yield Button(
            "Add Instance",
            action="add_instance",
            variant="primary",
            flat=True,
            id="add-instance",
        )
        yield StatusBar()
        yield Footer()

    def action_focus_previous(self):
        self.app.action_focus_previous()

    def action_focus_next(self):
        self.app.action_focus_next()

    def action_add_instance(self):
        self.add_instance()

    def action_select(self, acct: str):
        self.dismiss(acct)

    @on(LoggedIn)
    def handle_logged_in(self):
        self.reload()

    @work
    async def add_instance(self):
        instance = await self.app.push_screen_wait(AddInstanceModal())
        if not instance:
            return

        status_bar = self.query_one(StatusBar)
        async with status_bar.run_with_progress(
            progress="Creating application...",
            success="Application created",
            error="Failed creating application",
        ):
            await create_application(instance.instance, instance.base_url)
            self.reload()

    def reload(self):
        self.credentials = load_credentials()


class ConnectedInstance(Widget):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    ConnectedInstance {
        border: round $secondary;
        max-width: 80;
        height: auto;
        padding: 0 1;

        .instance-title {
            color: $primary;
            text-style: bold;
        }

        Horizontal {
            height: auto
        }
        Vertical {
            height: auto
        }
    }
    """

    def __init__(self, application: Application):
        super().__init__()
        self.application = application

    def compose(self):
        yield Horizontal(
            Vertical(
                Label(self.application.title, classes="instance-title"),
                Label(f"[@click=app.open_url]{self.application.base_url}[/]"),
            ),
            Button("Add Account", variant="primary", flat=True),
        )

    @on(Button.Pressed)
    def handle_button_pressed(self):
        self.log_in()

    @work
    async def log_in(self):
        screen = LoginScreen(self.application)
        account = await self.app.push_screen_wait(screen)
        if account:
            self.post_message(LoggedIn())


class LoginScreen(ModalScreen[Account | None]):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    LoginScreen {
        .instance_title {
            color: $primary;
            text-style: bold;
        }
        .container {
            height: auto;
            margin: 0 1;
        }
        Rule.-horizontal {
            margin: 0;
        }
        Link, Label {
            width: 100%;
        }
    }
    """

    def __init__(self, application: Application):
        super().__init__()
        self.application = application
        self.login_url = get_browser_login_url(self.application)
        self.in_progress = False

    def compose_modal(self):
        yield ModalTitle("Login")
        yield Vertical(
            Label(self.application.title, classes="instance_title"),
            Label(self.application.base_url),
            classes="container",
        )
        yield Rule()
        yield Vertical(
            Label("Open the link in your browser to log in and obtain the autorization code:"),
            Link(self.login_url),
            classes="container",
        )
        yield Rule()
        yield Input(placeholder="Authorization code")
        yield StatusBar()

    def on_mount(self):
        self.query_one(Input).focus()

    @on(Input.Submitted)
    def handle_input_submit(self, message: Input.Submitted):
        authorization_code = self.query_one(Input).value.strip()
        if not authorization_code or self.in_progress:
            return

        self.in_progress = True
        message.stop()
        self.login(authorization_code)

    @work
    async def login(self, authorization_code: str):
        status_bar = self.query_one(StatusBar)
        loading_message_id = status_bar.set_message("Logging in...")

        try:
            account = await login(self.application, authorization_code)
            status_bar.set_success_message("Logged in!")
            await asyncio.sleep(0.3)
            self.dismiss(account)
        except ResponseError as ex:
            self.app.show_error_modal(
                title="Login failed",
                message=f"HTTP {ex.status_code}\n{ex.error}\n{ex.description}",
            )
        except Exception as ex:
            status_bar.set_error_message(f"Error: {ex}")
        finally:
            self.in_progress = False
            status_bar.clear_message(loading_message_id)


class AddInstanceModal(ModalScreen[InstanceInfo | None]):
    DEFAULT_CSS = """
    AddInstanceModal {
        #search_label{
            padding: 0 1;
        }
        #instance_info {
            height: auto;
            margin-top: 1;
        }
        #instance_title {
            color: $primary;
            text-style: bold;
            padding: 0 1;
        }
        #instance_url {
            padding: 0 1;
        }
        #instance_description {
            border: round $panel;
            padding: 0 1;
            width: 1fr;
            height: auto;
        }
        #instance_menu {
            margin-top: 1;
        }
        StatusBar {
            margin: 1 0 0 1;
        }
    }
    """

    instance_info: reactive[InstanceInfo | None] = reactive(None)

    def compose_modal(self):
        yield ModalTitle("Add Instance")
        yield Label("Enter your instance's URL or domain:", id="search_label")
        yield Input(placeholder="mastodon.social", value="mastodon.social")

        yield Vertical(
            Label("Found instance", classes="text-header"),
            Label("", id="instance_title"),
            Link("", id="instance_url"),
            Label("", id="instance_description"),
            Menu(
                MenuItem("add_instance", "Add Instance"),
                MenuItem("cancel", "Cancel"),
                id="instance_menu",
            ),
            id="instance_info",
        )
        yield StatusBar()

    def watch_instance_info(self, _, instance_info: InstanceInfo | None):
        container = self.query_one("#instance_info", Vertical)

        if instance_info:
            url = self.query_one("#instance_url", Link)
            title = self.query_one("#instance_title", Label)
            description = self.query_one("#instance_description", Label)
            menu = self.query_one("#instance_menu", Menu)

            url.update(instance_info.base_url)
            title.update(instance_info.instance.title)
            description.update(
                instance_info.instance.short_description
                or "[gray]This instance has no description[/]"
            )
            menu.focus()
            container.remove_class("hide")
        else:
            container.add_class("hide")

    @on(Input.Submitted)
    def handle_input_submit(self, message: Input.Submitted):
        message.stop()
        self.instance_info = None
        base_url = message.input.value.strip().strip("/")
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
        self.fetch_instance_info(base_url)

    @on(Menu.ItemSelected)
    def handle_menu_item_selected(self, message: Menu.ItemSelected):
        message.stop()

        if message.item.code == "add_instance":
            self.dismiss(self.instance_info)

        if message.item.code == "cancel":
            self.dismiss(None)

    @work(exclusive=True)
    async def fetch_instance_info(self, base_url: str):
        status_bar = self.query_one(StatusBar)
        message_id = status_bar.set_message(f"[gray]Looking for an instance at {base_url} ...[/]")

        try:
            response = await anon_request("GET", f"{base_url}/api/v1/instance")
            instance = await from_response(Instance, response)
            status_bar.clear_message(message_id)

            self.instance_info = InstanceInfo(instance, base_url)
        except Exception as ex:
            status_bar.set_message(f"[red]Failed: {ex}[/]", 3)
        finally:
            status_bar.clear_message(message_id)
