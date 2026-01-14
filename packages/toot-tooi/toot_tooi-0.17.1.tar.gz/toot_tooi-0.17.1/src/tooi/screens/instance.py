from typing import Any

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Label, Markdown, Static
from typing_extensions import override

from tooi.data.instance import InstanceInfo
from tooi.entities import ExtendedDescription, Instance, InstanceV2
from tooi.screens.modal import ModalScreen, ModalTitle

# TODO: make instance v1 mandatory
# TODO: show v1 instance info if v2 is not available
# TODO: make j/k scroll


class InstanceScreen(ModalScreen[None]):
    def __init__(self, data: InstanceInfo):
        self.instance = data.instance
        self.instance_v2 = data.instance_v2
        self.extended_description = data.extended_description
        self.user_preferences = data.user_preferences
        super().__init__()

    @override
    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(self.instance.title)
        yield VerticalScroll(*self.compose_instance_info())
        yield Footer()

    def compose_instance_info(self) -> ComposeResult:
        # Fall back to instance v1 if v2 is not available
        if self.instance_v2:
            yield from self.compose_instance_v2(self.instance_v2)
        else:
            yield from self.compose_instance(self.instance)

        if self.extended_description:
            yield from self.compose_description(self.extended_description)

        yield from self.compose_user_preferences(self.user_preferences)

    def compose_instance_v2(self, instance: InstanceV2):
        yield Static(f"Domain: {instance.domain}", markup=False)

        yield Static("")
        yield Static(instance.description, markup=False)

        yield Static("")
        yield Static(f"Contact: {instance.contact.email}", markup=False)

        yield Static("")
        yield ModalTitle("Rules")
        for rule in instance.rules:
            yield Static(f"* {rule.text}", markup=False)

    def compose_instance(self, instance: Instance):
        yield Static("TODO: Intance goes here")

    def compose_description(self, description: ExtendedDescription):
        yield Static("")
        yield Markdown(description.content_md)

    def compose_user_preferences(self, user_preferences: dict[str, Any]):
        yield ModalTitle("User Preferences")
        for key, value in user_preferences.items():
            yield Label(f"{key}: {value}")
