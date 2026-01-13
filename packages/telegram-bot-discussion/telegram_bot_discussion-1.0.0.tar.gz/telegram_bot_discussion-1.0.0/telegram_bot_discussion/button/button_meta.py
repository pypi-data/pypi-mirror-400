from datetime import timedelta


ACTION: str = "action"
LIFE_TIME: str = "life_time"
TITLE: str = "title"


class ButtonMeta:
    """`ButtonMeta` is a special meta class for autogenerate properties values for object of `Button` classes."""

    action: str
    """ str: Unique action name for handling its reaction route in `ButtonHandler`."""
    life_time: timedelta = None
    """timedelta:  Clickable lifetime of the button. The default value `None` means no limits."""
    title: str
    """ str: Text on button."""
