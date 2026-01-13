from telegram import Update
from telegram.ext import CallbackContext


from telegram_bot_discussion.handlers.commands_handler.commands_handler import (
    CommandsHandler,
)
from telegram_bot_discussion.handlers.commands_handler import (
    CommandClassAccessDeny,
    CommandClassIsNotRegistered,
    CommandsMapIsEmpty,
)


class TemplateCommandsHandler(CommandsHandler):
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
            CommandClassAccessDeny,
            CommandsMapIsEmpty,
            CommandClassIsNotRegistered,
        ) as _:
            ...
