from typing import Generic, TypeVar, Type


from telegram.ext import CallbackContext


from ..constants.constants import _DISCUSSION


T = TypeVar("T")


class Contextual(Generic[T]):
    """`Contextual`-generic helps to fetch your `Discussion` inheritance from the context.

    Example:

    .. highlight:: python
    .. code-block:: python

        // It is your bot
        class YourBot(Discussion):
            additional_filed: str
            ...

        // Everywhere you need (Dialogues, Handlers, Middlewares)
        // get your Telegram-bot properties (like config, params, additional methods and etc.)
        // use this construction

        your_discussion_bot: YourBot = Contextual[YourBot](context)()
        print(your_discussion_bot.child_filed)

    """

    _superclass: Type

    context: CallbackContext

    def __init__(self, context: CallbackContext) -> None:
        if not getattr(Contextual, "_superclass", None):
            from .bot import (
                Discussion,
            )  # TODO: This once import solves circular import

            Contextual._superclass = Discussion
        self.context = context

    def instance(self) -> T:
        """Fetch instance of your Discussion-child from the context.

        But it's better to use shorter syntactic sugar:

        .. highlight:: python
        .. code-block:: python

            your_discussion_bot: YourBot = Contextual[YourBot](context)()

        Raises:
            ContextObjectIsNotDiscussion: when fetched object is not detected as Discussion-child.
        """
        stored = getattr(
            self.context.application,
            _DISCUSSION,
        )

        if not issubclass(stored.__class__, Contextual._superclass):
            raise ContextObjectIsNotDiscussion()
        return stored

    def __call__(self) -> T:
        return self.instance()


class ContextObjectIsNotDiscussion(Exception):
    def __str__(self):
        return "Context object is not Discussion"
