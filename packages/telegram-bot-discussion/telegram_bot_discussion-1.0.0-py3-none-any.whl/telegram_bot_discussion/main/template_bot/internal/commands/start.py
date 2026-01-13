from telegram import Update
from telegram.ext import CallbackContext


from telegram_bot_discussion.command import Command


class StartCommand(Command):

    class Meta(Command.Meta):
        action: str = "start"

    async def on_call(
        self,
        update: Update,
        context: CallbackContext,
    ): ...
