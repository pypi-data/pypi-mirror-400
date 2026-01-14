from rich import markup
from textual import on, work
from textual.containers import Container, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Input, Label, ListItem, Rule, TabPane

from tooi.api.search import search
from tooi.entities import Account, Search, Status, Tag
from tooi.goto import GotoContextTimeline, GotoHashtagTimeline
from tooi.http import ResponseError
from tooi.messages import GotoMessage, ShowAccount
from tooi.utils.from_dict import from_dict
from tooi.utils.html import get_text
from tooi.widgets.list_view import ListView


class SearchPane(TabPane):
    def compose(self):
        self.input = Input(placeholder="Search")

        with Vertical():
            yield self.input
            yield Rule()
            yield Container(id="search_results")

    def on_mount(self, _):
        self.input.focus()

    @on(Input.Submitted)
    def on_submit(self):
        self.update_results(Label("Loading..."))
        self.run_search(self.input.value)

    @work(exclusive=True)
    async def run_search(self, query: str):
        try:
            response = await search(query)
            results = from_dict(Search, await response.json())
            self.update_results(SearchResultsList(results))
        except ResponseError as ex:
            self.update_results(Vertical(*self._render_response_error(ex)))
        except Exception as ex:
            self.update_results(Label(f"[red]Unexpected error: {markup.escape(str(ex))}[/]"))

    def update_results(self, widget: Widget):
        results = self.query_one("#search_results")
        results.remove_children()
        results.mount(widget)

    def _render_response_error(self, ex: ResponseError):
        if ex.error:
            yield Label(f"[red]Error: {markup.escape(ex.error)}[/]")
        if ex.description:
            yield Label(f"[red]{markup.escape(ex.description)}[/]")
        if not ex.error and not ex.description:
            yield Label("[red]Unknown error[/]")


class SearchResultsList(VerticalScroll, can_focus=False):
    DEFAULT_CSS = """
    SearchResultsList {
        padding: 0 1;
    }
    """

    def __init__(self, results: Search):
        self.results = results
        super().__init__()

    @on(ListView.FocusNext)
    def on_next(self):
        # TODO: ideally when bottom is reached next focus should go to the
        # search bar, currently it goes to the tabs.
        self.screen.focus_next()

    @on(ListView.FocusPrevious)
    def on_previous(self):
        self.screen.focus_previous()

    def compose(self):
        if not self.results.accounts and not self.results.hashtags and not self.results.statuses:
            yield Label("No results found")

        if self.results.accounts:
            yield Label("Accounts:")
            with ResultList():
                for account in self.results.accounts:
                    yield AccountItem(account)

        if self.results.hashtags:
            yield Label("Hashtags:")
            with ResultList():
                for tag in self.results.hashtags:
                    yield TagItem(tag)

        if self.results.statuses:
            yield Label("Statuses:")
            with ResultList():
                for status in self.results.statuses:
                    yield StatusItem(status)


class ResultList(ListView):
    DEFAULT_CSS = """
    ResultList {
        margin-bottom: 1;
    }
    """

    @on(ListView.Selected)
    def on_selected(self, message: ListView.Selected):
        if isinstance(message.item, AccountItem):
            self.post_message(ShowAccount(message.item.account))
        if isinstance(message.item, StatusItem):
            self.post_message(GotoMessage(GotoContextTimeline(message.item.status)))
        if isinstance(message.item, TagItem):
            self.post_message(GotoMessage(GotoHashtagTimeline(message.item.tag.name)))


class AccountItem(ListItem):
    def __init__(self, account: Account):
        self.account = account
        super().__init__(Label(f"< @{account.acct} >", markup=False))


class StatusItem(ListItem):
    def __init__(self, status: Status):
        self.status = status
        excerpt = get_text(status.content).replace("\n", " ")[:50] + "…"
        label = f"#{status.id} @{status.account.acct}\n  {excerpt}"
        super().__init__(Label(f"< @{label} >", markup=False))


class TagItem(ListItem):
    def __init__(self, tag: Tag):
        self.tag = tag
        super().__init__(Label(f"< #{tag.name} >", markup=False))
