from textual.widgets import Select

VISIBILITY = {
    "public": "Public - Visible to everyone, shown in public timelines.",
    "unlisted": "Unlisted - Visible to public, but not included in public timelines.",
    "private": "Private - Visible to followers only, and to any mentioned users.",
    "direct": "Direct - Visible only to mentioned users.",
}


class VisibilitySelect(Select[str]):
    def __init__(self, initial_value: str):
        super().__init__(
            [(v, k) for k, v in VISIBILITY.items()],
            prompt="Visibility",
            allow_blank=False,
            value=initial_value,
        )
