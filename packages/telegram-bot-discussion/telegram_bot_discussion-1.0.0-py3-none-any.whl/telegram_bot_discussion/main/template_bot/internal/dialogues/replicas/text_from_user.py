from telegram import Update
from telegram.ext import CallbackContext


from telegram_bot_discussion.dialogue.replicas.base import Replica


class TextFromUser(Replica):
    value: str

    def __init__(
        self,
        value: str,
    ):
        self.value = value

    async def as_reply(
        self,
        _: Update,
        __: CallbackContext,
    ): ...
