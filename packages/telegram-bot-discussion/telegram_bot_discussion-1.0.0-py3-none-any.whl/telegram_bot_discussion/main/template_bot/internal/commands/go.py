from telegram import Update
from telegram.ext import CallbackContext


from telegram_bot_discussion import Contextual
from telegram_bot_discussion.command import Command
from telegram_bot_discussion.functions import get_from_id


from internal.bot import Template
from internal.dialogues.template_dialogue import TemplateDialogue


class GoCommand(Command):

    class Meta(Command.Meta):
        action: str = "go"
        title: str = "Let's go!"

    async def on_call(self, update: Update, context: CallbackContext):
        discussion: Template = Contextual[Template](context)()
        await discussion.get_replicas_handler().start_dialogue(
            update,
            context,
            get_from_id(update),
            TemplateDialogue(),
        )
