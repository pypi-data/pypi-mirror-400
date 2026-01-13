import io
import time
import json
import logging
import threading
from functools import wraps
from slack_sdk import WebClient
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log


log = logging.getLogger(__name__)


def check_connection(func):
    """
    Decorator to ensure Slack bot is connected before method execution.

    Args:
        func: The method to be decorated

    Returns:
        The wrapped function

    Raises:
        ValueError: If not connected
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.connected:
            raise ValueError(
                "Slack bot token is not set, please call configure_slack first or passed in token and recipient mapping")
        return func(self, *args, **kwargs)
    return wrapper


class SlackBot:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.client = None
        self._connected = False
        self.recipients = {}
        self.channel_list = {}

    @property
    def connected(self):
        return self._connected

    def id_from_name(self, name):
        slack_id = self.recipients.get(name)
        if slack_id is None:
            raise ValueError(f"Cannot find slack user {name}, did you forget to add?")
        return slack_id

    def connect(self, token: str):
        if not self.connected:
            self.client = WebClient(token=token)
            self._connected = True
        elif token == self.client.token:
            log.debug("Slack bot already connected")
        else:
            log.warning(f"Slack bot already connected with a different token: {self.client.token}")
        return self

    def add_recipient(self, recipient_id: str, recipient_name: str):
        self.recipients[recipient_id] = recipient_name

    @check_connection
    @retry(stop=stop_after_attempt(3),
           wait=wait_fixed(3),
           before_sleep=before_sleep_log(log, logging.ERROR)
           )
    def chat_post_message(self, blocks: list[dict], channel: str, text: str):
        try:
            resp = self.client.chat_postMessage(blocks=blocks, channel=channel, text=text)
        except Exception as e:
            log.error(f"Slack chat.postMessage failed. Recp: {channel}, Blocks content: {json.dumps(blocks, indent=2)}")
            raise
        return resp

    @check_connection
    def image_upload(self, buffer: io.BytesIO, file_name: str):
        response = self.client.files_upload_v2(
            file=buffer,
            filename=file_name
        )
        file_url = response["file"]["url_private"]
        time.sleep(1)
        return file_url


slack_bot = SlackBot()

