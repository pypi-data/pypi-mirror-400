from typing import Union
from abc import ABC, abstractmethod

from slack_message.bot import slack_bot, SlackBot
from slack_message.blocks import Header, Divider, Section, Context


class BaseSlackMessage(ABC):
    slack_bot: SlackBot = slack_bot

    def __init__(self, **kwargs):
        self.header = kwargs.get("header")
        self.sub_header = kwargs.get("sub_header")
        self.preview = kwargs.get("preview")
        self.footnote = kwargs.get("footnote")
        self.blocks = kwargs.get("blocks")
        self.preview = self.preview or self.header or self.sub_header or 'You got a new message'

    def __add__(self, other):
        combined_blocks = self.build_blocks() + other.build_blocks()
        combined_messages = CombinedSlackMessage(combined_blocks)
        if self.preview:
            combined_messages.preview = self.preview
        elif other.preview:
            combined_messages.preview = other.preview
        else:
            combined_messages.preview = "New Message"
        return combined_messages

    @abstractmethod
    def build_blocks(self) -> list:
        pass

    def build_image(self):
        pass

    def add_header(self):
        if self.header:
            return Header.plain_text(self.header) + Divider.divider()
        else:
            return []

    def add_sub_header(self):
        if self.sub_header:
            return Section.mrkdwn(self.sub_header)
        else:
            return []

    def add_footnote(self):
        if self.footnote:
            return Context.mrkdwn(self.footnote)
        else:
            return []

    def validate_blocks(self, blocks: list[dict]) -> list:
        return blocks

    def send(self, recipients: Union[list[str], str],
             token: str = None,
             recipient_mapping: dict = None
             ):
        if token and not self.slack_bot.connected:
            self.slack_bot.connect(token)
        if isinstance(recipients, str):
            recipients = [recipients]
        header_blocks = self.add_header()
        subheader_blocks = self.add_sub_header()
        main_blocks = self.build_blocks()
        footnote_blocks = self.add_footnote()
        blocks = header_blocks + subheader_blocks + main_blocks + footnote_blocks
        blocks = self.validate_blocks(blocks)
        for recipient in recipients:
            if isinstance(recipient, str):
                if recipient_mapping and recipient in recipient_mapping:
                    slack_id = recipient_mapping[recipient]
                else:
                    slack_id = self.slack_bot.id_from_name(recipient)
                self.slack_bot.chat_post_message(channel=slack_id,
                                                 blocks=blocks,
                                                 text=self.preview
                                                )
            else:
                raise ValueError("recipient must be a string")
    def send_image(self, recipients: Union[list[str], str]):
        pass


class CombinedSlackMessage(BaseSlackMessage):
    def __init__(self, blocks: list[dict]):
        super().__init__(**{})
        self.blocks = blocks

    def build_blocks(self) -> list:
        return self.blocks


class BaseTemplate(ABC):

    @abstractmethod
    def __init__(self):
        self.msg = None

    def send(self, recipients: Union[list[str], str]):
        self.msg.send(recipients)
