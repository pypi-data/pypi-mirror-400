from typing import Union


from telegram import (
    Update,
)
from telegram.ext import CallbackContext


__FROM_ID = "from_id"


class FromIdWasNotFetched(Exception):
    def __str__(self):
        return "from_user.id was not fetched"


def get_from_id(
    update: Update,
    context: Union[CallbackContext, None] = None,
) -> int:
    """get_from_id() try fetch `from_user.id` (from `update.message`, `update.callback_query` or `context`) of initiator (`User`), which appeal to `Telegram-bot`.

    :raises FromIdWasNotFetched: When initiator ID was not detected.
    """
    if update.message and update.message.from_user:
        if context:
            context.bot_data[__FROM_ID] = update.message.from_user.id
        return update.message.from_user.id
    # TODO: test
    elif update.callback_query and update.callback_query.from_user:
        if context:
            context.bot_data[__FROM_ID] = update.callback_query.from_user.id
        return update.callback_query.from_user.id
    elif context and context.bot_data.get(__FROM_ID):
        return context.bot_data.get(__FROM_ID)
    else:
        raise FromIdWasNotFetched()
