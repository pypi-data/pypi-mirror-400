from typing import Any


def class_dict(**classes: Any):
    """Helper for constructing widget classes.

    `**classes` keys are class names and values determine if the class should be
    applied or not.

    For example:

        class_dict(this_class=True, that_class=False)
    """

    return " ".join(k for k, v in classes.items() if v)
