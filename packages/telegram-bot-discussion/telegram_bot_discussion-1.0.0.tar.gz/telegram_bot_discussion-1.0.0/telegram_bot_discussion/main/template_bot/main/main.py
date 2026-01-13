from telegram_bot_discussion.ext.command_button.command_button import CommandButton
from telegram_bot_discussion.button.buttons_map import ButtonsMap
from telegram_bot_discussion.command.commands_map import CommandsMap
from telegram_bot_discussion.ext.coder import BSV_Coder
from telegram_bot_discussion.ext.logger import (
    LogLevel,
    Printer,
)

import sys

sys.path.append(".")

from internal.bot.bot import Template
from internal.commands.start import StartCommand
from internal.commands.go import GoCommand
from internal.config.config import TemplateConfig
from internal.handlers.buttons_handler.buttons_handler import (
    TemplateButtonsHandler,
)
from internal.handlers.commands_handler.commands_handler import (
    TemplateCommandsHandler,
)
from internal.handlers.replicas_handler.replicas_handler import (
    TemplateReplicasHandler,
)


TOKEN = ""
SECRET = ""


def main():

    if not TOKEN:
        raise Exception("`TOKEN`-var value was not set.")
    if not SECRET:
        raise Exception("`SECRET`-var value was not set.")

    bot_config = TemplateConfig(
        token=TOKEN,
        secret=SECRET,
    )

    logger = Printer(
        "template_bot",
        LogLevel.DEBUG,
    )

    bot = Template(
        logger,
        bot_config,
    )
    bot.init_application()
    bot.set_replicas_handler(TemplateReplicasHandler())

    commands: CommandsMap = CommandsMap()
    commands.add(StartCommand)
    commands.add(GoCommand)
    commands_handler = TemplateCommandsHandler(commands)
    commands_handler.set_commands_map(commands)
    bot.set_commands_handler(commands_handler)

    coder = BSV_Coder(bot_config.secret)
    buttons: ButtonsMap = ButtonsMap()
    buttons.add(CommandButton)
    bot.set_buttons_handler(TemplateButtonsHandler(coder, buttons))

    bot.start()


# python3 template_bot/main/main.py
if __name__ == "__main__":
    main()
