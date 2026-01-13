from typing import Tuple, Union


from telegram import Update
from telegram.ext import CallbackContext


class BaseMiddleware:
    """BaseMiddleware is base class for catch data at start of `handle()`-method
        in `ButtonsHandler`, `CommandsHandler`, `ReplicasHandler` work (for logging events, detect DDoS-activity and etc.).

        Recommended to use `Middleware`-class as mixin-approach in your `ButtonsHandler`, `CommandsHandler`, `ReplicasHandler`.

    Example:

    .. highlight:: python
    .. code-block:: python

        class RemixMiddleware(BaseMiddleware):
            async def middleware(
                self,
                update: Update,
                context: CallbackContext,
            ) -> Union[Tuple[Update, CallbackContext], None]:
            ...

        class YourReplicasHandler(RemixMiddleware, ReplicasHandler):
           ...

    """

    async def middleware(
        self,
        update: Update,
        context: CallbackContext,
    ) -> Union[Tuple[Update, CallbackContext], None]:
        return update, context
