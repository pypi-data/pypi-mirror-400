import logging

from textual import getters, on, work
from textual.markup import escape
from textual.widget import Widget
from textual.widgets import Label, ListItem, TabPane

from tooi.app import TooiApp
from tooi.api import conversations
from tooi.entities import Conversation
from tooi.goto import GotoContextTimeline
from tooi.messages import GotoMessage, ShowAccount
from tooi.utils.from_dict import from_response_list
from tooi.widgets.list_view import ListView

logger = logging.getLogger(__name__)

# TODO: page conversations, currently showing only the initial page
# TODO: display a notice when there are no conversations

class ConversationsPane(TabPane):
    app = getters.app(TooiApp)

    def __init__(self):
        super().__init__("Conversations")

    def compose(self):
        yield ListView()

    def on_mount(self):
        self.load_initial()

    @work
    async def load_initial(self):
        self.loading = True
        try:
            await self.load()
        except Exception as ex:
            self.app.show_error_modal("Failed loading conversations", ex=ex)
        finally:
            self.loading = False

    async def load(self):
        response = await conversations.get_conversations()
        self.conversations = await from_response_list(Conversation, response)
        list_view = self.query_one(ListView)
        list_view.mount_all(ConversationListItem(conv) for conv in self.conversations)
        list_view.focus()

    @on(ListView.Selected)
    def handle_conversation_selected(self, message: ListView.Selected):
        if status := self.conversations[message.index].last_status:
            self.post_message(GotoMessage(GotoContextTimeline(status)))


class ConversationListItem(ListItem):
    DEFAULT_CSS = """
    ConversationListItem {
        border: round $primary;
        height: auto;
        max-width: 80;
        padding: 0 1;

        .with {
            height: 1;
        }

        .summary {
            max-height: 4;
            max-width: 100%;
            color: $text-muted;
            margin-top: 1;
        }
    }
    """

    def __init__(self, conversation: Conversation):
        classes = "unread" if conversation.unread else ""
        super().__init__(*self.make_label(conversation), classes=classes)
        self.conversation = conversation

    def make_label(self, conversation: Conversation) -> list[Widget]:
        status = conversation.last_status
        summary_label = status.content_plaintext if status else ""

        return [
            WithLabel(conversation, classes="with"),
            Label(summary_label, classes="summary"),
        ]


class WithLabel(Label):
    def __init__(self, conversation: Conversation, classes: str | None = None):
        super().__init__(self.make_content(conversation), classes=classes)
        self.conversation = conversation

    def make_content(self, conversation: Conversation):
        if conversation.accounts:
            content = "With: "
            for idx, account in enumerate(conversation.accounts):
                if idx > 0:
                    content += ", "
                content += (
                    f"[@click=account_click('{account.acct}')]{escape(account.acct)}[/@click=]"
                )
        else:
            content = "With unknown?"

        return content

    def action_account_click(self, acct: str):
        try:
            account = next(a for a in self.conversation.accounts if a.acct == acct)
            self.post_message(ShowAccount(account))
        except Exception:
            logger.exception("Cannot find account")
