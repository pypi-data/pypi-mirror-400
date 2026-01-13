from telegram_bot_discussion.ext.command_button import CommandButton


class GoButton(CommandButton):

    class Meta(CommandButton.Meta):
        title: str = "Let's go"
