from telegram import Message, Update


from telegram_bot_discussion.dialogue import Dialogue, Phrase, Polemic
from telegram_bot_discussion.dialogue.replicas import NoNeedReactionReplica, StopReplica
from telegram_bot_discussion.functions import get_message


from internal.dialogues.replicas.text_from_user import TextFromUser
from internal.dialogues.replicas.text_from_bot import TextFromBot
from internal.dialogues.replicas.result import Result


def get_text_from_user(text_from_bot: str) -> Phrase:
    while True:
        update: Update = yield TextFromBot(text_from_bot)
        message = get_message(update)
        if not isinstance(message, Message):
            continue
        if message and message.text:
            return TextFromUser(value=message.text)


class TemplateDialogue(Dialogue):
    def dialogue(self) -> Polemic:
        _ = yield NoNeedReactionReplica(TextFromBot("Let's talk me some about you."))
        name: TextFromUser = yield from get_text_from_user("What is your name:")
        question: TextFromUser = yield from get_text_from_user("Enter your question:")
        contact: TextFromUser = yield from get_text_from_user(
            "Enter contact information:"
        )
        _ = yield NoNeedReactionReplica(
            Result(name.value, question.value, contact.value)
        )
        yield StopReplica(TextFromBot("Thank you. Our manager will contact you soon."))
