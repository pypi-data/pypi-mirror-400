from telegram_bot_discussion.config import Config


class TemplateConfig(Config):
    secret: str

    def __init__(
        self,
        token: str,
        secret: str,
    ):
        self.token = token
        self.secret = secret
