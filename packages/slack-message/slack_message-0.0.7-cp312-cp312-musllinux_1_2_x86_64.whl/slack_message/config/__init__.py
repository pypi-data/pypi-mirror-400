import os
from typing import Optional

from slack_message.bot import slack_bot


def configure_slack(users_mapping: dict[str, str], token: Optional[str]=None):
    if token:
        os.environ['SLACK_BOT_TOKEN'] = token
        slack_bot.connect(token=token)
    else:
        slack_bot.connect()

    for user_name, channel_id in users_mapping.items():
        slack_bot.add_recipient(user_name, channel_id)
