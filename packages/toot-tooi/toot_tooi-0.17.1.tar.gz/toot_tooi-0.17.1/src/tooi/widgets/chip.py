from textual.widgets import Label


class Chip(Label):
    DEFAULT_CSS = """
    Chip {
        border: round white;
        padding: 0 1;

        &.primary {
            color: $primary-lighten-3;
            border: round $primary;
        }
        &.secondary {
            color: $secondary;
            border: round $secondary;
        }
    }
    """

    def __init__(self, text: str, *, classes: str = ""):
        super().__init__(text, classes=classes, markup=False)
