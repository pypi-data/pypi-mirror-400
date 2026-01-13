from telegram import Update
from telegram.ext import CallbackContext


from telegram_bot_discussion import Contextual
from telegram_bot_discussion import Discussion
from telegram_bot_discussion.dialogue.replicas.base import Replica
from telegram_bot_discussion.functions import get_from_id


class TextFromBot(Replica):
    value: str

    def __init__(self, value: str):
        self.value = value

    async def as_reply(
        self,
        update: Update,
        context: CallbackContext,
    ):
        discussion: Discussion = Contextual[Discussion](context)()
        await discussion.bot().send_message(
            chat_id=get_from_id(update),
            text=self.value,
        )
