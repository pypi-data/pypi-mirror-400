from telegram import Update
from telegram.ext import CallbackContext


from telegram_bot_discussion.handlers.buttons_handler.buttons_handler import (
    ButtonsHandler,
)
from telegram_bot_discussion.handlers.buttons_handler import (
    ButtonClassAccessDeny,
    ButtonClassIsNotRegistered,
    ButtonDataSignificationError,
    ButtonClassLifeTimeOverflow,
    ButtonsMapIsEmpty,
)


class TemplateButtonsHandler(ButtonsHandler):
    async def handle(
        self,
        update: Update,
        context: CallbackContext,
    ):
        try:
            _ = await super().handle(
                update,
                context,
            )
        except (
            ButtonClassAccessDeny,
            ButtonClassIsNotRegistered,
            ButtonDataSignificationError,
            ButtonClassLifeTimeOverflow,
            ButtonsMapIsEmpty,
            Exception,
        ) as _:
            ...
