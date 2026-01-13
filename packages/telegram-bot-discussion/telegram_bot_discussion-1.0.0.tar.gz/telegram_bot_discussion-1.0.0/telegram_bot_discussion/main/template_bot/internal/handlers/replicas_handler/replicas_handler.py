from telegram import Message, Update
from telegram.ext import CallbackContext


from telegram_bot_discussion import Contextual
from telegram_bot_discussion.ext.command_button.commands_buttons_menu import (
    CommandsButtonsMenu,
)
from telegram_bot_discussion.functions import (
    get_message,
    get_from_id,
)
from telegram_bot_discussion.handlers.replicas_handler.replicas_handler import (
    ReplicasHandler,
)


from internal.bot.bot import Template
from internal.buttons.go import GoButton
from internal.commands.go import GoCommand


class TemplateReplicasHandler(ReplicasHandler):
    async def when_there_are_no_any_dialog(
        self,
        update: Update,
        context: CallbackContext,
    ):
        message = get_message(update)
        if not isinstance(message, Message):
            return
        from_id = get_from_id(update)
        if not from_id:
            return

        discussion: Template = Contextual[Template](context)()
        await message.reply_text(
            text="Buttons menu",
            reply_markup=CommandsButtonsMenu(
                coder=discussion.get_buttons_handler().coder,
                commands_buttons=[
                    [
                        GoButton(from_id, GoCommand()),
                    ]
                ],
            ).as_keyboard(),
        )
