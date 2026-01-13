from telegram import (
    Update,
    User,
)


class FromUserWasNotFetched(Exception):
    def __str__(self):
        return "from_user was not fetched"


def get_from_user(update: Update) -> User:
    """get_from_user() try fetch `User` (from `update.message`, `update.callback_query`) of initiator (it can be User, Chat, Channel), which appeal to `Telegram-bot`.

    :raises FromUserWasNotFetched: When initiator was not detected.
    """
    if update.message and update.message.from_user:
        return update.message.from_user
    elif update.callback_query and update.callback_query.from_user:
        return update.callback_query.from_user
    else:
        raise FromUserWasNotFetched()
