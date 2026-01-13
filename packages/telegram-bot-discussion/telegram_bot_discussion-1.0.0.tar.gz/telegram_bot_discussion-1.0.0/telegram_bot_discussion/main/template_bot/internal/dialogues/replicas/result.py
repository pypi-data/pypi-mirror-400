from telegram import Update
from telegram.ext import CallbackContext


from telegram_bot_discussion import Contextual
from telegram_bot_discussion.dialogue.replicas import Replica
from telegram_bot_discussion.functions import get_from_id


from internal.bot.bot import Template


class Result(Replica):
    name: str
    message: str
    contact: str

    def __init__(
        self,
        name: str,
        message: str,
        contact: str,
    ):
        self.name = name
        self.message = message
        self.contact = contact

    async def as_reply(
        self,
        update: Update,
        context: CallbackContext,
    ):
        discussion: Template = Contextual[Template](context)()
        await discussion.bot().send_message(
            chat_id=get_from_id(update, context),
            text=str(
                {
                    "name": self.name,
                    "message": self.message,
                    "contact": self.contact,
                }
            ),
        )
